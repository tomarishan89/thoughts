"""
ISSUE-4.59: Derive Omega_b h^2 from ECSK Torsion Baryogenesis
==============================================================

Derivation chain:
  ECSK bounce → Hehl-Datta four-fermion interaction → CP violation ε_CP
  → Sakharov conditions → baryon-to-photon ratio η
  → BBN → Ω_b h²

The ECSK torsion coupling is completely determined by G and c — zero free parameters.
"""


import sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# ============================================================
# Fundamental Constants (SI)
# ============================================================
G     = 6.67430e-11      # m³/(kg·s²)
c     = 2.99792458e8     # m/s
hbar  = 1.054571817e-34  # J·s
k_B   = 1.380649e-23     # J/K

# Planck units
M_P   = np.sqrt(hbar * c / G)              # Planck mass (kg) ≈ 2.176e-8 kg
E_P   = M_P * c**2                          # Planck energy (J) ≈ 1.956e9 J
T_P   = E_P / k_B                           # Planck temperature (K) ≈ 1.416e32 K
t_P   = np.sqrt(hbar * G / c**5)           # Planck time (s) ≈ 5.391e-44 s
rho_P = c**5 / (hbar * G**2)               # Planck density (kg/m³) ≈ 5.155e96 kg/m³

# Conversion: GeV
GeV_to_J  = 1.602176634e-10               # J per GeV
J_to_GeV  = 1.0 / GeV_to_J
E_P_GeV   = E_P * J_to_GeV                # ≈ 1.221e19 GeV
M_P_GeV   = E_P_GeV                        # In natural units, M_P c² = E_P

# Observed values (Planck 2018)
eta_obs       = 6.104e-10                   # baryon-to-photon ratio
Omega_b_h2_obs = 0.02237                    # baryon physical density
H_0           = 67.36                        # km/s/Mpc
h             = H_0 / 100.0

print("=" * 70)
print("ECSK TORSION BARYOGENESIS: Ω_b h² DERIVATION")
print("=" * 70)
print(f"\nPlanck mass:        M_P = {M_P:.4e} kg = {E_P_GeV:.4e} GeV")
print(f"Planck temperature: T_P = {T_P:.4e} K")
print(f"Planck density:     ρ_P = {rho_P:.4e} kg/m³")

# ============================================================
# Step 1: ECSK Torsion Coupling Constant
# ============================================================
# The Hehl-Datta four-fermion interaction Lagrangian:
#   L_torsion = -(3κ²/16) (ψ̄ γ⁵γᵘ ψ)(ψ̄ γ⁵γ_μ ψ)
# where κ² = 8πG/c⁴ (Einstein gravitational coupling)

kappa_sq = 8 * np.pi * G / c**4           # m/(J) = s²/(kg·m)
G_torsion = 3 * kappa_sq / 16              # Four-fermion coupling (m/J)

# In natural units (GeV^-2):
G_torsion_nat = G_torsion * (GeV_to_J) / (hbar * c)  # convert to GeV^-2
# Actually, more directly: G_torsion_nat = 3/(16) * 8π / M_P² (in natural units)
G_torsion_nat2 = 3 * 8 * np.pi / (16 * E_P_GeV**2)

print(f"\n--- Step 1: Torsion Coupling ---")
print(f"κ² = 8πG/c⁴ = {kappa_sq:.4e} s²/(kg·m)")
print(f"G_torsion = 3κ²/16 = {G_torsion:.4e} s²/(kg·m)")
print(f"G_torsion (natural) = {G_torsion_nat2:.4e} GeV⁻²")
print(f"Compare G_Fermi = 1.166e-5 GeV⁻² (Fermi weak coupling)")
print(f"Ratio G_torsion/G_Fermi = {G_torsion_nat2 / 1.166e-5:.4e}")

# ============================================================
# Step 2: CP Violation Parameter from Torsion
# ============================================================
# The Hehl-Datta term contains γ⁵, which makes it parity-violating.
# Under C-conjugation, the axial current changes sign relative to the 
# mass term, creating a matter-antimatter energy splitting:
#   ΔE = G_torsion · n_fermion ≈ G_torsion · T³ (at temperature T)
#
# The CP-violating asymmetry in decays:
#   ε_CP(T) ~ G_torsion · T² = (3π/2) · (T/M_P)²
#
# This is the KEY result: ε_CP is determined entirely by the ratio T/M_P,
# with the coefficient fixed by the torsion coupling.

