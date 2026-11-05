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


def collect_validation_results(db_path=None):
    """
    Run all data validation checks and return structured results.

    This function does not modify the database.
    """
    db_path = Path(db_path) if db_path is not None else DB_PATH

    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys = ON")

    checks = []

    def add_check(name, issue_count):
        checks.append({
            "name": name,
            "passed": issue_count == 0,
            "issue_count": issue_count,
        })

    try:
        # 1. Foreign key integrity
        foreign_key_errors = conn.execute(
            "PRAGMA foreign_key_check"
        ).fetchall()

        add_check(
            "Foreign key integrity",
            len(foreign_key_errors)
        )

        # 2. Employee IDs must be unique
        add_check(
            "Duplicate employee IDs",
            conn.execute("""
                SELECT COUNT(*) FROM (
                    SELECT employee_id
                    FROM Employee
                    GROUP BY employee_id
                    HAVING COUNT(*) > 1
                )
            """).fetchone()[0]
        )

        # 3. Salary must be positive
        add_check(
            "Invalid salary amounts",
            conn.execute("""
                SELECT COUNT(*)
                FROM SalaryRecord
                WHERE annual_base_salary <= 0
            """).fetchone()[0]
        )

        # 4. FTE must be greater than 0 and <= 1
        add_check(
            "Invalid salary FTE",
            conn.execute("""
                SELECT COUNT(*)
                FROM SalaryRecord
                WHERE fte <= 0 OR fte > 1
            """).fetchone()[0]
        )

        # 5. Salary dates must be valid
        add_check(
            "Invalid salary date ranges",
            conn.execute("""
                SELECT COUNT(*)
                FROM SalaryRecord
                WHERE effective_end IS NOT NULL
                AND effective_start >= effective_end
            """).fetchone()[0]
        )

        # 6. Assignment dates must be valid
        add_check(
            "Invalid assignment date ranges",
            conn.execute("""
                SELECT COUNT(*)
                FROM EmployeeAssignment
                WHERE effective_end IS NOT NULL
                AND effective_start >= effective_end
            """).fetchone()[0]
        )

        # 7. Compensation band arithmetic
        add_check(
            "Invalid compensation bands",
            conn.execute("""
                SELECT COUNT(*)
                FROM CompensationBand
                WHERE min_salary <= 0
                OR min_salary > midpoint_salary
                OR midpoint_salary > max_salary
            """).fetchone()[0]
        )

        # 8. Proposal statuses must be valid
        add_check(
            "Invalid proposal statuses",
            conn.execute("""
                SELECT COUNT(*)
                FROM AdjustmentProposal
                WHERE status NOT IN (
                    'DRAFT',
                    'SUBMITTED',
                    'APPROVED',
                    'REJECTED',
                    'WITHDRAWN'
                )
            """).fetchone()[0]
        )

        # 9. Approval events must have valid decisions
        add_check(
            "Invalid approval decisions",
            conn.execute("""
                SELECT COUNT(*)
                FROM ApprovalEvent
                WHERE decision NOT IN (
                    'APPROVED',
                    'REJECTED',
                    'RETURNED'
                )
            """).fetchone()[0]
        )

        # 10. Employee assignments must not overlap
        add_check(
            "Overlapping employee assignments",
            check_assignment_date_overlaps(conn)
        )

        # 11. Compensation bands must not overlap
        add_check(
            "Overlapping compensation bands",
            check_band_date_overlaps(conn)
        )

    finally:
        conn.close()

    total = len(checks)
    passed_count = sum(1 for item in checks if item["passed"])

    return {
        "database": str(db_path),
        "total_checks": total,
        "passed_checks": passed_count,
        "failed_checks": total - passed_count,
        "overall_status": "PASS" if passed_count == total else "FAIL",
        "checks": checks,
    }


def run_validations():
    results = collect_validation_results()

    print("\n========== DATA VALIDATION REPORT ==========\n")

    for item in results["checks"]:
        status = "PASS" if item["passed"] else "FAIL"
        print(
            f"{status:6} | {item['name']} "
            f"| Issues: {item['issue_count']}"
        )

    print("\n============================================")
    print(
        f"Checks passed: "
        f"{results['passed_checks']}/{results['total_checks']}"
    )
    print(f"Checks failed: {results['failed_checks']}")
    print("============================================")

    return results["overall_status"] == "PASS"


if __name__ == "__main__":
    run_validations()