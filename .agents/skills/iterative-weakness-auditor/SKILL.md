---
name: iterative-weakness-auditor
description: Enforces the Anti-Premature Closure Invariant, Downstream Frontier Propagation protocol, and multi-tier calculation audit protocols for mathematical physics manuscripts. Use whenever theoretical milestones or vulnerabilities are audited in draft.md or issues_log.md.
---

# Iterative Weakness Auditor Skill

This skill enforces unsparing referee-level mathematical physics, continuum mechanics, and non-equilibrium thermodynamic auditing across manuscripts. It prevents premature closure of theoretical gaps and ensures continuous downward refinement from lumped 0D models to continuum field-theoretic closures.

## Core Philosophical Invariant: The Non-Zero Active Frontier Rule
**Rule:** You MUST NEVER leave the active theoretical frontiers list empty. In mathematical physics, resolving a high-level lumped or mean-field approximation inevitably exposes downstream micro-hydrodynamic, kinetic, tensorial, or boundary-value constraints. Past iterations do NOT fade or diminish; they form the cumulative bedrock upon which increasingly microscopic conservation laws are rigorously established.

---

## 6-Layer Downstream Audit Protocol

Whenever a theoretical milestone is audited or moved to `[x] Formally Resolved`:

### 1. Dimensional Homogeneity & Metric Invariance
- **Check:** Are all algebraic and tensor terms dimensionally commensurate in SI units?
- **Stress-Test:** Look for logs of dimensioned quantities ($\ln c \to \ln(\gamma c / c^\ominus)$), sums of incommensurate measures (mass $[\mathrm{kg}]$ vs. entropy $[\mathrm{bits}]$ requiring Landauer parameter $\kappa_{\text{info}} \equiv \frac{k_B T \ln 2}{c^2}$), and tensor Frobenius double-dot contractions ($\mathbf{s}:\mathbf{s} = \frac{2}{3}\sigma_{\mathrm{vM}}^2$).

### 2. Spatial & Kinetic Dispersion Audit
- **Check:** Does the resolved model hold when spatial gradients or localized shocks are applied?
- **Stress-Test:** Eikonal-curvature wavefront retardation ($v_{\text{front}} = v_{\text{bistable}} - D_{\text{diff}}\mathcal{K}_{\text{front}}$), finite nucleation radius $r_0 > D_{\text{diff}}/v_{\text{bistable}}$, and dynamic phase-lag resonance ($\cos(\mathrm{Da}(x)) < 0 \iff \mathrm{Da} \in (\pi/2, 3\pi/2) \pmod{2\pi}$).

### 3. Kinematic & Tensorial Directionality Audit
- **Check:** Does the kinematic formulation capture both shear distortion and isotropic volumetric compression/tension?
- **Stress-Test:** Capped Drucker-Prager plasticity ($\min\{\sigma_{\text{yield}} - (\sqrt{3 J_2} + \alpha_{\text{DP}} I_1), p_{\text{crush}} - p, \sigma_{\text{cav}} - p\}$), and decoupling Maxwell deviatoric relaxation from isotropic bulk modulus.

### 4. Non-Linear PDE Principal Symbol & Parabolicity Preservation
- **Check:** Does the relativistic or regularized kinematic PDE preserve parabolic smoothing at singular limits?
- **Stress-Test:** Ensure velocity saturation on advective traction does NOT divide or cancel the second-order mean-curvature Laplacian term as $|\kappa| \to \infty$.

### 5. Non-Equilibrium Thermodynamics & Conservation Laws
- **Check:** Does the system satisfy the Second Law, Gouy-Stodola exergy theorem, and Rankine-Hugoniot shock relations?
- **Stress-Test:** Availability dissipation must reference ambient bath temperature ($T_{\text{ambient}}\int \sigma_{\text{total}} dV$); shock entropy must include cubic Hugoniot jump terms; trophic mass ingestion must include metabolic dissipation factor ($\eta_{\text{trophic}} < 1$).

### 6. Constitutive, Electrodiffusive & Hydrodynamic Closure
- **Check:** Are all coupling operators ($\mathcal{O}_{\text{coupling}}$) micro-hydrodynamically closed without arbitrary empirical multipliers?
- **Stress-Test:** Helmholtz-Smoluchowski electro-osmosis ($\mathbf{K}_{\text{eo}} \equiv \frac{\varepsilon_w \zeta}{\mu_{\text{fluid}}}\mathbb{I}$), Darcy-Nernst-Planck cross-coupling, and junctional electroneutral current conservation ($\sum z_i F (\mathbf{J}_i \cdot \hat{n}) \equiv 0$).

---

## Synchronization Protocol
- Update `draft.md` Section 6.2 under `#### Formally Resolved Theoretical Milestones` and `#### Active Theoretical Frontiers`.
- Maintain exact bilateral synchronization in `issues_log.md` with explicit issue tags (`ISSUE-X.Y`).
- Document all proof adjustments and master checklists in `review.md`.

