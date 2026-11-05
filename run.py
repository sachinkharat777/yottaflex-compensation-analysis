
from pathlib import Path
import sys

# Ensure execution starts from the project root.
ROOT = Path(__file__).resolve().parent

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.validation.validators import run_validations
from src.analysis.compensation import analyze_compensation
from src.analysis.disparity_detector import detect_disparities
from src.analysis.evidence_analyzer import analyze_evidence
from src.analysis.comparator import compare_employees


def main():

    print("\n" + "=" * 55)
    print(" YOTTAFLEX - COMPENSATION ANALYSIS SYSTEM")
    print("=" * 55)

    database_path = ROOT / "database" / "compensation.db"

    # Step 1: Check database availability.
    print("\n[1/5] Checking database...")

    if not database_path.exists():
        raise FileNotFoundError(
            "Database not found. Run python rebuild_database.py first."
        )

    print("Database found.")

    # Step 2: Validate database records.
    print("\n[2/5] Running database validations...")

    if not run_validations():
        raise RuntimeError(
            "Database validation failed. Analysis stopped."
        )

    # Step 3: Calculate compensation metrics.
    print("\n[3/5] Running compensation analysis...")

    analyze_compensation()

    # Step 4: Run disparity detection.
    print("\n[4/5] Running disparity detection...")

    detect_disparities()

    # Step 5: Run evidence and employee comparison.
    print("\n[5/5] Running evidence analysis...")

    analyze_evidence()

    print("\nRunning employee comparison...")

    compare_employees()

    # Final summary.
    print("\n" + "=" * 55)
    print("COMPENSATION ANALYSIS COMPLETED SUCCESSFULLY")
    print("=" * 55)

    print("\nGenerated reports:")

    output_directory = ROOT / "outputs"

    reports = [
        "compensation_analysis_2026-12-31.csv",
        "disparity_flags.csv",
        "evidence_based_review.csv",
        "employee_comparison.csv",
    ]

    for report in reports:
        report_path = output_directory / report

        if report_path.exists():
            print(f"[OK] {report}")
        else:
            print(f"[MISSING] {report}")

    print("\nAll workflow operations completed.")


if __name__ == "__main__":

    try:
        main()

    except Exception as error:

        print("\nWORKFLOW FAILED")
        print(f"Reason: {error}")

        sys.exit(1)