def epsilon_CP(T_GeV):
    """CP violation parameter from torsion at temperature T (in GeV)."""
    return (3 * np.pi / 2) * (T_GeV / E_P_GeV)**2

# Test at different scales
scales = {
    'Planck (bounce)': E_P_GeV,
    'GUT scale':       1e16,
    'Intermediate':    1e13,
    'Electroweak':     1e2,
}

print(f"\n--- Step 2: CP Violation Parameter ε_CP(T) = (3π/2)(T/M_P)² ---")
for name, T in scales.items():
    print(f"  {name:25s}: T = {T:.1e} GeV → ε_CP = {epsilon_CP(T):.4e}")

# ============================================================
# Step 3: Standard Model g_*(T) — Effective Degrees of Freedom
# ============================================================
# g_* counts the effective number of relativistic species at temperature T.
# Above the GUT scale, all SM fields are relativistic.

def g_star(T_GeV):
    """Standard Model effective relativistic degrees of freedom."""
    # Standard Model values (well-established):
    if T_GeV > 1e3:         # Above EW symmetry breaking (all SM particles)
        return 106.75        # Full Standard Model
    elif T_GeV > 1.0:       # QCD era (quarks + gluons)
        return 61.75         # After EW breaking, before QCD confinement
    elif T_GeV > 0.15:      # Hadron era
        return 17.25         # Pions, muons, electrons, neutrinos, photons
    elif T_GeV > 0.001:     # After muon annihilation
        return 10.75         # Electrons, neutrinos, photons
    elif T_GeV > 5e-4:      # After e+e- annihilation
        return 7.25          
    else:
        return 3.36          # Photons + neutrinos (after e+e-)

print(f"\n--- Step 3: g_*(T) ---")
for name, T in scales.items():
    print(f"  {name:25s}: g_* = {g_star(T):.2f}")

# ============================================================
# Step 4: Washout Factor κ
# ============================================================
# The washout factor depends on the ratio of the baryon-violating 
# interaction rate Γ_B to the Hubble rate H at temperature T:
#   K = Γ_B / H(T)
# 
# If K >> 1: strong washout, κ ~ K^{-1.2} (Buchmuller et al.)
# If K << 1: weak washout, κ ~ 1
# If K ~ 1:  optimal, κ ~ 0.1-0.3
#
# For the torsion mechanism:
#   Γ_torsion ~ G_torsion² · T⁵ (four-fermion interaction rate)
#   H(T) = (π/3)^{1/2} · g_*^{1/2} · T² / M_P (radiation-dominated)

def Hubble_rate(T_GeV):
    """Hubble rate H(T) in GeV (natural units)."""
    g = g_star(T_GeV)
    return np.sqrt(np.pi / 3) * np.sqrt(g) * T_GeV**2 / E_P_GeV

def torsion_interaction_rate(T_GeV):
    """Torsion four-fermion interaction rate Γ_torsion in GeV."""
    # Γ ~ G_torsion² · T⁵ (dimensional analysis for four-fermion)
    return G_torsion_nat2**2 * T_GeV**5

def washout_param_K(T_GeV):
    """Washout parameter K = Γ_torsion / H(T)."""
    return torsion_interaction_rate(T_GeV) / Hubble_rate(T_GeV)

def washout_factor(K):
    """Washout efficiency factor κ(K) — Buchmuller parametrization."""
    if K < 1e-3:
        return 1.0           # Weak washout: maximal efficiency
    elif K > 1e3:
        return 0.3 / K**1.2  # Strong washout
    else:
        return 0.3 * (1.0 + (K / 2.0)**1.2)**(-1)  # Interpolation

print(f"\n--- Step 4: Washout Parameter K = Γ_torsion / H(T) ---")
for name, T in scales.items():
    K = washout_param_K(T)
    kappa = washout_factor(K)
    print(f"  {name:25s}: K = {K:.4e}, κ = {kappa:.4e}")

# ============================================================
# Step 5: Baryon-to-Photon Ratio η(T_baryogenesis)
# ============================================================
# The standard formula:
#   n_B/s ≈ ε_CP · κ / g_*
#   η = n_B/n_γ ≈ 7 · (n_B/s)

