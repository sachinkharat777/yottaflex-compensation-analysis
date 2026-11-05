from datetime import date
from pathlib import Path
import json
import random
import sqlite3

try:
    from .config import (
        SEED,
        AS_OF_DATE,
        PROPOSAL_COUNT,
        SEED_OFFSETS,
    )
except ImportError:
    from config import (
        SEED,
        AS_OF_DATE,
        PROPOSAL_COUNT,
        SEED_OFFSETS,
    )


ROOT = Path(__file__).resolve().parents[2]
DB_PATH = ROOT / "database" / "compensation.db"
PROPOSAL_CREATED_AT = "2026-01-15T09:00:00"
FIXTURE_APPROVED_AT = "2026-01-16T09:00:00"
GROUP_GAP_THRESHOLD = 0.10


def _load_fx_rates(conn, as_of_date):
    rows = conn.execute(
        """
        SELECT currency_code, rate_to_inr
        FROM CurrencyRate
        WHERE effective_date = (
            SELECT MAX(c2.effective_date)
            FROM CurrencyRate c2
            WHERE c2.currency_code = CurrencyRate.currency_code
              AND c2.effective_date <= ?
        )
        """,
        (as_of_date,),
    ).fetchall()
    return {currency: rate for currency, rate in rows}


def _load_employee_compensation_records(conn, as_of_date):
    """
    Load only source records valid on the configured analysis date.
    Ground-truth files are deliberately not read by this generator.
    """
    return conn.execute(
        """
        SELECT
            e.employee_id,
            a.role_id,
            a.level_id,
            a.location_id,
            a.fte,
            s.annual_base_salary,
            s.currency_code,
            b.min_salary,
            b.midpoint_salary,
            b.max_salary,
            r.comparable_group,
            t.tenure_months,
            p.evidence_id,
            p.rating,
            fx.rate_to_inr
        FROM Employee e
        JOIN EmployeeAssignment a
          ON a.employee_id = e.employee_id
        JOIN SalaryRecord s
          ON s.employee_id = e.employee_id
        JOIN CompensationBand b
          ON b.role_id = a.role_id
         AND b.level_id = a.level_id
         AND b.location_id = a.location_id
         AND b.currency_code = s.currency_code
        JOIN Role r
          ON r.role_id = a.role_id
        JOIN TenureSnapshot t
          ON t.employee_id = e.employee_id
         AND t.as_of_date = ?
        JOIN PerformanceEvidence p
          ON p.evidence_id = (
              SELECT p2.evidence_id
              FROM PerformanceEvidence p2
              WHERE p2.employee_id = e.employee_id
                AND p2.evidence_date <= ?
              ORDER BY p2.evidence_date DESC, p2.evidence_id DESC
              LIMIT 1
          )
        JOIN CurrencyRate fx
          ON fx.currency_code = s.currency_code
         AND fx.effective_date = (
             SELECT MAX(fx2.effective_date)
             FROM CurrencyRate fx2
             WHERE fx2.currency_code = s.currency_code
               AND fx2.effective_date <= ?
         )
        WHERE e.employment_status = 'ACTIVE'
          AND a.effective_start <= ?
          AND (a.effective_end IS NULL OR a.effective_end > ?)
          AND s.effective_start <= ?
          AND (s.effective_end IS NULL OR s.effective_end > ?)
          AND b.effective_start <= ?
          AND (b.effective_end IS NULL OR b.effective_end > ?)
        ORDER BY e.employee_id
        """,
        (
            as_of_date,
            as_of_date,
            as_of_date,
            as_of_date, as_of_date,
            as_of_date, as_of_date,
            as_of_date, as_of_date,
        ),
    ).fetchall()


