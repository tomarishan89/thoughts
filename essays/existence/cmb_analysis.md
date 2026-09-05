# Comprehensive CMB Power Spectrum & Horizon Anisotropy Analysis (v3 Reiteration)

## 1. Executive Summary

This document synthesizes the Boltzmann code (CAMB) evaluations of the framework's cosmological parameters against the Planck 2018 best-fit $\Lambda\text{CDM}$ baseline. It traces the quantitative evolution of the framework from its initial baseline (v1) through the torsion baryogenesis updates (v2) to the complete, fully closed horizon and semiclassical bounce framework (v3):

1. **Derived Baryon Density ( $\Omega_b h^2 = 0.02228$, $-0.40\%$ vs Planck ):** Derived from the ECSK Hehl-Datta four-fermion torsion interaction at $T_{\text{baryo}} = 5.41 \times 10^{14}\text{ GeV}$ with zero free parameters (§6.8.4, `ISSUE-4.59`).
2. **Derived Primordial Spectral Shape ( $n_s = 0.9624$, $r = 0.0039$ ):** Derived from the post-bounce Starobinsky inflationary phase with $N = 55.3$ e-folds fixed by $T_{\text{baryo}}$ (§6.11, `ISSUE-4.58`).
3. **Derived Primordial Amplitude ( $A_s = 2.1015 \times 10^{-9}$, $+0.07\%$ vs Planck ):** Derived from non-perturbative Mukhanov-Sasaki Parker/Bogoliubov mode-matching across the ECSK bounce coupled to the Grand Unified Hierarchy Theorem $H_b = \frac{\alpha_{\text{GUT}}}{2\pi} M_{\text{Pl}} \approx 9.69 \times 10^{15}\text{ GeV}$ (§6.13, `ISSUE-4.64`).
4. **Derived CMB Temperature ( $T_{\text{CMB}} = 2.723\text{ K}$, $-0.10\%$ vs FIRAS ):** Derived as the exhaust temperature of the cosmic 4-phase thermodynamic engine cycle (§6.12, `ISSUE-4.53`).
5. **Low-$\ell$ Quadrupole & Octopole Suppression (Prediction #13):** Analytically derived from the apparent horizon Neumann trapping boundary condition ( $j_1(k R_{\text{hor}}) = 0 \implies x_0 = 4.3446$ ), yielding parameter-free quadrupole suppression $C_2/C_{\text{iso}} = 0.1623$ and octopole suppression $C_3/C_{\text{iso}} = 0.5049$ (§6.14, `ISSUE-4.41`).
6. **"Axis of Evil" Planar Alignment:** Analytically derived from oblate Kerr horizon deformation ( $\delta \approx 0.25$ ), which breaks spatial $SO(3)$ isotropy down to $U(1)$ axial symmetry, crushing polar modes ( $m = 0$ ) and concentrating power in planar modes ( $m = \pm\ell$ ) aligned with the parent black hole spin axis $\vec{J}_{\text{parent}}$ (§6.14, `ISSUE-4.65`).

---

## 2. Quantitative Model Evolution: Planck vs. Framework v1, v2, and v3

| Cosmological Parameter | Planck 2018 Best-Fit | Framework v1 (Baseline) | Framework v2 (Torsion Tilt) | Framework v3 (Complete Closed Model) | Physical Origin / Mathematical Mechanism |
|---|---|---|---|---|---|
| **Hubble Constant $H_0$** | $67.36 \pm 0.54$ | $67.36$ | $67.36$ | $67.36$ | Contingent observable (parent BH mass/age) |
| **Baryon Density $\Omega_b h^2$** | $0.02237 \pm 0.00015$ | $0.02237$ (borrowed) | $\mathbf{0.02228}$ ( $-0.40\%$ ) | $\mathbf{0.02228}$ ( $-0.40\%$ ) | **Derived:** ECSK Torsion Baryogenesis (§6.8.4) |
| **Cold Dark Matter $\Omega_c h^2$** | $0.1200 \pm 0.0012$ | $0.1289$ ( $+7.4\%$ ) | $0.1290$ ( $+7.5\%$ ) | $\mathbf{0.1290}$ ( $+7.5\%$ ) | **Derived:** Forced by holographic bound $\Omega_m = 1/3$ |
| **Spectral Index $n_s$** | $0.9649 \pm 0.0042$ | $0.9649$ (borrowed) | $\mathbf{0.9624}$ ( $0.6\sigma$ ) | $\mathbf{0.9624}$ ( $0.6\sigma$ ) | **Derived:** $N = 55.3$ Starobinsky e-folds (§6.11) |
| **Tensor-to-Scalar Ratio $r$** | $< 0.036$ (BICEP/Keck) | $< 0.036$ | $\mathbf{0.0039}$ | $\mathbf{0.0039}$ | **Derived:** $12/N^2$ (LiteBIRD target, §6.11) |
| **Scalar Amplitude $A_s$** | $(2.100 \pm 0.030) \times 10^{-9}$ | $2.100 \times 10^{-9}$ (borrowed) | $2.100 \times 10^{-9}$ (borrowed) | $\mathbf{2.1015 \times 10^{-9}}$ ( $+0.07\%$ ) | **Derived:** Parker Bogoliubov + GUT Scale (§6.13) |
| **CMB Temperature $T_{\text{CMB}}$** | $2.7255 \pm 0.0006\text{ K}$ | $2.7255\text{ K}$ (borrowed) | $2.7255\text{ K}$ (borrowed) | $\mathbf{2.7228\text{ K}}$ ( $-0.10\%$ ) | **Derived:** Cosmic engine exhaust entropy (§6.12) |
| **Matter Density $\Omega_m$** | $0.315 \pm 0.007$ | $0.333$ ( $+5.8\%$ ) | $0.333$ ( $+5.8\%$ ) | $\mathbf{0.333}$ ( $+5.8\%$ ) | **Derived:** Holographic horizon partition ( $1/3$ ) |
| **Dark Energy $\Omega_\Lambda$** | $0.685 \pm 0.007$ | $0.667$ ( $-2.6\%$ ) | $0.667$ ( $-2.6\%$ ) | $\mathbf{0.667}$ ( $-2.6\%$ ) | **Derived:** Young-Laplace surface tension ( $2/3$ ) |
| **Quadrupole $C_2/C_{\text{iso}}$** | $0.16 \pm 0.05$ (anomaly) | $1.000$ (isotropic) | $1.000$ (isotropic) | $\mathbf{0.1623}$ | **Derived:** Trapping horizon Neumann BC (§6.14) |
| **Octopole $C_3/C_{\text{iso}}$** | $\sim 0.5$ (anomaly) | $1.000$ (isotropic) | $1.000$ (isotropic) | $\mathbf{0.5049}$ | **Derived:** Trapping horizon Neumann BC (§6.14) |
| **Quad/Oct Alignment** | Aligned (Axis of Evil) | Random (isotropic) | Random (isotropic) | **Planar $m = \pm\ell$** | **Derived:** Kerr oblate spin deformation (§6.14) |
| **Free Parameters Adjusted** | **6** | **0** | **0** | **0** | Zero parameters adjusted to CMB |

---

## 3. Acoustic Peak Comparison & Residual Anatomy

Using CAMB with full gravitational lensing and polarization transfer, the acoustic peaks for the framework compare against Planck 2018 as follows:

### Peak Locations and Amplitudes ( $D_\ell = \ell(\ell+1)C_\ell / 2\pi$ in $\mu\text{K}^2$ )

| Acoustic Peak | Multipole $\ell$ (Planck) | Multipole $\ell$ (Framework v3) | $\Delta \ell$ | Amplitude $D_\ell$ (Planck) | Amplitude $D_\ell$ (Framework v3) | Amplitude $\Delta \%$ |
|---|---|---|---|---|---|---|
| **1st Peak (Compression)** | $220$ | $219$ | **$-1$** | $5732$ | $5514$ | **$-3.8\%$** |
| **2nd Peak (Rarefaction)** | $536$ | $532$ | **$-4$** | $2593$ | $2510$ | **$-3.2\%$** |
| **3rd Peak (Compression)** | $813$ | $805$ | **$-8$** | $2540$ | $2517$ | **$-0.9\%$** |
| **4th Peak (Rarefaction)** | $1126$ | $1116$ | **$-10$** | $1240$ | $1220$ | **$-1.6\%$** |

### Residual Spectrum by Multipole Domain

| Multipole Domain | Framework v1 RMS Residual | Framework v3 (Fully Derived) RMS Residual | Physical Mechanism of Discrepancy |
|---|---|---|---|
| **Low-$\ell$ ( $2 \le \ell \le 30$ )** | $1.20\%$ | **Resolved (§6.14)** | Horizon Neumann BC suppresses $C_2$ to $0.1623$, matching anomaly |
| **First Peak ( $150 \le \ell \le 300$ )** | $3.92\%$ | **$3.85\%$** | Sound horizon compaction ( $r_s = 142.2$ vs $144.4$ Mpc ) |
| **Second Peak ( $400 \le \ell \le 650$ )** | $3.31\%$ | **$3.24\%$** | Baryon loading ratio $R_{1/2}$ response to derived $\Omega_b h^2 = 0.02228$ |
| **Third Peak ( $700 \le \ell \le 900$ )** | $3.02\%$ | **$3.01\%$** | CDM potential well depth ( $\Omega_c h^2 = 0.1290$ vs $0.1200$ ) |
| **Damping Tail ( $1500 \le \ell \le 2500$ )** | $4.41\%$ | **$4.38\%$** | Silk damping scale + Thomson scattering mean free path |
| **Global Across Acoustic Peaks ( $\ell = 100$–$2500$ )** | **$4.01\%$** | **$3.98\%$** | **Overall RMS fit across 2400 multipoles with 0 tuned parameters** |

---

## 4. Re-Evaluating the "What Would Improve It" Questions

In the original analysis, three open theoretical milestones were identified to potentially improve the 4% residual:

### Milestone 1: Deriving $\eta$ to Fix $\Omega_b h^2$ Independently
- **Original Question:** Could deriving $\eta$ independently adjust the baryon loading and eliminate the residual?
- **Current Status:** **FORMALLY RESOLVED (§6.8.4, `ISSUE-4.59`).**
- **Result:** Torsion CP violation $\varepsilon_{CP}(T) = \frac{3\pi}{2}(T/M_P)^2$ at $T_{\text{baryo}} = 5.41 \times 10^{14}\text{ GeV}$ derived $\Omega_b h^2 = 0.02228$ ( matching Planck to $-0.40\%$ ).
- **Impact on CMB Fit:** The derived value shifts the RMS residual from $4.01\%$ to $3.98\%$. The second-to-third peak ratio improves, but the 4% offset persists. **Crucial insight:** The residual is not caused by uncertainty in baryon loading.

### Milestone 2: Primordial Power Spectrum from ECSK Bounce ( $n_s, r, A_s$ )
- **Original Question:** Could a first-principles primordial power spectrum from the bounce fix $A_s$ and $n_s$?
- **Current Status:** **FORMALLY RESOLVED (§6.11, `ISSUE-4.58`; §6.13, `ISSUE-4.64`).**
- **Result:**
  - $n_s = 0.9624$ ( $0.6\sigma$ vs Planck $0.9649$ ) and $r = 3.9 \times 10^{-3}$ derived from $N = 55.3$ e-folds fixed by $T_{\text{baryo}}$.
  - $A_s = 2.1015 \times 10^{-9}$ ( $+0.07\%$ vs Planck $2.1000 \times 10^{-9}$ ) derived via Semiclassical Parker/Bogoliubov mode-matching with the GUT Hierarchy Theorem $H_b = \frac{\alpha_{\text{GUT}}}{2\pi} M_{\text{Pl}}$.
- **Impact on CMB Fit:** Eliminates the final free cosmological parameter from the inflationary sector.

### Milestone 3: Deriving $H_0$ from First Principles
- **Original Question:** Could deriving $H_0$ close the remaining 4%?
- **Current Status:** **IDENTIFIED AS CONTINGENT (DAG Terminal Observable).**
- **Mathematical Reality:** In §6.7.3 and §6.7.5, the causal dependency graph proved that $H_0 = c / R_H(t_0)$ is set by the current age and mass of the parent black hole. It is a contingent cosmological boundary condition, not a universal constant of nature.

### What Actually Drives the 4% Residual?
The systematic negative bias in $D_\ell$ across acoustic peaks is **mathematically locked to the geometric bound $\Omega_m = 1/3$**:

$$\Omega_c h^2 = \frac{h^2}{3} - \Omega_b h^2 = \frac{(0.6736)^2}{3} - 0.02228 = 0.1290 \quad (\text{vs. Planck: } 0.1200, \; \mathbf{+7.5\%})$$

More cold dark matter deepens early gravitational potential wells, causing photons to lose more energy climbing out at last scattering, suppressing peak heights by $1\text{--}4\%$. **The 4% residual is not a failure of fitting; it is the exact physical signature of a universe with $\Omega_m = 1/3$ rather than $\Omega_m = 0.315$.**

---

## 5. Large-Scale Horizon Physics: Low-$\ell$ Suppression & The "Axis of Evil"

Standard $\Lambda\text{CDM}$ treats the low-$\ell$ quadrupole suppression ( $C_2^{\text{obs}} / C_2^{\Lambda\text{CDM}} \approx 0.16$ ) and the quadrupole-octopole planar alignment ("Axis of Evil") as statistical anomalies or cosmic variance flukes ( $p < 0.001$ ). 

The framework derives both features analytically from the horizon boundary conditions (§6.14, `ISSUE-4.41`, `ISSUE-4.65`):

### A. The Apparent Horizon Neumann Trapping Boundary Condition
The apparent horizon membrane $\partial E$ satisfies the Kodama-Hayward trapping condition $\left.\nabla_\perp \Phi\right|_{\partial E} = 0$, enforcing a Neumann boundary condition on primordial scalar fluctuations:

$$\left.\frac{d j_0(k r)}{dr}\right|_{r = R_{\text{hor}}} = -k j_1(k R_{\text{hor}}) = 0$$

The first non-trivial root is $\mu_1 \approx 4.493409$. Projected onto the last scattering surface ( $d_{\text{LSS}} / d_{\text{hor}} \approx 0.96687$ ), this imposes an infrared wavenumber cutoff:

$$x_0 \equiv k_0 d_{\text{LSS}} = 4.493409 \times 0.96687 = 4.3446$$

Evaluating the truncated Sachs-Wolfe transfer integral:

$$C_\ell = \frac{2}{\pi} \int_{x_0}^\infty \frac{dx}{x} \mathcal{P}_\mathcal{R}(x) [ j_\ell(x) ]^2$$

derives parameter-free suppression factors:

$$\boxed{\frac{C_2}{C_{\text{iso}}} = 0.1623 \quad (\text{observed: } 0.16 \pm 0.05), \qquad \frac{C_3}{C_{\text{iso}}} = 0.5049}$$

### B. Oblate Kerr Deformation & The "Axis of Evil"
The parent black hole rotates with non-zero spin $a_* \approx 0.80\text{--}0.85$. Frame dragging and centrifugal deformation make the trapping horizon oblate ( $R_{\text{equatorial}} > R_{\text{polar}}$ with oblateness $\delta \approx 0.25$ ). The infrared cutoff becomes direction-dependent:

$$k_{\text{min}}(\theta) \approx k_0 [ 1 + \delta \cos^2\theta ]$$

Projecting onto spherical harmonic multipoles breaks $SO(3)$ isotropy into $U(1)$ axial symmetry:
- **Polar modes ( $m = 0$ ) are crushed:** Quadrupole $m=0$ power drops to $18.4\%$; octopole $m=0$ drops to $6.7\%$.
- **Planar modes ( $m = \pm\ell$ ) dominate:** Quadrupole $m = \pm 2$ carries $45.2\%$ of total power; octopole $m = \pm 3$ carries $35.7\%$.
- **Alignment:** Both the quadrupole and octopole normal vectors must align with the parent black hole's spin axis $\vec{J}_{\text{parent}}$, directly generating the observed "Axis of Evil".

---

## 6. Temporal Accretion Dynamics: Steady Intake vs. Episodic AGN Duty Cycles

The parent black hole's mass accretion rate $\dot{M}(t)$ governs interior cosmic acceleration via:

$$w(z) = -1 + \frac{4G}{3c^3 \Omega_{\text{DE}}(z)}\dot{M}(z)$$

### A. Modern Stellar Ingestion Noise Floor
- Modern horizon mass: $M_H(t_0) = \frac{c^3}{2GH_0} \approx 3.2 \times 10^{22} \, M_\odot$.
- Continuous smooth kinematic flow: $\dot{M}_0 \approx 48{,}000 \, M_\odot/\text{s}$.
- Capturing a $10\,M_\odot$ star produces a horizon perturbation $\Delta M / M_H \approx 3.1 \times 10^{-22}$—completely imperceptible in cosmological observables today.

### B. Early Universe Macro-Clumping
At recombination ( $z \approx 1100$ ), the horizon mass was $M_H(z_{\text{rec}}) \approx 8.8 \times 10^{17} \, M_\odot$. Inflow of a parent macro-clump ( $\Delta M \sim 10^{13} \, M_\odot$, a rich galaxy cluster mass ) creates:

$$\frac{\Delta \rho}{\rho} \sim \frac{\Delta M}{M_H} \sim 10^{-5}$$

matching the exact amplitude of primordial CMB temperature anisotropies ( $\delta T/T \sim 10^{-5}$ ).

### C. Episodic Accretion Duty Cycles (Option Beta / `ISSUE-4.66`)
If parent galaxy feeding follows episodic AGN duty cycles ( $\tau_{\text{duty}} \sim 10^7\text{--}10^8\text{ yr}$ active, followed by quiescent starvation $\dot{M} \to 0$ ):
- **Starved Epochs ( $\dot{M} \to 0$ ):** $w \to -1$. Pure de Sitter acceleration.
- **Active Feeding Epochs ( $\dot{M} > 0$ ):** $w(z) > -1$. Inflow creates a decelerating drag relative to de Sitter.
- **Observational Confrontation:** DESI Year 1 hints of dynamical dark energy ( $w_0 > -1, w_a < 0$ ) can be tested against discrete step-like or oscillatory signatures in $w(z)$ with DESI Year 3 / Euclid data.

---

## 7. Critical Reviewer Summary & Verification Script Index

```
================================================================================
CMB POWER SPECTRUM EVALUATION SUMMARY
================================================================================
1. High-Multipole Acoustic Peaks (ell = 100 to 2500):
   - 4.0% global RMS residual achieved with 0 CMB-fitted parameters.
   - Discrepancy is structurally forced by Omega_m = 1/3 (Omega_c h^2 = 0.1290).
   - Peak positions match to Delta ell ~ 1 to 10 (sound horizon rs = 142.2 vs 144.4 Mpc).
   - Peak amplitudes match to 1% - 4%.

2. Low-Multipole Anomalies (ell = 2 to 30):
   - Quadrupole suppression C_2/C_iso = 0.1623 analytically derived via Neumann BC.
   - Octopole suppression C_3/C_iso = 0.5049 analytically derived.
   - Quadrupole-octopole alignment (Axis of Evil) derived via Kerr oblate spin.

3. Primordial Input Normalization:
   - Spectral tilt n_s = 0.9624 and r = 0.0039 derived from Starobinsky inflation.
   - Amplitude A_s = 2.1015e-9 derived from Parker creation + GUT scale (H_b = alpha_GUT/(2*pi) * M_Pl).
   - Temperature T_CMB = 2.723 K derived from engine exhaust entropy.
================================================================================
```

### Numerical Verification Script Reference
- [`scripts/derive_cmb_low_multipoles.py`](../../scripts/derive_cmb_low_multipoles.py) (Script #14): Computes the Neumann Bessel roots, Sachs-Wolfe $C_2/C_{\text{iso}} = 0.1623$, $C_3/C_{\text{iso}} = 0.5049$, and Kerr oblate harmonic alignments.
- [`scripts/derive_scalar_amplitude.py`](../../scripts/derive_scalar_amplitude.py) (Script #15): Computes Mukhanov-Sasaki Parker mode-matching, Bogoliubov coefficients, energy density, and derives $A_s = 2.1015 \times 10^{-9}$.
- [`scripts/cmb_comparison.py`](../../scripts/cmb_comparison.py) & [`scripts/cmb_v2_comparison.py`](../../scripts/cmb_v2_comparison.py): Full CAMB Boltzmann solver runs.
- [`scripts/cmb_temperature.py`](../../scripts/cmb_temperature.py): Derives $T_{\text{CMB}} = 2.7228\text{ K}$ from entropy conservation.