def eta_from_torsion(T_baryo_GeV):
    """Compute baryon-to-photon ratio η from ECSK torsion baryogenesis."""
    eps = epsilon_CP(T_baryo_GeV)
    g = g_star(T_baryo_GeV)
    K = washout_param_K(T_baryo_GeV)
    kappa = washout_factor(K)
    n_B_over_s = eps * kappa / g
    eta = 7.04 * n_B_over_s  # s ≈ 7.04 n_γ
    return eta, eps, g, kappa, K

def Omega_b_h2_from_eta(eta):
    """Convert η to Ω_b h² via BBN."""
    # Standard BBN relation: Ω_b h² ≈ 3.65 × 10⁷ η
    return 3.65e7 * eta

print(f"\n--- Step 5: η and Ω_b h² from Torsion Baryogenesis ---")
print(f"{'T_baryo (GeV)':>15s}  {'ε_CP':>12s}  {'g_*':>8s}  {'K':>12s}  {'κ':>12s}  {'η':>12s}  {'Ω_b h²':>12s}  {'Ratio':>8s}")
print("-" * 110)

T_scan = np.logspace(1, 19, 500)  # From 10 GeV to 10^19 GeV
eta_scan = []
Obh2_scan = []

for T in T_scan:
    eta_val, eps, g, kappa, K = eta_from_torsion(T)
    eta_scan.append(eta_val)
    Obh2_scan.append(Omega_b_h2_from_eta(eta_val))

eta_scan = np.array(eta_scan)
Obh2_scan = np.array(Obh2_scan)

# Print key scales
key_temps = [1e2, 1e4, 1e6, 1e8, 1e10, 1e12, 1e14, 1e16, 1e18, 1e19]
for T in key_temps:
    eta_val, eps, g, kappa, K = eta_from_torsion(T)
    Obh2 = Omega_b_h2_from_eta(eta_val)
    ratio = eta_val / eta_obs if eta_val > 0 else 0
    print(f"  {T:>13.1e}  {eps:>12.4e}  {g:>8.2f}  {K:>12.4e}  {kappa:>12.4e}  {eta_val:>12.4e}  {Obh2:>12.4e}  {ratio:>8.2f}")

# ============================================================
# Step 6: Find the baryogenesis temperature that matches observed η
# ============================================================
# Find T where η(T) = η_obs

# Since η(T) is not monotonic (it increases with T from torsion ε_CP 
# but washout also depends on T), find the crossing
print(f"\n--- Step 6: Match to Observed η = {eta_obs:.3e} ---")

# Find where eta_scan is closest to eta_obs
idx_match = np.argmin(np.abs(eta_scan - eta_obs))
T_match = T_scan[idx_match]
eta_match = eta_scan[idx_match]
Obh2_match = Obh2_scan[idx_match]

# More precise: find all crossings
crossings = []
for i in range(len(eta_scan) - 1):
    if eta_scan[i] > 0 and eta_scan[i+1] > 0:
        if (np.log10(eta_scan[i]) - np.log10(eta_obs)) * (np.log10(eta_scan[i+1]) - np.log10(eta_obs)) < 0:
            # Linear interpolation in log-log
            f1 = np.log10(eta_scan[i]) - np.log10(eta_obs)
            f2 = np.log10(eta_scan[i+1]) - np.log10(eta_obs)
            t_cross = 10**(np.log10(T_scan[i]) - f1 * (np.log10(T_scan[i+1]) - np.log10(T_scan[i])) / (f2 - f1))
            crossings.append(t_cross)
            
            eta_c, eps_c, g_c, kappa_c, K_c = eta_from_torsion(t_cross)
            Obh2_c = Omega_b_h2_from_eta(eta_c)
            print(f"  CROSSING at T_baryo = {t_cross:.4e} GeV")
            print(f"    ε_CP = {eps_c:.4e}")
            print(f"    g_*  = {g_c:.2f}")
            print(f"    K    = {K_c:.4e}")
            print(f"    κ    = {kappa_c:.4e}")
            print(f"    η    = {eta_c:.4e} (observed: {eta_obs:.4e})")
            print(f"    Ω_b h² = {Obh2_c:.5f} (observed: {Omega_b_h2_obs:.5f})")
            print(f"    Error = {100*(Obh2_c - Omega_b_h2_obs)/Omega_b_h2_obs:.2f}%")

