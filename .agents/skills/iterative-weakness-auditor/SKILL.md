---
name: iterative-weakness-auditor
description: Enforces the Anti-Premature Closure Invariant and Downstream Frontier Propagation protocol for mathematical physics manuscripts. Use whenever theoretical milestones or vulnerabilities are resolved in draft.md or issues_log.md.
---

# Iterative Weakness Auditor Skill

This skill enforces strict referee-level vulnerability auditing to prevent premature closure of theoretical gaps in mathematical physics, continuum mechanics, and non-equilibrium thermodynamic manuscripts.

## Core Invariant: The Non-Zero Active Frontier Rule
**Rule:** You MUST NEVER leave the active theoretical frontiers list empty. In mathematical physics, solving a lumped or 0D milestone inevitably unmasks deeper spatial, kinetic, or hydrodynamic boundary-value problems.

## 3-Step Downstream Audit Protocol

Whenever a milestone is moved to `[x] Formally Resolved`:

### 1. Spatial & Kinetic Dispersion Audit
- **Check:** Does the resolved model assume spatial homogeneity (0D or mean-field)?
- **Stress-Test:** Introduce spatial diffusion ($D_{\text{diff}}$), localized point impacts, or non-uniform field gradients.
- **Log if Open:** Dynamic spatial localization, wavefront lag, or localized stress concentrations (e.g., $\mathrm{Da}(x_{\text{impact}}) > 1$ vs. $\mathrm{Da}(x_{\text{distal}}) \ll 1$).

### 2. Kinematic & Tensorial Directionality Audit
- **Check:** Does the kinematic formulation assume a single scalar or directional sign convention?
- **Stress-Test:** Contrast compressive convective erosion ($\mathbf{v}_n \cdot \hat{n} < 0$) with tensile hoop-stress swelling and bursting ($P > \sigma_{\text{yield}}$).
- **Log if Open:** Strain-to-failure tensor criteria or anisotropic failure envelopes.

### 3. Constitutive & Hydrodynamic Closure Audit
- **Check:** Are coupling operators or flux transfers relying on phenomenological parameters (e.g., efficiency $\eta \in [0, 1]$)?
- **Stress-Test:** Demand microscopic field equations (e.g., Darcy porous flow, Nernst-Planck electrodiffusion, Navier-Stokes traction).
- **Log if Open:** Missing hydrodynamic closure for the macro-Lyapunov functional.

## Synchronization Protocol
- Update `draft.md` Section 6.2 under `#### Active Theoretical Frontiers (Pending Physical Resolution)`.
- Synchronize `issues_log.md` with explicit issue tags (`ISSUE-X.Y`).
- Commit and push immediately to GitHub.
