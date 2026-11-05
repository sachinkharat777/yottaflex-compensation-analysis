"""
Central configuration for synthetic data generation.
"""

# Reproducibility
SEED = 20261022

# Dataset size
EMPLOYEE_COUNT = 5000

# Related record limits
PROMOTION_COUNT = 500
PROPOSAL_COUNT = 250

# Reference dates
AS_OF_DATE = "2026-01-01"

# Random seed offsets for independent generators
SEED_OFFSETS = {
    "employees": 0,
    "promotions": 100,
    "transactions": 200,
    "supporting": 300,
}