def _build_candidates(records):
    """
    Use the project's existing screening rules:
      - Below/above compensation band.
      - Compa-ratio outside the 0.80–1.20 screening range.
      - Comparable-group salary gap of at least 10%.

    Below-band and material comparable-group-gap cases can produce draft
    proposals. Above-band cases remain human-review exceptions and do not
    receive an automatic increase.
    """
    group_salaries_inr = {}

    for row in records:
        (
            employee_id, role_id, level_id, location_id, fte,
            actual_salary, currency_code, min_salary, midpoint_salary,
            max_salary, comparable_group, tenure_months, evidence_id,
            rating, rate_to_inr,
        ) = row

        if not fte or fte <= 0 or not rate_to_inr or rate_to_inr <= 0:
            continue

        full_time_salary = actual_salary / fte
        normalized_salary_inr = full_time_salary * rate_to_inr
        group_key = (comparable_group, level_id, location_id)
        group_salaries_inr.setdefault(group_key, []).append(
            normalized_salary_inr
        )

    group_averages_inr = {
        key: sum(values) / len(values)
        for key, values in group_salaries_inr.items()
        if values
    }

    candidates = []

    for row in records:
        (
            employee_id, role_id, level_id, location_id, fte,
            actual_salary, currency_code, min_salary, midpoint_salary,
            max_salary, comparable_group, tenure_months, evidence_id,
            rating, rate_to_inr,
        ) = row

        if (
            not fte or fte <= 0
            or not rate_to_inr or rate_to_inr <= 0
            or rating is None
            or tenure_months is None
        ):
            continue

        full_time_salary = actual_salary / fte
        compa_ratio = full_time_salary / midpoint_salary
        group_key = (comparable_group, level_id, location_id)
        group_average_inr = group_averages_inr.get(group_key)

        if group_average_inr is None or group_average_inr <= 0:
            continue

        normalized_salary_inr = full_time_salary * rate_to_inr
        group_gap = (
            (group_average_inr - normalized_salary_inr) / group_average_inr
        )

        below_band = full_time_salary < min_salary
        above_band = full_time_salary > max_salary

        # Above-band cases are exceptions for human review, not increase
        # recommendations. Within-band cases are not automatically adjusted
        # unless the existing comparable-group screening rule is triggered.
        if above_band:
            continue

        if below_band:
            target_full_time_salary = min_salary
            rule = "BELOW_COMPENSATION_BAND"
            reason = (
                "Current FTE-normalized salary is below the effective "
                "compensation-band minimum. The draft recommendation targets "
                "the band minimum."
            )
        elif group_gap >= GROUP_GAP_THRESHOLD:
            group_average_local = group_average_inr / rate_to_inr
            target_full_time_salary = min(
                max_salary,
                max(min_salary, group_average_local),
            )
            rule = "COMPARABLE_GROUP_GAP"
            reason = (
                "Current FTE- and currency-normalized salary is at least "
                "10% below the comparable-group average. The draft target "
                "uses the group average, constrained to the employee's "
                "effective compensation band."
            )
        else:
            continue

        if target_full_time_salary <= full_time_salary:
            continue

        proposed_actual_salary = round(target_full_time_salary * fte, 2)

        reason += (
            f" Evidence context: performance rating {rating:.1f}/5; "
            f"tenure {tenure_months} months; "
            f"compa-ratio {compa_ratio:.3f}; "
            f"comparable-group gap {group_gap:.1%}. "
            "This is a review recommendation, not a final compensation decision."
        )

        candidates.append({
            "employee_id": employee_id,
            "currency_code": currency_code,
            "proposed_salary": proposed_actual_salary,
            "evidence_id": evidence_id,
            "reason": reason,
            "rule": rule,
            "compa_ratio": compa_ratio,
            "group_gap": group_gap,
        })

    return candidates


