import hashlib
import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

from src.generator.config import (
    SEED,
    EMPLOYEE_COUNT,
    PROMOTION_COUNT,
    PROPOSAL_COUNT,
    AS_OF_DATE,
    SEED_OFFSETS,
)
from src.validation.validators import collect_validation_results


ROOT = Path(__file__).resolve().parents[2]
DB_PATH = ROOT / "database" / "compensation.db"
OUTPUT_DIR = ROOT / "outputs"
JSON_DIR = OUTPUT_DIR / "exports"

SQL_EXPORT_PATH = OUTPUT_DIR / "compensation_database.sql"
VALIDATION_JSON_PATH = OUTPUT_DIR / "validation_summary.json"
VALIDATION_MD_PATH = OUTPUT_DIR / "validation_summary.md"
MANIFEST_PATH = OUTPUT_DIR / "source_manifest.json"


def sha256_file(file_path):
    """Calculate the SHA-256 checksum of a file."""
    digest = hashlib.sha256()

    with open(file_path, "rb") as file:
        for chunk in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(chunk)

    return digest.hexdigest()


def write_json(file_path, data):
    """Write JSON using UTF-8 encoding."""
    file_path.parent.mkdir(parents=True, exist_ok=True)

    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(
            data,
            file,
            indent=2,
            ensure_ascii=False,
            default=str,
        )


def quote_identifier(identifier):
    """Safely quote a SQLite table identifier."""
    return '"' + identifier.replace('"', '""') + '"'


def get_table_names(conn):
    """Return all user-created SQLite table names."""
    rows = conn.execute("""
        SELECT name
        FROM sqlite_master
        WHERE type = 'table'
          AND name NOT LIKE 'sqlite_%'
        ORDER BY name
    """).fetchall()

    return [row[0] for row in rows]


def export_tables_to_json(conn, table_names):
    """Export every database table as a separate JSON array."""
    JSON_DIR.mkdir(parents=True, exist_ok=True)

    row_counts = {}
    exported_files = []

    for table_name in table_names:
        query = f"SELECT * FROM {quote_identifier(table_name)}"
        cursor = conn.execute(query)

        columns = [description[0] for description in cursor.description]
        records = [
            dict(zip(columns, row))
            for row in cursor.fetchall()
        ]

        output_path = JSON_DIR / f"{table_name}.json"
        write_json(output_path, records)

        row_counts[table_name] = len(records)
        exported_files.append(output_path)

        print(f"JSON exported: {table_name} ({len(records)} rows)")

    return row_counts, exported_files


def export_database_to_sql(conn):
    """Export the complete SQLite database as SQL statements."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    with open(SQL_EXPORT_PATH, "w", encoding="utf-8") as file:
        for statement in conn.iterdump():
            file.write(statement + "\n")

    print(f"SQL exported: {SQL_EXPORT_PATH.name}")
    return SQL_EXPORT_PATH


def export_validation_summary():
    """Generate machine-readable and human-readable validation reports."""
    results = collect_validation_results(DB_PATH)

    write_json(VALIDATION_JSON_PATH, results)

    lines = [
        "# Data Validation Summary",
        "",
        f"- Generated: {datetime.now(timezone.utc).isoformat()}",
        f"- Database: `{DB_PATH.relative_to(ROOT)}`",
        f"- Overall status: **{results['overall_status']}**",
        f"- Checks passed: {results['passed_checks']}/{results['total_checks']}",
        f"- Checks failed: {results['failed_checks']}",
        "",
        "## Validation checks",
        "",
        "| Check | Status | Issues |",
        "|---|---|---:|",
    ]

    for item in results["checks"]:
        status = "PASS" if item["passed"] else "FAIL"
        lines.append(
            f"| {item['name']} | {status} | {item['issue_count']} |"
        )

    lines.extend([
        "",
        "## Interpretation",
        "",
        "A check passes when its detected issue count is zero.",
        "A failed check indicates records that require investigation.",
        "",
    ])

    VALIDATION_MD_PATH.write_text(
        "\n".join(lines),
        encoding="utf-8",
    )

    print(
        f"Validation: {results['passed_checks']}/"
        f"{results['total_checks']} checks passed"
    )

    return results


def create_source_manifest(row_counts, exported_files, sql_path):
    """Create a manifest describing the source and exported artifacts."""
    files_to_hash = [
        DB_PATH,
        ROOT / "database" / "schema.sql",
        *exported_files,
        sql_path,
        VALIDATION_JSON_PATH,
        VALIDATION_MD_PATH,
    ]

    checksums = {}

    for file_path in files_to_hash:
        relative_path = file_path.relative_to(ROOT).as_posix()
        checksums[relative_path] = sha256_file(file_path)

    manifest = {
        "project": "YottaFlex Compensation Analysis",
        "source_type": "Synthetic compensation dataset",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "database": "database/compensation.db",
        "configuration": {
            "seed": SEED,
            "employee_count": EMPLOYEE_COUNT,
            "promotion_count": PROMOTION_COUNT,
            "proposal_count": PROPOSAL_COUNT,
            "as_of_date": AS_OF_DATE,
            "seed_offsets": SEED_OFFSETS,
        },
        "database_summary": {
            "table_count": len(row_counts),
            "total_rows": sum(row_counts.values()),
            "row_counts": row_counts,
        },
        "checksums": {
            "algorithm": "SHA-256",
            "files": checksums,
        },
    }

    write_json(MANIFEST_PATH, manifest)

    print(f"Manifest exported: {MANIFEST_PATH.name}")
    return manifest


def run_exports():
    """Run the complete export workflow."""
    if not DB_PATH.exists():
        raise FileNotFoundError(
            f"Database not found: {DB_PATH}"
        )

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    JSON_DIR.mkdir(parents=True, exist_ok=True)

    print("\n========== PHASE 8: DATA EXPORT ==========\n")

    conn = sqlite3.connect(DB_PATH)

    try:
        table_names = get_table_names(conn)

        if not table_names:
            raise RuntimeError("No database tables were found.")

        row_counts, exported_files = export_tables_to_json(
            conn,
            table_names,
        )

        sql_path = export_database_to_sql(conn)

    finally:
        conn.close()

    validation_results = export_validation_summary()

    create_source_manifest(
        row_counts,
        exported_files,
        sql_path,
    )

    print("\n==========================================")
    print(f"Tables exported: {len(row_counts)}")
    print(f"Rows exported: {sum(row_counts.values())}")
    print(f"Validation status: {validation_results['overall_status']}")
    print("Export workflow completed.")
    print("==========================================")

    if validation_results["overall_status"] != "PASS":
        raise RuntimeError(
            "Exports were created, but database validation failed. "
            "Review outputs/validation_summary.md."
        )


if __name__ == "__main__":
    run_exports()