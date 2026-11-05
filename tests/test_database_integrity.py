import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.validation.validators import (
    check_assignment_date_overlaps,
    check_band_date_overlaps
)

DB_PATH = ROOT / "database" / "compensation.db"


def test_foreign_key_integrity():
    con = sqlite3.connect(DB_PATH)

    result = con.execute("PRAGMA foreign_key_check").fetchall()

    con.close()

    assert len(result) == 0


def test_assignment_date_overlaps():
    con = sqlite3.connect(DB_PATH)

    result = check_assignment_date_overlaps(con)

    con.close()

    assert result == 0


def test_compensation_band_date_overlaps():
    con = sqlite3.connect(DB_PATH)

    result = check_band_date_overlaps(con)

    con.close()

    assert result == 0


def test_employee_records_exist():
    con = sqlite3.connect(DB_PATH)

    result = con.execute(
        "SELECT COUNT(*) FROM Employee"
    ).fetchone()[0]

    con.close()

    assert result > 0


def test_salary_records_exist():
    con = sqlite3.connect(DB_PATH)

    result = con.execute(
        "SELECT COUNT(*) FROM SalaryRecord"
    ).fetchone()[0]

    con.close()

    assert result > 0

def test_all_salary_currencies_have_conversion_rates():
    con = sqlite3.connect(DB_PATH)

    missing_rates = con.execute("""
        SELECT DISTINCT s.currency_code
        FROM SalaryRecord s
        LEFT JOIN CurrencyRate c
            ON s.currency_code = c.currency_code
        WHERE c.currency_code IS NULL
    """).fetchall()

    con.close()

    assert len(missing_rates) == 0    