if not crossings:
    print(f"  No exact crossing found. Closest match:")
    print(f"  T_baryo = {T_match:.4e} GeV, η = {eta_match:.4e}, Ω_b h² = {Obh2_match:.5f}")
    print(f"  Ratio η/η_obs = {eta_match/eta_obs:.4f}")

# ============================================================
# Step 7: Framework Structural Bounds on η
# ============================================================
print(f"\n{'=' * 70}")
print(f"FRAMEWORK STRUCTURAL BOUNDS")
print(f"{'=' * 70}")

# Upper bound: maximal CP violation (ε_CP = 1) with no washout (κ = 1)
# η_max = 7 / g_* 
eta_max_GUT = 7.04 / 106.75
print(f"\n1. UPPER BOUND (ε_CP=1, κ=1):")
print(f"   η_max = 7.04/g_* = {eta_max_GUT:.4e}")
print(f"   This bounds η < 0.066 at any temperature above EW scale")

# Lower bound: η > 0 (Sakharov conditions satisfied at bounce)
print(f"\n2. LOWER BOUND: η > 0 (Sakharov conditions proved in §6.8.2)")

# Structural estimate: torsion coupling gives ε_CP(T) = (3π/2)(T/M_P)²
# The framework-preferred baryogenesis scale is where torsion effects
# are significant but not maximal.
#
# The "natural" scale is where ε_CP · κ / g_* ~ η_obs
# Given ε_CP = (3π/2)(T/M_P)² and κ ~ 1 (weak washout at GUT scale):
# (3π/2)(T/M_P)² / g_* ~ η_obs
# T² ~ η_obs · g_* · M_P² / (3π/2)
# T ~ M_P · sqrt(η_obs · g_* · 2/(3π))

T_natural = E_P_GeV * np.sqrt(eta_obs * 106.75 * 2 / (3 * np.pi))
print(f"\n3. NATURAL BARYOGENESIS SCALE (from torsion ε_CP matching η_obs):")
print(f"   T_baryo = M_P · √(η_obs · g_* · 2/(3π))")
print(f"   T_baryo = {T_natural:.4e} GeV")
print(f"   log₁₀(T_baryo) = {np.log10(T_natural):.2f}")
print(f"   (Compare: GUT scale ~ 10^16 GeV, Intermediate scale ~ 10^13 GeV)")

# Verify
eta_natural, eps_natural, g_natural, kappa_natural, K_natural = eta_from_torsion(T_natural)
Obh2_natural = Omega_b_h2_from_eta(eta_natural)
print(f"\n   Verification at T = {T_natural:.4e} GeV:")
print(f"   ε_CP = {eps_natural:.4e}")
print(f"   κ    = {kappa_natural:.4e}")
print(f"   η    = {eta_natural:.4e}")
print(f"   Ω_b h² = {Obh2_natural:.5f}")

# ============================================================
# Step 8: BBN Constraint on Ω_b h²
# ============================================================
# Standard BBN: Ω_b h² = 3.65 × 10⁷ · η
# For η = 6.1e-10: Ω_b h² = 0.02227
# Planck 2018: Ω_b h² = 0.02237 ± 0.00015

print(f"\n--- Step 8: BBN Conversion ---")
print(f"BBN relation: Ω_b h² = 3.65 × 10⁷ · η")
print(f"For η_obs = {eta_obs:.3e}: Ω_b h² = {Omega_b_h2_from_eta(eta_obs):.5f}")
print(f"Planck 2018:                Ω_b h² = {Omega_b_h2_obs:.5f}")

# ============================================================
# PLOT: η(T_baryo) with observed value
# ============================================================
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 7))

# Left panel: η vs T
ax1.loglog(T_scan, eta_scan, 'b-', linewidth=2, label=r'$\eta(T)$ from ECSK torsion')
ax1.axhline(y=eta_obs, color='r', linestyle='--', linewidth=1.5, label=f'Planck 2018: η = {eta_obs:.2e}')
ax1.axvline(x=1e16, color='gray', linestyle=':', alpha=0.5, label='GUT scale')
ax1.axvline(x=1e2, color='gray', linestyle='-.', alpha=0.5, label='EW scale')
if crossings:
    for tc in crossings:
        ax1.axvline(x=tc, color='green', linestyle='-', alpha=0.7, linewidth=2,
                    label=f'Match: T = {tc:.2e} GeV')
