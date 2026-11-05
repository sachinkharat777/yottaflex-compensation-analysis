
import csv
import sqlite3
import statistics
from pathlib import Path
from collections import defaultdict

DB_PATH = Path("database/compensation.db")

INPUT_PATH = Path(
    "outputs/compensation_analysis_2026-12-31.csv"
)

OUTPUT_PATH = Path(
    "outputs/employee_comparison.csv"
)


def compare_employees():

    if not INPUT_PATH.exists():
        raise FileNotFoundError(
            "Run compensation.py before employee comparison."
        )

    with open(
        INPUT_PATH,
        newline="",
        encoding="utf-8"
    ) as file:
        records = list(csv.DictReader(file))

    # Load comparable groups from Role table.
    with sqlite3.connect(DB_PATH) as conn:
        role_groups = dict(
            conn.execute(
                "SELECT role_id, comparable_group FROM Role"
            ).fetchall()
        )

    # Group employees by comparable group, level and location.
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
            row["location_id"]
        )

        groups[key].append(row)

    results = []

    for key, employees in groups.items():

        salaries = [
            float(employee["normalized_salary_inr"])
            for employee in employees
        ]

        group_average = statistics.mean(salaries)
        group_median = statistics.median(salaries)
        group_minimum = min(salaries)
        group_maximum = max(salaries)

        salary_std_dev = (
            statistics.stdev(salaries)
            if len(salaries) > 1
            else 0.0
        )

        salary_range = group_maximum - group_minimum

        for employee in employees:

            salary = float(
                employee["normalized_salary_inr"]
            )

            if group_median > 0:
                gap_percentage = (
                    (salary - group_median) / group_median
                ) * 100
            else:
                gap_percentage = 0.0

            results.append({

                "employee_id": employee["employee_id"],

                "comparable_group": key[0],

                "level_id": key[1],

                "location_id": key[2],

                "normalized_salary_inr": round(salary, 2),

                "group_size": len(employees),

                "group_average_inr": round(
                    group_average, 2
                ),

                "group_median_inr": round(
                    group_median, 2
                ),

                "group_minimum_inr": round(
                    group_minimum, 2
                ),

                "group_maximum_inr": round(
                    group_maximum, 2
                ),

                "salary_range_inr": round(
                    salary_range, 2
                ),

                "salary_std_dev_inr": round(
                    salary_std_dev, 2
                ),

                "gap_from_median_percent": round(
                    gap_percentage, 2
                )
            })

    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    columns = [
        "employee_id",
        "comparable_group",
        "level_id",
        "location_id",
        "normalized_salary_inr",
        "group_size",
        "group_average_inr",
        "group_median_inr",
        "group_minimum_inr",
        "group_maximum_inr",
        "salary_range_inr",
        "salary_std_dev_inr",
        "gap_from_median_percent"
    ]

    with open(
        OUTPUT_PATH,
        "w",
        newline="",
        encoding="utf-8"
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=columns
        )

        writer.writeheader()
        writer.writerows(results)

    print("\nEMPLOYEE COMPARISON COMPLETED")
    print("--------------------------------")

    print(f"Employees compared: {len(results)}")

    print(f"Comparable groups: {len(groups)}")

    print(f"Output: {OUTPUT_PATH}")


if __name__ == "__main__":
    compare_employees()
