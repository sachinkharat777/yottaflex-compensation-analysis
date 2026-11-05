import csv
import sqlite3
from pathlib import Path

DB_PATH = Path("database/compensation.db")
OUTPUT_PATH = Path("outputs/compensation_analysis_2026-12-31.csv")

AS_OF_DATE = "2026-12-31"


def analyze_compensation():

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    with sqlite3.connect(DB_PATH) as conn:

        conn.row_factory = sqlite3.Row

        query = """
        SELECT
            e.employee_id,
            a.role_id,
            a.level_id,
            a.location_id,
            a.fte,

            s.salary_id,
            s.annual_base_salary,
            s.currency_code AS salary_currency,

            b.band_id,
            b.min_salary,
            b.midpoint_salary,
            b.max_salary,
            b.currency_code AS band_currency,

            (
                SELECT cr.rate_to_inr
                FROM CurrencyRate cr
                WHERE cr.currency_code = s.currency_code
                  AND cr.effective_date <= ?
                ORDER BY cr.effective_date DESC
                LIMIT 1
            ) AS salary_fx_rate,

            (
                SELECT cr.rate_to_inr
                FROM CurrencyRate cr
                WHERE cr.currency_code = b.currency_code
                  AND cr.effective_date <= ?
                ORDER BY cr.effective_date DESC
                LIMIT 1
            ) AS band_fx_rate

        FROM Employee e

        LEFT JOIN EmployeeAssignment a
            ON e.employee_id = a.employee_id
            AND a.effective_start <= ?
            AND (
                a.effective_end IS NULL
                OR a.effective_end > ?
            )

        LEFT JOIN SalaryRecord s
            ON e.employee_id = s.employee_id
            AND s.effective_start <= ?
            AND (
                s.effective_end IS NULL
                OR s.effective_end > ?
            )

        LEFT JOIN CompensationBand b
            ON a.role_id = b.role_id
            AND a.level_id = b.level_id
            AND a.location_id = b.location_id
            AND b.effective_start <= ?
            AND (
                b.effective_end IS NULL
                OR b.effective_end > ?
            )

        ORDER BY e.employee_id
        """

        params = (AS_OF_DATE,) * 8
        records = conn.execute(query, params).fetchall()

    results = []

    for record in records:

        result = {
            "employee_id": record["employee_id"],
            "role_id": record["role_id"],
            "level_id": record["level_id"],
            "location_id": record["location_id"],
            "fte": record["fte"],
            "salary_id": record["salary_id"],
            "salary_currency": record["salary_currency"],
            "band_id": record["band_id"],
            "normalized_salary_inr": None,
            "band_min_inr": None,
            "band_midpoint_inr": None,
            "band_max_inr": None,
            "compa_ratio": None,
            "band_position_percent": None,
            "band_status": None,
            "analysis_status": None,
        }

        # Check required records.
        if record["salary_id"] is None:
            result["analysis_status"] = "MISSING_SALARY"
            results.append(result)
            continue

        if record["fte"] is None or record["fte"] <= 0:
            result["analysis_status"] = "INVALID_FTE"
            results.append(result)
            continue

        if record["band_id"] is None:
            result["analysis_status"] = "MISSING_BAND"
            results.append(result)
            continue

        if (
            record["salary_fx_rate"] is None
            or record["band_fx_rate"] is None
        ):
            result["analysis_status"] = "MISSING_FX_RATE"
            results.append(result)
            continue

        # Normalize employee salary to full-time equivalent.
        normalized_salary = (
            record["annual_base_salary"] / record["fte"]
        )

        # Convert salary and band values into INR.
        normalized_salary_inr = (
            normalized_salary * record["salary_fx_rate"]
        )

        band_min_inr = (
            record["min_salary"] * record["band_fx_rate"]
        )

        band_midpoint_inr = (
            record["midpoint_salary"] * record["band_fx_rate"]
        )

        band_max_inr = (
            record["max_salary"] * record["band_fx_rate"]
        )

        # Calculate compensation metrics.
        compa_ratio = (
            normalized_salary_inr / band_midpoint_inr
        )

        band_position = (
            (normalized_salary_inr - band_min_inr)
            / (band_max_inr - band_min_inr)
        ) * 100

        if normalized_salary_inr < band_min_inr:
            band_status = "BELOW_BAND"

        elif normalized_salary_inr > band_max_inr:
            band_status = "ABOVE_BAND"

        else:
            band_status = "WITHIN_BAND"

        result.update({
            "normalized_salary_inr": round(normalized_salary_inr, 2),
            "band_min_inr": round(band_min_inr, 2),
            "band_midpoint_inr": round(band_midpoint_inr, 2),
            "band_max_inr": round(band_max_inr, 2),
            "compa_ratio": round(compa_ratio, 4),
            "band_position_percent": round(band_position, 2),
            "band_status": band_status,
            "analysis_status": "SUCCESS",
        })

        results.append(result)

    # Export the analysis results.
    if results:
        with open(
            OUTPUT_PATH,
            "w",
            newline="",
            encoding="utf-8"
        ) as file:

            writer = csv.DictWriter(
                file,
                fieldnames=results[0].keys()
            )

            writer.writeheader()
            writer.writerows(results)

    successful = sum(
        row["analysis_status"] == "SUCCESS"
        for row in results
    )

    print("\nCOMPENSATION ANALYSIS COMPLETED")
    print("--------------------------------")
    print(f"Employees analyzed: {len(results)}")
    print(f"Successful analyses: {successful}")
    print(f"Unsuccessful analyses: {len(results) - successful}")
    print(f"Output file: {OUTPUT_PATH}")


if __name__ == "__main__":
    analyze_compensation()