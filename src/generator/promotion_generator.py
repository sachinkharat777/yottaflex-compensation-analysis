
from datetime import date, timedelta
from pathlib import Path
import random
import sqlite3

ROOT = Path(__file__).resolve().parents[2]
DB_PATH = ROOT / "database" / "compensation.db"

SEED = 20261022
PROMOTION_COUNT = 500

PROMOTION_START = date(2025, 1, 1)
PROMOTION_END = date(2025, 12, 1)


def generate_promotions():
    rng = random.Random(SEED)

    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("PRAGMA foreign_keys = ON")

        eligible = conn.execute(
            """
            SELECT
                a.assignment_id,
                a.employee_id,
                a.role_id,
                a.level_id,
                a.location_id,
                a.fte,
                e.hire_date,
                l.seniority_rank
            FROM EmployeeAssignment a
            JOIN Employee e
                ON e.employee_id = a.employee_id
            JOIN Level l
                ON l.level_id = a.level_id
            WHERE a.effective_end IS NULL
              AND e.hire_date <= '2024-01-01'
              AND l.seniority_rank < 4
            ORDER BY a.employee_id
            """
        ).fetchall()

        if not eligible:
            raise ValueError("No eligible employees found.")

        sample = rng.sample(
            eligible,
            k=min(PROMOTION_COUNT, len(eligible))
        )

        levels = conn.execute(
            """
            SELECT level_id, seniority_rank
            FROM Level
            """
        ).fetchall()

        next_level = {
            rank: level_id
            for level_id, rank in levels
        }

        total = 0

        for index, employee in enumerate(sample, start=1):
            (
                old_assignment_id,
                employee_id,
                role_id,
                old_level_id,
                location_id,
                fte,
                hire_date,
                current_rank,
            ) = employee

            new_level_id = next_level.get(current_rank + 1)

            if new_level_id is None:
                continue

            days = (PROMOTION_END - PROMOTION_START).days
            promotion_date = PROMOTION_START + timedelta(
                days=rng.randrange(days)
            )

            promotion_id = f"PROMO-2025-{index:06d}"
            new_assignment_id = f"ASG-PROMO-2025-{index:06d}"

            conn.execute(
                """
                UPDATE EmployeeAssignment
                SET effective_end = ?,
                    change_reason = 'PROMOTION'
                WHERE assignment_id = ?
                """,
                (promotion_date.isoformat(), old_assignment_id),
            )

            conn.execute(
                """
                INSERT INTO EmployeeAssignment (
                    assignment_id,
                    employee_id,
                    role_id,
                    level_id,
                    location_id,
                    fte,
                    effective_start,
                    effective_end,
                    change_reason
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, NULL, ?)
                """,
                (
                    new_assignment_id,
                    employee_id,
                    role_id,
                    new_level_id,
                    location_id,
                    fte,
                    promotion_date.isoformat(),
                    "PROMOTION",
                ),
            )

            conn.execute(
                """
                INSERT INTO Promotion (
                    promotion_id,
                    employee_id,
                    from_role_id,
                    from_level_id,
                    to_role_id,
                    to_level_id,
                    effective_date,
                    status
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    promotion_id,
                    employee_id,
                    role_id,
                    old_level_id,
                    role_id,
                    new_level_id,
                    promotion_date.isoformat(),
                    "COMPLETED",
                ),
            )

            total += 1

        print(f"Eligible employees: {len(eligible)}")
        print(f"Completed promotions generated: {total}")


if __name__ == "__main__":
    generate_promotions()
