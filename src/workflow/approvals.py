
import sqlite3
import json
from datetime import datetime, timezone

DB_PATH = "database/compensation.db"


def submit_proposal(proposal_id, actor):
    """Move a proposal from DRAFT to SUBMITTED."""

    now = datetime.now(timezone.utc).isoformat()

    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("PRAGMA foreign_keys = ON")

        proposal = conn.execute(
            """
            SELECT status
            FROM AdjustmentProposal
            WHERE proposal_id = ?
            """,
            (proposal_id,)
        ).fetchone()

        if proposal is None:
            raise ValueError("Proposal not found.")

        if proposal[0] != "DRAFT":
            raise ValueError("Only DRAFT proposals can be submitted.")

        conn.execute(
            """
            UPDATE AdjustmentProposal
            SET status = 'SUBMITTED'
            WHERE proposal_id = ?
            """,
            (proposal_id,)
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
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                f"AUD-{proposal_id}-SUBMIT",
                "AdjustmentProposal",
                proposal_id,
                "SUBMITTED",
                json.dumps({"status": "DRAFT"}),
                json.dumps({"status": "SUBMITTED"}),
                actor,
                now
            )
        )

    print(f"{proposal_id} submitted successfully.")


def decide_proposal(proposal_id, decision, approver_id, comments):
    """Approve or reject a submitted proposal."""

    decision = decision.upper()

    if decision not in ("APPROVED", "REJECTED"):
        raise ValueError("Decision must be APPROVED or REJECTED.")

    now = datetime.now(timezone.utc).isoformat()

    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("PRAGMA foreign_keys = ON")

        proposal = conn.execute(
            """
            SELECT status
            FROM AdjustmentProposal
            WHERE proposal_id = ?
            """,
            (proposal_id,)
        ).fetchone()

        if proposal is None:
            raise ValueError("Proposal not found.")

        if proposal[0] != "SUBMITTED":
            raise ValueError(
                "Only SUBMITTED proposals can be approved or rejected."
            )

        conn.execute(
            """
            UPDATE AdjustmentProposal
            SET status = ?
            WHERE proposal_id = ?
            """,
            (decision, proposal_id)
        )

        conn.execute(
            """
            INSERT INTO ApprovalEvent (
                approval_event_id,
                proposal_id,
                decision,
                approver_id,
                comments,
                event_timestamp
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                f"APR-{proposal_id}-001",
                proposal_id,
                decision,
                approver_id,
                comments,
                now
            )
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
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                f"AUD-{proposal_id}-DECISION",
                "AdjustmentProposal",
                proposal_id,
                decision,
                json.dumps({"status": "SUBMITTED"}),
                json.dumps({"status": decision}),
                approver_id,
                now
            )
        )

    print(f"{proposal_id} decision recorded: {decision}")


def list_proposals():
    """Display proposals and their current statuses."""

    with sqlite3.connect(DB_PATH) as conn:
        rows = conn.execute(
            """
            SELECT proposal_id, employee_id, status
            FROM AdjustmentProposal
            ORDER BY proposal_id
            LIMIT 20
            """
        ).fetchall()

    for row in rows:
        print(row)


if __name__ == "__main__":

    print("\n--- Compensation Approval Workflow ---")
    print("1. List proposals")
    print("2. Submit a proposal")
    print("3. Approve or reject a proposal")

    choice = input("\nChoose an option: ").strip()

    if choice == "1":
        list_proposals()

    elif choice == "2":
        proposal_id = input("Enter proposal ID: ").strip()
        actor = input("Enter submitter ID/name: ").strip()
        submit_proposal(proposal_id, actor)

    elif choice == "3":
        proposal_id = input("Enter proposal ID: ").strip()
        decision = input("Enter APPROVED or REJECTED: ").strip()
        approver = input("Enter approver ID/name: ").strip()
        comments = input("Enter decision comments: ").strip()

        decide_proposal(
            proposal_id,
            decision,
            approver,
            comments
        )

    else:
        print("Invalid option.")
