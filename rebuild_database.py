from pathlib import Path
from datetime import datetime
import shutil
import sqlite3
import sys
import traceback

ROOT = Path(__file__).resolve().parent
DB_PATH = ROOT / "database" / "compensation.db"
SCHEMA_PATH = ROOT / "database" / "schema.sql"

# Preserve the current database before rebuilding.
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
BACKUP_PATH = ROOT / "database" / f"compensation_backup_before_rebuild_{timestamp}.db"


def get_count(conn, table):
    return conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]


def validate_database():
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("PRAGMA foreign_keys = ON")

        expected = {
            "Role": 50,
            "Level": 4,
            "Location": 3,
            "CompensationBand": 1800,
            "Employee": 5000,
            "EmployeeAssignment": 5500,
            "Promotion": 500,
            "PerformanceEvidence": 5000,
            "TenureSnapshot": 5000,
            "AdjustmentProposal": 250,
            "ProposalEvidence": 250,
            "CurrencyRate": 2,
        }

        print("\nDATABASE VALIDATION")
        print("-" * 40)

        for table, expected_count in expected.items():
            actual_count = get_count(conn, table)
            print(f"{table}: {actual_count}")

            if actual_count != expected_count:
                raise RuntimeError(
                    f"{table}: expected {expected_count}, " f"found {actual_count}"
                )

        salary_count = get_count(conn, "SalaryRecord")
        approval_count = get_count(conn, "ApprovalEvent")

        print(f"SalaryRecord: {salary_count}")
        print(f"ApprovalEvent: {approval_count}")

        if salary_count < 5000:
            raise RuntimeError("Insufficient salary records.")

        if approval_count > 250:
            raise RuntimeError("Unexpected approval event count.")

        foreign_key_errors = conn.execute("PRAGMA foreign_key_check").fetchall()

        if foreign_key_errors:
            raise RuntimeError(f"Foreign key errors found: {foreign_key_errors[:5]}")

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
            raise RuntimeError(f"Found {assignment_overlaps} assignment overlaps.")

        print("Foreign key check: PASSED")
        print("Assignment overlap check: PASSED")


def rebuild():
    if not DB_PATH.exists():
        raise FileNotFoundError(f"Existing database not found: {DB_PATH}")

    if not SCHEMA_PATH.exists():
        raise FileNotFoundError(f"Schema file not found: {SCHEMA_PATH}")

    # Step 1: Create a safety backup.
    shutil.copy2(DB_PATH, BACKUP_PATH)
    print(f"Safety backup created: {BACKUP_PATH.name}")

    try:
        # Step 2: Create a fresh database from the schema.
        DB_PATH.unlink()

        with sqlite3.connect(DB_PATH) as conn:
            conn.execute("PRAGMA foreign_keys = ON")
            schema = SCHEMA_PATH.read_text(encoding="utf-8")
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
        generate_employees()

        print("\n[3/5] Generating promotion history...")
        generate_promotions()

        print("\n[4/5] Generating salary history...")
        generate_salary_history()

        print("\n[5/5] Generating supporting records...")
        generate_supporting_records()

        # Step 5: Validate the generated database.
        validate_database()

        print("\n" + "=" * 45)
        print("DATABASE REBUILD COMPLETED SUCCESSFULLY")
        print(f"Database: {DB_PATH}")
        print(f"Backup: {BACKUP_PATH}")
        print("=" * 45)

    except Exception:
        print("\nDATABASE REBUILD FAILED.")
        print("Restoring the original database...")

        if DB_PATH.exists():
            DB_PATH.unlink()

        shutil.copy2(BACKUP_PATH, DB_PATH)

        print("Original database restored.")
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    rebuild()
