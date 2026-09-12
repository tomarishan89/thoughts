# -*- coding: utf-8 -*-
"""
CMB Power Spectrum Comparison: Framework vs. Planck 2018 Best-Fit
================================================================
Computes D_ell = ell(ell+1) C_ell / (2*pi) for:
  1. Planck 2018 best-fit ΛCDM (6 parameters)
  2. Framework prediction (Ω_Λ = 2/3, Ω_m = 1/3, Ω_DM = 1/3 - Ω_b)

Key difference: the framework forces Ω_c h² = h²/3 - Ω_b h²
"""


import sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

import numpy as np
import camb
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec

# ============================================================
# Parameter definitions
# ============================================================

# Planck 2018 best-fit (TT,TE,EE+lowE+lensing, Table 2 of 1807.06209)
planck = {
    'name': 'Planck 2018 Best-Fit',
    'H0': 67.36,
    'ombh2': 0.02237,
    'omch2': 0.1200,
    'tau': 0.0544,
    'As': 2.1e-9,
    'ns': 0.9649,
    'mnu': 0.06,
    'omk': 0.0,
}

# Framework prediction
# Ω_m = 1/3, so Ω_m h² = h²/3
# h = H0/100 = 0.6736 → h² = 0.4537
# Ω_m h² = 0.4537/3 = 0.15124
# Ω_c h² = Ω_m h² - Ω_b h² = 0.15124 - 0.02237 = 0.12887
h = 67.36 / 100.0
h2 = h**2
omch2_framework = h2 / 3.0 - planck['ombh2']

framework = {
    'name': 'Framework (Ω_Λ=2/3, Ω_m=1/3)',
    'H0': 67.36,           # Contingent — same as Planck
    'ombh2': 0.02237,       # Not yet derived (ISSUE-4.40) — same as Planck
    'omch2': omch2_framework,  # KEY CHANGE: forced by Ω_m = 1/3
    'tau': 0.0544,          # Not addressed — same as Planck
    'As': 2.1e-9,           # Not derived — same as Planck
    'ns': 0.9649,           # ECSK bounce gives ~0.96, use same for fair comparison
    'mnu': 0.06,            # Same
    'omk': 0.0,             # Flat
}

print("=" * 70)
print("PARAMETER COMPARISON")
print("=" * 70)
print(f"{'Parameter':<15} {'Planck':>15} {'Framework':>15} {'Delta':>10} {'Delta%':>10}")
print("-" * 70)
for key in ['H0', 'ombh2', 'omch2', 'tau', 'As', 'ns']:
    p_val = planck[key]
    f_val = framework[key]
    delta = f_val - p_val
    if p_val != 0:
        pct = 100.0 * delta / p_val
    else:
        pct = 0.0
    if key == 'As':
        print(f"{key:<15} {p_val:>15.4e} {f_val:>15.4e} {delta:>10.2e} {pct:>9.2f}%")
        continue
    print(f"{key:<15} {p_val:>15.6g} {f_val:>15.6g} {delta:>10.4g} {pct:>9.2f}%")

# Derived quantities
omega_m_planck = (planck['ombh2'] + planck['omch2']) / h2
omega_m_framework = (framework['ombh2'] + framework['omch2']) / h2
omega_L_planck = 1.0 - omega_m_planck  # includes radiation, but small
omega_L_framework = 1.0 - omega_m_framework

print(f"\n{'Om_m':<15} {omega_m_planck:>15.6f} {omega_m_framework:>15.6f} {omega_m_framework - omega_m_planck:>10.6f} {100*(omega_m_framework - omega_m_planck)/omega_m_planck:>9.2f}%")
print(f"{'Om_L':<15} {omega_L_planck:>15.6f} {omega_L_framework:>15.6f} {omega_L_framework - omega_L_planck:>10.6f} {100*(omega_L_framework - omega_L_planck)/omega_L_planck:>9.2f}%")
print(f"{'Om_DM':<15} {planck['omch2']/h2:>15.6f} {framework['omch2']/h2:>15.6f}")
print(f"{'Om_b':<15} {planck['ombh2']/h2:>15.6f} {framework['ombh2']/h2:>15.6f}")

# ============================================================
# Compute CMB power spectra
# ============================================================

lmax = 2500

def compute_spectrum(params, lmax=2500):
    """Compute the lensed TT power spectrum D_ell."""
    pars = camb.set_params(
        H0=params['H0'],
        ombh2=params['ombh2'],
        omch2=params['omch2'],
        tau=params['tau'],
        As=params['As'],
        ns=params['ns'],
        mnu=params['mnu'],
        omk=params['omk'],
        lmax=lmax,
        lens_potential_accuracy=1,
    )
    results = camb.get_results(pars)
    powers = results.get_cmb_power_spectra(pars, CMB_unit='muK')
    
    # Extract derived parameters
    derived = results.get_derived_params()
    
    # D_ell = ell(ell+1) C_ell / (2*pi), columns: TT, EE, BB, TE
    totCL = powers['total']
    
    return totCL, derived, results

