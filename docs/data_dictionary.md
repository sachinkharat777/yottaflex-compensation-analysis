# Data Dictionary — YottaFlex Compensation Analysis

## 1. Overview

This document describes the database structure, tables, columns, relationships, and constraints used in the YottaFlex Compensation Analysis project.

The application uses SQLite as its relational database.

The database contains **15 tables** organized around employee information, organizational structure, compensation history, performance evidence, adjustment proposals, approvals, and audit records.

## 2. Database Summary

| Category | Tables |
|---|---|
| Master Data | Role, Level, Location, Employee |
| Compensation | CompensationBand, SalaryRecord, CurrencyRate |
| Employee History | EmployeeAssignment, Promotion, TenureSnapshot |
| Performance Evidence | PerformanceEvidence |
| Proposal Management | AdjustmentProposal, ProposalEvidence |
| Approval and Audit | ApprovalEvent, AuditEvent |

**Total tables: 15**

## 3. Table Definitions

### 3.1 Role

Stores organizational job roles and comparable-group information.

| Column | Description |
|---|---|
| role_id | Unique identifier for a role; primary key |
| role_name | Name of the job role; unique and required |
| job_family | Functional job family |
| comparable_group | Group used for employee compensation comparisons |
| comparison_rationale | Explanation of the comparison grouping |

### 3.2 Level

Stores job levels and their seniority order.

| Column | Description |
|---|---|
| level_id | Unique level identifier; primary key |
| level_name | Name of the job level; unique |
| seniority_rank | Numeric seniority order; unique |

### 3.3 Location

Stores employee work-location information.

| Column | Description |
|---|---|
| location_id | Unique location identifier; primary key |
| location_name | Name of the work location |
| country_code | Country identifier |
| currency_code | Currency associated with the location |

### 3.4 Employee

Stores basic employee information.

| Column | Description |
|---|---|
| employee_id | Unique employee identifier; primary key |
| hire_date | Employee hiring date |
| employment_status | Employment status: ACTIVE, ON_LEAVE, or TERMINATED |
| created_at | Timestamp when the employee record was created |

### 3.5 CompensationBand

Stores salary ranges for specific role, level, and location combinations.

| Column | Description |
|---|---|
| band_id | Unique compensation-band identifier; primary key |
| role_id | Related role identifier; foreign key |
| level_id | Related level identifier; foreign key |
| location_id | Related location identifier; foreign key |
| min_salary | Minimum salary in the band |
| midpoint_salary | Midpoint salary in the band |
| max_salary | Maximum salary in the band |
| currency_code | Currency used for the salary band |
| effective_start | Date when the band becomes effective |
| effective_end | Date when the band expires; nullable |

Constraints:
- Minimum salary must be positive.
- Minimum salary must not exceed midpoint salary.
- Midpoint salary must not exceed maximum salary.
- Effective end date must be later than the start date when provided.

### 3.6 EmployeeAssignment

Stores employee role, level, location, and FTE assignment history.

| Column | Description |
|---|---|
| assignment_id | Unique assignment identifier; primary key |
| employee_id | Related employee identifier; foreign key |
| role_id | Assigned role identifier; foreign key |
| level_id | Assigned level identifier; foreign key |
| location_id | Assigned location identifier; foreign key |
| fte | Full-Time Equivalent value |
| effective_start | Assignment start date |
| effective_end | Assignment end date; nullable |
| change_reason | Reason for the assignment or change |

Constraints:
- FTE must be greater than 0 and no greater than 1.
- Effective end date must be later than the start date when provided.

### 3.7 SalaryRecord

Stores historical annual base salary information.

| Column | Description |
|---|---|
| salary_id | Unique salary-record identifier; primary key |
| employee_id | Related employee identifier; foreign key |
| annual_base_salary | Annual base salary amount |
| currency_code | Currency of the salary |
| fte | Full-Time Equivalent associated with the salary |
| effective_start | Salary effective start date |
| effective_end | Salary effective end date; nullable |
| recorded_at | Timestamp when the salary record was recorded |
| source | Origin of the salary record |

Constraints:
- Annual base salary must be positive.
- FTE must be greater than 0 and no greater than 1.
- Effective end date must be later than the start date when provided.

### 3.8 Promotion

Stores employee promotion history.

| Column | Description |
|---|---|
| promotion_id | Unique promotion identifier; primary key |
| employee_id | Related employee identifier; foreign key |
| from_role_id | Previous role identifier; foreign key; nullable |
| from_level_id | Previous level identifier; foreign key; nullable |
| to_role_id | New role identifier; foreign key |
| to_level_id | New level identifier; foreign key |
| effective_date | Date the promotion becomes effective |
| status | Promotion status: PROPOSED, APPROVED, REJECTED, or COMPLETED |

### 3.9 PerformanceEvidence

Stores performance-related evidence used during employee reviews.

| Column | Description |
|---|---|
| evidence_id | Unique evidence identifier; primary key |
| employee_id | Related employee identifier; foreign key |
| evidence_type | Type of performance evidence |
| rating | Numeric performance rating; nullable |
| description | Description of the evidence |
| evidence_date | Date associated with the evidence |
| source_reference | Reference to the evidence source; nullable |

