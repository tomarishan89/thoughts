---
name: predictability-loop
description: Iterative self-improvement loop for the predictability engine. Runs the backtester, updates empirical documents, requests adversarial reviews, and actively resolves downstream theoretical and empirical issues.
---

# Predictability Loop

This skill defines the iterative self-improvement loop for the financial predictability engine. When instructed to "run the predictability loop", execute the following sequence precisely.

## Step 1: Execution

Run the predictability engine pipeline to generate fresh empirical results.
- Run `predictability_engine/backtester.py`.
- Run `predictability_engine/analysis.py`.
- Verify the outputs (e.g., `validation_scorecard_v3.json`, `sector_stratified_scorecard.json`).

## Step 2: Documentation Update

Update the empirical results in `foundations/empirical_predictability_test_results.md` based on the new outputs.
- Ensure the $p$-values, FDR $q$-values, precision, recall, and sector-stratified failure rates are accurately reflected.

## Step 3: Adversarial Review

Adopt the personas of Reviewer $\Psi$ (The Adversarial Referee) and Reviewer $\Omega$ (The Impartial Referee) as defined in `AGENTS.md`.
- Read the updated `empirical_predictability_test_results.md`.
- Reviewer $\Psi$ must attack the new results, identify failure modes, dimensional inconsistencies, and update `partial_reviewer_critique.md` with kill conditions.
- Reviewer $\Omega$ must impartially assess the progress and update `impartial_reviewer_assessment.md`.

## Step 4: Consolidation & Active Issue Resolution

This is the core engineering and theoretical phase.
1. Extract the kill conditions and theoretical flaws identified by the reviewers and log them in `issues_log.md` (maintaining the Non-Zero Active Frontier Invariant).
2. **Actively pick up the newly logged (or highest priority existing) issues and work on them.** This involves:
   - Modifying mathematical models and variables.
   - Using scratchpad scripts to verify equations and run the EdS rule numerical limits (Rule 5.1).
   - Updating `FINANCIAL_MASTER_FRAMEWORK.md`, `financial_systems_framework.md`, and the relevant files in `foundations/` to mathematically formalize the resolution.
3. Modify the Python codebase in `predictability_engine/` (e.g., `mass_vector.py`, `backtester.py`, `analysis.py`) to computationally implement the theoretical fixes.

## Step 5: Iteration

If running in a multi-iteration loop, proceed to the next iteration (back to Step 1).
If the required number of iterations is complete, halt and notify the user.
