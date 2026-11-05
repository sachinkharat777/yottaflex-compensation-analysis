import sqlite3
from pathlib import Path

DB_PATH = Path("database/compensation.db")


def create_adjustment_proposal(employee_id):

    with sqlite3.connect(DB_PATH) as conn:

        conn.row_factory = sqlite3.Row

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
              AND a.effective_end IS NULL
              AND s.effective_end = '2027-01-01'
              AND b.effective_end IS NULL

            ORDER BY s.effective_start DESC
            LIMIT 1
            """,
            (employee_id,),
        ).fetchone()

        if employee is None:
            raise ValueError(
                "Employee, current salary, assignment, or band not found."
            )

        if employee["currency_code"] != employee["band_currency"]:
            raise ValueError(
                "Salary and band currencies differ. Normalize currencies first."
            )

        current_salary = employee["annual_base_salary"]
        fte = employee["fte"]

        current_fte_salary = current_salary / fte

        minimum = employee["min_salary"]
        midpoint = employee["midpoint_salary"]
        maximum = employee["max_salary"]

        if current_fte_salary < minimum:

            recommended_fte_salary = minimum
            reason = "Salary is below the compensation band minimum."

        elif current_fte_salary > maximum:

            recommended_fte_salary = current_fte_salary
            reason = "Salary exceeds the band maximum; human review required."

        else:

            recommended_fte_salary = current_fte_salary
            reason = "Salary is already within the compensation band."

        proposed_salary = round(
            recommended_fte_salary * fte,
            2
        )

        proposal_id = conn.execute(
            """
            SELECT COUNT(*) FROM AdjustmentProposal
            """
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
                f"{{'proposed_salary': {proposed_salary}}}",
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