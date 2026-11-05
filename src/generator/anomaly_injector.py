import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

GENERATED_DIR = ROOT / "data" / "generated"
GROUND_TRUTH_DIR = ROOT / "data" / "ground_truth"

CASES_FILE = GENERATED_DIR / "anomaly_cases.csv"
GROUND_TRUTH_FILE = GROUND_TRUTH_DIR / "ground_truth.csv"

AS_OF_DATE = "2026-12-31"
CASES_PER_ISSUE = 50
CLEAN_CASES = 20

ISSUES = {
    "EXPIRED_COMPENSATION_BAND": "Compensation band expired on or before the analysis date",
    "FTE_NORMALIZATION_ERROR": "Reported normalized salary does not equal salary divided by FTE",
    "MISSING_FX_RATE": "Currency conversion rate is unavailable",
    "UNAPPROVED_ADJUSTMENT": "Adjustment was applied without a recorded approval event",
    "INCOMPARABLE_ROLE_GROUPING": "Multiple roles share a comparison group without documented rationale",
}


def create_base_case(entity_id):
    salary = 80000.0
    fte = 0.8

    return {
        "entity_id": entity_id,
        "as_of_date": AS_OF_DATE,
        "band_effective_end": "2027-01-01",
        "annual_base_salary": salary,
        "fte": fte,
        "reported_normalized_salary": salary / fte,
        "currency_code": "INR",
        "fx_rate_present": True,
        "proposal_status": "DRAFT",
        "adjustment_applied": False,
        "approval_event_present": False,
        "comparable_group": "CG-01",
        "role_count_in_group": 1,
        "comparison_rationale": "Roles share similar responsibilities and skills",
    }


def generate_cases():
    GENERATED_DIR.mkdir(parents=True, exist_ok=True)
    GROUND_TRUTH_DIR.mkdir(parents=True, exist_ok=True)

    cases = []
    ground_truth = []

    issue_number = 0

    for issue_type, explanation in ISSUES.items():
        issue_number += 1

        for index in range(1, CASES_PER_ISSUE + 1):
            entity_id = f"ANOM-{issue_number}-{index:03d}"
            case = create_base_case(entity_id)

            if issue_type == "EXPIRED_COMPENSATION_BAND":
                case["band_effective_end"] = "2026-01-01"

            elif issue_type == "FTE_NORMALIZATION_ERROR":
                case["fte"] = 0.5
                case["reported_normalized_salary"] = case["annual_base_salary"]

            elif issue_type == "MISSING_FX_RATE":
                case["currency_code"] = "GBP"
                case["fx_rate_present"] = False

            elif issue_type == "UNAPPROVED_ADJUSTMENT":
                case["proposal_status"] = "APPROVED"
                case["adjustment_applied"] = True
                case["approval_event_present"] = False

            elif issue_type == "INCOMPARABLE_ROLE_GROUPING":
                case["role_count_in_group"] = 3
                case["comparison_rationale"] = ""

            cases.append(case)

            ground_truth.append({
                "entity_id": entity_id,
                "issue_type": issue_type,
                "rule_violated": explanation,
                "expected_decision": "FLAG_FOR_REVIEW",
            })

    # Add clean records to measure false positives.
    for index in range(1, CLEAN_CASES + 1):
        entity_id = f"CLEAN-{index:03d}"
        cases.append(create_base_case(entity_id))

    fieldnames = list(create_base_case("EXAMPLE").keys())

    with open(CASES_FILE, "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(cases)

    with open(GROUND_TRUTH_FILE, "w", newline="", encoding="utf-8") as file:
        fieldnames = [
            "entity_id",
            "issue_type",
            "rule_violated",
            "expected_decision",
        ]
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(ground_truth)

    print("Anomaly benchmark generated successfully.")
    print(f"Total cases: {len(cases)}")
    print(f"Anomaly cases: {len(ground_truth)}")
    print(f"Clean cases: {CLEAN_CASES}")
    print(f"Cases file: {CASES_FILE}")
    print(f"Ground truth file: {GROUND_TRUTH_FILE}")


if __name__ == "__main__":
    generate_cases()