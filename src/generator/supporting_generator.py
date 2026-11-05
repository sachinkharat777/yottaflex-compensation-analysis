
from datetime import date
from pathlib import Path
import json
import random
import sqlite3

ROOT = Path(__file__).resolve().parents[2]
DB_PATH = ROOT / "database" / "compensation.db"

SEED = 20261022
AS_OF_DATE = "2026-01-01"


def generate_supporting_records():
    rng = random.Random(SEED)

    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("PRAGMA foreign_keys = ON")

        employees = conn.execute(
            "SELECT employee_id, hire_date FROM Employee ORDER BY employee_id"
        ).fetchall()

        # Synthetic currency conversion rates.
        fx_rates = [
            ("FX-INR-2026", "INR", 1.0, AS_OF_DATE, "SYNTHETIC_ASSUMPTION"),
            ("FX-GBP-2026", "GBP", 110.0, AS_OF_DATE, "SYNTHETIC_ASSUMPTION"),
        ]

        conn.executemany(
            """
            INSERT OR IGNORE INTO CurrencyRate
            (currency_rate_id, currency_code, rate_to_inr, effective_date, source)
            VALUES (?, ?, ?, ?, ?)
            """,
            fx_rates,
        )

        tenure_records = []
        evidence_records = []

        for employee_id, hire_date in employees:
            hired = date.fromisoformat(hire_date)
            as_of = date.fromisoformat(AS_OF_DATE)

            months = max(
                0,
                (as_of.year - hired.year) * 12
                + as_of.month - hired.month
                - (1 if as_of.day < hired.day else 0),
            )

            tenure_records.append(
                (
                    f"TEN-{employee_id}-2026",
                    employee_id,
                    AS_OF_DATE,
                    months,
                )
            )

            evidence_records.append(
                (
                    f"EVD-{employee_id}-2026",
                    employee_id,
                    "PERFORMANCE_REVIEW",
                    round(rng.uniform(2.5, 5.0), 1),
                    "Synthetic annual performance evidence",
                    "2025-12-15",
                    "SYNTHETIC_GENERATOR",
                )
            )

        conn.executemany(
            """
            INSERT OR IGNORE INTO TenureSnapshot
            (tenure_id, employee_id, as_of_date, tenure_months)
            VALUES (?, ?, ?, ?)
            """,
            tenure_records,
        )

        conn.executemany(
            """
            INSERT OR IGNORE INTO PerformanceEvidence
            (
                evidence_id, employee_id, evidence_type, rating,
                description, evidence_date, source_reference
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            evidence_records,
        )

        proposals = []
        proposal_evidence = []
        approval_events = []
        audit_events = []

        sample = rng.sample(employees, k=min(250, len(employees)))

        for index, (employee_id, _) in enumerate(sample, start=1):
            proposal_id = f"ADJ-2026-{index:06d}"

            salary_row = conn.execute(
                """
                SELECT annual_base_salary, currency_code
                FROM SalaryRecord
                WHERE employee_id = ?
                ORDER BY effective_start DESC
                LIMIT 1
                """,
                (employee_id,),
            ).fetchone()

            if salary_row is None:
                continue

            current_salary, currency_code = salary_row

            proposed_salary = round(
                current_salary * rng.uniform(1.03, 1.12), 2
            )

            # Keep the workflow test proposal deterministic.
            if index == 2:
                status = "APPROVED"
            else:
                status = rng.choice(
                    ["SUBMITTED", "APPROVED", "REJECTED", "DRAFT"]
                )

            proposals.append(
                (
                    proposal_id,
                    employee_id,
                    proposed_salary,
                    currency_code,
                    "Synthetic adjustment proposal for workflow testing",
                    status,
                    "2026-01-15T09:00:00",
                )
            )

            evidence_id = f"EVD-{employee_id}-2026"
            proposal_evidence.append((proposal_id, evidence_id))

            # Record proposal creation in the audit history.
            audit_events.append(
                (
                    f"AUD-{proposal_id}-001",
                    "AdjustmentProposal",
                    proposal_id,
                    "PROPOSAL_CREATED",
                    None,
                    json.dumps({"status": "SUBMITTED"}),
                    "SYSTEM-GENERATOR",
                    "2026-01-15T09:00:00",
                )
            )

            if status in ("APPROVED", "REJECTED"):
                approval_events.append(
                    (
                        f"APR-{proposal_id}",
                        proposal_id,
                        status,
                        "APPROVER-001",
                        "Synthetic decision for workflow testing",
                        "2026-01-16T09:00:00",
                    )
                )

                audit_events.append(
                    (
                        f"AUD-{proposal_id}-002",
                        "AdjustmentProposal",
                        proposal_id,
                        f"PROPOSAL_{status}",
                        json.dumps({"status": "SUBMITTED"}),
                        json.dumps({"status": status}),
                        "APPROVER-001",
                        "2026-01-16T09:00:00",
                    )
                )

        conn.executemany(
            """
            INSERT OR IGNORE INTO AdjustmentProposal
            (
                proposal_id, employee_id, proposed_annual_salary,
                currency_code, reason, status, created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            proposals,
        )

        conn.executemany(
            """
            INSERT OR IGNORE INTO ProposalEvidence
            (proposal_id, evidence_id)
            VALUES (?, ?)
            """,
            proposal_evidence,
        )

        conn.executemany(
            """
            INSERT OR IGNORE INTO ApprovalEvent
            (
                approval_event_id, proposal_id, decision,
                approver_id, comments, event_timestamp
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            approval_events,
        )

        conn.executemany(
            """
            INSERT OR IGNORE INTO AuditEvent
            (
                audit_event_id, entity_type, entity_id, action,
                old_values, new_values, actor, event_timestamp
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            audit_events,
        )

        print(f"Tenure snapshots: {len(tenure_records)}")
        print(f"Performance evidence records: {len(evidence_records)}")
        print(f"Adjustment proposals: {len(proposals)}")
        print(f"Approval events: {len(approval_events)}")
        print(f"Audit events: {len(audit_events)}")


if __name__ == "__main__":
    generate_supporting_records()
