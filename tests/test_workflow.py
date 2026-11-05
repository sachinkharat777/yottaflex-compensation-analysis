import sqlite3

DB_PATH = "database/compensation.db"


def test_approved_proposal_has_approval_event():
    con = sqlite3.connect(DB_PATH)

    result = con.execute("""
        SELECT
            p.status,
            COUNT(a.approval_event_id)
        FROM AdjustmentProposal p
        LEFT JOIN ApprovalEvent a
            ON p.proposal_id = a.proposal_id
        WHERE p.proposal_id = 'ADJ-2026-000002'
        GROUP BY p.proposal_id
    """).fetchone()

    con.close()

    assert result is not None
    assert result[0] == "APPROVED"
    assert result[1] >= 1


def test_approved_proposal_has_audit_history():
    con = sqlite3.connect(DB_PATH)

    result = con.execute("""
        SELECT COUNT(*)
        FROM AuditEvent
        WHERE entity_id = 'ADJ-2026-000002'
    """).fetchone()

    con.close()

    assert result[0] >= 2