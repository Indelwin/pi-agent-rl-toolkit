from pi_learn.mining import mine_examples_from_traces
from pi_learn.traces import TraceStore
from pi_learn.types import RolloutTrace, ScoreResult


def test_mines_completed_examples_from_store(tmp_path):
    store = TraceStore(tmp_path / "traces.sqlite")
    store.insert_run(
        RolloutTrace(
            run_id="good",
            task_id="task-1",
            category="file_ops",
            program_id="pi-agent-env",
            input={"prompt": "write file"},
            output={"response": "done"},
            status="completed",
            score=ScoreResult(reward=0.9),
            started_at=2,
            completed_at=3,
            duration_ms=1,
        )
    )
    store.insert_run(
        RolloutTrace(
            run_id="low",
            program_id="pi-agent-env",
            input={"prompt": "write file"},
            output={"response": "bad"},
            status="completed",
            score=ScoreResult(reward=0.1),
            started_at=1,
            completed_at=2,
            duration_ms=1,
        )
    )

    examples = mine_examples_from_traces(
        store,
        program_id="pi-agent-env",
        min_reward=0.5,
    )
    store.close()

    assert len(examples) == 1
    assert examples[0].id == "good"
    assert examples[0].input == {"prompt": "write file"}
    assert examples[0].output == {"response": "done"}
    assert examples[0].score == 0.9
