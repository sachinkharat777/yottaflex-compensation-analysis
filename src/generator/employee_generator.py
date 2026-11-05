
from datetime import date, timedelta
from pathlib import Path
import random
import sqlite3

try:
    from .config import SEED, EMPLOYEE_COUNT, SEED_OFFSETS
except ImportError:
    from config import SEED, EMPLOYEE_COUNT, SEED_OFFSETS


ROOT = Path(__file__).resolve().parents[2]
DB_PATH = ROOT / "database" / "compensation.db"


def random_hire_date(rng):
    start = date(2021, 1, 1)
    end = date(2026, 1, 1)

    days = (end - start).days

    return start + timedelta(days=rng.randint(0, days))


def generate_employees(employee_count=EMPLOYEE_COUNT, seed=SEED):

    if employee_count < 1:
        raise ValueError("employee_count must be at least 1.")

    actual_seed = seed + SEED_OFFSETS["employees"]
    rng = random.Random(actual_seed)

    with sqlite3.connect(DB_PATH) as conn:

        conn.execute("PRAGMA foreign_keys = ON")

        roles = conn.execute("""
            SELECT role_id FROM Role ORDER BY role_id
        """).fetchall()

        levels = conn.execute("""
            SELECT level_id FROM Level ORDER BY seniority_rank
        """).fetchall()

        locations = conn.execute("""
            SELECT location_id FROM Location ORDER BY location_id
        """).fetchall()

        roles = [row[0] for row in roles]
        levels = [row[0] for row in levels]
        locations = [row[0] for row in locations]

        if not roles or not levels or not locations:
            raise RuntimeError(
                "Master data is missing. Run master_generator first."
            )

        combinations = [
            (role_id, level_id)
            for role_id in roles
            for level_id in levels
        ]

        employees = []
        assignments = []

        for number in range(1, employee_count + 1):

            employee_id = f"EMP-{number:06d}"
            assignment_id = f"ASG-{number:06d}"

            hire_date = random_hire_date(rng).isoformat()

            role_id, level_id = combinations[
                (number - 1) % len(combinations)
            ]

            location_id = locations[
                (number - 1) % len(locations)
            ]

            fte = rng.choice([1.0, 1.0, 1.0, 0.8, 0.5])

            employees.append((
                employee_id,
                hire_date,
                "ACTIVE",
                "2026-01-01T00:00:00"
            ))

            assignments.append((
                assignment_id,
                employee_id,
                role_id,
                level_id,
                location_id,
                fte,
                hire_date,
                None,
                "INITIAL_ASSIGNMENT"
            ))

        conn.executemany("""
            INSERT OR IGNORE INTO Employee (
                employee_id, hire_date, employment_status, created_at
            )
            VALUES (?, ?, ?, ?)
        """, employees)

        conn.executemany("""
            INSERT OR IGNORE INTO EmployeeAssignment (
                assignment_id, employee_id, role_id, level_id,
                location_id, fte, effective_start, effective_end,
                change_reason
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, assignments)

    print("Employee generation completed.")
    print(f"Employees generated: {len(employees)}")
    print(f"Assignments generated: {len(assignments)}")
    print(f"Role-level combinations: {len(combinations)}")
    print(f"Seed used: {actual_seed}")

    return len(employees)


if __name__ == "__main__":
    generate_employees()
