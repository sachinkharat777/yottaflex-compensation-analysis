import csv
import sqlite3
from pathlib import Path
from collections import defaultdict

DB_PATH = Path("database/compensation.db")

INPUT_PATH = Path(
    "outputs/compensation_analysis_2026-12-31.csv"
)

OUTPUT_PATH = Path(
    "outputs/disparity_flags.csv"
)

LOW_COMPA_RATIO = 0.80
HIGH_COMPA_RATIO = 1.20
GAP_THRESHOLD = 0.10


def detect_disparities():

    if not INPUT_PATH.exists():
        raise FileNotFoundError(
            "Run compensation.py before disparity detection."
        )

    with open(INPUT_PATH, newline="", encoding="utf-8") as file:
        records = list(csv.DictReader(file))

    # Load role comparison groups.
    with sqlite3.connect(DB_PATH) as conn:
        role_groups = dict(
            conn.execute(
                "SELECT role_id, comparable_group FROM Role"
            ).fetchall()
        )

    # Group employees by comparable role group,
    # level and location.
    groups = defaultdict(list)

    for row in records:

        if row["analysis_status"] != "SUCCESS":
            continue

        comparable_group = role_groups.get(row["role_id"])

        if not comparable_group:
            continue

        key = (
            comparable_group,
            row["level_id"],
            row["location_id"],
        )

        groups[key].append(row)

    flags = []

    for key, employees in groups.items():

        salaries = [
            float(employee["normalized_salary_inr"])
            for employee in employees
        ]

        group_average = sum(salaries) / len(salaries)

        for employee in employees:

            employee_id = employee["employee_id"]
            salary = float(employee["normalized_salary_inr"])
            compa_ratio = float(employee["compa_ratio"])
            band_status = employee["band_status"]

            reasons = []

            # Rule 1: Below minimum.
            if band_status == "BELOW_BAND":
                reasons.append("BELOW_COMPENSATION_BAND")

            # Rule 2: Above maximum.
            if band_status == "ABOVE_BAND":
                reasons.append("ABOVE_COMPENSATION_BAND")

            # Rule 3: Low compa-ratio.
            if compa_ratio < LOW_COMPA_RATIO:
                reasons.append("LOW_COMPA_RATIO")

            # Rule 4: High compa-ratio.
            if compa_ratio > HIGH_COMPA_RATIO:
                reasons.append("HIGH_COMPA_RATIO")

            # Rule 5: Difference from comparable-group average.
            if group_average > 0:

                gap_percentage = (
                    (group_average - salary) / group_average
                ) * 100

                if gap_percentage >= GAP_THRESHOLD * 100:
                    reasons.append(
                        "BELOW_COMPARABLE_GROUP_AVERAGE"
                    )

            else:
                gap_percentage = 0

            if reasons:

                flags.append({
                    "employee_id": employee_id,
                    "comparable_group": key[0],
                    "level_id": key[1],
                    "location_id": key[2],
                    "normalized_salary_inr": round(salary, 2),
                    "group_average_inr": round(group_average, 2),
                    "compa_ratio": compa_ratio,
                    "gap_percentage": round(gap_percentage, 2),
                    "flag_reasons": "|".join(reasons),
                    "review_required": "YES",
                })

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    columns = [
        "employee_id",
        "comparable_group",
        "level_id",
        "location_id",
        "normalized_salary_inr",
        "group_average_inr",
        "compa_ratio",
        "gap_percentage",
        "flag_reasons",
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
        writer.writerows(flags)

    print("\nDISPARITY DETECTION COMPLETED")
    print("--------------------------------")
    print(f"Employees checked: {len(records)}")
    print(f"Comparable groups: {len(groups)}")
    print(f"Employees flagged: {len(flags)}")
    print(f"Output: {OUTPUT_PATH}")


if __name__ == "__main__":
    detect_disparities()