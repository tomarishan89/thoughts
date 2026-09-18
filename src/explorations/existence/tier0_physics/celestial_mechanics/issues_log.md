# Celestial Mechanics Issues Log & Active Frontiers

This log tracks all identified theoretical gaps, mathematical inconsistencies, open vulnerabilities, and milestone resolutions for the celestial mechanics sub-domain ([`celestial_mechanics_framework.md`](celestial_mechanics_framework.md) and [`CELESTIAL_MASTER_FRAMEWORK.md`](CELESTIAL_MASTER_FRAMEWORK.md)).

---

## Status Legend

- `[ ]` Open / Active Theoretical Frontier
- `[~]` In Progress / Partially Resolved
- `[X]` Formally Resolved & Mathematically Closed
- `[DEFERRED]` Logged and deferred to future exploratory phases

---

## Active Theoretical Frontiers & Priority Master Table

| Issue ID | Priority | Epistemic Type | Domain | Description | Downstream Target / Kill Condition | Status |
|:---|:---|:---|:---|:---|:---|:---|
| **V-3B-1** | Resolved | Type (a) | 3-Body Dynamics | Scalar asymmetry metric non-diagnostic for resonance stability | Proved scalar time-average asymmetry fails to separate Kirkwood from Hilda orbits | `[X]` |
| **V-3B-2** | Resolved | Type (a) | 3-Body Dynamics | Phase-alignment tensor discriminates Kirkwood chaos from Hilda stability | Proved cross-correlation phase tensor $\mathbf{A}_{\text{phase}}$ yields $4.2\times$ contrast between Kirkwood and Hilda | `[X]` |
| **V-QM-10** | Resolved | Type (a) | Dynamical Systems | Ab initio 3-body stability criterion from player hierarchy | Derived via Tisserand + resonance protection mechanism; $\lambda_{\max}/\lambda_{\min}$ predicted $= 3.55$ vs empirical $4.2$ | `[X]` |
| **V-L-2** | Resolved | Type (a) | Field Theory | Screened Poisson sourcing equation for inter-body deformation | Derived $(\nabla^2 - \xi^{-2})\Phi_{\mathcal{G}} = -4\pi G \rho_{\mathcal{G}}$ with Yukawa Green's function closing $w_{ij}$ | `[X]` |
| **V-3B-3** | Active | Type (a) | 3-Body Dynamics | Composite Imaginary-Sector Closure Problem for multi-body systems | Formulate emergent composite imaginary anisotropy $\mathbf{A}_{\mathfrak{Im}}^{(\text{composite})}$ for $N$-body systems | `[ ]` |
| **V-QM-10.1** | Active | Type (a)/(b) | Dynamical Systems | Second-order secular resonance coupling for 5:2 and 7:3 Kirkwood gaps | Extend binary $j:1$ vs $j:j-1$ classification to include higher-order secular resonance overlap ( Murray & Dermott Ch. 7.3 ) | `[ ]` |
| **V-QM-10.2** | Active | Type (a) | Exoplanet Dynamics | Rank-2 tidal tensor extension for eccentric Jupiter ( $e_J = 0.048$ ) | Replace scalar $\kappa_J$ with full rank-2 tidal tensor; connects to exoplanet stability theory | `[ ]` |
| **V-QM-10.3** | Active | Type (a) | Existence Equation Bridge | Map orbital Resistance $R_{\text{orbital}} = \Omega_{\text{stab}} - 1$ to framework existence equation | Prove $R_{\text{orbital}} = 0 \Leftrightarrow$ orbital boundary at critical point; close the conceptual loop to existence equation | `[ ]` |

---

## Detailed Issue Analysis & Resolution Records

### ISSUE V-3B-1: Failure of Scalar Asymmetry Metrics in Orbital Dynamics

- **Epistemic Classification:** Type (a) — Original Derivation
- **Status:** `[X]` Formally Resolved & Mathematically Closed
- **Priority:** Critical
- **Theoretical Gap:**  
  Earlier iterations attempted to classify three-body stability using scalar asymmetry measures ( such as scalar eccentricity or distance variance ).
- **Formal Resolution:**  
  Numerical simulations over 50,000 years in [`../../scripts/threebody_player_hierarchy.py`](../../scripts/threebody_player_hierarchy.py) proved that scalar metrics fail: stable Hilda asteroids undergo large scalar eccentricity oscillations ( $e \sim 0.15\text{--}0.30$ ) comparable to unstable Kirkwood asteroids. Scalar metrics ignore phase space angle correlations. Closed and documented in [`celestial_mechanics_framework.md`](celestial_mechanics_framework.md) §2.
- **Downstream Active Frontier (Rule 2):**  
  **ISSUE V-3B-2:** Formulation of the rank-2 phase-alignment tensor $\mathbf{A}_{\text{phase}}$.

---

### ISSUE V-3B-2: Phase-Alignment Tensor Discrimination

- **Epistemic Classification:** Type (a) — Original Derivation
- **Status:** `[X]` Formally Resolved & Mathematically Closed
- **Priority:** Critical
- **Theoretical Gap:**  
  Need a rigorous mathematical invariant that separates the stable libration of Hilda asteroids from the chaotic clearing of Kirkwood gaps.
- **Formal Resolution:**  
  Defined the rank-2 phase-alignment tensor $\mathbf{A}_{\text{phase}} \equiv \mathbf{n}_{\text{ecc}} \otimes \nabla\varpi$. For Hilda (3:2), conjunctions occur strictly at perihelion, yielding secular torque cancellation $\mathcal{T}_{\text{sec}} = \text{Tr}(\mathbf{A}_{\text{phase}} \cdot \nabla V_{\text{pert}}) = 0$ and an eigenvalue ratio $\lambda_{\max}/\lambda_{\min} \ge 4.0$. For Kirkwood (3:1), chaotic phase wandering washes out directional correlation, giving $\lambda_{\max}/\lambda_{\min} \to 1.0$.
- **Downstream Active Frontier (Rule 2):**  
  **ISSUE V-QM-10.1:** Higher-order secular resonance overlap for second-order resonances ( 5:2 and 7:3 ).
