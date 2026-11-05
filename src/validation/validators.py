import sqlite3
from pathlib import Path

DB_PATH = Path("database/compensation.db")


def check_assignment_date_overlaps(conn):
    query = """
        SELECT COUNT(*)
        FROM EmployeeAssignment a
        JOIN EmployeeAssignment b
          ON a.employee_id = b.employee_id
         AND a.assignment_id < b.assignment_id
         AND a.effective_start < COALESCE(b.effective_end, '9999-12-31')
         AND b.effective_start < COALESCE(a.effective_end, '9999-12-31')
    """
    return conn.execute(query).fetchone()[0]


def check_band_date_overlaps(conn):
    query = """
        SELECT COUNT(*)
        FROM CompensationBand a
        JOIN CompensationBand b
          ON a.role_id = b.role_id
         AND a.level_id = b.level_id
         AND a.location_id = b.location_id
         AND a.band_id < b.band_id
         AND a.effective_start < COALESCE(b.effective_end, '9999-12-31')
         AND b.effective_start < COALESCE(a.effective_end, '9999-12-31')
    """
    return conn.execute(query).fetchone()[0]


def run_validations():

    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")

    checks = []

    def check(name, sql):
        count = conn.execute(sql).fetchone()[0]
        checks.append((name, count == 0, count))

    # 1. Foreign key integrity
    foreign_key_errors = conn.execute(
        "PRAGMA foreign_key_check"
    ).fetchall()

    checks.append((
        "Foreign key integrity",
        len(foreign_key_errors) == 0,
        len(foreign_key_errors)
    ))

    # 2. Employee IDs must be unique
    check(
        "Duplicate employee IDs",
        """
        SELECT COUNT(*) FROM (
            SELECT employee_id
            FROM Employee
            GROUP BY employee_id
            HAVING COUNT(*) > 1
        )
        """
    )

    # 3. Salary must be positive
    check(
        "Invalid salary amounts",
        """
        SELECT COUNT(*)
        FROM SalaryRecord
        WHERE annual_base_salary <= 0
        """
    )

    # 4. FTE must be greater than 0 and <= 1
    check(
        "Invalid salary FTE",
        """
        SELECT COUNT(*)
        FROM SalaryRecord
        WHERE fte <= 0 OR fte > 1
        """
    )

    # 5. Salary dates must be valid
    check(
        "Invalid salary date ranges",
        """
        SELECT COUNT(*)
        FROM SalaryRecord
        WHERE effective_end IS NOT NULL
        AND effective_start >= effective_end
        """
    )

    # 6. Assignment dates must be valid
    check(
        "Invalid assignment date ranges",
        """
        SELECT COUNT(*)
        FROM EmployeeAssignment
        WHERE effective_end IS NOT NULL
        AND effective_start >= effective_end
        """
    )

    # 7. Compensation band arithmetic
    check(
        "Invalid compensation bands",
        """
        SELECT COUNT(*)
        FROM CompensationBand
        WHERE min_salary <= 0
        OR min_salary > midpoint_salary
        OR midpoint_salary > max_salary
        """
    )

    # 8. Proposal statuses must be valid
    check(
        "Invalid proposal statuses",
        """
        SELECT COUNT(*)
        FROM AdjustmentProposal
        WHERE status NOT IN (
            'DRAFT',
            'SUBMITTED',
            'APPROVED',
            'REJECTED',
            'WITHDRAWN'
        )
        """
    )

    # 9. Approval events must have valid decisions
    check(
        "Invalid approval decisions",
        """
        SELECT COUNT(*)
        FROM ApprovalEvent
        WHERE decision NOT IN (
            'APPROVED',
            'REJECTED',
            'RETURNED'
        )
        """
    )

    # 10. An employee must not have overlapping assignments
    assignment_overlap_count = check_assignment_date_overlaps(conn)
    checks.append((
        "Overlapping employee assignments",
        assignment_overlap_count == 0,
        assignment_overlap_count
    ))

    # 11. A role/level/location must not have overlapping bands
    band_overlap_count = check_band_date_overlaps(conn)
    checks.append((
        "Overlapping compensation bands",
        band_overlap_count == 0,
        band_overlap_count
    ))

    conn.close()

    print("\n========== DATA VALIDATION REPORT ==========\n")

    for name, passed, count in checks:
        status = "PASS" if passed else "FAIL"
        print(f"{status:6} | {name} | Issues: {count}")

    total = len(checks)
    passed_count = sum(1 for _, passed, _ in checks if passed)

    print("\n============================================")
    print(f"Checks passed: {passed_count}/{total}")
    print(f"Checks failed: {total - passed_count}")
    print("============================================")

    return total == passed_count


if __name__ == "__main__":
    run_validations()