ax1.set_xlabel(r'Baryogenesis Temperature $T$ (GeV)', fontsize=13)
ax1.set_ylabel(r'Baryon-to-photon ratio $\eta$', fontsize=13)
ax1.set_title(r'ECSK Torsion Baryogenesis: $\eta(T_{\mathrm{baryo}})$', fontsize=14)
ax1.set_xlim(1e1, 1e19)
ax1.set_ylim(1e-30, 1e0)
ax1.legend(fontsize=10, loc='lower right')
ax1.grid(True, alpha=0.3)

# Right panel: Ω_b h² vs T
ax2.loglog(T_scan, Obh2_scan, 'b-', linewidth=2, label=r'$\Omega_b h^2(T)$ from ECSK')
ax2.axhline(y=Omega_b_h2_obs, color='r', linestyle='--', linewidth=1.5, 
            label=f'Planck 2018: {Omega_b_h2_obs}')
ax2.axhline(y=Omega_b_h2_obs + 0.00015, color='r', linestyle=':', alpha=0.5)
ax2.axhline(y=Omega_b_h2_obs - 0.00015, color='r', linestyle=':', alpha=0.5)
ax2.axvline(x=1e16, color='gray', linestyle=':', alpha=0.5, label='GUT scale')
if crossings:
    for tc in crossings:
        ax2.axvline(x=tc, color='green', linestyle='-', alpha=0.7, linewidth=2,
                    label=f'Match: T = {tc:.2e} GeV')
ax2.set_xlabel(r'Baryogenesis Temperature $T$ (GeV)', fontsize=13)
ax2.set_ylabel(r'$\Omega_b h^2$', fontsize=13)
ax2.set_title(r'Baryon Physical Density from ECSK Torsion', fontsize=14)
ax2.set_xlim(1e1, 1e19)
ax2.set_ylim(1e-25, 1e1)
ax2.legend(fontsize=10, loc='lower right')
ax2.grid(True, alpha=0.3)

plt.tight_layout()
import os
output_dir = os.environ.get('OUTPUT_DIR', os.path.dirname(os.path.abspath(__file__)))
plt.savefig(os.path.join(output_dir, 'baryogenesis_torsion.png'), dpi=150, bbox_inches='tight')
print(f"\nPlot saved to baryogenesis_torsion.png")

# ============================================================
# Step 9: Summary Assessment
# ============================================================
print(f"\n{'=' * 70}")
print(f"SUMMARY ASSESSMENT")
print(f"{'=' * 70}")
print(f"""
WHAT THE FRAMEWORK DERIVES FROM FIRST PRINCIPLES:
1. ε_CP(T) = (3π/2)(T/M_P)²  — CP violation from torsion coupling
   (zero free parameters: coefficient is 3π/2 from ECSK Lagrangian)

2. If baryogenesis occurs at GUT scale (T ~ 10¹⁶ GeV):
   ε_CP ~ {epsilon_CP(1e16):.4e}

3. With SM g_* = 106.75 and torsion washout:
   η ~ ε_CP · κ / g_*

4. The "natural" baryogenesis temperature that matches η_obs:
   T_baryo ~ {T_natural:.2e} GeV (log₁₀ T = {np.log10(T_natural):.1f})

WHAT REMAINS EXTERNAL:
1. The baryogenesis temperature T_baryo is not uniquely fixed by the 
   framework. It depends on the reheating temperature after inflation,
   which requires the inflationary potential (linked to ISSUE-4.58).

2. The washout factor κ depends on the detailed particle content at 
   T_baryo. For the torsion mechanism, the interaction rate is so weak
   (G_torsion ~ 10⁻³⁸ GeV⁻²) that washout is negligible at all scales
   below Planck — this is actually a clean result.

3. The BBN conversion η → Ω_b h² is standard nuclear physics (not 
   framework-dependent).

BOTTOM LINE:
  η is determined by ε_CP = (3π/2)(T_baryo/M_P)² up to the choice of 
  T_baryo. The framework predicts the FUNCTIONAL FORM of η(T) with zero
  free parameters, but does not uniquely fix T_baryo without the 
  inflationary sector (ISSUE-4.58).
""")
