PRAGMA foreign_keys = ON;

-- 1. MASTER DATA

CREATE TABLE IF NOT EXISTS Role (
    role_id TEXT PRIMARY KEY,
    role_name TEXT NOT NULL UNIQUE,
    job_family TEXT NOT NULL,
    comparable_group TEXT,
    comparison_rationale TEXT
);

CREATE TABLE IF NOT EXISTS Level (
    level_id TEXT PRIMARY KEY,
    level_name TEXT NOT NULL UNIQUE,
    seniority_rank INTEGER NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS Location (
    location_id TEXT PRIMARY KEY,
    location_name TEXT NOT NULL,
    country_code TEXT NOT NULL,
    currency_code TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS Employee (
    employee_id TEXT PRIMARY KEY,
    hire_date TEXT NOT NULL,
    employment_status TEXT NOT NULL
        CHECK (employment_status IN (
            'ACTIVE', 'ON_LEAVE', 'TERMINATED'
        )),
    created_at TEXT NOT NULL
);

-- 2. COMPENSATION BANDS

CREATE TABLE IF NOT EXISTS CompensationBand (
    band_id TEXT PRIMARY KEY,
    role_id TEXT NOT NULL,
    level_id TEXT NOT NULL,
    location_id TEXT NOT NULL,
    min_salary REAL NOT NULL,
    midpoint_salary REAL NOT NULL,
    max_salary REAL NOT NULL,
    currency_code TEXT NOT NULL,
    effective_start TEXT NOT NULL,
    effective_end TEXT,

    FOREIGN KEY (role_id) REFERENCES Role(role_id),
    FOREIGN KEY (level_id) REFERENCES Level(level_id),
    FOREIGN KEY (location_id) REFERENCES Location(location_id),

    CHECK (min_salary > 0),
    CHECK (min_salary <= midpoint_salary),
    CHECK (midpoint_salary <= max_salary),
    CHECK (
        effective_end IS NULL
        OR effective_end > effective_start
    )
);

-- 3. EMPLOYEE ROLE / LEVEL / LOCATION HISTORY

CREATE TABLE IF NOT EXISTS EmployeeAssignment (
    assignment_id TEXT PRIMARY KEY,
    employee_id TEXT NOT NULL,
    role_id TEXT NOT NULL,
    level_id TEXT NOT NULL,
    location_id TEXT NOT NULL,
    fte REAL NOT NULL,
    effective_start TEXT NOT NULL,
    effective_end TEXT,
    change_reason TEXT NOT NULL,

    FOREIGN KEY (employee_id) REFERENCES Employee(employee_id),
    FOREIGN KEY (role_id) REFERENCES Role(role_id),
    FOREIGN KEY (level_id) REFERENCES Level(level_id),
    FOREIGN KEY (location_id) REFERENCES Location(location_id),

    CHECK (fte > 0 AND fte <= 1),
    CHECK (
        effective_end IS NULL
        OR effective_end > effective_start
    )
);

-- 4. SALARY HISTORY

CREATE TABLE IF NOT EXISTS SalaryRecord (
    salary_id TEXT PRIMARY KEY,
    employee_id TEXT NOT NULL,
    annual_base_salary REAL NOT NULL,
    currency_code TEXT NOT NULL,
    fte REAL NOT NULL,
    effective_start TEXT NOT NULL,
    effective_end TEXT,
    recorded_at TEXT NOT NULL,
    source TEXT NOT NULL,

    FOREIGN KEY (employee_id) REFERENCES Employee(employee_id),

    CHECK (annual_base_salary > 0),
    CHECK (fte > 0 AND fte <= 1),
    CHECK (
        effective_end IS NULL
        OR effective_end > effective_start
    )
);

-- 5. PROMOTION HISTORY

CREATE TABLE IF NOT EXISTS Promotion (
    promotion_id TEXT PRIMARY KEY,
    employee_id TEXT NOT NULL,
    from_role_id TEXT,
    from_level_id TEXT,
    to_role_id TEXT NOT NULL,
    to_level_id TEXT NOT NULL,
    effective_date TEXT NOT NULL,
    status TEXT NOT NULL
        CHECK (status IN ('PROPOSED', 'APPROVED', 'REJECTED', 'COMPLETED')),

    FOREIGN KEY (employee_id) REFERENCES Employee(employee_id),
    FOREIGN KEY (from_role_id) REFERENCES Role(role_id),
    FOREIGN KEY (from_level_id) REFERENCES Level(level_id),
    FOREIGN KEY (to_role_id) REFERENCES Role(role_id),
    FOREIGN KEY (to_level_id) REFERENCES Level(level_id)
);

-- 6. PERFORMANCE EVIDENCE

CREATE TABLE IF NOT EXISTS PerformanceEvidence (
    evidence_id TEXT PRIMARY KEY,
    employee_id TEXT NOT NULL,
    evidence_type TEXT NOT NULL,
    rating REAL,
    description TEXT NOT NULL,
    evidence_date TEXT NOT NULL,
    source_reference TEXT,

    FOREIGN KEY (employee_id) REFERENCES Employee(employee_id)
);

-- 7. TENURE SNAPSHOTS

CREATE TABLE IF NOT EXISTS TenureSnapshot (
    tenure_id TEXT PRIMARY KEY,
    employee_id TEXT NOT NULL,
    as_of_date TEXT NOT NULL,
    tenure_months INTEGER NOT NULL,

    FOREIGN KEY (employee_id) REFERENCES Employee(employee_id),
    CHECK (tenure_months >= 0),
    UNIQUE (employee_id, as_of_date)
);

-- 8. CURRENCY CONVERSION RATES
-- rate_to_inr means: 1 unit of this currency = rate_to_inr INR.

CREATE TABLE IF NOT EXISTS CurrencyRate (
    currency_rate_id TEXT PRIMARY KEY,
    currency_code TEXT NOT NULL,
    rate_to_inr REAL NOT NULL,
    effective_date TEXT NOT NULL,
    source TEXT NOT NULL,

    CHECK (rate_to_inr > 0),
    UNIQUE (currency_code, effective_date)
);

-- 9. ADJUSTMENT PROPOSALS

CREATE TABLE IF NOT EXISTS AdjustmentProposal (
    proposal_id TEXT PRIMARY KEY,
    employee_id TEXT NOT NULL,
    proposed_annual_salary REAL NOT NULL,
    currency_code TEXT NOT NULL,
    reason TEXT NOT NULL,
    status TEXT NOT NULL
        CHECK (status IN (
            'DRAFT', 'SUBMITTED', 'APPROVED',
            'REJECTED', 'WITHDRAWN'
        )),
    created_at TEXT NOT NULL,

    FOREIGN KEY (employee_id) REFERENCES Employee(employee_id),
    CHECK (proposed_annual_salary > 0)
);

-- A proposal can have multiple pieces of supporting evidence.
-- An evidence record can support multiple proposals.

CREATE TABLE IF NOT EXISTS ProposalEvidence (
    proposal_id TEXT NOT NULL,
    evidence_id TEXT NOT NULL,

    PRIMARY KEY (proposal_id, evidence_id),
    FOREIGN KEY (proposal_id)
        REFERENCES AdjustmentProposal(proposal_id),
    FOREIGN KEY (evidence_id)
        REFERENCES PerformanceEvidence(evidence_id)
);

-- 10. APPROVAL HISTORY

CREATE TABLE IF NOT EXISTS ApprovalEvent (
    approval_event_id TEXT PRIMARY KEY,
    proposal_id TEXT NOT NULL,
    decision TEXT NOT NULL
        CHECK (decision IN ('APPROVED', 'REJECTED', 'RETURNED')),
    approver_id TEXT NOT NULL,
    comments TEXT,
    event_timestamp TEXT NOT NULL,

    FOREIGN KEY (proposal_id)
        REFERENCES AdjustmentProposal(proposal_id)
);

-- 11. AUDIT HISTORY

CREATE TABLE IF NOT EXISTS AuditEvent (
    audit_event_id TEXT PRIMARY KEY,
    entity_type TEXT NOT NULL,
    entity_id TEXT NOT NULL,
    action TEXT NOT NULL,
    old_values TEXT,
    new_values TEXT,
    actor TEXT NOT NULL,
    event_timestamp TEXT NOT NULL
);

-- 12. INDEXES FOR COMMON LOOKUPS

CREATE INDEX IF NOT EXISTS idx_assignment_employee_dates
ON EmployeeAssignment(employee_id, effective_start, effective_end);

CREATE INDEX IF NOT EXISTS idx_salary_employee_dates
ON SalaryRecord(employee_id, effective_start, effective_end);

CREATE INDEX IF NOT EXISTS idx_band_lookup
ON CompensationBand(role_id, level_id, location_id, effective_start);

CREATE INDEX IF NOT EXISTS idx_evidence_employee
ON PerformanceEvidence(employee_id);

CREATE INDEX IF NOT EXISTS idx_proposal_employee
ON AdjustmentProposal(employee_id);

CREATE INDEX IF NOT EXISTS idx_approval_proposal
ON ApprovalEvent(proposal_id);