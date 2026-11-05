
import shutil
import sqlite3
from pathlib import Path

from src.validation import validators


# --------------------------------------------------
# Assignment overlap tests
# --------------------------------------------------

def test_assignment_overlap_detected():
    conn = sqlite3.connect(":memory:")

    conn.execute("""
        CREATE TABLE EmployeeAssignment (
            assignment_id TEXT,
            employee_id TEXT,
            effective_start TEXT,
            effective_end TEXT
        )
    """)

    conn.executemany(
        """
        INSERT INTO EmployeeAssignment
        VALUES (?, ?, ?, ?)
        """,
        [
            ("ASG-001", "EMP-001", "2024-01-01", "2025-01-01"),
            ("ASG-002", "EMP-001", "2024-06-01", None),
        ],
    )

    assert validators.check_assignment_date_overlaps(conn) == 1

    conn.close()


def test_adjacent_assignments_are_not_overlapping():
    conn = sqlite3.connect(":memory:")

    conn.execute("""
        CREATE TABLE EmployeeAssignment (
            assignment_id TEXT,
            employee_id TEXT,
            effective_start TEXT,
            effective_end TEXT
        )
    """)

    conn.executemany(
        """
        INSERT INTO EmployeeAssignment
        VALUES (?, ?, ?, ?)
        """,
        [
            ("ASG-001", "EMP-001", "2024-01-01", "2025-01-01"),
            ("ASG-002", "EMP-001", "2025-01-01", None),
        ],
    )

    assert validators.check_assignment_date_overlaps(conn) == 0

    conn.close()


# --------------------------------------------------
# Compensation band overlap tests
# --------------------------------------------------

def test_compensation_band_overlap_detected():
    conn = sqlite3.connect(":memory:")

    conn.execute("""
        CREATE TABLE CompensationBand (
            band_id INTEGER,
            role_id TEXT,
            level_id TEXT,
            location_id TEXT,
            effective_start TEXT,
            effective_end TEXT
        )
    """)

    conn.executemany(
        """
        INSERT INTO CompensationBand
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        [
            (1, "ROLE-001", "LEVEL-001", "LOC-001",
             "2024-01-01", "2025-06-01"),
            (2, "ROLE-001", "LEVEL-001", "LOC-001",
             "2025-01-01", None),
        ],
    )

    assert validators.check_band_date_overlaps(conn) == 1

    conn.close()


def test_different_roles_can_have_overlapping_bands():
    conn = sqlite3.connect(":memory:")

    conn.execute("""
        CREATE TABLE CompensationBand (
            band_id INTEGER,
            role_id TEXT,
            level_id TEXT,
            location_id TEXT,
            effective_start TEXT,
            effective_end TEXT
        )
    """)

    conn.executemany(
        """
        INSERT INTO CompensationBand
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        [
            (1, "ROLE-001", "LEVEL-001", "LOC-001",
             "2024-01-01", None),
            (2, "ROLE-002", "LEVEL-001", "LOC-001",
             "2024-01-01", None),
        ],
    )

    assert validators.check_band_date_overlaps(conn) == 0

    conn.close()


# --------------------------------------------------
# Full database validation tests
# --------------------------------------------------

def test_existing_database_passes_validations(monkeypatch, tmp_path):
    source_db = Path("database/compensation.db")

    assert source_db.exists(), "Project database was not found."

    test_db = tmp_path / "compensation_test.db"
    shutil.copy2(source_db, test_db)

    monkeypatch.setattr(validators, "DB_PATH", test_db)

    assert validators.run_validations() is True


def test_validation_detects_invalid_salary(monkeypatch, tmp_path):
    source_db = Path("database/compensation.db")

    assert source_db.exists(), "Project database was not found."

    test_db = tmp_path / "compensation_invalid_test.db"
    shutil.copy2(source_db, test_db)

    conn = sqlite3.connect(test_db)

    conn.execute("PRAGMA ignore_check_constraints = ON")

    conn.execute("""
        UPDATE SalaryRecord
        SET annual_base_salary = 0
        WHERE salary_id = (
            SELECT salary_id
            FROM SalaryRecord
            LIMIT 1
        )
    """)

    conn.commit()
    conn.close()

    monkeypatch.setattr(validators, "DB_PATH", test_db)

    assert validators.run_validations() is False
