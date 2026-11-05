# System Architecture — YottaFlex Compensation Analysis

## 1. Overview

The YottaFlex Compensation Analysis project is a modular, Python-based analytical application designed to examine employee compensation, identify potential compensation anomalies, and support a controlled adjustment proposal workflow.

The system uses SQLite for persistent data storage, Python for data generation and analysis, Pandas and NumPy for data processing, and Streamlit with Plotly for interactive visualization.

The application is designed for local execution using synthetic employee and compensation data.

## 2. Architectural Design

The application separates responsibilities into six main components:

1. Data Generation
2. Database and Storage
3. Data Validation
4. Compensation Analysis
5. Proposal and Approval Workflow
6. Dashboard and Reporting

This separation makes the system easier to maintain, test, and extend.

## 3. High-Level Architecture

```text
             DATA GENERATION
                    |
                    v
              SQLITE DATABASE
                    |
                    v
             DATA VALIDATION
                    |
                    v
           COMPENSATION ANALYSIS
                    |
          +---------+----------+
          |         |          |
          v         v          v
       DISPARITY  EVIDENCE   EMPLOYEE
       DETECTION  ANALYSIS   COMPARISON
          |         |          |
          +---------+----------+
                    |
                    v
                CSV OUTPUTS
                    |
                    v
             STREAMLIT DASHBOARD
                    |
                    v
          ADJUSTMENT PROPOSALS
                    |
                    v
           SUBMISSION / DECISION
                    |
             +------+------+
             |             |
             v             v
          APPROVED       REJECTED
             |             |
             +------+------+
                    |
                    v
           AUDIT AND APPROVAL
                 RECORDS
```

## 4. Component Details

### 4.1 Data Generation

Location: `src/generator/`

Responsible for generating synthetic organizational and compensation data.

Generated information includes:

- Employee records
- Role and level information
- Work locations
- Compensation bands
- Employee assignments
- Salary history
- Promotion history
- Performance evidence
- Tenure snapshots
- Currency conversion rates
- Adjustment proposals

A fixed random seed is used where applicable to support reproducibility.

The generated dataset is intended for development and demonstration, not real HR decisions.

### 4.2 Database Layer

Location: `database/`

The project uses SQLite for structured data storage.

The database schema is defined in:

`database/schema.sql`

The database contains 15 related tables covering organizational information, employee compensation, historical records, evidence, proposals, approvals, and audit events.

Primary keys and foreign keys maintain relationships between entities.

The application enables foreign-key enforcement during relevant database operations.

### 4.3 Validation Layer

Location: `src/validation/`

The validation module checks database integrity and important business rules.

Validations include:

- Foreign-key integrity
- Duplicate employee identifiers
- Positive salary values
- Valid FTE values
- Salary date ranges
- Assignment date ranges
- Compensation-band arithmetic
- Proposal status validity
- Approval decision validity
- Overlapping employee assignments
- Overlapping compensation bands

The validation process helps identify inconsistent data before analytical results are generated.

### 4.4 Analysis Layer

Location: `src/analysis/`

The analysis layer contains separate modules for different analytical responsibilities.

**Compensation Analysis**

Calculates normalized compensation, currency-converted salary, compa-ratio, compensation-band position, and band status.

**Disparity Detection**

Identifies records meeting predefined compensation screening conditions.

**Evidence Analysis**

Uses comparable-group information, performance evidence, and tenure context to identify candidates for further review.

**Employee Comparison**

Calculates descriptive statistics for comparable employee groups, including average, median, minimum, maximum, range, and standard deviation.

### 4.5 Workflow Layer

Location: `src/workflow/`

The workflow layer manages compensation adjustment proposals and approval decisions.

It separates proposal creation from approval.

The implemented lifecycle is:

```text
DRAFT -> SUBMITTED -> APPROVED
                   -> REJECTED
```

Workflow operations store proposal status changes and associated approval and audit events.

An approval changes the proposal status. It does not automatically update an employee's salary.

### 4.6 Dashboard Layer

Location: `app/dashboard.py`

The dashboard uses Streamlit and Plotly.

It provides:

- Compensation overview
- Employee and compensation filters
- Compensation distribution charts
- Compa-ratio visualization
- Disparity flags
- Evidence-based review results
- Adjustment proposal status
- Employee compensation details
- CSV download
- Proposal submission and decision controls

The dashboard reads generated analysis reports and accesses the SQLite database for proposal-related operations.

## 5. Data Flow

The application follows this execution sequence:

1. Synthetic data is generated and stored in SQLite.
2. The database validation module checks data integrity.
3. Compensation analysis calculates employee-level compensation metrics.
4. Disparity detection applies screening rules.
5. Evidence analysis evaluates additional employee context.
6. Employee comparison calculates comparable-group statistics.
7. Analytical results are exported as CSV files.
8. The Streamlit dashboard reads the reports and database.
9. Authorized workflow actions can submit or decide proposals.
10. Approval and audit events are stored in SQLite.

The primary analytical entry point is:

`run.py`

The database regeneration entry point is:

`rebuild_database.py`

These scripts have different responsibilities. Running the analysis does not intentionally regenerate the entire synthetic dataset.

## 6. Data Storage and Outputs

### Database

`database/compensation.db`

Stores employee, organizational, historical compensation, evidence, proposal, approval, and audit information.

### Generated Reports

The `outputs/` directory stores:

- `compensation_analysis_2026-12-31.csv`
- `disparity_flags.csv`
- `evidence_based_review.csv`
- `employee_comparison.csv`

These reports provide an exportable view of the analytical results.

## 7. Execution Architecture

The project runs locally.

Required dependencies are installed using:

```cmd
python -m pip install -r requirements.txt
```

The analytical workflow is started using:

```cmd
python run.py
```

The dashboard is started using:

```cmd
streamlit run app\dashboard.py
```

Automated tests are executed using:

```cmd
pytest -v
```

## 8. Design Principles

### Modularity

Each component has a defined responsibility. Data generation, validation, analysis, and workflow operations are separated.

### Reproducibility

Synthetic data generation uses deterministic configuration to support repeatable development and testing.

### Data Integrity

Relational constraints and validation checks help maintain consistent records.

### Traceability

Proposal decisions and workflow actions are recorded separately from employee salary records.

### Transparency

Compensation screening rules and calculations are explicit and inspectable.

### Human Oversight

The system provides analytical findings and proposal-management capabilities. It does not independently make final compensation decisions.

## 9. Current Limitations

- The system uses synthetic data.
- Screening rules use predefined thresholds.
- Comparable-group analysis uses a limited set of attributes.
- The dashboard is designed for local execution.
- Proposal approval does not automatically implement salary changes.
- Production-grade authentication, authorization, and concurrent workflow handling are outside the current implementation.

## 10. Future Architecture Improvements

Potential improvements include:

- Configurable screening rules
- More advanced statistical analysis
- Role-based access control
- Production database integration
- Improved concurrent proposal handling
- Automated report versioning
- More comprehensive integration testing
- Controlled salary-update integration

---

**Project:** YottaFlex Compensation Analysis  
**Architecture:** Modular Python application with SQLite and Streamlit  
**Data:** Synthetic and reproducible