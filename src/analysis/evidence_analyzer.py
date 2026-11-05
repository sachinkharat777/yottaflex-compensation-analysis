
import csv
import sqlite3
from pathlib import Path
from collections import defaultdict
from statistics import median

DB_PATH = Path("database/compensation.db")

INPUT_PATH = Path(
    "outputs/compensation_analysis_2026-12-31.csv"
)

OUTPUT_PATH = Path(
    "outputs/evidence_based_review.csv"
)

GAP_THRESHOLD = 10
MIN_GROUP_SIZE = 3


def analyze_evidence():

    if not INPUT_PATH.exists():
        raise FileNotFoundError(
            "Run compensation.py first."
        )

    with open(INPUT_PATH, newline="", encoding="utf-8") as file:
        records = list(csv.DictReader(file))

    with sqlite3.connect(DB_PATH) as conn:

        conn.row_factory = sqlite3.Row

        role_groups = {
            row["role_id"]: row["comparable_group"]
            for row in conn.execute(
                """
                SELECT role_id, comparable_group
                FROM Role
                """
            )
        }

        # Keep only the latest performance evidence per employee.
        evidence_data = {}

        evidence_rows = conn.execute(
            """
            SELECT employee_id, rating, evidence_type
            FROM PerformanceEvidence
            ORDER BY evidence_date DESC, rowid DESC
            """
        )

        for row in evidence_rows:
            evidence_data.setdefault(
                row["employee_id"],
                row
            )

        tenure_data = {
            row["employee_id"]: row["tenure_months"]
            for row in conn.execute(
                """
                SELECT employee_id, tenure_months
                FROM TenureSnapshot
                WHERE as_of_date = '2026-01-01'
                """
            )
        }

    # Create comparable employee groups.
    groups = defaultdict(list)

    for row in records:

        if row["analysis_status"] != "SUCCESS":
            continue

        group = role_groups.get(row["role_id"])

        if not group:
            continue

        key = (
            group,
            row["level_id"],
            row["location_id"],
        )

        groups[key].append(row)

    results = []

    for key, employees in groups.items():

        salaries = [
            float(row["normalized_salary_inr"])
            for row in employees
        ]

        group_median_salary = median(salaries)

        ratings = []
        tenures = []

        for row in employees:

            evidence = evidence_data.get(row["employee_id"])
            tenure = tenure_data.get(row["employee_id"])

            if evidence and evidence["rating"] is not None:
                ratings.append(float(evidence["rating"]))

            if tenure is not None:
                tenures.append(int(tenure))

        group_median_rating = (
            median(ratings) if ratings else None
        )

        group_median_tenure = (
            median(tenures) if tenures else None
        )

        # Very small groups are not suitable for peer comparisons.
        if len(employees) < MIN_GROUP_SIZE:
            continue

        for row in employees:

            employee_id = row["employee_id"]

            salary = float(row["normalized_salary_inr"])

            rating_record = evidence_data.get(employee_id)
            tenure = tenure_data.get(employee_id)

            rating = (
                float(rating_record["rating"])
                if rating_record
                and rating_record["rating"] is not None
                else None
            )

            gap_percentage = (
                (group_median_salary - salary)
                / group_median_salary
            ) * 100

            if gap_percentage >= GAP_THRESHOLD:

                if (
                    rating is None
                    or tenure is None
                    or group_median_rating is None
                    or group_median_tenure is None
                ):

                    assessment = "INSUFFICIENT_EVIDENCE"

                elif (
                    rating >= group_median_rating
                    and tenure >= group_median_tenure
                ):

                    assessment = "STRONGER_DOCUMENTED_PROFILE"

                elif (
                    rating < group_median_rating
                    and tenure < group_median_tenure
                ):

                    assessment = "POTENTIAL_CONTEXTUAL_FACTORS"

                else:

                    assessment = "REQUIRES_HUMAN_REVIEW"

                results.append({
                    "employee_id": employee_id,
                    "comparable_group": key[0],
                    "level_id": key[1],
                    "location_id": key[2],
                    "employee_salary_inr": round(salary, 2),
                    "group_median_salary_inr": round(
                        group_median_salary, 2
                    ),
                    "salary_gap_percent": round(
                        gap_percentage, 2
                    ),
                    "performance_rating": rating,
                    "group_median_rating": group_median_rating,
                    "tenure_months": tenure,
                    "group_median_tenure_months": group_median_tenure,
                    "evidence_assessment": assessment,
                    "review_required": "YES",
                })

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    columns = [
        "employee_id",
        "comparable_group",
        "level_id",
        "location_id",
        "employee_salary_inr",
        "group_median_salary_inr",
        "salary_gap_percent",
        "performance_rating",
        "group_median_rating",
        "tenure_months",
        "group_median_tenure_months",
        "evidence_assessment",
        "review_required",
    ]

    with open(
        OUTPUT_PATH,
        "w",
        newline="",
        encoding="utf-8"
    ) as file:

        writer = csv.DictWriter(file, fieldnames=columns)
        writer.writeheader()
        writer.writerows(results)

    print("\nEVIDENCE ANALYSIS COMPLETED")
    print("--------------------------------")
    print(f"Employees checked: {len(records)}")
    print(f"Comparable groups: {len(groups)}")
    print(f"Employees requiring review: {len(results)}")
    print(f"Report: {OUTPUT_PATH}")


if __name__ == "__main__":
    analyze_evidence()