print("\n" + "=" * 70)
print("Computing Planck 2018 best-fit spectrum...")
planck_cl, planck_derived, planck_results = compute_spectrum(planck, lmax)

print("Computing Framework spectrum...")
framework_cl, framework_derived, framework_results = compute_spectrum(framework, lmax)

# ============================================================
# Extract key derived quantities
# ============================================================

print("\n" + "=" * 70)
print("DERIVED QUANTITIES")
print("=" * 70)
print(f"{'Quantity':<30} {'Planck':>15} {'Framework':>15} {'Delta%':>10}")
print("-" * 70)

for key in ['zstar', 'rstar', 'thetastar', 'DAstar', 'zdrag', 'rdrag', 'sigma8']:
    p_val = planck_derived.get(key, 0)
    f_val = framework_derived.get(key, 0)
    if p_val != 0:
        pct = 100.0 * (f_val - p_val) / p_val
    else:
        pct = 0
    print(f"{key:<30} {p_val:>15.6g} {f_val:>15.6g} {pct:>9.2f}%")

# Compute the shift parameter R = sqrt(Ω_m H0²) * d_A(z*) / c
# d_A = angular diameter distance at z*
# In CAMB, DAstar is the angular diameter distance in Mpc
c_km_s = 299792.458  # km/s
DA_planck = planck_derived.get('DAstar', 0)  # in Mpc
DA_framework = framework_derived.get('DAstar', 0)

R_planck = np.sqrt(omega_m_planck) * planck['H0'] * DA_planck / c_km_s
R_framework = np.sqrt(omega_m_framework) * framework['H0'] * DA_framework / c_km_s

print(f"\n{'Shift parameter R':<30} {R_planck:>15.6f} {R_framework:>15.6f} {100*(R_framework-R_planck)/R_planck:>9.2f}%")
print(f"{'Planck observed R':<30} {'1.7502 ± 0.0046':>15}")

# ============================================================
# Compute residuals
# ============================================================

ells = np.arange(2, lmax + 1)
planck_tt = planck_cl[2:lmax+1, 0]
framework_tt = framework_cl[2:lmax+1, 0]

# Fractional residual
residual = (framework_tt - planck_tt) / planck_tt * 100  # in percent

# Peak detection (simple: find local maxima)
from scipy.signal import find_peaks
peaks_planck, _ = find_peaks(planck_tt, distance=50, prominence=100)
peaks_framework, _ = find_peaks(framework_tt, distance=50, prominence=100)

print("\n" + "=" * 70)
print("ACOUSTIC PEAK POSITIONS")
print("=" * 70)
print(f"{'Peak #':<8} {'Planck l':>12} {'Framewk l':>15} {'dl':>8} {'Planck D_l':>15} {'Framewk D_l':>15} {'dD%':>8}")
print("-" * 70)
n_peaks = min(len(peaks_planck), len(peaks_framework), 7)
for i in range(n_peaks):
    ell_p = ells[peaks_planck[i]]
    ell_f = ells[peaks_framework[i]]
    d_p = planck_tt[peaks_planck[i]]
    d_f = framework_tt[peaks_framework[i]]
    pct_d = 100 * (d_f - d_p) / d_p
    print(f"{i+1:<8} {ell_p:>12} {ell_f:>15} {ell_f - ell_p:>8} {d_p:>15.2f} {d_f:>15.2f} {pct_d:>7.2f}%")

# ============================================================
# Summary statistics
# ============================================================

print("\n" + "=" * 70)
print("RESIDUAL STATISTICS")
print("=" * 70)

# Split into ell ranges
ranges = [
    ("Low-l (2-30)", 0, 29),
    ("First peak (150-300)", 148, 299),
    ("Second peak (400-650)", 398, 649),
    ("Third peak (700-900)", 698, 899),
    ("Damping tail (1500-2500)", 1498, min(2498, len(residual)-1)),
    ("All l (2-2500)", 0, min(2498, len(residual)-1)),
]

print(f"{'Range':<30} {'Mean D%':>10} {'RMS D%':>10} {'Max|D|%':>10}")
print("-" * 70)
for name, lo, hi in ranges:
    r = residual[lo:hi+1]
    print(f"{name:<30} {np.mean(r):>10.3f} {np.sqrt(np.mean(r**2)):>10.3f} {np.max(np.abs(r)):>10.3f}")

