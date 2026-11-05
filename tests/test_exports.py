
import hashlib
import json
import sqlite3
import shutil

from src.exports import export_data


def create_sample_database(db_path):
    """Create a small SQLite database for isolated export tests."""
    conn = sqlite3.connect(db_path)

    conn.execute("""
        CREATE TABLE Employee (
            employee_id TEXT PRIMARY KEY,
            employee_name TEXT NOT NULL
        )
    """)

    conn.executemany(
        "INSERT INTO Employee VALUES (?, ?)",
        [
            ("E001", "Employee One"),
            ("E002", "Employee Two"),
        ],
    )

    conn.commit()
    conn.close()


def test_sha256_file_returns_correct_hash(tmp_path):
    file_path = tmp_path / "sample.txt"
    file_path.write_text("YottaFlex", encoding="utf-8")

    expected = hashlib.sha256(b"YottaFlex").hexdigest()

    assert export_data.sha256_file(file_path) == expected


def test_write_json_creates_valid_json(tmp_path):
    file_path = tmp_path / "sample.json"
    data = {"employees": 2, "status": "PASS"}

    export_data.write_json(file_path, data)

    assert file_path.exists()

    with open(file_path, encoding="utf-8") as file:
        loaded = json.load(file)

    assert loaded == data


def test_get_table_names_returns_user_tables(tmp_path):
    db_path = tmp_path / "sample.db"
    create_sample_database(db_path)

    conn = sqlite3.connect(db_path)

    try:
        table_names = export_data.get_table_names(conn)
    finally:
        conn.close()

    assert table_names == ["Employee"]


def test_export_tables_to_json_preserves_database_rows(
    tmp_path,
    monkeypatch,
):
    db_path = tmp_path / "sample.db"
    create_sample_database(db_path)

    json_dir = tmp_path / "exports"
    monkeypatch.setattr(export_data, "JSON_DIR", json_dir)

    conn = sqlite3.connect(db_path)

    try:
        row_counts, exported_files = (
            export_data.export_tables_to_json(
                conn,
                ["Employee"],
            )
        )
    finally:
        conn.close()

    assert row_counts == {"Employee": 2}
    assert len(exported_files) == 1

    with open(json_dir / "Employee.json", encoding="utf-8") as file:
        records = json.load(file)

    assert len(records) == 2
    assert records[0]["employee_id"] == "E001"
    assert records[1]["employee_id"] == "E002"


def test_sql_export_can_be_restored(tmp_path, monkeypatch):
    source_db = tmp_path / "source.db"
    restored_db = tmp_path / "restored.db"
    create_sample_database(source_db)

    sql_path = tmp_path / "compensation_database.sql"

    monkeypatch.setattr(
        export_data,
        "SQL_EXPORT_PATH",
        sql_path,
    )

    conn = sqlite3.connect(source_db)

    try:
        export_data.export_database_to_sql(conn)
    finally:
        conn.close()

    assert sql_path.exists()

    restored_conn = sqlite3.connect(restored_db)

    try:
        with open(sql_path, encoding="utf-8") as file:
            restored_conn.executescript(file.read())

        count = restored_conn.execute(
            "SELECT COUNT(*) FROM Employee"
        ).fetchone()[0]

        assert count == 2

    finally:
        restored_conn.close()


def test_validation_summary_generates_json_and_markdown(
    tmp_path,
    monkeypatch,
):
    if not export_data.DB_PATH.exists():
        raise AssertionError("Project database does not exist.")

    test_db = tmp_path / "compensation.db"
    shutil.copy2(export_data.DB_PATH, test_db)

    monkeypatch.setattr(export_data, "ROOT", tmp_path)
    monkeypatch.setattr(export_data, "DB_PATH", test_db)
    monkeypatch.setattr(
        export_data,
        "VALIDATION_JSON_PATH",
        tmp_path / "validation_summary.json",
    )
    monkeypatch.setattr(
        export_data,
        "VALIDATION_MD_PATH",
        tmp_path / "validation_summary.md",
    )

    results = export_data.export_validation_summary()

    assert results["total_checks"] == 11
    assert results["passed_checks"] == 11
    assert results["failed_checks"] == 0
    assert results["overall_status"] == "PASS"

    assert (tmp_path / "validation_summary.json").exists()
    assert (tmp_path / "validation_summary.md").exists()

    with open(
        tmp_path / "validation_summary.json",
        encoding="utf-8",
    ) as file:
        saved_results = json.load(file)

    assert saved_results["overall_status"] == "PASS"


def test_manifest_contains_configuration_and_checksums(
    tmp_path,
    monkeypatch,
):
    db_path = tmp_path / "database" / "compensation.db"
    schema_path = tmp_path / "database" / "schema.sql"
    json_file = tmp_path / "outputs" / "exports" / "Employee.json"
    sql_file = tmp_path / "outputs" / "compensation_database.sql"
    validation_json = tmp_path / "outputs" / "validation_summary.json"
    validation_md = tmp_path / "outputs" / "validation_summary.md"

    db_path.parent.mkdir(parents=True)
    db_path.write_bytes(b"sample database")

    schema_path.write_text(
        "CREATE TABLE Employee;",
        encoding="utf-8",
    )

    json_file.parent.mkdir(parents=True)
    json_file.write_text("[]", encoding="utf-8")

    sql_file.write_text(
        "CREATE TABLE Employee;",
        encoding="utf-8",
    )

    validation_json.write_text("{}", encoding="utf-8")
    validation_md.write_text("# Validation", encoding="utf-8")

    monkeypatch.setattr(export_data, "ROOT", tmp_path)
    monkeypatch.setattr(export_data, "DB_PATH", db_path)
    monkeypatch.setattr(
        export_data,
        "MANIFEST_PATH",
        tmp_path / "outputs" / "source_manifest.json",
    )
    monkeypatch.setattr(
        export_data,
        "VALIDATION_JSON_PATH",
        validation_json,
    )
    monkeypatch.setattr(
        export_data,
        "VALIDATION_MD_PATH",
        validation_md,
    )

    manifest = export_data.create_source_manifest(
        {"Employee": 2},
        [json_file],
        sql_file,
    )

    assert manifest["configuration"]["seed"] == 20261022
    assert manifest["database_summary"]["table_count"] == 1
    assert manifest["database_summary"]["total_rows"] == 2
    assert manifest["checksums"]["algorithm"] == "SHA-256"

    assert (
        "database/compensation.db"
        in manifest["checksums"]["files"]
    )

    assert (
        tmp_path / "outputs" / "source_manifest.json"
    ).exists()
