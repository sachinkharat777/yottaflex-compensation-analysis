# Phase 6 — Synthetic Data Realism and Rule-Driven Proposals

## Purpose

This phase improves the realism of the clean synthetic compensation baseline and
generates adjustment proposals from documented compensation-screening rules.
It does not make final compensation decisions.

## Salary-history realism

- Each employee receives one deterministic relative position within the
  applicable compensation band.
- The position is sampled from a triangular distribution between 15% and 85%
  of the band range, with the mode at 50%.
- The same employee-specific position is reused across salary-history periods.
- Effective-dated band changes and assignment/promotion changes drive salary
  movement across periods.
- Actual salary remains FTE-adjusted in `SalaryRecord`.
- The clean baseline remains inside the applicable compensation band. Deliberate
  data-quality anomalies remain isolated in the anomaly benchmark.

These are synthetic data-generation assumptions, not market salary claims.

## Proposal screening

The generator reads employee, assignment, salary, band, role, tenure, performance,
and currency-rate records. It does not read `ground_truth.csv`.

### Normalization

1. Full-time-equivalent salary = recorded annual salary / FTE.
2. INR-normalized salary = full-time-equivalent salary × effective currency rate.
3. Compa-ratio = FTE-normalized salary / compensation-band midpoint.
4. Comparable-group averages are calculated using the same comparable group,
   level, and location, after INR normalization.

### Existing screening rules reused

- Below band: FTE-normalized salary is below the effective band minimum.
- Above band: FTE-normalized salary is above the effective band maximum.
- Compa-ratio screening boundaries: below 0.80 or above 1.20.
- Comparable-group gap: employee salary is at least 10% below the average for
  the same comparable group, level, and location.

### Proposal outcomes

- Below-band cases may receive a draft recommendation toward the band minimum.
- A qualifying comparable-group gap may receive a draft recommendation toward
  the comparable-group average, constrained to the employee's effective band.
- Above-band cases are not given automatic increases; they remain human-review
  exceptions.
- Within-band cases without a qualifying comparable-group gap do not receive
  an automatic adjustment proposal.
- Performance rating and tenure are attached as evidence context. No additional
  performance or tenure eligibility threshold is invented.
- Proposals are created as `DRAFT`; the one `ADJ-2026-000002` approved record is
  retained solely as a deterministic workflow test fixture.
- Approval does not update `SalaryRecord`. Final compensation decisions remain
  under human oversight.

## Reproducibility and traceability

- The configured seed and supporting-generator seed offset control sampling.
- Proposal evidence links to the employee's latest performance evidence available
  on the configured analysis date.
- Proposal reasons record the screening rule and relevant normalized metrics.
- Audit events record proposal creation and the deterministic approval fixture.
- Currency rates are sourced from `CurrencyRate`; missing rates are not silently
  replaced with guessed conversions.
