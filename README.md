# YottaFlex Compensation Analysis

A Python and SQLite-based compensation analytics and decision-support system that analyzes employee pay, compares salaries against compensation bands and comparable employee groups, identifies records requiring further review, and manages compensation adjustment proposals through an auditable approval workflow.

The project uses synthetic employee and compensation data and provides a Streamlit dashboard for exploring analysis results and managing proposals.

---

## Table of Contents

1. [Project Overview](#project-overview)
2. [Business Problem](#business-problem)
3. [Project Objectives](#project-objectives)
4. [Key Features](#key-features)
5. [Technology Stack](#technology-stack)
6. [System Architecture](#system-architecture)
7. [Database Design](#database-design)
8. [Data Generation](#data-generation)
9. [Compensation Analysis](#compensation-analysis)
10. [Disparity Detection](#disparity-detection)
11. [Evidence-Based Review](#evidence-based-review)
12. [Employee Comparison](#employee-comparison)
13. [Adjustment Proposal Workflow](#adjustment-proposal-workflow)
14. [Anomaly Detection Evaluation](#anomaly-detection-evaluation)
15. [Streamlit Dashboard](#streamlit-dashboard)
16. [Project Structure](#project-structure)
17. [Installation and Setup](#installation-and-setup)
18. [Running the Project](#running-the-project)
19. [Generated Reports](#generated-reports)
20. [Validation and Testing](#validation-and-testing)
21. [Design Decisions and Assumptions](#design-decisions-and-assumptions)
22. [Limitations and Future Improvements](#limitations-and-future-improvements)
23. [AI Usage and Transparency](#ai-usage-and-transparency)
24. [Security and Repository Hygiene](#security-and-repository-hygiene)
25. [Submission Notes](#submission-notes)

---

## Project Overview

Compensation analysis requires more than comparing employees' annual salaries. Pay can vary due to job responsibilities, seniority, location, employment percentage, compensation structures, and historical changes.

This project provides a structured approach to analyzing employee compensation using relational data, deterministic calculations, configurable screening rules, and supporting employee evidence.

The system:

- Generates a reproducible synthetic workforce and compensation dataset.
- Stores employee, assignment, salary, compensation band, performance, and workflow information in SQLite.
- Normalizes compensation to a full-time-equivalent basis.
- Converts compensation into a common INR comparison currency.
- Compares employee compensation with applicable compensation bands.
- Identifies potential compensation anomalies and records requiring review.
- Considers performance evidence and employee tenure during review analysis.
- Generates adjustment proposals for eligible review cases.
- Tracks proposal submission, approval, rejection, and audit events.
- Evaluates five additional anomaly detection rules using a controlled synthetic benchmark.
- Presents results through an interactive Streamlit dashboard.

**Important:** The system is a decision-support tool. Its flags identify cases for investigation; they do not establish discrimination, unfair treatment, or an incorrect salary.

---

## Business Problem

Organizations may maintain employee compensation information across different roles, levels, locations, currencies, and employment arrangements.

Analyzing this information manually can make it difficult to:

- Identify employees whose compensation falls outside established salary bands.
- Compare employees working in equivalent or comparable roles.
- Account for differences in full-time and part-time employment.
- Understand how compensation changes across historical assignments.
- Identify unusual differences in compensation.
- Consider supporting evidence before proposing an adjustment.
- Maintain a traceable record of compensation-related decisions.

The objective of this project is to build a reproducible analytical workflow that organizes this information, applies consistent comparison rules, highlights records requiring attention, and supports a controlled proposal-review process.

---

## Project Objectives

1. Build a relational compensation database with appropriate relationships and integrity constraints.
2. Generate reproducible synthetic workforce and compensation data.
3. Maintain historical employee assignments and salary records.
4. Normalize salary values using employee FTE.
5. Convert salary values into INR for consistent comparison.
6. Calculate compensation ratios and salary-band positions.
7. Identify potential compensation anomalies using defined rules.
8. Incorporate performance and tenure evidence into review analysis.
9. Generate compensation adjustment proposals.
10. Maintain approval and audit histories.
11. Build an interactive dashboard for reviewing results.
12. Evaluate anomaly detection rules using ground-truth labels and standard classification metrics.
13. Validate the database, analytical outputs, and important workflow behavior.

---

## Key Features

| Feature | Description |
|---|---|
| Synthetic data generation | Reproducible generation of employees, roles, salary history, and supporting records |
| Relational database | SQLite database with 15 related tables |
| Historical records | Employee assignments and salary records across multiple years |
| FTE normalization | Converts compensation to a full-time-equivalent basis |
| Currency normalization | Converts salary and band values into INR |
| Compensation analysis | Calculates band position, compa-ratio, and band status |
| Disparity screening | Flags potential compensation anomalies using defined thresholds |
| Evidence-based review | Considers comparable-group salary differences, performance, and tenure |
| Proposal management | Creates and tracks compensation adjustment proposals |
| Approval workflow | Supports submission, approval, and rejection |
| Audit history | Records proposal-related workflow events |
| Anomaly benchmark | Generates controlled anomaly scenarios with separate ground truth |
| Evaluation metrics | Calculates precision, recall, and F1-score |
| Interactive dashboard | Displays metrics, visualizations, filters, and employee-level details |
| CSV and JSON outputs | Exports analytical results and evaluation metrics |
| Automated tests | Tests important calculations, integrity conditions, and workflow behavior |

---

## Technology Stack

| Technology | Purpose |
|---|---|
| Python | Core programming language and application logic |
| SQLite | Relational database and persistent storage |
| Pandas | Data handling and report processing |
| NumPy | Numerical operations |
| Streamlit | Interactive dashboard |
| Plotly | Interactive data visualizations |
| CSV | Analytical report and benchmark data storage |
| JSON | Evaluation metrics storage |
| Pytest | Automated testing |
| Git and GitHub | Version control and project hosting |

The project uses local technologies and does not require a paid cloud service or hosted database.

---

## System Architecture

The project follows a modular architecture that separates data generation, database storage, analysis, validation, workflow management, evaluation, and dashboard presentation.

### High-Level Workflow

```text
Synthetic Data Generation
          |
          v
     SQLite Database
          |
          v
   Database Validation
          |
          v
 Compensation Analysis
          |
          v
    Disparity Detection
          |
          v
   Evidence-Based Review
          |
          v
    Employee Comparison
          |
          v
       CSV Reports
          |
          v
   Streamlit Dashboard
          |
          v
 Adjustment Proposal Workflow
          |
          v
   Approval / Rejection
          |
          v
 Approval and Audit Records
```

### Anomaly Evaluation Workflow

```text
Synthetic Anomaly Generation
          |
          v
   Generated Test Cases
          |
          +--------------------+
          |                    |
          v                    v
   Detection Rules        Ground Truth
          |                    |
          v                    |
    Predictions               |
          |                    |
          +---------+----------+
                    |
                    v
             Evaluation
                    |
                    v
       Precision / Recall / F1
                    |
                    v
         JSON Metrics Report
```

The evaluation pipeline is separate from the main compensation database. It does not modify the existing compensation database or use ground-truth labels while generating detector predictions.

### Main Components

**1. Data Generation**

Generates synthetic employees, organizational reference data, compensation bands, assignments, salary history, performance evidence, tenure snapshots, and adjustment proposals.

**2. Database Layer**

Stores structured information in SQLite and maintains relationships through primary keys, foreign keys, and validation constraints.

**3. Analysis Layer**

Performs compensation calculations, disparity screening, evidence-based review, and employee-level comparisons.

**4. Validation Layer**

Checks database integrity and business rules before analytical results are accepted.

**5. Workflow Layer**

Manages adjustment proposal creation, submission, approval, rejection, and audit records.

**6. Evaluation Layer**

Runs rule-based anomaly detection against generated benchmark cases and compares predictions with independently generated ground-truth labels.

**7. Presentation Layer**

Uses Streamlit and Plotly to display analytical results and provide an interface for proposal management.

---

## Database Design

The project uses SQLite as its relational database.

The database contains 15 tables:

| Table | Purpose |
|---|---|
| `Role` | Stores job roles and comparable role groups |
| `Level` | Stores organizational levels |
| `Location` | Stores employee work locations |
| `Employee` | Stores employee master information |
| `CompensationBand` | Stores salary ranges for role, level, and location combinations |
| `EmployeeAssignment` | Stores employee role, level, location, and FTE assignments |
| `SalaryRecord` | Stores historical employee salary records |
| `Promotion` | Stores employee promotion history |
| `PerformanceEvidence` | Stores employee performance-related evidence |
| `TenureSnapshot` | Stores employee tenure information |
| `CurrencyRate` | Stores currency conversion rates |
| `AdjustmentProposal` | Stores proposed compensation adjustments and their status |
| `ProposalEvidence` | Stores evidence associated with adjustment proposals |
| `ApprovalEvent` | Stores proposal approval and rejection decisions |
| `AuditEvent` | Stores workflow-related audit information |

### Database Design Considerations

- Primary keys uniquely identify records.
- Foreign keys maintain relationships between related tables.
- Foreign-key enforcement is enabled during relevant database operations.
- Date fields represent effective periods for assignments, salary records, and compensation bands.
- Validation logic checks for invalid or overlapping effective periods.
- Proposal decisions are stored separately from employee salary records.

This structure supports historical analysis and traceability rather than relying on a single current-salary table.

---

## Data Generation

The project uses deterministic synthetic data rather than real employee information.

The generated main dataset includes:

| Data Category | Generated Volume |
|---|---:|
| Roles | 50 |
| Levels | 4 |
| Locations | 3 |
| Compensation bands | 1,800 |
| Employees | 5,000 |
| Promotions | 500 |
| Salary records | 14,504 |
| Tenure snapshots | 5,000 |
| Performance evidence records | 5,000 |
| Adjustment proposals | 250 |

The dataset includes compensation and salary history covering 2024, 2025, and 2026.

A fixed random seed is used by the generators to support repeatable synthetic data generation.

**Note:** These figures describe the generated project dataset, not a real organization's workforce.

---

## Compensation Analysis

The compensation analysis module calculates employee compensation metrics using employee salary, FTE, applicable compensation bands, and currency conversion rates.

### 1. FTE Normalization

Employees may work full-time or part-time. Comparing their actual annual salary without considering FTE can produce misleading results.

The project normalizes salary to a full-time-equivalent basis:

\[
\text{Normalized Salary} =
\frac{\text{Actual Annual Salary}}{\text{FTE}}
\]

For example, an employee earning ₹600,000 at 0.5 FTE has a normalized salary of ₹1,200,000.

### 2. Currency Conversion

Compensation values are converted into INR using the applicable stored currency conversion rate.

\[
\text{Salary in INR} =
\text{Salary in Source Currency}
\times
\text{Currency Rate}
\]

This allows salary and compensation-band comparisons to use a common currency.

### 3. Compa-Ratio

Compa-ratio measures normalized employee compensation relative to the midpoint of the applicable compensation band.

\[
\text{Compa-Ratio} =
\frac{\text{Normalized Salary}}
{\text{Compensation Band Midpoint}}
\]

Interpretation:

- Below 1.0: Salary is below the band midpoint.
- Equal to 1.0: Salary is at the band midpoint.
- Above 1.0: Salary is above the band midpoint.

### 4. Compensation Band Status

The system compares normalized salary with the applicable band minimum and maximum.

Possible classifications:

- `BELOW_BAND`
- `WITHIN_BAND`
- `ABOVE_BAND`

The analysis also calculates the employee's position within the compensation band.

The analysis uses **31 December 2026** as its configured analysis date.

---

## Disparity Detection

The disparity detection module identifies employees who meet one or more compensation screening conditions.

Employees are grouped using:

- Comparable role group
- Organizational level
- Work location

The module evaluates the following conditions:

| Rule | Screening Condition |
|---|---|
| Below compensation band | Salary is below the applicable band minimum |
| Above compensation band | Salary is above the applicable band maximum |
| Low compa-ratio | Compa-ratio is below 0.80 |
| High compa-ratio | Compa-ratio is above 1.20 |
| Comparable-group salary gap | Salary is at least 10% below the comparable-group average |

An employee can receive more than one flag.

The output includes the employee identifier, comparison group, normalized salary, group average, compa-ratio, salary gap percentage, and reasons for flagging.

**Interpretation:** These rules are screening mechanisms. A flagged employee requires contextual review; a flag alone is not evidence of compensation discrimination or unfairness.

---

## Evidence-Based Review

The evidence-based review module extends compensation screening by considering additional employee context.

It uses:

- Comparable role groups
- Organizational level
- Work location
- Salary differences within comparable groups
- Performance evidence
- Employee tenure

The implementation uses a minimum comparable-group size of three and a 10% salary-gap threshold for its relevant group-based review logic.

The latest available performance evidence is used when selecting an employee's evidence record.

The purpose is to provide additional context for human review rather than automatically determine an employee's eligibility for a salary increase.

Output:

`outputs/evidence_based_review.csv`

---

## Employee Comparison

The employee comparison module provides descriptive statistics for comparable employee groups.

It calculates:

- Group average salary
- Group median salary
- Minimum salary
- Maximum salary
- Salary range
- Standard deviation
- Employee-level difference from the group median

The analysis provides a descriptive view of compensation variation.

A difference from the group average or median should not be interpreted as proof of unfair treatment. Additional business context may be needed, including responsibilities, experience, performance, and other relevant factors.

Output:

`outputs/employee_comparison.csv`

---

## Adjustment Proposal Workflow

The project includes a proposal workflow to demonstrate how compensation analysis can support a controlled review process.

### Proposal Generation

The proposal module evaluates employee compensation records and generates proposals according to the implemented rules.

Examples include:

- Below-band cases may receive a proposed salary based on the applicable band minimum.
- Above-band cases can be flagged for human review.
- Employees within the band may have no salary adjustment proposed by this rule.

A proposal is not an automatic salary change.

### Proposal Lifecycle

```text
DRAFT
  |
  v
SUBMITTED
  |
  +------------------+
  |                  |
  v                  v
APPROVED           REJECTED
```

### Workflow Actions

**Draft**

A proposal is created and stored in the database.

**Submitted**

A submitter records the proposal for approval.

**Approved or Rejected**

An approver records a decision and provides comments.

### Auditability

The workflow stores approval events and audit events to maintain a history of proposal-related actions.

**Important:** Approval changes the proposal's workflow status. It does not automatically update the employee's salary record. Actual salary implementation would require a separate controlled process.

---

## Anomaly Detection Evaluation

A separate synthetic benchmark evaluates five compensation-related anomaly detection rules.

The benchmark is designed to test whether the implemented rules correctly identify deliberately constructed anomaly scenarios.

### Anomaly Types

| Issue Type | Description |
|---|---|
| `EXPIRED_COMPENSATION_BAND` | Salary analysis uses a compensation band that has expired |
| `FTE_NORMALIZATION_ERROR` | Salary is reported without correct FTE normalization |
| `MISSING_FX_RATE` | A required foreign exchange conversion rate is unavailable |
| `UNAPPROVED_ADJUSTMENT` | An adjustment is marked approved without a corresponding approval event |
| `INCOMPARABLE_ROLE_GROUPING` | Multiple roles are grouped together without a comparison rationale |

### Benchmark Dataset

| Dataset Detail | Count |
|---|---:|
| Total benchmark records | 270 |
| Injected anomaly cases | 250 |
| Clean control cases | 20 |
| Anomaly types | 5 |
| Positive cases per anomaly type | 50 |

The benchmark generator creates the test cases and a separate ground-truth CSV.

The detection module reads the generated cases and produces predictions. It does not read the ground-truth labels.

The evaluation module compares the predictions against ground truth.

### Evaluation Metrics

The following classification metrics are calculated:

**Precision**

\[
\text{Precision} = \frac{TP}{TP+FP}
\]

Measures the proportion of predicted anomalies that are actual labelled anomalies.

**Recall**

\[
\text{Recall} = \frac{TP}{TP+FN}
\]

Measures the proportion of actual labelled anomalies detected by the rules.

**F1-score**

\[
F1 = 2 \times \frac{\text{Precision}\times\text{Recall}}
{\text{Precision}+\text{Recall}}
\]

Measures the harmonic mean of precision and recall.

### Evaluation Results

The controlled benchmark produced the following results:

| Metric | Result |
|---|---:|
| True Positives | 250 |
| False Positives | 0 |
| False Negatives | 0 |
| Precision | 100% |
| Recall | 100% |
| F1-score | 100% |

Each of the five anomaly types achieved:

| Metric | Result per anomaly type |
|---|---:|
| True Positives | 50 |
| False Positives | 0 |
| False Negatives | 0 |
| Precision | 100% |
| Recall | 100% |
| F1-score | 100% |

### Evaluation Files

| File | Responsibility |
|---|---|
| `src/generator/anomaly_injector.py` | Generates controlled anomaly scenarios |
| `src/evaluation/detector.py` | Applies detection rules to generated cases |
| `src/evaluation/evaluate.py` | Calculates evaluation metrics |
| `data/generated/anomaly_cases.csv` | Contains generated benchmark records |
| `data/ground_truth/ground_truth.csv` | Contains independent ground-truth labels |
| `outputs/evaluation_predictions.csv` | Contains detector predictions |
| `outputs/evaluation_metrics.json` | Stores evaluation results |
| `docs/evaluation.md` | Documents the evaluation methodology and limitations |

### Important Evaluation Limitation

The 100% results apply only to the controlled synthetic benchmark. The cases were deliberately constructed to test specific detection rules.

They do not establish 100% accuracy on real-world compensation data or demonstrate generalization to unseen organizational data.

Independent validation using manually reviewed real-world or independently sourced benchmark records would be required to assess real-world detection performance.

---

## Streamlit Dashboard

The project includes a Streamlit dashboard for exploring compensation analysis results.

### Dashboard Capabilities

- Employee compensation overview
- Total employees analyzed
- Employees within compensation bands
- Disparity review counts
- Adjustment proposal counts
- Location filters
- Role filters
- Level filters
- Compensation-band status filters
- Compensation distribution visualization
- Salary distribution by level
- Compa-ratio analysis
- Disparity review table
- Evidence-based review table
- Adjustment proposal status overview
- Employee-level compensation details
- CSV report download
- Proposal submission
- Proposal approval and rejection

The dashboard reads analytical CSV outputs and the SQLite database.

Proposal actions modify the database, so they should be used deliberately when testing or demonstrating the workflow.

---

## Project Structure

```text
yottaflex-compensation-analysis/
│
├── app/
│   └── dashboard.py
│
├── data/
│   ├── generated/
│   │   └── anomaly_cases.csv
│   └── ground_truth/
│       └── ground_truth.csv
│
├── database/
│   ├── schema.sql
│   └── compensation.db
│
├── docs/
│   ├── architecture.md
│   ├── assumptions.md
│   ├── data_dictionary.md
│   └── evaluation.md
│
├── outputs/
│   ├── compensation_analysis_2026-12-31.csv
│   ├── disparity_flags.csv
│   ├── evidence_based_review.csv
│   ├── employee_comparison.csv
│   ├── evaluation_predictions.csv
│   └── evaluation_metrics.json
│
├── prompts/
│   └── prompt_history.md
│
├── src/
│   ├── analysis/
│   ├── evaluation/
│   ├── generator/
│   ├── validation/
│   └── workflow/
│
├── tests/
│   ├── test_analysis.py
│   ├── test_database_integrity.py
│   ├── test_evaluation.py
│   └── test_workflow.py
│
├── .gitignore
├── README.md
├── rebuild_database.py
├── requirements.txt
└── run.py
```

### Important Files

| File | Responsibility |
|---|---|
| `run.py` | Runs the main analytical workflow |
| `rebuild_database.py` | Rebuilds the database and regenerates synthetic data |
| `database/schema.sql` | Defines database tables and constraints |
| `app/dashboard.py` | Runs the Streamlit dashboard |
| `src/evaluation/detector.py` | Detects the five benchmark anomaly types |
| `src/evaluation/evaluate.py` | Calculates precision, recall, and F1-score |
| `src/generator/anomaly_injector.py` | Generates controlled synthetic anomaly scenarios |
| `requirements.txt` | Lists Python dependencies |
| `docs/architecture.md` | Describes system architecture |
| `docs/assumptions.md` | Documents project assumptions |
| `docs/data_dictionary.md` | Describes database fields and data |
| `docs/evaluation.md` | Documents evaluation methodology and limitations |
| `prompts/prompt_history.md` | Records AI-assisted development prompts |

---

## Installation and Setup

### Prerequisites

- Python 3.11 or later
- Git
- Windows Command Prompt or another compatible terminal

### 1. Clone the Repository

```cmd
git clone https://github.com/sachinkharat777/yottaflex-compensation-analysis.git
cd yottaflex-compensation-analysis
```

### 2. Create a Virtual Environment

```cmd
py -3.11 -m venv venv
```

### 3. Activate the Virtual Environment

**Windows Command Prompt:**

```cmd
venv\Scripts\activate
```

**macOS / Linux:**

```bash
source venv/bin/activate
```

### 4. Install Dependencies

```cmd
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

### Dependencies

The project uses:

- pandas
- numpy
- streamlit
- plotly
- pytest

SQLite and other standard-library modules are included with Python.

---

## Running the Project

Run commands from the project root directory with the virtual environment activated.

### Step 1: Run the Analysis Workflow

```cmd
python run.py
```

The workflow performs database validations, runs the analytical modules, and generates the report files.

The existing database is used. This command is intended to analyze the current database rather than regenerate the dataset.

### Step 2: Launch the Dashboard

```cmd
streamlit run app/dashboard.py
```

Open the local URL displayed in the terminal.

On Windows Command Prompt, this command also works:

```cmd
streamlit run app\dashboard.py
```

### Step 3: Generate the Anomaly Benchmark

```cmd
python -m src.generator.anomaly_injector
```

This generates:

- `data/generated/anomaly_cases.csv`
- `data/ground_truth/ground_truth.csv`

The benchmark is separate from the main compensation database.

### Step 4: Run Anomaly Detection

```cmd
python -m src.evaluation.detector
```

This generates:

`outputs/evaluation_predictions.csv`

### Step 5: Evaluate Detection Performance

```cmd
python -m src.evaluation.evaluate
```

This compares predictions with ground truth and generates:

`outputs/evaluation_metrics.json`

### Step 6: Run Automated Tests

```cmd
python -m pytest -v
```

The tests verify important calculations, database integrity, business rules, evaluation metrics, and workflow behavior.

### Important: Rebuilding the Main Database

To regenerate the synthetic database, use:

```cmd
python rebuild_database.py
```

**Warning:** This operation rebuilds the database and may replace existing proposal and approval state. Run it only when a fresh dataset is required.

It should not be used as a routine substitute for `python run.py`.

---

## Generated Reports

The main analysis workflow generates four CSV reports in the `outputs/` directory.

| Report | Description |
|---|---|
| `compensation_analysis_2026-12-31.csv` | Employee-level normalized compensation, band information, and compa-ratio |
| `disparity_flags.csv` | Employees identified by configured disparity screening rules |
| `evidence_based_review.csv` | Review candidates with additional employee evidence and comparable-group context |
| `employee_comparison.csv` | Employee-level comparison metrics and descriptive group statistics |

The anomaly evaluation workflow generates:

| Report | Description |
|---|---|
| `evaluation_predictions.csv` | Anomaly predictions from the detection rules |
| `evaluation_metrics.json` | Overall and per-issue evaluation metrics |

These reports can be opened in spreadsheet applications or processed using Python.

---

## Validation and Testing

Data quality and workflow correctness are important because compensation analysis depends on accurate relationships and calculations.

### Database Validations

The validation module checks:

1. Foreign-key integrity
2. Duplicate employee identifiers
3. Positive salary values
4. Valid FTE ranges
5. Salary effective-date ranges
6. Assignment effective-date ranges
7. Compensation-band arithmetic
8. Valid adjustment proposal statuses
9. Approval decision validity
10. Overlapping employee assignments
11. Overlapping compensation bands

### Automated Tests

The project includes Pytest tests covering:

- Compensation calculations
- Database integrity
- Assignment and compensation-band constraints
- Currency conversion
- Analytical logic
- Evaluation metric calculations
- False-positive and false-negative scenarios
- Proposal status transitions
- Approval and audit records

### Verified Results

During development, the following results were obtained:

| Verification | Result |
|---|---:|
| Automated tests | 20 passed |
| Database validation checks | 11 of 11 passed |
| Employees processed by compensation analysis | 5,000 |
| Disparity screening candidates | 1,292 |
| Evidence-based review candidates | 1,250 |
| Employee comparison records | 5,000 |
| Comparable employee groups | 120 |

### Anomaly Benchmark Results

| Verification | Result |
|---|---:|
| Total benchmark records | 270 |
| Injected anomaly cases | 250 |
| Clean control cases | 20 |
| Anomaly types evaluated | 5 |
| True positives | 250 |
| False positives | 0 |
| False negatives | 0 |
| Precision | 100% |
| Recall | 100% |
| F1-score | 100% |

These results describe the tested project state and controlled synthetic benchmark. They may change if the data or rules are modified.

The number of flagged employees represents review candidates, not confirmed compensation problems.

---

## Design Decisions and Assumptions

### 1. Synthetic Data

Synthetic data is used to demonstrate the system without exposing real employee compensation information.

### 2. Reproducible Generation

Fixed random seeds are used in the data generation process to support repeatable results.

### 3. Relational Database

SQLite was selected because the project can run locally without requiring a separate database server.

### 4. Full-Time-Equivalent Comparison

Salary normalization is used to make compensation comparisons more meaningful across different employment percentages.

### 5. Common Currency

INR is used as the common comparison currency for the implemented analysis.

### 6. Comparable Groups

Employees are compared using role-group, level, and location dimensions. These dimensions provide a structured baseline but do not capture every factor that may explain compensation differences.

### 7. Rule-Based Screening

The project uses explicit thresholds for compensation-band status, compa-ratio, and group salary gaps.

This approach is transparent and easier to inspect than an unexplained automated score.

### 8. Human Review

The system identifies records for review and supports proposal decisions. It does not independently make final compensation decisions.

### 9. Separate Evaluation Benchmark

The anomaly evaluation dataset is separate from the main compensation database. This allows controlled testing without modifying the primary analytical dataset.

Further assumptions and implementation details are documented in:

- `docs/assumptions.md`
- `docs/architecture.md`
- `docs/data_dictionary.md`
- `docs/evaluation.md`

---

## Limitations and Future Improvements

### Current Limitations

- The dataset is synthetic and does not represent a real workforce.
- Screening rules use predefined thresholds that may require calibration for a real organization.
- Comparable-group analysis uses a limited set of employee attributes.
- Descriptive salary differences do not establish causation or unfair treatment.
- Performance and tenure are supporting context, not a complete measure of employee contribution.
- Currency comparisons depend on the conversion rates stored in the database.
- Proposal approval does not automatically update employee salary records.
- The anomaly evaluation uses controlled synthetic cases and does not establish real-world detection accuracy.
- The application is designed for local execution and has not been presented as a production HR system.
- The analysis does not establish legal compliance or replace a formal compensation audit.

### Potential Future Improvements

- Add more detailed compensation factors and configurable comparison groups.
- Introduce statistical significance testing and confidence intervals.
- Add configurable screening thresholds through the dashboard.
- Add more detailed historical compensation trend analysis.
- Improve proposal ID generation and concurrent workflow handling.
- Add role-based access control for submitters and approvers.
- Add stronger audit-event serialization and reporting.
- Add explicit data import and validation for real-world datasets.
- Add reproducible report metadata and run timestamps.
- Expand integration and end-to-end tests.
- Evaluate detection rules on independently reviewed datasets.
- Introduce a separate controlled salary-update process after approval.

---

## AI Usage and Transparency

AI tools were used as development assistance during this project.

AI assistance included support with:

- Understanding the project requirements.
- Planning the project structure and implementation sequence.
- Debugging Python and SQLite issues.
- Reviewing analytical logic and edge cases.
- Improving database validation and workflow handling.
- Preparing documentation and execution instructions.
- Developing and testing the anomaly evaluation workflow.

AI-generated suggestions were not treated as automatically correct. Code and analytical behavior were reviewed, modified where necessary, and tested through direct execution, database checks, generated report inspection, and automated tests.

The prompt history is maintained separately in:

`prompts/prompt_history.md`

The prompt history should accurately represent the prompts submitted to AI tools during development. It should not present reconstructed summaries as verbatim prompts.

The candidate remains responsible for understanding the implementation, its design choices, and its limitations.

---

## Security and Repository Hygiene

Before making the repository public:

- Do not commit passwords, API keys, credentials, or private configuration.
- Do not include real employee or confidential compensation information.
- Do not include the local virtual environment.
- Review generated files and database contents before publishing.
- Ensure that the repository contains only files you are authorized to share.
- Keep the prompt history and supporting documentation available for reviewers.

The project uses synthetic data for demonstration.

---

## Submission Notes

This repository is organized to support independent review and local execution.

A reviewer should be able to:

1. Clone the repository.
2. Install the dependencies.
3. Run the analysis workflow.
4. Inspect the generated CSV reports.
5. Launch the Streamlit dashboard.
6. Generate the anomaly benchmark.
7. Run the anomaly detection and evaluation workflow.
8. Run the automated tests.
9. Review the database schema and supporting documentation.
10. Understand the assumptions, limitations, and AI-assisted development process.

The project is intended to demonstrate structured problem-solving, data engineering, analytical reasoning, validation, anomaly detection, and transparent development practices.

---

## Author

**Sachin Kharat**

Project: YottaFlex Compensation Analysis

GitHub: https://github.com/sachinkharat777
