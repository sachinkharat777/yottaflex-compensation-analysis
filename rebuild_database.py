
from pathlib import Path
from datetime import datetime
import argparse
import shutil
import sqlite3
import sys
import traceback

from src.generator.config import (
    SEED,
    EMPLOYEE_COUNT,
    PROMOTION_COUNT,
    PROPOSAL_COUNT,
)


ROOT = Path(__file__).resolve().parent
DB_PATH = ROOT / "database" / "compensation.db"
SCHEMA_PATH = ROOT / "database" / "schema.sql"


def get_count(conn, table):
    return conn.execute(
        f"SELECT COUNT(*) FROM {table}"
    ).fetchone()[0]


def validate_database(
    employee_count,
    promotion_count,
    proposal_count,
):

    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("PRAGMA foreign_keys = ON")

        expected = {
            "Role": 50,
            "Level": 4,
            "Location": 3,
            "CompensationBand": 1800,
            "Employee": employee_count,
            "EmployeeAssignment": employee_count + promotion_count,
            "Promotion": promotion_count,
            "PerformanceEvidence": employee_count,
            "TenureSnapshot": employee_count,
            "AdjustmentProposal": proposal_count,
            "ProposalEvidence": proposal_count,
            "CurrencyRate": 2,
        }

        print("\nDATABASE VALIDATION")
        print("-" * 45)

        for table, expected_count in expected.items():

            actual_count = get_count(conn, table)

            print(
                f"{table}: {actual_count} "
                f"(expected: {expected_count})"
            )

            if actual_count != expected_count:
                raise RuntimeError(
                    f"{table}: expected {expected_count}, "
                    f"found {actual_count}"
                )

        salary_count = get_count(conn, "SalaryRecord")
        approval_count = get_count(conn, "ApprovalEvent")

        print(f"SalaryRecord: {salary_count}")
        print(f"ApprovalEvent: {approval_count}")

        if employee_count > 0 and salary_count < employee_count:
            raise RuntimeError("Insufficient salary records.")

        if approval_count > proposal_count:
            raise RuntimeError("Unexpected approval event count.")

        foreign_key_errors = conn.execute(
            "PRAGMA foreign_key_check"
        ).fetchall()

        if foreign_key_errors:
            raise RuntimeError(
                f"Foreign key errors found: {foreign_key_errors[:5]}"
            )

        assignment_overlaps = conn.execute("""
            SELECT COUNT(*)
            FROM EmployeeAssignment a
            JOIN EmployeeAssignment b
              ON a.employee_id = b.employee_id
             AND a.assignment_id < b.assignment_id
             AND a.effective_start <
                 COALESCE(b.effective_end, '9999-12-31')
             AND b.effective_start <
                 COALESCE(a.effective_end, '9999-12-31')
        """).fetchone()[0]

        if assignment_overlaps:
            raise RuntimeError(
                f"Found {assignment_overlaps} assignment overlaps."
            )

        print("Foreign key check: PASSED")
        print("Assignment overlap check: PASSED")

        return True


def rebuild(
    employee_count=EMPLOYEE_COUNT,
    seed=SEED,
    promotion_count=PROMOTION_COUNT,
    proposal_count=PROPOSAL_COUNT,
):

    if employee_count < 1:
        raise ValueError("Employee count must be at least 1.")

    if promotion_count < 0 or proposal_count < 0:
        raise ValueError("Promotion and proposal counts cannot be negative.")

    if not DB_PATH.exists():
        raise FileNotFoundError(
            f"Existing database not found: {DB_PATH}"
        )

    if not SCHEMA_PATH.exists():
        raise FileNotFoundError(
            f"Schema file not found: {SCHEMA_PATH}"
        )

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    backup_path = (
        ROOT / "database"
        / f"compensation_backup_before_rebuild_{timestamp}.db"
    )

    # Step 1: Create a safety backup.
    shutil.copy2(DB_PATH, backup_path)

    print(f"Safety backup created: {backup_path.name}")

    try:

        # Step 2: Create a fresh database from the schema.
        DB_PATH.unlink()

        with sqlite3.connect(DB_PATH) as conn:
            conn.execute("PRAGMA foreign_keys = ON")

            schema = SCHEMA_PATH.read_text(
                encoding="utf-8"
            )

            conn.executescript(schema)

        print("\nFresh database created.")

        # Step 3: Import generators.
        from src.generator.master_generator import generate_master_data
        from src.generator.employee_generator import generate_employees
        from src.generator.promotion_generator import generate_promotions
        from src.generator.transaction_generator import generate_salary_history
        from src.generator.supporting_generator import generate_supporting_records

        # Step 4: Run generators in dependency order.
        print("\n[1/5] Generating master data...")
        generate_master_data()

        print("\n[2/5] Generating employees...")
        generated_employees = generate_employees(
            employee_count=employee_count,
            seed=seed,
        )

        if generated_employees != employee_count:
            raise RuntimeError(
                f"Expected {employee_count} employees, "
                f"generated {generated_employees}."
            )

        print("\n[3/5] Generating promotion history...")
        generated_promotions = generate_promotions(
            promotion_count=promotion_count,
            seed=seed,
        )

        print("\n[4/5] Generating salary history...")
        generated_salary_records = generate_salary_history(
            seed=seed,
        )

        print("\n[5/5] Generating supporting records...")
        supporting_counts = generate_supporting_records(
            seed=seed,
            proposal_count=proposal_count,
        )

        # Step 5: Validate actual generated counts.
        validate_database(
            employee_count=generated_employees,
            promotion_count=generated_promotions,
            proposal_count=supporting_counts["proposals"],
        )

        print("\n" + "=" * 50)
        print("DATABASE REBUILD COMPLETED SUCCESSFULLY")
        print(f"Employees: {generated_employees}")
        print(f"Promotions: {generated_promotions}")
        print(f"Salary records: {generated_salary_records}")
        print(f"Proposals: {supporting_counts['proposals']}")
        print(f"Seed: {seed}")
        print(f"Database: {DB_PATH}")
        print(f"Backup: {backup_path}")
        print("=" * 50)

        return True

    except Exception:

        print("\nDATABASE REBUILD FAILED.")
        print("Restoring the original database...")

        if DB_PATH.exists():
            DB_PATH.unlink()

        shutil.copy2(backup_path, DB_PATH)

        print("Original database restored.")

        traceback.print_exc()

        raise


if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description="Rebuild the synthetic compensation database."
    )

    parser.add_argument(
        "--employees",
        type=int,
        default=EMPLOYEE_COUNT,
        help="Number of employees to generate.",
    )

    parser.add_argument(
        "--seed",
        type=int,
        default=SEED,
        help="Random seed for reproducible generation.",
    )

    parser.add_argument(
        "--promotions",
        type=int,
        default=PROMOTION_COUNT,
        help="Maximum number of promotions to generate.",
    )

    parser.add_argument(
        "--proposals",
        type=int,
        default=PROPOSAL_COUNT,
        help="Maximum number of adjustment proposals.",
    )

    args = parser.parse_args()

    try:
        rebuild(
            employee_count=args.employees,
            seed=args.seed,
            promotion_count=args.promotions,
            proposal_count=args.proposals,
        )

    except Exception:
        sys.exit(1)
