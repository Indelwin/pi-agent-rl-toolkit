from pi_learn.metrics import (
    all_fields_match,
    average_metrics,
    contains_field_match,
    exact_field_match,
    jaccard_field_similarity,
)


def test_exact_field_match_normalizes_case_and_whitespace():
    metric = exact_field_match("answer")

    score = metric({"answer": "  Jupiter "}, {"output": {"answer": "jupiter"}})

    assert score == 1.0


def test_contains_field_match_allows_longer_responses():
    metric = contains_field_match("answer")

    score = metric(
        {"answer": "The answer is Jupiter."},
        {"output": {"answer": "jupiter"}},
    )

    assert score == 1.0


def test_jaccard_field_similarity_scores_token_overlap():
    metric = jaccard_field_similarity("answer")

    score = metric(
        {"answer": "red blue"},
        {"output": {"answer": "red green"}},
    )

    assert score == 1 / 3


def test_all_fields_match_is_all_or_nothing():
    metric = all_fields_match(["a", "b"])

    assert metric({"a": "x", "b": "y"}, {"output": {"a": "x", "b": "y"}}) == 1.0
    assert metric({"a": "x", "b": "z"}, {"output": {"a": "x", "b": "y"}}) == 0.0


def test_average_metrics_clamps_and_averages():
    metric = average_metrics([
        lambda _prediction, _example: 2.0,
        lambda _prediction, _example: -1.0,
    ])

    assert metric({}, {"output": {}}) == 0.5
