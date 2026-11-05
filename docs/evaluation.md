
# Anomaly Detection Evaluation

## 1. Objective

Evaluate five compensation-related anomaly detection rules using a controlled synthetic dataset with independently generated ground-truth labels.

## 2. Dataset

- Total records: 270
- Anomaly records: 250
- Clean control records: 20
- Anomaly types: 5
- Positive examples per anomaly type: 50

## 3. Evaluated Anomaly Types

1. Expired compensation band
2. Incorrect FTE salary normalization
3. Missing foreign exchange rate
4. Approved adjustment without an approval event
5. Incomparable roles grouped without a comparison rationale

## 4. Evaluation Method

The detector reads the generated anomaly cases and produces predictions without accessing ground-truth labels.

The evaluation module independently compares predictions with ground truth using entity ID and issue type.

Metrics calculated:

- True Positives (TP)
- False Positives (FP)
- False Negatives (FN)
- Precision
- Recall
- F1-score

## 5. Results

| Metric | Result |
|---|---:|
| True Positives | 250 |
| False Positives | 0 |
| False Negatives | 0 |
| Precision | 1.00 |
| Recall | 1.00 |
| F1-score | 1.00 |

All five anomaly types achieved an F1-score of 1.00 on this benchmark.

## 6. Limitations

This is a controlled synthetic benchmark. The anomaly cases were deliberately constructed to test specific detection rules.

The results demonstrate rule correctness on the generated scenarios. They should not be interpreted as evidence of equivalent performance on real-world compensation data.

Further evaluation using independently sourced, manually reviewed compensation records is required to assess generalization.
