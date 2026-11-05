
from datetime import date
from pathlib import Path
import random
import sqlite3

ROOT = Path(__file__).resolve().parents[2]
DB_PATH = ROOT / "database" / "compensation.db"

SEED = 20261022
YEARS = [2024, 2025, 2026]


def generate_salary_history():
    rng = random.Random(SEED)

    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("PRAGMA foreign_keys = ON")

        employees = conn.execute("""
            SELECT employee_id, hire_date
            FROM Employee
            ORDER BY employee_id
        """).fetchall()

        assignments = conn.execute("""
            SELECT
                assignment_id,
                employee_id,
                role_id,
                level_id,
                location_id,
                fte,
                effective_start,
                effective_end
            FROM EmployeeAssignment
            ORDER BY employee_id, effective_start
        """).fetchall()

        bands = conn.execute("""
            SELECT
                role_id,
                level_id,
                location_id,
                min_salary,
                max_salary,
                currency_code,
                effective_start,
                effective_end
            FROM CompensationBand
            ORDER BY effective_start
        """).fetchall()

        # Group assignments by employee.
        assignment_lookup = {}

        for assignment in assignments:
            assignment_lookup.setdefault(
                assignment[1], []
            ).append(assignment)

        salary_records = []

        for employee_id, hire_date in employees:

            hire_date = date.fromisoformat(hire_date)

            employee_assignments = assignment_lookup.get(
                employee_id, []
            )

            if not employee_assignments:
                raise RuntimeError(
                    f"No assignment found for {employee_id}"
                )

            segment_number = 0

            for year in YEARS:

                year_start = date(year, 1, 1)
                year_end = date(year + 1, 1, 1)

                for assignment in employee_assignments:

                    (
                        assignment_id,
                        assigned_employee,
                        role_id,
                        level_id,
                        location_id,
                        fte,
                        assignment_start,
                        assignment_end,
                    ) = assignment

                    assignment_start = date.fromisoformat(
                        assignment_start
                    )

                    assignment_end = (
                        date.fromisoformat(assignment_end)
                        if assignment_end else None
                    )

                    # Find the period where the employee
                    # was hired and this assignment was active.
                    segment_start = max(
                        year_start,
                        hire_date,
                        assignment_start,
                    )

                    segment_end = min(
                        year_end,
                        assignment_end or year_end,
                    )

                    if segment_start >= segment_end:
                        continue

                    # Find the compensation band applicable
                    # to this role, level and location.
                    matching_bands = [
                        band for band in bands
                        if (
                            band[0] == role_id
                            and band[1] == level_id
                            and band[2] == location_id
                            and date.fromisoformat(band[6])
                            <= segment_start
                            and (
                                band[7] is None
                                or date.fromisoformat(band[7])
                                >= segment_end
                            )
                        )
                    ]

                    if len(matching_bands) != 1:
                        raise RuntimeError(
                            f"Expected exactly one active band for "
                            f"{employee_id}, assignment {assignment_id}, "
                            f"period {segment_start} to {segment_end}. "
                            f"Found: {len(matching_bands)}"
                        )

                    band = matching_bands[0]

                    (
                        _,
                        _,
                        _,
                        min_salary,
                        max_salary,
                        currency_code,
                        _,
                        _,
                    ) = band

                    # Generate full-time-equivalent salary first.
                    full_time_salary = rng.uniform(
                        min_salary,
                        max_salary,
                    )

                    # Convert to actual paid salary using FTE.
                    actual_salary = round(
                        full_time_salary * fte,
                        2,
                    )

                    segment_number += 1

                    salary_id = (
                        f"SAL-{employee_id}-{year}-"
                        f"{segment_number:02d}"
                    )

                    salary_records.append((
                        salary_id,
                        employee_id,
                        actual_salary,
                        currency_code,
                        fte,
                        segment_start.isoformat(),
                        segment_end.isoformat(),
                        f"{segment_start.isoformat()}T00:00:00",
                        "SYNTHETIC_GENERATOR",
                    ))

        # Verify that every generated salary references
        # a valid employee and has a valid FTE.
        for record in salary_records:
            if not 0 < record[4] <= 1:
                raise RuntimeError(
                    f"Invalid FTE for salary record {record[0]}"
                )

            if record[2] <= 0:
                raise RuntimeError(
                    f"Invalid salary for {record[0]}"
                )

        conn.executemany("""
            INSERT INTO SalaryRecord (
                salary_id,
                employee_id,
                annual_base_salary,
                currency_code,
                fte,
                effective_start,
                effective_end,
                recorded_at,
                source
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, salary_records)

        print("Salary history generated successfully.")
        print(f"Employees processed: {len(employees)}")
        print(f"Assignments processed: {len(assignments)}")
        print(f"Salary records generated: {len(salary_records)}")


if __name__ == "__main__":
    generate_salary_history()
