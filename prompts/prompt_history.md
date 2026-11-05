# AI Prompt History and Usage Disclosure

## 1. How I Used AI in This Project

During the development of my YottaFlex Compensation Analysis project, I used AI as a supporting tool to understand concepts, plan the implementation, debug errors, review code, and prepare documentation.

I did not rely on AI blindly. I used it to understand the logic behind different components, followed the implementation step by step, executed the code, checked the outputs, and made corrections whenever required.

My main goal was to build a working project while understanding how each component functions.

## 2. How I Used AI During Development

### Project Planning and Architecture

I used AI to understand how to structure a compensation analysis project and divide it into smaller modules.

I asked questions about:
- How to organize the project directory.
- How to separate database, data generation, analysis, validation, and workflow logic.
- How different components should communicate with each other.

I reviewed the suggested structure and implemented the project step by step.

### Database Design and Development

I used AI to understand relational database design and implement the SQLite database.

I discussed:
- Designing tables and relationships.
- Primary keys and foreign keys.
- Database constraints and indexes.
- Employee assignments, salary history, promotions, and compensation bands.
- Maintaining data integrity.

I inspected the database schema and verified that the database contained all 15 expected tables.

### Synthetic Data Generation

I used AI for guidance while developing Python scripts to generate synthetic employee, salary, promotion, and performance data.

I reviewed the generation logic, executed the scripts, and checked the generated records in the database.

### Compensation Analysis

I used AI to understand and implement compensation-related calculations, including:

- FTE-normalized salary.
- Currency conversion into INR.
- Compa-ratio.
- Compensation band position.
- Salary comparisons within employee groups.

I reviewed the formulas and executed the analysis to verify the generated results.

### Disparity Detection and Evidence Analysis

I used AI to help implement screening rules for identifying employees whose compensation required further review.

I also used AI to understand how performance evidence and employee context could be considered during the review process.

During development, I identified an issue in the latest performance evidence selection logic. I reviewed the implementation, corrected the logic, and executed it again to verify the result.

### Employee Comparison

I used AI to understand descriptive statistical comparisons between employees in similar groups.

I implemented and reviewed calculations involving group averages, medians, minimums, maximums, standard deviation, and percentage differences from group medians.

### Proposal and Approval Workflow

I used AI to understand how to structure a compensation adjustment workflow.

I implemented the proposal lifecycle:

`DRAFT -> SUBMITTED -> APPROVED / REJECTED`

I also reviewed how approval events and audit events are recorded.

One important behavior I verified is that approving a proposal changes its status but does not automatically update the employee's salary.

### Dashboard Development

I used AI for guidance while developing the Streamlit dashboard and its Plotly visualizations.

I implemented and tested:
- Employee compensation filters.
- KPI metrics.
- Compensation distribution charts.
- Salary and compa-ratio visualizations.
- Disparity and evidence review tables.
- Proposal status tracking.
- Proposal submission and approval controls.
- CSV downloads.

I launched the dashboard locally and inspected its functionality.

### Debugging, Testing, and Documentation

Whenever I encountered errors, I shared the relevant code or terminal output with AI to understand the cause and identify possible corrections.

I also used AI to help prepare the README, architecture documentation, assumptions, data dictionary, and testing documentation.

I executed the application and test suite to verify the implementation.

## 3. Representative Prompts I Used

The following are summaries of the types of prompts I used during development, rather than exact copies of every conversation.

**Project planning**
- Help me build this compensation analysis project step by step.
- Explain the project architecture and what each folder should contain.
- Guide me through the implementation without skipping steps.

**Database development**
- Help me design the SQLite database schema for this project.
- Explain the relationships between employee, salary, promotion, and compensation band tables.
- Help me debug database constraints and validation errors.

**Analysis**
- Help me implement FTE-normalized salary calculations.
- Explain compa-ratio and how to calculate it.
- Help me identify compensation disparities using comparable employee groups.
- Review my analysis logic and help me understand the results.

**Workflow**
- Help me implement a proposal approval workflow.
- Explain how to record approval events and audit history.
- Help me verify that proposal approval does not directly change employee salary.

**Dashboard and testing**
- Help me build a Streamlit dashboard using my existing project modules.
- Help me debug errors using my terminal output.
- Help me validate the database and test the complete workflow.

**Documentation**
- Help me document the project architecture, assumptions, and database tables.
- Review my documentation for consistency with the actual implementation.

## 4. How AI Helped Me Work Faster

AI helped me save development time by:

- Explaining unfamiliar concepts in simple terms.
- Helping me break a large project into smaller tasks.
- Identifying errors and suggesting debugging approaches.
- Helping me understand analytical formulas and database relationships.
- Reviewing implementation logic.
- Preparing documentation more efficiently.

Instead of spending time searching for every issue independently, I could discuss the problem, understand the suggested solution, and test it directly in my development environment.

## 5. What I Reviewed and Verified Myself

I made sure to execute and inspect the implementation instead of assuming that suggested code would work correctly.

My verification activities included:

1. Checking the project directory and source files.
2. Executing the database generation and rebuild scripts.
3. Inspecting the SQLite database and its 15 tables.
4. Running database integrity and business-rule validations.
5. Executing the complete analytical workflow using `python run.py`.
6. Inspecting the generated CSV reports.
7. Reviewing the compensation calculations and comparison results.
8. Launching and inspecting the Streamlit dashboard.
9. Running the automated test suite.
10. Reviewing the documentation against the actual implementation.

### Verification Results

During the recorded verification run:

- 15 database tables were present.
- 11 out of 11 database validation checks passed.
- 16 automated tests passed.
- Compensation analysis processed 5,000 employees.
- Four analytical CSV reports were generated.
- The Streamlit dashboard launched successfully.

## 6. My Understanding and Responsibility

I understand that AI-generated code and explanations can contain mistakes or assumptions that may not fit the project.

Whenever I used AI-generated suggestions, I reviewed the relevant logic, executed the code, checked the results, and corrected issues when necessary.

I am responsible for the final implementation and for understanding the project's database structure, analytical calculations, validation rules, and proposal workflow.

## 7. Final Disclosure

I used AI as a development assistant throughout this project for planning, coding guidance, debugging, code review, testing guidance, and documentation.

However, I also worked through the implementation step by step, executed the application locally, reviewed its outputs, and validated its functionality.

The project uses synthetic employee data and is intended to demonstrate compensation analysis, disparity screening, evidence-based review, and adjustment proposal management.

---

**Project:** YottaFlex Compensation Analysis  
**Development Environment:** Python, SQLite, Streamlit  
**AI Assistance:** Planning, implementation guidance, debugging, review, and documentation