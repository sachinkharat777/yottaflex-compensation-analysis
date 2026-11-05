# AI Prompt History and Usage Disclosure

## 1. How I Used AI in This Project

During the development of my YottaFlex Compensation Analysis project, I used AI as a supporting tool to understand concepts, plan implementation, debug errors, review code, and prepare documentation.

I did not rely on AI blindly. I used it to understand the logic behind different components, implement changes step by step, execute the code, inspect the outputs, and correct issues when required.

The prompts below are representative summaries of my interactions. They are not presented as verbatim copies of every prompt or conversation.

## 2. How I Used AI During Development

### Project Planning and Architecture

I used AI to understand how to structure the compensation analysis project into separate modules.

Topics included:
- Organizing the project directory.
- Separating database, data generation, analysis, validation, evaluation, exports, and workflow logic.
- Understanding how different components interact.
- Planning implementation and testing in manageable stages.

### Database Design and Development

I used AI to understand relational database design and SQLite implementation.

Topics included:
- Tables, relationships, primary keys, and foreign keys.
- Database constraints and indexes.
- Employee assignments, salary history, promotions, and compensation bands.
- Database integrity and validation.

I inspected the database and verified that it contained 15 tables.

### Synthetic Data Generation and Reproducibility

I used AI for guidance while developing Python scripts to generate synthetic employee, salary, promotion, and supporting records.

I also worked on:
- Configurable employee, promotion, and proposal counts.
- Seed-based random generation.
- Separating random seeds by generation stage.
- Rebuilding the database safely.
- Comparing generated database checksums to assess reproducibility.

### Compensation Analysis

I used AI to understand and implement compensation calculations, including:
- Full-Time Equivalent (FTE) salary normalization.
- Currency conversion into INR.
- Compa-ratio.
- Compensation band position.
- Salary comparisons within comparable employee groups.

I reviewed the formulas and inspected the generated analytical results.

### Disparity Detection and Evidence-Based Review

I used AI to understand and implement rule-based screening for compensation cases that may require further review.

I also used AI to understand how performance evidence, employee context, and comparable groups should be considered during review.

During development, I investigated issues in the selection of the latest performance evidence and corrected the implementation after reviewing the results.

### Employee Comparison

I used AI to understand descriptive statistical comparisons between employees in similar groups.

The analysis includes group averages, medians, minimums, maximums, standard deviation, and percentage differences from group medians.

### Anomaly Detection and Evaluation

I used AI to help structure a separate synthetic benchmark for evaluating anomaly detection.

The benchmark includes five anomaly categories and clean control cases. I also worked on separating anomaly detection from ground-truth evaluation so that the detector does not use the expected labels to make its predictions.

I reviewed the evaluation metrics and documented the limitation that results on a controlled synthetic benchmark do not establish real-world detection accuracy.

### Proposal and Approval Workflow

I used AI to understand how to structure a compensation adjustment proposal workflow.

The lifecycle is:

`DRAFT -> SUBMITTED -> APPROVED / REJECTED`

I reviewed the recording of approval events and audit events. I also verified the intended behavior that approving a proposal changes its status but does not automatically update the employee's salary.

### Dashboard Development

I used AI for guidance while developing the Streamlit dashboard and Plotly visualizations.

Dashboard functionality includes:
- Employee compensation filters.
- KPI metrics.
- Compensation distribution charts.
- Salary and compa-ratio visualizations.
- Disparity and evidence review tables.
- Proposal status tracking.
- Proposal submission and approval controls.
- CSV downloads.

I launched the dashboard locally and inspected its functionality.

### Validation, Exports, and Documentation

I used AI to help implement database validation reporting and project exports.

The export workflow produces:
- JSON exports for database tables.
- A SQL database dump.
- A structured validation summary in JSON.
- A readable validation summary in Markdown.
- A source manifest containing generation configuration, row counts, and SHA-256 checksums.

I also used AI to help prepare and review the README, architecture documentation, assumptions, data dictionary, proposal rules, evaluation documentation, and this disclosure.

