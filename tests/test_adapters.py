from pi_learn.adapters import completion_to_tool_records, trace_from_verifiers_completion
from pi_learn.tasks import load_tasks
from pi_learn.types import ScoreResult


def test_completion_to_tool_records_pairs_calls_and_results():
    completion = [
        {
            "role": "assistant",
            "tool_calls": [
                {
                    "id": "call-1",
                    "function": {
                        "name": "bash",
                        "arguments": "{\"command\":\"pwd\"}",
                    },
                }
            ],
        },
        {
            "role": "tool",
            "tool_call_id": "call-1",
            "content": "{\"output\":\"/tmp\",\"exit_code\":0,\"error\":null}",
        },
        {"role": "assistant", "content": "The directory is /tmp."},
    ]

    calls, results = completion_to_tool_records(completion)

    assert calls[0].tool_name == "bash"
    assert calls[0].args == {"command": "pwd"}
    assert results[0].success is True
    assert results[0].tool_name == "bash"


def test_trace_from_verifiers_completion_builds_run_events():
    task = load_tasks()[0]
    trace = trace_from_verifiers_completion(
        task=task,
        completion=[{"role": "assistant", "content": "Jupiter is largest."}],
        score=ScoreResult(reward=1.0, dimensions={"task_completion": 1.0}),
        run_id="run-1",
        started_at=10,
        completed_at=20,
    )

    assert trace.run_id == "run-1"
    assert trace.task_id == task.id
    assert trace.output == {
        "response": "Jupiter is largest.",
        "answer": task.verify,
    }
    assert trace.duration_ms == 10
    assert trace.score is not None
    assert trace.score.reward == 1.0
