
from pathlib import Path
import sqlite3

ROOT = Path(__file__).resolve().parents[2]
DB_PATH = ROOT / "database" / "compensation.db"

# 10 comparable job groups, with 5 roles in each group.
ROLE_GROUPS = {
    "DATA_ANALYTICS": (
        "Data Analytics",
        "Roles focused on business reporting, analytics and interpreting data.",
        [
            "Data Analyst",
            "BI Analyst",
            "Product Analyst",
            "Business Analyst",
            "Reporting Analyst",
        ],
    ),
    "DATA_SCIENCE": (
        "Data Science",
        "Roles focused on statistical analysis, experimentation and predictive modeling.",
        [
            "Data Scientist",
            "Applied Scientist",
            "Decision Scientist",
            "Research Scientist",
            "Quantitative Analyst",
        ],
    ),
    "ML_ENGINEERING": (
        "ML Engineering",
        "Roles focused on developing and deploying machine learning systems.",
        [
            "ML Engineer",
            "MLOps Engineer",
            "ML Platform Engineer",
            "Computer Vision Engineer",
            "NLP Engineer",
        ],
    ),
    "SOFTWARE_ENGINEERING": (
        "Software Engineering",
        "Roles focused on designing, building and maintaining software.",
        [
            "Software Engineer",
            "Backend Engineer",
            "Frontend Engineer",
            "Full Stack Engineer",
            "Mobile Engineer",
        ],
    ),
    "DATA_ENGINEERING": (
        "Data Engineering",
        "Roles focused on data pipelines, integration and data platforms.",
        [
            "Data Engineer",
            "Analytics Engineer",
            "ETL Developer",
            "Data Platform Engineer",
            "Big Data Engineer",
        ],
    ),
    "CLOUD_DEVOPS": (
        "Cloud and DevOps",
        "Roles focused on infrastructure, cloud platforms and reliability.",
        [
            "DevOps Engineer",
            "Cloud Engineer",
            "Site Reliability Engineer",
            "Platform Engineer",
            "Infrastructure Engineer",
        ],
    ),
    "CYBERSECURITY": (
        "Cybersecurity",
        "Roles focused on protecting systems, applications and information.",
        [
            "Security Analyst",
            "Security Engineer",
            "Application Security Engineer",
            "Threat Intelligence Analyst",
            "IAM Engineer",
        ],
    ),
    "QUALITY_ENGINEERING": (
        "Quality Engineering",
        "Roles focused on software testing, automation and quality assurance.",
        [
            "QA Engineer",
            "Automation Engineer",
            "Software Development Engineer in Test",
            "Performance Engineer",
            "Test Analyst",
        ],
    ),
    "PRODUCT_DESIGN": (
        "Product and Design",
        "Roles focused on product strategy, user experience and product operations.",
        [
            "Product Manager",
            "Technical Product Manager",
            "UX Designer",
            "UX Researcher",
            "Product Operations Analyst",
        ],
    ),
    "IT_OPERATIONS": (
        "IT Operations",
        "Roles focused on technical support, systems and IT infrastructure.",
        [
            "Technical Support Engineer",
            "Systems Administrator",
            "IT Support Analyst",
            "Network Engineer",
            "Database Administrator",
        ],
    ),
}

LEVELS = [
    ("LEVEL-001", "Junior", 1),
    ("LEVEL-002", "Mid", 2),
    ("LEVEL-003", "Senior", 3),
    ("LEVEL-004", "Lead", 4),
]

LOCATIONS = [
    ("LOC-001", "Pune", "IN", "INR"),
    ("LOC-002", "Bengaluru", "IN", "INR"),
    ("LOC-003", "London", "GB", "GBP"),
]

LEVEL_MULTIPLIERS = {
    "Junior": 1.00,
    "Mid": 1.45,
    "Senior": 1.90,
    "Lead": 2.35,
}


def generate_roles():
    roles = []
    role_number = 1

    for group_id, (family, rationale, role_names) in ROLE_GROUPS.items():
        for role_name in role_names:
            role_id = f"ROLE-{role_number:03d}"

            roles.append(
                (
                    role_id,
                    role_name,
                    family,
                    group_id,
                    rationale,
                )
            )

            role_number += 1

    return roles



def generate_bands(roles):
    bands = []

    for role_index, (role_id, _, _, _, _) in enumerate(roles):

        for level_id, level_name, _ in LEVELS:

            for location_id, _, _, currency in LOCATIONS:

                if currency == "INR":
                    base_salary = 450_000 + role_index * 45_000
                else:
                    base_salary = 32_000 + role_index * 2_500

                for year in [2024, 2025, 2026]:

                    # Synthetic annual salary growth assumption.
                    historical_factor = 1.04 ** (year - 2026)

                    midpoint = (
                        base_salary
                        * historical_factor
                        * LEVEL_MULTIPLIERS[level_name]
                    )

                    band_id = (
                        f"BAND-{role_id}-{level_id}-{location_id}-{year}"
                    )

                    effective_start = f"{year}-01-01"
                    effective_end = f"{year + 1}-01-01"

                    bands.append(
                        (
                            band_id,
                            role_id,
                            level_id,
                            location_id,
                            round(midpoint * 0.80, 2),
                            round(midpoint, 2),
                            round(midpoint * 1.20, 2),
                            currency,
                            effective_start,
                            effective_end,
                        )
                    )

    return bands



def generate_master_data():
    roles = generate_roles()
    bands = generate_bands(roles)

    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("PRAGMA foreign_keys = ON")

        conn.executemany(
            """
            INSERT OR IGNORE INTO Role (
                role_id,
                role_name,
                job_family,
                comparable_group,
                comparison_rationale
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            roles,
        )

        conn.executemany(
            """
            INSERT OR IGNORE INTO Level (
                level_id,
                level_name,
                seniority_rank
            )
            VALUES (?, ?, ?)
            """,
            LEVELS,
        )

        conn.executemany(
            """
            INSERT OR IGNORE INTO Location (
                location_id,
                location_name,
                country_code,
                currency_code
            )
            VALUES (?, ?, ?, ?)
            """,
            LOCATIONS,
        )

        conn.executemany(
            """
            INSERT OR IGNORE INTO CompensationBand (
                band_id,
                role_id,
                level_id,
                location_id,
                min_salary,
                midpoint_salary,
                max_salary,
                currency_code,
                effective_start,
                effective_end
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            bands,
        )

    print("Master data generation completed.")
    print(f"Roles: {len(roles)}")
    print(f"Levels: {len(LEVELS)}")
    print(f"Role-level combinations: {len(roles) * len(LEVELS)}")
    print(f"Locations: {len(LOCATIONS)}")
    print(f"Compensation bands: {len(bands)}")


if __name__ == "__main__":
    generate_master_data()