## 3. Representative Prompts

The following are summaries of the types of prompts used during development, rather than exact copies of every conversation.

**Project planning**
- Help me build the compensation analysis project step by step.
- Explain the project architecture and the responsibility of each folder.
- Guide me through the implementation without skipping important steps.

**Database development**
- Help me design the SQLite database schema.
- Explain the relationships between employee, salary, promotion, and compensation band tables.
- Help me debug database constraints and validation errors.

**Data generation and reproducibility**
- Help me make the synthetic data generator configurable.
- Explain how random seeds affect reproducibility.
- Help me verify whether repeated database generation produces identical results.

**Compensation analysis**
- Help me implement FTE-normalized salary calculations.
- Explain compa-ratio and how to calculate it.
- Help me identify compensation differences within comparable employee groups.
- Review the analysis logic and explain the results.

**Anomaly evaluation**
- Help me create synthetic anomaly cases and ground-truth labels.
- Help me implement a detector and evaluate its predictions.
- Explain precision, recall, and F1-score.
- Help me document the limitations of a synthetic benchmark.

**Workflow**
- Help me implement a proposal approval workflow.
- Explain how to record approval events and audit history.
- Help me verify that proposal approval does not directly change employee salary.

**Dashboard and testing**
- Help me build a Streamlit dashboard using the project modules.
- Help me debug errors using terminal output.
- Help me validate the database and test the workflow.
- Help me create tests for data generation, validation, and exports.

**Documentation**
- Help me document the architecture, assumptions, and database tables.
- Review the documentation for consistency with the implementation.
- Help me document AI usage transparently.

## 4. How AI Helped Me Work Faster

AI helped me:
- Understand unfamiliar concepts and formulas.
- Break a large project into smaller implementation tasks.
- Investigate errors and identify debugging approaches.
- Understand database relationships and analytical logic.
- Review implementation decisions.
- Prepare tests and documentation more efficiently.

I used the suggestions as development assistance and checked the relevant implementation in my local environment.

## 5. What I Reviewed and Verified Myself

My verification activities included:

1. Inspecting the project structure and source files.
2. Executing the database generation and analysis workflows.
3. Inspecting the SQLite database and its tables.
4. Running database integrity and business-rule validations.
5. Reviewing compensation calculations and analytical outputs.
6. Inspecting generated CSV reports.
7. Reviewing the anomaly benchmark and evaluation metrics.
8. Launching and inspecting the Streamlit dashboard.
9. Running the automated test suite.
10. Generating and checking JSON, SQL, and validation exports.
11. Reviewing the README and supporting documentation.

### Recorded Verification Results

In the latest recorded verification run:

- 15 database tables were present.
- 38,340 rows were present across those tables.
- 11 out of 11 database validation checks passed.
- 48 automated tests passed.
- The synthetic dataset contained 5,000 employees.
- JSON exports were generated for all 15 database tables.
- A SQL database dump was generated.
- A validation summary and source manifest were generated.

These results describe the recorded local verification run. They should not be interpreted as proof of production readiness or real-world compensation fairness.

## 6. My Understanding and Responsibility

I understand that AI-generated code and explanations can contain mistakes or assumptions that do not fit the project.

I reviewed suggested changes, executed the relevant code, inspected the results, and corrected issues when necessary.

I am responsible for the final submitted implementation and for understanding its database structure, analytical calculations, validation rules, evaluation approach, and proposal workflow.

## 7. Final Disclosure

I used AI as a development assistant throughout this project for planning, implementation guidance, debugging, code review, testing guidance, and documentation.

I also worked through the implementation step by step, executed the application locally, reviewed its outputs, and ran the available validations and automated tests.

The project uses synthetic employee data. It demonstrates compensation analysis, disparity screening, evidence-based review, anomaly evaluation, and adjustment proposal management. It is not a production compensation decision system.

---

**Project:** YottaFlex Compensation Analysis  
**Development Environment:** Python, SQLite, Streamlit  
**AI Assistance:** Planning, implementation guidance, debugging, review, testing, and documentation