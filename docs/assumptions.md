# Assumptions and Business Rules

## 1. Purpose

This document describes the assumptions, business rules, and design decisions used in the YottaFlex Compensation Analysis project.

The project uses synthetic employee and compensation data to demonstrate compensation analysis, disparity screening, evidence-based review, and adjustment proposal management.

These assumptions are intended for demonstration and analytical purposes. They should not be treated as actual organizational compensation policies.

## 2. Dataset Assumptions

### 2.1 Synthetic Employee Data

- All employee records are synthetically generated.
- The dataset contains 5,000 employee records.
- Employee identifiers are generated for the project.
- Hiring dates fall between 2021 and 2026.
- The dataset contains no real employee personal or compensation information.

### 2.2 Organizational Structure

The synthetic organization uses:

- 50 job roles
- 4 job levels
- 3 work locations
- 600 possible role-level-location combinations

Compensation bands are maintained across three years, resulting in 1,800 compensation-band records.

### 2.3 Employment Type and FTE

Employees may have different Full-Time Equivalent (FTE) values.

Examples include:

- 1.0 FTE: Full-time
- 0.8 FTE: 80% working arrangement
- 0.5 FTE: 50% working arrangement

FTE is used to normalize compensation for comparison.

## 3. Compensation Calculation Assumptions

### 3.1 FTE Normalization

Employees working different FTE arrangements should not be compared using raw salary alone.

Normalized salary is calculated as:

Normalized Salary = Actual Salary / FTE

For example:

If an employee earns ₹600,000 at 0.5 FTE:

Normalized Salary = ₹600,000 / 0.5

Normalized Salary = ₹1,200,000

This provides a full-time-equivalent basis for comparison.

### 3.2 Currency Conversion

- Compensation analysis uses INR as the reporting currency.
- Currency conversion rates are stored in the database.
- Salary values are converted using the applicable stored exchange rate.
- The analysis depends on the currency-rate data available in the synthetic dataset.

### 3.3 Compensation Analysis Date

The compensation analysis uses:

**31 December 2026**

This date provides a consistent reference point for evaluating employee assignments and compensation records.

### 3.4 Compa-Ratio

Compa-ratio measures an employee's normalized salary relative to the midpoint of the applicable compensation band.

Compa-Ratio = Normalized Salary / Compensation Band Midpoint

Interpretation:

- Below 1.0: Salary is below the band midpoint.
- Equal to 1.0: Salary is at the band midpoint.
- Above 1.0: Salary is above the band midpoint.

A compa-ratio is a comparison metric, not a direct measure of employee performance or compensation fairness.

### 3.5 Compensation Band Position

The employee's normalized salary is evaluated against the applicable compensation band's minimum and maximum values.

Possible classifications include:

- Below Band
- Within Band
- Above Band

Being outside a compensation band indicates a condition requiring review. It does not automatically establish an error or unfair treatment.

## 4. Disparity Detection Assumptions

The disparity detection module uses predefined screening conditions.

The implemented conditions include:

### 4.1 Below-Band Compensation

Employees whose normalized compensation falls below the applicable band minimum are flagged.

### 4.2 Above-Band Compensation

Employees whose normalized compensation exceeds the applicable band maximum are flagged.

### 4.3 Extreme Compa-Ratio

The system flags:

- Compa-ratio below 0.80
- Compa-ratio above 1.20

These thresholds identify potentially unusual compensation positions for further review.

### 4.4 Comparable-Group Salary Difference

Employees are compared with employees in the same defined comparison group.

A salary difference of at least 10% below the comparable-group average is flagged.

The comparison is based on the grouping attributes implemented in the analysis module.

### 4.5 Interpretation of Flags

Disparity flags are screening indicators.

They do not prove:

- Discrimination
- Unfair compensation
- Incorrect salary decisions
- Policy violations
- Employee underperformance

Additional investigation and human judgment are required before taking action.

## 5. Evidence-Based Review Assumptions

The evidence-based review module considers available performance evidence and employee context.

The review uses the latest available performance evidence for an employee.

The analysis is intended to support further investigation rather than automatically recommend a final compensation decision.

Important considerations:

- Missing evidence may limit the ability to evaluate an employee.
- Performance scores should not be interpreted as a complete measure of employee contribution.
- Tenure and performance context should be reviewed together.
- Comparable-group results depend on the available synthetic data.

## 6. Employee Comparison Assumptions

The employee comparison module calculates descriptive statistics for comparable employee groups.

The metrics include:

- Average salary
- Median salary
- Minimum salary
- Maximum salary
- Salary range
- Standard deviation
- Percentage difference from the group median

The median is included because it is less sensitive to unusually high or low salary values than the mean.

These statistics describe salary distributions. They do not independently establish whether compensation decisions are fair.

## 7. Adjustment Proposal Assumptions

The proposal workflow uses predefined rules to create adjustment proposals.

The current implementation follows these principles:

- Below-band compensation can generate a proposal toward the applicable band minimum.
- Above-band compensation can be flagged for human review.
- Employees within the compensation band are not automatically assigned a salary adjustment.

Proposal creation does not mean that an adjustment has been approved.

### 7.1 Proposal Lifecycle

The implemented lifecycle is:

DRAFT → SUBMITTED → APPROVED

DRAFT → SUBMITTED → REJECTED

Each workflow action is recorded through the relevant approval and audit records.

### 7.2 Approval Behavior

- A proposal must be submitted before a decision can be recorded.
- A submitted proposal can be approved or rejected.
- Approval changes the proposal status.
- Approval does not automatically update the employee's salary.
- Salary implementation would require a separate controlled process.

## 8. Database and Data Integrity Assumptions

The project uses SQLite as its relational database.

The following principles are applied:

- Employee and organizational identifiers should be unique.
- Foreign-key relationships should remain valid.
- Salary values should be positive.
- FTE values should be within the supported range.
- Employee assignment periods should not overlap.
- Compensation band records should satisfy the implemented date and arithmetic checks.
- Proposal statuses and approval decisions should use valid values.

Database validations are executed before analytical processing.

## 9. Reproducibility Assumptions

- Synthetic data generation uses a fixed random seed where applicable.
- The database regeneration process is separate from the analytical execution process.
- `rebuild_database.py` regenerates the database.
- `run.py` executes validations and analytical workflows against the existing database.
- Rebuilding the database can replace existing proposal and approval state.

Users should avoid rebuilding the database when they want to preserve workflow activity.

## 10. Limitations

The current implementation has the following limitations:

1. The dataset is synthetic and may not represent real organizational compensation patterns.
2. Disparity thresholds are predefined rather than statistically or organizationally calibrated.
3. Comparable-group analysis uses a limited set of attributes.
4. Performance evidence may not capture all aspects of employee contribution.
5. Currency conversion depends on the available synthetic exchange-rate records.
6. The project does not establish legal compliance or prove compensation fairness.
7. Proposal approval does not automatically implement salary changes.
8. Production authentication, authorization, and advanced concurrent workflow controls are not included.

## 11. Future Improvements

Possible improvements include:

- Configurable compensation policies and screening thresholds.
- More detailed employee comparison criteria.
- Additional statistical fairness analysis.
- Improved handling of missing evidence.
- Role-based access control.
- Integration with a production HR information system.
- Automated salary implementation after authorized approval.
- More extensive testing using real-world edge cases.

---

**Project:** YottaFlex Compensation Analysis  
**Document:** Assumptions and Business Rules  
**Data Source:** Synthetic dataset  
**Analysis Reference Date:** 31 December 2026