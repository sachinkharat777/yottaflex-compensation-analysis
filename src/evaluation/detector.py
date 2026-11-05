
import pandas as pd
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CASES_PATH = ROOT / "data" / "generated" / "anomaly_cases.csv"
OUTPUT_PATH = ROOT / "outputs" / "evaluation_predictions.csv"


def detect_anomalies():

    df = pd.read_csv(CASES_PATH)
    predictions = []

    for _, row in df.iterrows():

        entity_id = row["entity_id"]

        # 1. Expired compensation band
        if row["band_effective_end"] <= row["as_of_date"]:
            predictions.append((entity_id, "EXPIRED_COMPENSATION_BAND"))

        # 2. Incorrect FTE normalization
        if (
            row["fte"] < 1
            and abs(
                row["reported_normalized_salary"]
                - row["annual_base_salary"]
            ) < 0.01
        ):
            predictions.append((entity_id, "FTE_NORMALIZATION_ERROR"))

        # 3. Missing foreign exchange rate
        if not bool(row["fx_rate_present"]):
            predictions.append((entity_id, "MISSING_FX_RATE"))

        # 4. Approved adjustment without approval event
        if (
            row["proposal_status"] == "APPROVED"
            and not bool(row["approval_event_present"])
        ):
            predictions.append((entity_id, "UNAPPROVED_ADJUSTMENT"))

                # 5. Incomparable roles grouped without rationale
        if (
            row["role_count_in_group"] > 1
            and (
                pd.isna(row["comparison_rationale"])
                or not str(row["comparison_rationale"]).strip()
            )
        ):
            predictions.append((entity_id, "INCOMPARABLE_ROLE_GROUPING"))
            
    result = pd.DataFrame(
        predictions,
        columns=["entity_id", "issue_type"]
    )

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    result.to_csv(OUTPUT_PATH, index=False)

    print("Detection completed.")
    print(f"Predictions: {len(result)}")
    print(f"Saved to: {OUTPUT_PATH}")

    return result


if __name__ == "__main__":
    detect_anomalies()
