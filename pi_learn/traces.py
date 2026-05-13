"""SQLite storage and JSONL portability for rollout traces."""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any

from .types import RolloutEvent, RolloutTrace, ScoreResult

_SCHEMA = """
PRAGMA journal_mode = WAL;
PRAGMA synchronous = NORMAL;
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS runs (
  run_id TEXT PRIMARY KEY,
  task_id TEXT,
  category TEXT,
  program_id TEXT NOT NULL,
  program_version TEXT,
  model TEXT,
  provider TEXT,
  input_json TEXT NOT NULL,
  output_json TEXT,
  status TEXT NOT NULL,
  score_json TEXT,
  error TEXT,
  started_at INTEGER NOT NULL,
  completed_at INTEGER NOT NULL,
  duration_ms INTEGER NOT NULL,
  meta_json TEXT
);

CREATE INDEX IF NOT EXISTS runs_by_program ON runs(program_id, started_at DESC);
CREATE INDEX IF NOT EXISTS runs_by_status ON runs(status);
CREATE INDEX IF NOT EXISTS runs_by_category ON runs(category);
CREATE INDEX IF NOT EXISTS runs_by_model ON runs(model);
CREATE INDEX IF NOT EXISTS runs_by_started_at ON runs(started_at);

CREATE TABLE IF NOT EXISTS run_events (
  run_id TEXT NOT NULL,
  ordinal INTEGER NOT NULL,
  topic TEXT NOT NULL,
  payload_json TEXT NOT NULL,
  created_at INTEGER NOT NULL,
  PRIMARY KEY (run_id, ordinal),
  FOREIGN KEY (run_id) REFERENCES runs(run_id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS run_events_by_topic ON run_events(topic);

CREATE TABLE IF NOT EXISTS schema_meta (
  key TEXT PRIMARY KEY,
  value TEXT NOT NULL
);

INSERT OR IGNORE INTO schema_meta (key, value) VALUES ('schema_version', '1');
"""


