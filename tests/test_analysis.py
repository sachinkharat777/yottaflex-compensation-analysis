
import pandas as pd


def test_compa_ratio_calculation():

    salary = 1_200_000
    midpoint = 1_000_000

    compa_ratio = salary / midpoint

    assert compa_ratio == 1.2


def test_band_position_calculation():

    salary = 1_000_000
    minimum = 800_000
    maximum = 1_200_000

    band_position = (
        (salary - minimum)
        / (maximum - minimum)
    ) * 100

    assert band_position == 50


def test_salary_below_band():

    salary = 700_000
    minimum = 800_000

    assert salary < minimum


def test_salary_above_band():

    salary = 1_300_000
    maximum = 1_200_000

    assert salary > maximum


def test_fte_normalization():

    actual_salary = 800_000
    fte = 0.8

    normalized_salary = actual_salary / fte

    assert normalized_salary == 1_000_000


def test_missing_salary_data():

    data = pd.DataFrame({
        "employee_id": ["EMP-001", "EMP-002"],
        "salary": [500_000, None]
    })

    missing_count = data["salary"].isna().sum()

    assert missing_count == 1


def test_currency_conversion():

    salary_gbp = 10_000
    gbp_to_inr = 110

    salary_inr = salary_gbp * gbp_to_inr

    assert salary_inr == 1_100_000


def test_comparable_group_separation():

    employees = pd.DataFrame({
        "employee_id": ["EMP-001", "EMP-002"],
        "comparable_group": ["DATA", "ML"]
    })

    assert (
        employees.loc[0, "comparable_group"]
        != employees.loc[1, "comparable_group"]
    )
