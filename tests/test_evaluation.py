
import pandas as pd

from src.evaluation.evaluate import calculate_metrics


def test_perfect_detection():
    actual = {("E1", "MISSING_FX_RATE")}
    predicted = {("E1", "MISSING_FX_RATE")}

    result = calculate_metrics(actual, predicted)

    assert result["true_positives"] == 1
    assert result["false_positives"] == 0
    assert result["false_negatives"] == 0
    assert result["f1_score"] == 1.0


def test_false_positive():
    actual = {("E1", "MISSING_FX_RATE")}
    predicted = {
        ("E1", "MISSING_FX_RATE"),
        ("E2", "MISSING_FX_RATE")
    }

    result = calculate_metrics(actual, predicted)

    assert result["false_positives"] == 1
    assert result["precision"] == 0.5


def test_false_negative():
    actual = {
        ("E1", "MISSING_FX_RATE"),
        ("E2", "MISSING_FX_RATE")
    }
    predicted = {("E1", "MISSING_FX_RATE")}

    result = calculate_metrics(actual, predicted)

    assert result["false_negatives"] == 1
    assert result["recall"] == 0.5


def test_no_predictions():
    actual = {("E1", "MISSING_FX_RATE")}
    predicted = set()

    result = calculate_metrics(actual, predicted)

    assert result["precision"] == 0
    assert result["recall"] == 0
    assert result["f1_score"] == 0