### 3.10 TenureSnapshot

Stores employee tenure information at a specific reference date.

| Column | Description |
|---|---|
| tenure_id | Unique tenure snapshot identifier; primary key |
| employee_id | Related employee identifier; foreign key |
| as_of_date | Date on which tenure is calculated |
| tenure_months | Employee tenure in months |

Constraint:
- Tenure months cannot be negative.
- Each employee can have only one snapshot per reference date.

### 3.11 CurrencyRate

Stores currency conversion rates relative to INR.

| Column | Description |
|---|---|
| currency_rate_id | Unique currency-rate identifier; primary key |
| currency_code | Currency code |
| rate_to_inr | INR value of one unit of the specified currency |
| effective_date | Date the exchange rate applies |
| source | Source of the exchange-rate record |

For example, if rate_to_inr is 83, one unit of that currency is equivalent to INR 83.

Constraints:
- Exchange rate must be positive.
- Currency code and effective date must form a unique combination.

### 3.12 AdjustmentProposal

Stores proposed employee compensation adjustments.

| Column | Description |
|---|---|
| proposal_id | Unique proposal identifier; primary key |
| employee_id | Related employee identifier; foreign key |
| proposed_annual_salary | Proposed annual salary amount |
| currency_code | Currency of the proposed salary |
| reason | Explanation for the proposal |
| status | Proposal status: DRAFT, SUBMITTED, APPROVED, REJECTED, or WITHDRAWN |
| created_at | Timestamp when the proposal was created |

Constraint:
- Proposed annual salary must be positive.

### 3.13 ProposalEvidence

Links adjustment proposals with supporting performance evidence.

| Column | Description |
|---|---|
| proposal_id | Related proposal identifier; foreign key |
| evidence_id | Related performance evidence identifier; foreign key |

The combination of proposal_id and evidence_id forms the composite primary key.

This creates a many-to-many relationship:
- One proposal can reference multiple evidence records.
- One evidence record can support multiple proposals.

### 3.14 ApprovalEvent

Stores approval decisions and their associated details.

| Column | Description |
|---|---|
| approval_event_id | Unique approval-event identifier; primary key |
| proposal_id | Related proposal identifier; foreign key |
| decision | Decision: APPROVED, REJECTED, or RETURNED |
| approver_id | Identifier of the person or actor making the decision |
| comments | Optional decision comments |
| event_timestamp | Timestamp of the approval event |

### 3.15 AuditEvent

Stores audit information for workflow and entity changes.

| Column | Description |
|---|---|
| audit_event_id | Unique audit-event identifier; primary key |
| entity_type | Type of entity affected |
| entity_id | Identifier of the affected entity |
| action | Action performed |
| old_values | Previous values, when available |
| new_values | Updated values, when available |
| actor | Person or process performing the action |
| event_timestamp | Timestamp of the recorded action |

## 4. Table Relationships

The database uses primary keys and foreign keys to maintain relational integrity.

Main relationships:

- Role → CompensationBand
- Level → CompensationBand
- Location → CompensationBand
- Employee → EmployeeAssignment
- Role → EmployeeAssignment
- Level → EmployeeAssignment
- Location → EmployeeAssignment
- Employee → SalaryRecord
- Employee → Promotion
- Employee → PerformanceEvidence
- Employee → TenureSnapshot
- Employee → AdjustmentProposal
- AdjustmentProposal → ProposalEvidence
- PerformanceEvidence → ProposalEvidence
- AdjustmentProposal → ApprovalEvent

AuditEvent stores entity references without a direct foreign-key constraint.

## 5. Database Constraints and Indexes

### Integrity Constraints

The schema implements:
- Primary-key constraints.
- Foreign-key constraints.
- Unique constraints.
- NOT NULL constraints.
- CHECK constraints for salary, FTE, dates, and workflow statuses.

### Indexes

The schema creates the following indexes to support common queries:

| Index | Table | Indexed columns |
|---|---|---|
| idx_assignment_employee_dates | EmployeeAssignment | employee_id, effective_start, effective_end |
| idx_salary_employee_dates | SalaryRecord | employee_id, effective_start, effective_end |
| idx_band_lookup | CompensationBand | role_id, level_id, location_id, effective_start |
| idx_evidence_employee | PerformanceEvidence | employee_id |
| idx_proposal_employee | AdjustmentProposal | employee_id |
| idx_approval_proposal | ApprovalEvent | proposal_id |

## 6. Important Data Interpretation Notes

- Employee and compensation records are synthetic.
- Salary values may use different currencies.
- INR is the reporting currency used by the analysis.
- FTE is used to normalize salary for comparison.
- Effective dates determine which assignment, salary, and compensation band records apply.
- Nullable end dates represent records without a specified end date.
- Approval events and audit events provide workflow traceability.
- An approved proposal does not automatically update an employee's salary.

## 7. Source of Truth

The authoritative database definitions are maintained in:

`database/schema.sql`

This document describes the schema implemented in that file.

---

**Project:** YottaFlex Compensation Analysis  
**Database:** SQLite  
**Total Tables:** 15  
**Data:** Synthetic employee and compensation records