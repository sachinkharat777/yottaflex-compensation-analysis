from datetime import date
from pathlib import Path
import json
import sqlite3

ROOT = Path(__file__).resolve().parents[2]
DB_PATH = ROOT / "database" / "compensation.db"


def create_adjustment_proposal(employee_id):
    as_of_date = date.today().isoformat()

    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")

        employee = conn.execute(
            """
            SELECT
                e.employee_id,
                a.role_id,
                a.level_id,
                a.location_id,
                a.fte,
                s.annual_base_salary,
                s.currency_code,
                s.salary_id,
                b.min_salary,
                b.midpoint_salary,
                b.max_salary,
                b.band_id,
                b.currency_code AS band_currency
            FROM Employee e
            JOIN EmployeeAssignment a
                ON e.employee_id = a.employee_id
            JOIN SalaryRecord s
                ON e.employee_id = s.employee_id
            JOIN CompensationBand b
                ON a.role_id = b.role_id
                AND a.level_id = b.level_id
                AND a.location_id = b.location_id
            WHERE e.employee_id = ?
              AND a.effective_start <= ?
              AND (a.effective_end IS NULL OR a.effective_end > ?)
              AND s.effective_start <= ?
              AND (s.effective_end IS NULL OR s.effective_end > ?)
              AND b.effective_start <= ?
              AND (b.effective_end IS NULL OR b.effective_end > ?)
            ORDER BY s.effective_start DESC
            LIMIT 1
            """,
            (
                employee_id,
                as_of_date, as_of_date,
                as_of_date, as_of_date,
                as_of_date, as_of_date,
            ),
        ).fetchone()

        if employee is None:
            raise ValueError(
                "Employee, current salary, assignment, or effective "
                "compensation band not found for today's date."
            )

        if employee["currency_code"] != employee["band_currency"]:
            raise ValueError(
                "Salary and band currencies differ. Normalize currencies first."
            )

        current_salary = employee["annual_base_salary"]
        fte = employee["fte"]

        if fte <= 0:
            raise ValueError("Employee FTE must be greater than zero.")

        current_fte_salary = current_salary / fte
        minimum = employee["min_salary"]
        maximum = employee["max_salary"]

        if current_fte_salary < minimum:
            recommended_fte_salary = minimum
            reason = (
                "Salary is below the effective compensation-band minimum. "
                "Draft recommendation targets the band minimum."
            )
        elif current_fte_salary > maximum:
            recommended_fte_salary = current_fte_salary
            reason = (
                "Salary exceeds the effective compensation-band maximum; "
                "human review required. No automatic increase recommended."
            )
        else:
            recommended_fte_salary = current_fte_salary
            reason = (
                "Salary is already within the effective compensation band. "
                "No automatic increase recommended."
            )

        proposed_salary = round(recommended_fte_salary * fte, 2)

        proposal_id = conn.execute(
            "SELECT COUNT(*) FROM AdjustmentProposal"
        ).fetchone()[0] + 1
        proposal_id = f"ADJ-2026-{proposal_id:06d}"

        conn.execute(
            """
            INSERT INTO AdjustmentProposal (
                proposal_id,
                employee_id,
                proposed_annual_salary,
                currency_code,
                reason,
                status,
                created_at
            )
            VALUES (?, ?, ?, ?, ?, 'DRAFT', datetime('now'))
            """,
            (
                proposal_id,
                employee_id,
                proposed_salary,
                employee["currency_code"],
                reason,
            ),
        )

        conn.execute(
            """
            INSERT INTO AuditEvent (
                audit_event_id,
                entity_type,
                entity_id,
                action,
                old_values,
                new_values,
                actor,
                event_timestamp
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, datetime('now'))
            """,
            (
                f"AUD-{proposal_id}",
                "AdjustmentProposal",
                proposal_id,
                "PROPOSAL_CREATED",
                None,
                json.dumps({
                    "proposed_salary": proposed_salary,
                    "status": "DRAFT",
                    "as_of_date": as_of_date,
                }),
                "SYSTEM",
            ),
        )

        conn.commit()

        return {
            "proposal_id": proposal_id,
            "employee_id": employee_id,
            "current_salary": current_salary,
            "recommended_salary": proposed_salary,
            "reason": reason,
            "status": "DRAFT",
        }


if __name__ == "__main__":
    result = create_adjustment_proposal("EMP-000001")

    print("\nADJUSTMENT RECOMMENDATION")
    print("-------------------------")

    for key, value in result.items():
        print(f"{key}: {value}")