def generate_supporting_records(seed=SEED, proposal_count=PROPOSAL_COUNT):
    if proposal_count < 0:
        raise ValueError("proposal_count cannot be negative.")

    actual_seed = seed + SEED_OFFSETS["supporting"]
    rng = random.Random(actual_seed)
    as_of = date.fromisoformat(AS_OF_DATE)

    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("PRAGMA foreign_keys = ON")

        employees = conn.execute(
            """
            SELECT employee_id, hire_date
            FROM Employee
            ORDER BY employee_id
            """
        ).fetchall()

        fx_rates = [
            (
                "FX-INR-2026",
                "INR",
                1.0,
                AS_OF_DATE,
                "SYNTHETIC_ASSUMPTION",
            ),
            (
                "FX-GBP-2026",
                "GBP",
                110.0,
                AS_OF_DATE,
                "SYNTHETIC_ASSUMPTION",
            ),
        ]

        conn.executemany(
            """
            INSERT OR IGNORE INTO CurrencyRate (
                currency_rate_id,
                currency_code,
                rate_to_inr,
                effective_date,
                source
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            fx_rates,
        )

        tenure_records = []
        evidence_records = []

        for employee_id, hire_date_value in employees:
            hired = date.fromisoformat(hire_date_value)
            months = max(
                0,
                (as_of.year - hired.year) * 12
                + as_of.month - hired.month
                - (1 if as_of.day < hired.day else 0),
            )

            tenure_records.append((
                f"TEN-{employee_id}-2026",
                employee_id,
                AS_OF_DATE,
                months,
            ))

            evidence_records.append((
                f"EVD-{employee_id}-2026",
                employee_id,
                "PERFORMANCE_REVIEW",
                round(rng.uniform(2.5, 5.0), 1),
                "Synthetic annual performance evidence",
                "2025-12-15",
                "SYNTHETIC_GENERATOR",
            ))

        conn.executemany(
            """
            INSERT OR IGNORE INTO TenureSnapshot (
                tenure_id, employee_id, as_of_date, tenure_months
            )
            VALUES (?, ?, ?, ?)
            """,
            tenure_records,
        )

        conn.executemany(
            """
            INSERT OR IGNORE INTO PerformanceEvidence (
                evidence_id,
                employee_id,
                evidence_type,
                rating,
                description,
                evidence_date,
                source_reference
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            evidence_records,
        )

        records = _load_employee_compensation_records(conn, AS_OF_DATE)
        candidates = _build_candidates(records)

        selected = rng.sample(
            candidates,
            k=min(proposal_count, len(candidates)),
        )

        proposals = []
        proposal_evidence = []
        approval_events = []
        audit_events = []

        for index, candidate in enumerate(selected, start=1):
            proposal_id = f"ADJ-2026-{index:06d}"

            # Preserve one deterministic approved fixture for workflow tests.
            # All other generated proposals remain drafts for human review.
            status = "APPROVED" if index == 2 else "DRAFT"

            proposals.append((
                proposal_id,
                candidate["employee_id"],
                candidate["proposed_salary"],
                candidate["currency_code"],
                candidate["reason"],
                status,
                PROPOSAL_CREATED_AT,
            ))

            proposal_evidence.append((
                proposal_id,
                candidate["evidence_id"],
            ))

            audit_events.append((
                f"AUD-{proposal_id}-001",
                "AdjustmentProposal",
                proposal_id,
                "PROPOSAL_CREATED",
                None,
                json.dumps({
                    "status": "DRAFT",
                    "rule": candidate["rule"],
                    "compa_ratio": round(candidate["compa_ratio"], 4),
                    "comparable_group_gap": round(candidate["group_gap"], 4),
                }),
                "SYSTEM-GENERATOR",
                PROPOSAL_CREATED_AT,
            ))

            if status == "APPROVED":
                approval_events.append((
                    f"APR-{proposal_id}",
                    proposal_id,
                    "APPROVED",
                    "APPROVER-001",
                    "Deterministic approved fixture for workflow testing.",
                    FIXTURE_APPROVED_AT,
                ))

                audit_events.append((
                    f"AUD-{proposal_id}-002",
                    "AdjustmentProposal",
                    proposal_id,
                    "PROPOSAL_APPROVED",
                    json.dumps({"status": "DRAFT"}),
                    json.dumps({"status": "APPROVED"}),
                    "APPROVER-001",
                    FIXTURE_APPROVED_AT,
                ))

        conn.executemany(
            """
            INSERT OR IGNORE INTO AdjustmentProposal (
                proposal_id,
                employee_id,
                proposed_annual_salary,
                currency_code,
                reason,
                status,
                created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            proposals,
        )

        conn.executemany(
            """
            INSERT OR IGNORE INTO ProposalEvidence (proposal_id, evidence_id)
            VALUES (?, ?)
            """,
            proposal_evidence,
        )

        conn.executemany(
            """
            INSERT OR IGNORE INTO ApprovalEvent (
                approval_event_id,
                proposal_id,
                decision,
                approver_id,
                comments,
                event_timestamp
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            approval_events,
        )

        conn.executemany(
            """
            INSERT OR IGNORE INTO AuditEvent (
                audit_event_id,
                entity_type,
                entity_id,
                action,
                old_values,
                new_values,
                actor,
                event_timestamp
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            audit_events,
        )

        print(f"Tenure snapshots: {len(tenure_records)}")
        print(f"Performance evidence records: {len(evidence_records)}")
        print(f"Eligible rule-based candidates: {len(candidates)}")
        print(f"Adjustment proposals generated: {len(proposals)}")
        print(f"Approval events: {len(approval_events)}")
        print(f"Audit events: {len(audit_events)}")
        print(f"Seed used: {actual_seed}")

        return {
            "tenure_snapshots": len(tenure_records),
            "performance_evidence": len(evidence_records),
            "eligible_candidates": len(candidates),
            "proposals": len(proposals),
            "approval_events": len(approval_events),
            "audit_events": len(audit_events),
        }


if __name__ == "__main__":
    generate_supporting_records()
