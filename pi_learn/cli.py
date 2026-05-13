"""Command line interface for pi_learn artifacts."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from .mining import mine_examples_from_traces
from .traces import TraceStore


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    if not hasattr(args, "handler"):
        parser.print_help()
        return 0
    return int(args.handler(args))


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="pi-learn")
    subcommands = parser.add_subparsers(dest="command")

    trace = subcommands.add_parser("trace", help="Inspect trace artifacts")
    trace_sub = trace.add_subparsers(dest="trace_command")

    trace_list = trace_sub.add_parser("list", help="List stored traces")
    _add_db(trace_list)
    trace_list.add_argument("--program-id")
    trace_list.add_argument("--status")
    trace_list.add_argument("--category")
    trace_list.add_argument("--limit", type=int, default=20)
    trace_list.set_defaults(handler=_trace_list)

    trace_show = trace_sub.add_parser("show", help="Show one stored trace as JSON")
    _add_db(trace_show)
    trace_show.add_argument("run_id")
    trace_show.set_defaults(handler=_trace_show)

    trace_export = trace_sub.add_parser("export", help="Export traces to JSONL")
    _add_db(trace_export)
    trace_export.add_argument("--output", "-o", required=True)
    trace_export.add_argument("--program-id")
    trace_export.add_argument("--status")
    trace_export.add_argument("--category")
    trace_export.add_argument("--limit", type=int, default=1000)
    trace_export.set_defaults(handler=_trace_export)

    examples = subcommands.add_parser("examples", help="Mine optimizer examples")
    examples_sub = examples.add_subparsers(dest="examples_command")

    mine = examples_sub.add_parser("mine", help="Mine examples from completed traces")
    _add_db(mine)
    mine.add_argument("--program-id")
    mine.add_argument("--min-reward", type=float)
    mine.add_argument("--limit", type=int, default=100)
    mine.add_argument("--output", "-o")
    mine.set_defaults(handler=_examples_mine)

    return parser


def _add_db(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--db",
        default="pi-learn-traces.sqlite",
        help="Path to trace SQLite database",
    )


def _trace_list(args: argparse.Namespace) -> int:
    with TraceStore(args.db) as store:
        runs = store.list_runs(
            program_id=args.program_id,
            status=args.status,
            category=args.category,
            limit=args.limit,
        )
    if not runs:
        print("No traces found.")
        return 0
    for run in runs:
        reward = "" if run.score is None else f" reward={run.score.reward:.3f}"
        print(
            f"{run.run_id}\t{run.status}\t{run.program_id}\t"
            f"{run.task_id or '-'}\t{run.category or '-'}{reward}"
        )
    return 0


def _trace_show(args: argparse.Namespace) -> int:
    with TraceStore(args.db) as store:
        run = store.get_run(args.run_id)
    if run is None:
        print(f"Trace not found: {args.run_id}", file=sys.stderr)
        return 1
    print(_json(run.to_dict()))
    return 0


def _trace_export(args: argparse.Namespace) -> int:
    with TraceStore(args.db) as store:
        count = store.export_jsonl(
            args.output,
            program_id=args.program_id,
            status=args.status,
            category=args.category,
            limit=args.limit,
        )
    print(f"Exported {count} traces to {args.output}")
    return 0


def _examples_mine(args: argparse.Namespace) -> int:
    with TraceStore(args.db) as store:
        examples = mine_examples_from_traces(
            store,
            program_id=args.program_id,
            min_reward=args.min_reward,
            limit=args.limit,
        )
    lines = [_json(example.to_dict()) for example in examples]
    if args.output:
        path = Path(args.output)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("\n".join(lines) + ("\n" if lines else ""))
        print(f"Wrote {len(lines)} examples to {args.output}")
    else:
        for line in lines:
            print(line)
    return 0


def _json(value: dict[str, Any]) -> str:
    return json.dumps(value, indent=2, sort_keys=True)


if __name__ == "__main__":
    raise SystemExit(main())