class TraceStore:
    """Durable trace store backed by SQLite."""

    def __init__(self, path: str | Path):
        self.path = str(path)
        if self.path != ":memory:":
            Path(self.path).expanduser().parent.mkdir(parents=True, exist_ok=True)
            self.path = str(Path(self.path).expanduser())
        self._db = sqlite3.connect(self.path)
        self._db.row_factory = sqlite3.Row
        self._closed = False
        self._db.executescript(_SCHEMA)

    def close(self) -> None:
        if self._closed:
            return
        self._closed = True
        self._db.close()

    def __enter__(self) -> "TraceStore":
        return self

    def __exit__(self, *_args: object) -> None:
        self.close()

    def insert_run(self, trace: RolloutTrace) -> None:
        """Insert or replace a run and its events atomically."""

        self._assert_open()
        with self._db:
            self._db.execute(
                """
                INSERT OR REPLACE INTO runs (
                  run_id, task_id, category, program_id, program_version,
                  model, provider, input_json, output_json, status, score_json,
                  error, started_at, completed_at, duration_ms, meta_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    trace.run_id,
                    trace.task_id,
                    trace.category,
                    trace.program_id,
                    trace.program_version,
                    trace.model,
                    trace.provider,
                    _to_json(trace.input),
                    None if trace.output is None else _to_json(trace.output),
                    trace.status,
                    None if trace.score is None else _to_json(trace.score.to_dict()),
                    trace.error,
                    trace.started_at,
                    trace.completed_at,
                    trace.duration_ms,
                    _to_json(trace.meta),
                ),
            )
            self._db.execute("DELETE FROM run_events WHERE run_id = ?", (trace.run_id,))
            self._db.executemany(
                """
                INSERT INTO run_events (
                  run_id, ordinal, topic, payload_json, created_at
                ) VALUES (?, ?, ?, ?, ?)
                """,
                [
                    (
                        event.run_id,
                        event.ordinal,
                        event.topic,
                        _to_json(event.payload),
                        event.created_at,
                    )
                    for event in trace.events
                ],
            )

    def get_run(self, run_id: str) -> RolloutTrace | None:
        """Return a run with its events, or None when absent."""

        self._assert_open()
        row = self._db.execute(
            "SELECT * FROM runs WHERE run_id = ?",
            (run_id,),
        ).fetchone()
        if row is None:
            return None
        return _row_to_trace(row, self.list_events(run_id))

    def list_runs(
        self,
        *,
        program_id: str | None = None,
        status: str | None = None,
        category: str | None = None,
        model: str | None = None,
        started_after: int | None = None,
        started_before: int | None = None,
        limit: int = 100,
        offset: int = 0,
        order: str = "desc",
    ) -> list[RolloutTrace]:
        """List run rows. Events are omitted for cheap listing."""

        self._assert_open()
        clauses: list[str] = []
        params: list[Any] = []
        if program_id is not None:
            clauses.append("program_id = ?")
            params.append(program_id)
        if status is not None:
            clauses.append("status = ?")
            params.append(status)
        if category is not None:
            clauses.append("category = ?")
            params.append(category)
        if model is not None:
            clauses.append("model = ?")
            params.append(model)
        if started_after is not None:
            clauses.append("started_at >= ?")
            params.append(started_after)
        if started_before is not None:
            clauses.append("started_at <= ?")
            params.append(started_before)
        where = f"WHERE {' AND '.join(clauses)}" if clauses else ""
        sort = "ASC" if order == "asc" else "DESC"
        rows = self._db.execute(
            f"""
            SELECT * FROM runs
            {where}
            ORDER BY started_at {sort}
            LIMIT ? OFFSET ?
            """,
            (*params, limit, offset),
        ).fetchall()
        return [_row_to_trace(row, []) for row in rows]

    def list_events(self, run_id: str) -> list[RolloutEvent]:
        """Return captured events for a run in insertion order."""

        self._assert_open()
        rows = self._db.execute(
            """
            SELECT * FROM run_events
            WHERE run_id = ?
            ORDER BY ordinal ASC
            """,
            (run_id,),
        ).fetchall()
        return [
            RolloutEvent(
                run_id=str(row["run_id"]),
                ordinal=int(row["ordinal"]),
                topic=str(row["topic"]),
                payload=_from_json(row["payload_json"], None),
                created_at=int(row["created_at"]),
            )
            for row in rows
        ]

    def export_jsonl(
        self,
        path: str | Path,
        *,
        program_id: str | None = None,
        status: str | None = None,
        category: str | None = None,
        limit: int = 1000,
    ) -> int:
        """Export filtered traces to JSONL. Returns the number exported."""

        runs = self.list_runs(
            program_id=program_id,
            status=status,
            category=category,
            limit=limit,
        )
        count = 0
        output_path = Path(path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with output_path.open("w") as handle:
            for run in runs:
                full = self.get_run(run.run_id)
                if full is None:
                    continue
                handle.write(_to_json(full.to_dict()) + "\n")
                count += 1
        return count

    def import_jsonl(self, path: str | Path) -> int:
        """Import traces from JSONL. Returns the number imported."""

        count = 0
        with Path(path).open() as handle:
            for line in handle:
                if not line.strip():
                    continue
                trace = RolloutTrace.from_mapping(json.loads(line))
                self.insert_run(trace)
                count += 1
        return count

    def stats(self) -> dict[str, Any]:
        """Return small aggregate stats for CLI and UI surfaces."""

        self._assert_open()
        total = self._db.execute("SELECT COUNT(*) AS count FROM runs").fetchone()["count"]
        by_status = {
            row["status"]: row["count"]
            for row in self._db.execute(
                "SELECT status, COUNT(*) AS count FROM runs GROUP BY status"
            ).fetchall()
        }
        by_program = {
            row["program_id"]: row["count"]
            for row in self._db.execute(
                """
                SELECT program_id, COUNT(*) AS count
                FROM runs
                GROUP BY program_id
                ORDER BY count DESC
                """
            ).fetchall()
        }
        return {
            "total": total,
            "by_status": by_status,
            "by_program": by_program,
        }

    def _assert_open(self) -> None:
        if self._closed:
            raise RuntimeError("TraceStore is closed")


def _row_to_trace(row: sqlite3.Row, events: list[RolloutEvent]) -> RolloutTrace:
    score_data = _from_json(row["score_json"], None)
    status = str(row["status"])
    if status not in ("completed", "failed", "cancelled"):
        status = "failed"
    return RolloutTrace(
        run_id=str(row["run_id"]),
        task_id=row["task_id"],
        category=row["category"],
        program_id=str(row["program_id"]),
        program_version=row["program_version"],
        model=row["model"],
        provider=row["provider"],
        input=_from_json(row["input_json"], {}),
        output=None if row["output_json"] is None else _from_json(row["output_json"], {}),
        status=status,
        score=None if score_data is None else ScoreResult.from_mapping(score_data),
        error=row["error"],
        started_at=int(row["started_at"]),
        completed_at=int(row["completed_at"]),
        duration_ms=int(row["duration_ms"]),
        meta=_from_json(row["meta_json"], {}),
        events=events,
    )


def _to_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def _from_json(raw: str | None, fallback: Any) -> Any:
    if raw is None:
        return fallback
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return fallback
