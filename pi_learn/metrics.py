"""Metric helpers for rollout scoring and optimizer mining."""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import Any

MetricFn = Callable[[dict[str, Any], dict[str, Any]], float | Awaitable[float]]


def exact_field_match(
    field: str,
    *,
    case_sensitive: bool = False,
    trim: bool = True,
) -> MetricFn:
    """Return 1.0 when prediction and example output match exactly."""

    def metric(prediction: dict[str, Any], example: dict[str, Any]) -> float:
        expected = _normalize(_field(example, "output", field), case_sensitive, trim)
        actual = _normalize(prediction.get(field), case_sensitive, trim)
        if expected == "" and actual == "":
            return 0.0
        return 1.0 if expected == actual else 0.0

    return metric


def contains_field_match(field: str) -> MetricFn:
    """Return 1.0 when prediction contains the expected field text."""

    def metric(prediction: dict[str, Any], example: dict[str, Any]) -> float:
        expected = _stringify(_field(example, "output", field)).strip().lower()
        actual = _stringify(prediction.get(field)).strip().lower()
        if expected == "":
            return 0.0
        return 1.0 if expected in actual else 0.0

    return metric


def jaccard_field_similarity(field: str) -> MetricFn:
    """Token-set Jaccard similarity for a string output field."""

    def metric(prediction: dict[str, Any], example: dict[str, Any]) -> float:
        expected = _tokenize(_field(example, "output", field))
        actual = _tokenize(prediction.get(field))
        if not expected and not actual:
            return 0.0
        union = expected | actual
        if not union:
            return 0.0
        return len(expected & actual) / len(union)

    return metric


def all_fields_match(fields: list[str]) -> MetricFn:
    """Return 1.0 only when all fields match exactly."""

    metrics = [exact_field_match(field) for field in fields]

    def metric(prediction: dict[str, Any], example: dict[str, Any]) -> float:
        for field_metric in metrics:
            if field_metric(prediction, example) < 1.0:
                return 0.0
        return 1.0

    return metric


def average_metrics(metrics: list[MetricFn]) -> MetricFn:
    """Return the mean score from multiple synchronous metrics."""

    def metric(prediction: dict[str, Any], example: dict[str, Any]) -> float:
        if not metrics:
            return 0.0
        total = 0.0
        for item in metrics:
            value = item(prediction, example)
            if hasattr(value, "__await__"):
                raise TypeError("average_metrics only supports synchronous metrics")
            total += _clamp01(float(value))
        return total / len(metrics)

    return metric


def _field(container: dict[str, Any], section: str, field: str) -> Any:
    value = container.get(section, {})
    if isinstance(value, dict):
        return value.get(field)
    return None


def _normalize(value: Any, case_sensitive: bool, trim: bool) -> str:
    text = _stringify(value)
    if trim:
        text = text.strip()
    if not case_sensitive:
        text = text.lower()
    return text


def _stringify(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value
    return str(value)


def _tokenize(value: Any) -> set[str]:
    return {
        token
        for token in _stringify(value).strip().lower().split()
        if token
    }


def _clamp01(value: float) -> float:
    if value < 0.0:
        return 0.0
    if value > 1.0:
        return 1.0
    return value
