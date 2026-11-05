from datetime import date
from pathlib import Path
import random
import sqlite3

try:
    from .config import SEED, SEED_OFFSETS
except ImportError:
    from config import SEED, SEED_OFFSETS


ROOT = Path(__file__).resolve().parents[2]
DB_PATH = ROOT / "database" / "compensation.db"

YEARS = [2024, 2025, 2026]


def generate_salary_history(seed=SEED):
    """
    Generate effective-dated salary history using a stable employee-specific
    position within each applicable compensation band.

    A triangular distribution (mode at the band midpoint) avoids the
    unrealistic flat uniform distribution while keeping clean baseline
    salaries inside their effective compensation bands.
    """
    actual_seed = seed + SEED_OFFSETS["transactions"]
    rng = random.Random(actual_seed)

    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("PRAGMA foreign_keys = ON")

        employees = conn.execute(
            """
            SELECT employee_id, hire_date
            FROM Employee
            ORDER BY employee_id
            """
        ).fetchall()

        assignments = conn.execute(
            """
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
            """
        ).fetchall()

        bands = conn.execute(
            """
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
            """
        ).fetchall()

        assignment_lookup = {}
        for assignment in assignments:
            assignment_lookup.setdefault(assignment[1], []).append(assignment)

        # Keep each employee at a consistent relative position in their bands.
        # Annual band movement and promotions then drive salary progression.
        employee_band_position = {
            employee_id: rng.triangular(0.15, 0.85, 0.50)
            for employee_id, _ in employees
        }

        salary_records = []

        for employee_id, hire_date_value in employees:
            hire_date = date.fromisoformat(hire_date_value)
            employee_assignments = assignment_lookup.get(employee_id, [])

            if not employee_assignments:
                raise RuntimeError(f"No assignment found for {employee_id}")

            band_position = employee_band_position[employee_id]
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
                        assignment_start_value,
                        assignment_end_value,
                    ) = assignment

                    assignment_start = date.fromisoformat(assignment_start_value)
                    assignment_end = (
                        date.fromisoformat(assignment_end_value)
                        if assignment_end_value else None
                    )

                    segment_start = max(year_start, hire_date, assignment_start)
                    segment_end = min(
                        year_end,
                        assignment_end or year_end,
                    )

                    if segment_start >= segment_end:
                        continue

                    matching_bands = [
                        band for band in bands
                        if (
                            band[0] == role_id
                            and band[1] == level_id
                            and band[2] == location_id
                            and date.fromisoformat(band[6]) <= segment_start
                            and (
                                band[7] is None
                                or date.fromisoformat(band[7]) >= segment_end
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
                    min_salary = band[3]
                    max_salary = band[4]
                    currency_code = band[5]

                    full_time_salary = min_salary + (
                        (max_salary - min_salary) * band_position
                    )
                    actual_salary = round(full_time_salary * fte, 2)

                    segment_number += 1
                    salary_id = (
                        f"SAL-{employee_id}-{year}-{segment_number:02d}"
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

        for record in salary_records:
            if not 0 < record[4] <= 1:
                raise RuntimeError(f"Invalid FTE for salary record {record[0]}")
            if record[2] <= 0:
                raise RuntimeError(f"Invalid salary for {record[0]}")

        conn.executemany(
            """
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
            """,
            salary_records,
        )

        print("Salary history generated successfully.")
        print(f"Employees processed: {len(employees)}")
        print(f"Assignments processed: {len(assignments)}")
        print(f"Salary records generated: {len(salary_records)}")
        print(f"Seed used: {actual_seed}")

        return len(salary_records)


if __name__ == "__main__":
    generate_salary_history()
