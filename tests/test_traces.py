from pi_learn.traces import TraceStore
from pi_learn.types import RolloutEvent, RolloutTrace, ScoreResult


def make_trace(run_id: str = "run-1") -> RolloutTrace:
    return RolloutTrace(
        run_id=run_id,
        task_id="task-1",
        category="terminal",
        program_id="pi-agent-env",
        program_version="0.1.0",
        model="test-model",
        provider="test-provider",
        input={"prompt": "list files"},
        output={"response": "done"},
        status="completed",
        score=ScoreResult(reward=0.75, dimensions={"task_completion": 0.75}),
        started_at=1000,
        completed_at=1250,
        duration_ms=250,
        events=[
            RolloutEvent(
                run_id=run_id,
                ordinal=0,
                topic="tool.call",
                payload={"tool_name": "bash"},
                created_at=1010,
            )
        ],
    )


def test_trace_store_inserts_lists_and_loads_events(tmp_path):
    store = TraceStore(tmp_path / "traces.sqlite")
    trace = make_trace()

    store.insert_run(trace)

    runs = store.list_runs(program_id="pi-agent-env", status="completed")
    loaded = store.get_run("run-1")
    store.close()

    assert [run.run_id for run in runs] == ["run-1"]
    assert loaded is not None
    assert loaded.score is not None
    assert loaded.score.reward == 0.75
    assert loaded.events[0].payload == {"tool_name": "bash"}


def test_trace_store_exports_and_imports_jsonl(tmp_path):
    source = TraceStore(tmp_path / "source.sqlite")
    source.insert_run(make_trace("run-a"))
    export_path = tmp_path / "export.jsonl"

    count = source.export_jsonl(export_path)
    target = TraceStore(tmp_path / "target.sqlite")
    imported = target.import_jsonl(export_path)
    loaded = target.get_run("run-a")
    source.close()
    target.close()

    assert count == 1
    assert imported == 1
    assert loaded is not None
    assert loaded.events[0].topic == "tool.call"


def test_trace_store_stats(tmp_path):
    store = TraceStore(tmp_path / "traces.sqlite")
    store.insert_run(make_trace("run-a"))
    store.insert_run(
        RolloutTrace(
            run_id="run-b",
            program_id="other",
            input={},
            output=None,
            status="failed",
            error="boom",
            started_at=1000,
            completed_at=1001,
            duration_ms=1,
        )
    )

    stats = store.stats()
    store.close()

    assert stats["total"] == 2
    assert stats["by_status"] == {"completed": 1, "failed": 1}
    assert stats["by_program"] == {"pi-agent-env": 1, "other": 1}
