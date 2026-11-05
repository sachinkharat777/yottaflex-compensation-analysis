
import random

import pytest

from src.generator.config import (
    SEED,
    EMPLOYEE_COUNT,
    PROMOTION_COUNT,
    PROPOSAL_COUNT,
    SEED_OFFSETS,
)
from src.generator.employee_generator import (
    generate_employees,
    random_hire_date,
)
from src.generator.promotion_generator import generate_promotions
from src.generator.supporting_generator import (
    generate_supporting_records,
    _build_candidates,
)


def make_record(
    employee_id,
    salary,
    fte=1.0,
    min_salary=80.0,
    midpoint=100.0,
    max_salary=120.0,
    group="DATA_ANALYST",
):
    """Create a compensation record for proposal-rule tests."""
    return (
        employee_id,
        "ROLE-001",
        "LEVEL-001",
        "LOCATION-001",
        fte,
        salary,
        "INR",
        min_salary,
        midpoint,
        max_salary,
        group,
        24,
        f"EVD-{employee_id}",
        4.0,
        1.0,
    )


# --------------------------------------------------
# Configuration tests
# --------------------------------------------------

def test_generator_configuration_defaults():
    assert SEED == 20261022
    assert EMPLOYEE_COUNT == 5000
    assert PROMOTION_COUNT == 500
    assert PROPOSAL_COUNT == 250


def test_generator_seed_offsets_are_independent():
    assert SEED_OFFSETS["employees"] == 0
    assert SEED_OFFSETS["promotions"] == 100
    assert SEED_OFFSETS["transactions"] == 200
    assert SEED_OFFSETS["supporting"] == 300


# --------------------------------------------------
# Employee generator tests
# --------------------------------------------------

def test_employee_generator_rejects_zero_employees():
    with pytest.raises(ValueError):
        generate_employees(employee_count=0)


def test_employee_generator_rejects_negative_employees():
    with pytest.raises(ValueError):
        generate_employees(employee_count=-1)


def test_random_hire_date_is_reproducible():
    first = random_hire_date(random.Random(SEED))
    second = random_hire_date(random.Random(SEED))

    assert first == second


def test_random_hire_date_is_within_expected_range():
    hire_date = random_hire_date(random.Random(SEED))

    from datetime import date

    assert date(2021, 1, 1) <= hire_date <= date(2026, 1, 1)


# --------------------------------------------------
# Promotion generator tests
# --------------------------------------------------

def test_promotion_generator_rejects_negative_count():
    with pytest.raises(ValueError):
        generate_promotions(promotion_count=-1)


# --------------------------------------------------
# Supporting generator tests
# --------------------------------------------------

def test_supporting_generator_rejects_negative_proposals():
    with pytest.raises(ValueError):
        generate_supporting_records(proposal_count=-1)


def test_below_band_employee_receives_minimum_band_target():
    record = make_record(
        employee_id="EMP-001",
        salary=70.0,
    )

    candidates = _build_candidates([record])

    assert len(candidates) == 1
    assert candidates[0]["employee_id"] == "EMP-001"
    assert candidates[0]["proposed_salary"] == 80.0
    assert candidates[0]["rule"] == "BELOW_COMPENSATION_BAND"


def test_below_band_proposal_respects_fte():
    record = make_record(
        employee_id="EMP-002",
        salary=35.0,
        fte=0.5,
    )

    candidates = _build_candidates([record])

    assert len(candidates) == 1

    # Full-time target = 80
    # Actual FTE-adjusted target = 80 * 0.5
    assert candidates[0]["proposed_salary"] == 40.0


def test_above_band_employee_is_not_automatically_adjusted():
    record = make_record(
        employee_id="EMP-003",
        salary=130.0,
    )

    candidates = _build_candidates([record])

    assert candidates == []


def test_comparable_group_salary_gap_generates_proposal():
    records = [
        make_record(
            employee_id="EMP-004",
            salary=80.0,
            min_salary=50.0,
            midpoint=100.0,
            max_salary=150.0,
        ),
        make_record(
            employee_id="EMP-005",
            salary=120.0,
            min_salary=50.0,
            midpoint=100.0,
            max_salary=150.0,
        ),
    ]

    candidates = _build_candidates(records)

    assert len(candidates) == 1
    assert candidates[0]["employee_id"] == "EMP-004"
    assert candidates[0]["rule"] == "COMPARABLE_GROUP_GAP"
    assert candidates[0]["proposed_salary"] == 100.0


def test_comparable_group_gap_does_not_exceed_band_maximum():
    records = [
        make_record(
            employee_id="EMP-006",
            salary=50.0,
            min_salary=50.0,
            midpoint=100.0,
            max_salary=110.0,
        ),
        make_record(
            employee_id="EMP-007",
            salary=150.0,
            min_salary=50.0,
            midpoint=100.0,
            max_salary=200.0,
        ),
    ]

    candidates = _build_candidates(records)

    assert len(candidates) == 1
    assert candidates[0]["proposed_salary"] <= 110.0


def test_within_band_employee_without_group_gap_gets_no_proposal():
    record = make_record(
        employee_id="EMP-008",
        salary=100.0,
    )

    candidates = _build_candidates([record])

    assert candidates == []


def test_missing_performance_rating_excludes_candidate():
    record = list(make_record(
        employee_id="EMP-009",
        salary=70.0,
    ))

    record[13] = None

    candidates = _build_candidates([tuple(record)])

    assert candidates == []
