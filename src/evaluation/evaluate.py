
import json
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]

GROUND_TRUTH_PATH = ROOT / "data" / "ground_truth" / "ground_truth.csv"
PREDICTIONS_PATH = ROOT / "outputs" / "evaluation_predictions.csv"
METRICS_PATH = ROOT / "outputs" / "evaluation_metrics.json"


def calculate_metrics(actual, predicted):

    tp = len(actual & predicted)
    fp = len(predicted - actual)
    fn = len(actual - predicted)

    precision = tp / (tp + fp) if tp + fp else 0
    recall = tp / (tp + fn) if tp + fn else 0

    f1 = (
        2 * precision * recall / (precision + recall)
        if precision + recall else 0
    )

    return {
        "true_positives": tp,
        "false_positives": fp,
        "false_negatives": fn,
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "f1_score": round(f1, 4)
    }


def evaluate():

    ground_truth = pd.read_csv(GROUND_TRUTH_PATH)
    predictions = pd.read_csv(PREDICTIONS_PATH)

    actual = set(
        zip(ground_truth["entity_id"], ground_truth["issue_type"])
    )

    predicted = set(
        zip(predictions["entity_id"], predictions["issue_type"])
    )

    issue_types = sorted(
        set(ground_truth["issue_type"]) |
        set(predictions["issue_type"])
    )

    per_issue = {}

    for issue in issue_types:

        actual_issue = {
            item for item in actual if item[1] == issue
        }

        predicted_issue = {
            item for item in predicted if item[1] == issue
        }

        per_issue[issue] = calculate_metrics(
            actual_issue,
            predicted_issue
        )

    overall = calculate_metrics(actual, predicted)

    report = {
        "evaluation_type": "Controlled synthetic anomaly benchmark",
        "ground_truth_cases": len(actual),
        "predicted_cases": len(predicted),
        "overall": overall,
        "per_issue_type": per_issue
    }

    METRICS_PATH.parent.mkdir(parents=True, exist_ok=True)

    with open(METRICS_PATH, "w", encoding="utf-8") as file:
        json.dump(report, file, indent=4)

    print("\nOVERALL METRICS")
    print(json.dumps(overall, indent=4))

    print("\nPER ISSUE TYPE")
    for issue, metrics in per_issue.items():
        print(f"\n{issue}")
        print(json.dumps(metrics, indent=4))

    print(f"\nReport saved to: {METRICS_PATH}")


if __name__ == "__main__":
    evaluate()