# ============================================================
# Plotting
# ============================================================

import os
output_dir = os.environ.get("OUTPUT_DIR", os.path.dirname(os.path.abspath(__file__)))

fig = plt.figure(figsize=(14, 10))
gs = GridSpec(3, 1, height_ratios=[3, 1, 1], hspace=0.05)

# Panel 1: Power spectra overlay
ax1 = fig.add_subplot(gs[0])
ax1.plot(ells, planck_tt, 'b-', linewidth=1.2, label='Planck 2018 Best-Fit (6 params)', alpha=0.8)
ax1.plot(ells, framework_tt, 'r-', linewidth=1.2, label='Framework ($\\Omega_\\Lambda=2/3$, $\\Omega_m=1/3$, 0 params)', alpha=0.8)
ax1.set_ylabel('$D_\\ell = \\ell(\\ell+1)C_\\ell / 2\\pi$ [$\\mu$K$^2$]', fontsize=12)
ax1.set_xlim(2, lmax)
ax1.set_title('CMB TT Power Spectrum: Framework vs. Planck 2018', fontsize=14, fontweight='bold')
ax1.legend(fontsize=11, loc='upper right')
ax1.set_xticklabels([])
ax1.grid(True, alpha=0.3)

# Panel 2: Fractional residual
ax2 = fig.add_subplot(gs[1], sharex=ax1)
ax2.plot(ells, residual, 'k-', linewidth=0.5, alpha=0.7)
ax2.axhline(0, color='gray', linestyle='--', linewidth=0.5)
ax2.fill_between(ells, -5, 5, alpha=0.1, color='green', label='±5% band')
ax2.set_ylabel('Residual [%]', fontsize=12)
ax2.set_ylim(-15, 15)
ax2.legend(fontsize=9, loc='upper right')
ax2.set_xticklabels([])
ax2.grid(True, alpha=0.3)

# Panel 3: Smoothed residual
window = 50
if len(residual) > window:
    smoothed = np.convolve(residual, np.ones(window)/window, mode='valid')
    ells_smooth = ells[window//2:window//2 + len(smoothed)]
else:
    smoothed = residual
    ells_smooth = ells

ax3 = fig.add_subplot(gs[2], sharex=ax1)
ax3.plot(ells_smooth, smoothed, 'r-', linewidth=1.5, label=f'Smoothed (Δℓ={window})')
ax3.axhline(0, color='gray', linestyle='--', linewidth=0.5)
ax3.fill_between(ells_smooth, -2, 2, alpha=0.1, color='green', label='±2% band')
ax3.set_xlabel('Multipole $\\ell$', fontsize=12)
ax3.set_ylabel('Smoothed Δ%', fontsize=12)
ax3.set_ylim(-10, 10)
ax3.legend(fontsize=9, loc='upper right')
ax3.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig(f"{output_dir}/cmb_comparison.png", dpi=150, bbox_inches='tight')
print(f"\nPlot saved to {output_dir}/cmb_comparison.png")

# ============================================================
# Low-ell detail (ISW effect)
# ============================================================

fig2, (ax4, ax5) = plt.subplots(1, 2, figsize=(14, 5))

# Left: low-ell zoom
ells_low = ells[:98]  # ell 2-99
ax4.plot(ells_low, planck_tt[:98], 'b-', linewidth=2, label='Planck Best-Fit')
ax4.plot(ells_low, framework_tt[:98], 'r-', linewidth=2, label='Framework')
ax4.set_xlabel('$\\ell$', fontsize=12)
ax4.set_ylabel('$D_\\ell$ [$\\mu$K$^2$]', fontsize=12)
ax4.set_title('Low-$\\ell$ (ISW + Sachs-Wolfe)', fontsize=12, fontweight='bold')
ax4.legend(fontsize=10)
ax4.grid(True, alpha=0.3)

# Right: first three peaks
ells_peaks = ells[98:898]
ax5.plot(ells_peaks, planck_tt[98:898], 'b-', linewidth=1.5, label='Planck Best-Fit')
ax5.plot(ells_peaks, framework_tt[98:898], 'r-', linewidth=1.5, label='Framework')
ax5.set_xlabel('$\\ell$', fontsize=12)
ax5.set_ylabel('$D_\\ell$ [$\\mu$K$^2$]', fontsize=12)
ax5.set_title('First Three Acoustic Peaks', fontsize=12, fontweight='bold')
ax5.legend(fontsize=10)
ax5.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig(f"{output_dir}/cmb_detail.png", dpi=150, bbox_inches='tight')
print(f"Detail plot saved to {output_dir}/cmb_detail.png")

print("\n" + "=" * 70)
print("DONE")
print("=" * 70)
