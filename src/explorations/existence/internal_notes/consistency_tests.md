# Manuscript Consistency Test Suite

*Analogous to a software regression test suite: run these checks whenever a new equation, concept, or section is introduced into `draft.md`. Each test is a necessary condition, not sufficient. Failure of any test is a mandatory stop — log it in `issues_log.md` before continuing.*

---

## How to Use

When adding a new mathematical object (equation, operator, theorem, mapping), run through each test below sequentially. Record PASS / FAIL / N/A. Any FAIL must be immediately logged as an Active Vulnerability in `issues_log.md`.

---

## Test Group 1: Dimensional Homogeneity

**T1.1 — SI Unit Balance**
Every equation must balance dimensionally in SI units. For each new equation, verify both sides have identical units.

**T1.2 — Landauer Erasure Charge**
Any imaginary computation must carry a Landauer cost charged to the real metabolic budget: W_Landauer = n_bits * k_B * T * ln(2)  [W]
Verify: is this cost subtracted from E_total?

**T1.3 — Information Density Rate**
Any local computation density must be in [bits/(m^3*s)]. Failure: adding an extensive bit-count to an intensive entropy production rate.

---

## Test Group 2: Thermodynamic Sign Consistency

**T2.1 — Second Law (Universal)**
All universal entropy production must satisfy: dG_univ/dt <= 0

**T2.2 — Ego Free-Energy Sign (Survival Condition)**
dG_Ego/dt >= 0 (survival), dG_Ego/dt < 0 (starvation/lysis)
Verify: does the new term conflate the Ego internal G with the universal G?

**T2.3 — Fuel Sufficiency Threshold**
E_fuel_dot >= E_crit_dot = T_ambient * S_gen_internal_dot

---

## Test Group 3: Causality & Relativistic Bounds

**T3.1 — Sub-Luminal Boundary Velocity**
All boundary normal velocities: v_n = c*v_classical / sqrt(c^2 + v_classical^2) < c

**T3.2 — Causal Signal Propagation**
No new coupling operator may imply instantaneous action-at-a-distance.

---

## Test Group 4: Bekenstein-Landauer Hierarchy

**T4.1 — Imaginary Cannot Exceed Real (Bekenstein)**
S_Im <= S_R = |dE_R| * c^3 / (4*G*hbar*ln(2))

**T4.2 — Sub-Ego Dependency Hierarchy**
Any imaginary entity must be shown dependent on a real physical carrier. Verify the collapse ODE is satisfied when dE_R -> 0.

---

## Test Group 5: Operator Typing

**T5.1 — Hilbert Space Domain**
All operators on rho_E must be on H = L^2(Omega_C, dmu_h). Jump operators must have [L_k]*[rho]*[L_k†] = [s^-1] in the GKSL generator.

**T5.2 — CPTP Preservation**
Tr(L_hat * rho_hat) = 0. Verify sum_k L_k† L_k is self-adjoint.

**T5.3 — Multiplication Operator Composition**
Jump operators coupling a field F_k must use L_k = O_k * M_sqrt(F_k), not tensor product.

---

## Test Group 6: Boundary Coupling Consistency

**T6.1 — Coupling Operator Derivation**
New coupling operators must be derived as Euler-Lagrange divergence across shared boundary, not asserted phenomenologically.

**T6.2 — Electroneutrality at Junctions**
sum_i z_i * F * (J_i . n_hat) = 0

**T6.3 — Imaginary-Real Bidirectional Balance**
For any imaginary-real coupling channel, verify the net balance is explicit:
E_k_net_dot = -k_B*T*ln(2)*s_k_dot + eta_sense * I_sense
Neither channel may be implicitly one-directional without physical justification.

---

## Test Group 7: Scope & Co-Author Safety

**T7.1 — Tier Scope Check**
New content must be Tier I or II (physical/biological). Cognitive/Societal (Tier III/IV) specifics go to cognitive_social_extensions.md.

**T7.2 — No Undefined Placeholder Functions**
No generic mapping Phi(x,y) may appear without explicit functional form.

**T7.3 — Citation/Derivability Standard**
Every new theorem must either cite a published result or provide an in-manuscript derivation.

---

## Test Group 8: Self-Referential Coupling

**T8.1 — Circular Dependency Detection**
If a new sub-ego's expression signal $\sigma_k$ feeds back into the dynamics that determine its own seeding rate $\dot{\mathcal{I}}_{\text{sense}}$, the system is self-referential. This cannot be resolved with a simple ODE — it requires a fixed-point analysis. Check:
*Does the new coupling create a loop of the form: $A$ seeds $B$, and $B$'s output modifies $A$'s seeding rate?*
- If YES: a fixed-point equation must be written and solved (or shown to converge) before the result can be declared closed.
- If the loop is in the runaway regime (positive feedback, no damping): log the runaway threshold as an Active Vulnerability in `issues_log.md`.

**T8.2 — Type A / Type I Sub-Ego Classification**
Any newly introduced sub-ego must be explicitly classified:
- **Type A (Autonomous):** coupling $\sigma_k^A: \Omega_R \to \Omega_R$, no imaginary mediation, must satisfy $\partial \sigma_k^A / \partial E_k^{Im} = 0$.
- **Type I (Imaginary-mediated):** coupling routes through $\Omega_{Im}$, can be suppressed by active boundary resistance at Landauer cost.
Failure to classify is equivalent to T7.2 (placeholder) — flag and log.

**T8.3 — Cessation-Class Sub-Ego Check**
If the new sub-ego models the entity's own structural failure (cessation, lysis, collapse), verify the thermodynamic threshold condition is explicitly stated:

$$\sigma_{\text{cessation}} \cdot \frac{\partial \dot{E}_{\text{fuel}}}{\partial \sigma} \geq k_B T \ln 2 \cdot \dot{s}_{\text{cessation}}$$

Without this, the self-referential feedback direction (asset vs. accelerant) is indeterminate.

---

## Quick Checklist (Rapid-Review Mode)

For minor additions (single equation or term):
- [ ] T1.1 (Unit balance)
- [ ] T2.1 + T2.2 (Sign consistency)
- [ ] T4.1 (Bekenstein check)
- [ ] T7.1 (Scope)
- [ ] T7.2 (No placeholders)

For major additions (new section, operator, theorem): run all tests above, plus:
- [ ] T8.1 (Self-referential loop check)
- [ ] T8.2 (Sub-ego type classification)

---

Last updated: 2026-08-21. Maintained in sync with issues_log.md.