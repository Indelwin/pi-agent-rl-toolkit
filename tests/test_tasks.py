from pi_learn.tasks import category_counts, load_tasks


def test_load_tasks_from_bundled_environment_data():
    tasks = load_tasks()

    assert len(tasks) == 598
    assert tasks[0].id == "syn_0001"
    assert tasks[0].category == "zero_tool"
    assert tasks[0].requires_tool is False
    assert tasks[0].max_tool_calls == 0


def test_category_counts_are_deterministic():
    counts = category_counts(load_tasks())

    assert counts == {
        "code_execution": 100,
        "file_ops": 54,
        "multi_step": 32,
        "planning": 32,
        "self_improvement": 34,
        "terminal": 99,
        "zero_tool": 247,
    }
