# -*- coding: utf-8 -*-
"""
ISSUE-4.57: CMB Residual with Framework-Derived Omega_b h^2
============================================================
Three models compared:
  1. Planck 2018 best-fit (6-param LCDM)
  2. Framework v1: Omega_m=1/3, Omega_b h^2 = 0.02237 (Planck value)
  3. Framework v2: Omega_m=1/3, Omega_b h^2 = 0.02228 (derived from torsion baryogenesis, section 6.8.4)

Key question: Does using the framework's own Omega_b h^2 = 0.02228
improve or worsen the 4.0% RMS residual?
"""


import sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

import numpy as np
import camb
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
from scipy.signal import find_peaks

import os
output_dir = os.environ.get("OUTPUT_DIR", os.path.dirname(os.path.abspath(__file__)))

# ============================================================
# Parameter sets
# ============================================================

h = 67.36 / 100.0
h2 = h**2

# 1. Planck 2018 best-fit
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

# 2. Framework v1: Omega_m = 1/3, but Omega_b h^2 borrowed from Planck
ombh2_planck = 0.02237
framework_v1 = {
    'name': 'Framework v1 (Planck Ob)',
    'H0': 67.36,
    'ombh2': ombh2_planck,
    'omch2': h2 / 3.0 - ombh2_planck,  # = 0.12887
    'tau': 0.0544,
    'As': 2.1e-9,
    'ns': 0.9649,
    'mnu': 0.06,
    'omk': 0.0,
}

# 3. Framework v2: Omega_m = 1/3, Omega_b h^2 = 0.02228 (derived from torsion baryogenesis)
ombh2_derived = 0.02228
framework_v2 = {
    'name': 'Framework v2 (Derived Ob)',
    'H0': 67.36,
    'ombh2': ombh2_derived,
    'omch2': h2 / 3.0 - ombh2_derived,  # = 0.12896
    'tau': 0.0544,
    'As': 2.1e-9,
    'ns': 0.9649,
    'mnu': 0.06,
    'omk': 0.0,
}

models = [planck, framework_v1, framework_v2]

print("=" * 90)
print("PARAMETER COMPARISON: THREE MODELS")
print("=" * 90)
print(f"{'Parameter':<15} {'Planck':<15} {'Framework v1':<15} {'Framework v2':<15} {'v1-Planck':<12} {'v2-Planck':<12}")
print("-" * 90)
for key in ['H0', 'ombh2', 'omch2', 'tau', 'ns']:
    p = planck[key]; v1 = framework_v1[key]; v2 = framework_v2[key]
    d1 = 100*(v1-p)/p if p != 0 else 0
    d2 = 100*(v2-p)/p if p != 0 else 0
    print(f"{key:<15} {p:<15.6g} {v1:<15.6g} {v2:<15.6g} {d1:<+11.3f}% {d2:<+11.3f}%")

# Derived Omega_m
for m in models:
    m['Om_m'] = (m['ombh2'] + m['omch2']) / h2
    m['Om_L'] = 1.0 - m['Om_m']
    m['Om_b'] = m['ombh2'] / h2
    m['Om_DM'] = m['omch2'] / h2

print(f"\n{'Omega_m':<15} {planck['Om_m']:<15.6f} {framework_v1['Om_m']:<15.6f} {framework_v2['Om_m']:<15.6f}")
print(f"{'Omega_Lambda':<15} {planck['Om_L']:<15.6f} {framework_v1['Om_L']:<15.6f} {framework_v2['Om_L']:<15.6f}")
print(f"{'Omega_b':<15} {planck['Om_b']:<15.6f} {framework_v1['Om_b']:<15.6f} {framework_v2['Om_b']:<15.6f}")
print(f"{'Omega_DM':<15} {planck['Om_DM']:<15.6f} {framework_v1['Om_DM']:<15.6f} {framework_v2['Om_DM']:<15.6f}")

# ============================================================
# Compute spectra
# ============================================================

lmax = 2500

def compute_spectrum(params, lmax=2500):
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
    derived = results.get_derived_params()
    return powers['total'], derived, results

results_all = {}
for m in models:
    print(f"\nComputing {m['name']}...")
    cl, derived, res = compute_spectrum(m, lmax)
    results_all[m['name']] = {'cl': cl, 'derived': derived, 'results': res}

ells = np.arange(2, lmax + 1)

# ============================================================
# Derived quantities comparison
# ============================================================

print("\n" + "=" * 90)
print("DERIVED QUANTITIES")
print("=" * 90)
print(f"{'Quantity':<20} {'Planck':<15} {'Framework v1':<15} {'Framework v2':<15} {'dv1%':<10} {'dv2%':<10}")
print("-" * 90)

for key in ['zstar', 'rstar', 'thetastar', 'DAstar', 'zdrag', 'rdrag', 'sigma8']:
    p = results_all[planck['name']]['derived'].get(key, 0)
    v1 = results_all[framework_v1['name']]['derived'].get(key, 0)
    v2 = results_all[framework_v2['name']]['derived'].get(key, 0)
    dp1 = 100*(v1-p)/p if p != 0 else 0
    dp2 = 100*(v2-p)/p if p != 0 else 0
    print(f"{key:<20} {p:<15.6g} {v1:<15.6g} {v2:<15.6g} {dp1:<+9.3f}% {dp2:<+9.3f}%")

# ============================================================
# Acoustic peaks
# ============================================================

planck_tt = results_all[planck['name']]['cl'][2:lmax+1, 0]
v1_tt = results_all[framework_v1['name']]['cl'][2:lmax+1, 0]
v2_tt = results_all[framework_v2['name']]['cl'][2:lmax+1, 0]

peaks_p, _ = find_peaks(planck_tt, distance=50, prominence=100)
peaks_v1, _ = find_peaks(v1_tt, distance=50, prominence=100)
peaks_v2, _ = find_peaks(v2_tt, distance=50, prominence=100)

print("\n" + "=" * 90)
print("ACOUSTIC PEAK COMPARISON")
print("=" * 90)
print(f"{'Peak':<6} {'Planck l':<10} {'v1 l':<10} {'v2 l':<10} {'Planck D_l':<12} {'v1 D_l':<12} {'v2 D_l':<12} {'dv1%':<8} {'dv2%':<8}")
print("-" * 90)

n_peaks = min(len(peaks_p), len(peaks_v1), len(peaks_v2), 7)
for i in range(n_peaks):
    lp = ells[peaks_p[i]]; lv1 = ells[peaks_v1[i]]; lv2 = ells[peaks_v2[i]]
    dp = planck_tt[peaks_p[i]]; dv1 = v1_tt[peaks_v1[i]]; dv2 = v2_tt[peaks_v2[i]]
    pct1 = 100*(dv1-dp)/dp; pct2 = 100*(dv2-dp)/dp
    print(f"{i+1:<6} {lp:<10} {lv1:<10} {lv2:<10} {dp:<12.1f} {dv1:<12.1f} {dv2:<12.1f} {pct1:<+7.2f}% {pct2:<+7.2f}%")

# ============================================================
# Residual statistics
# ============================================================

res_v1 = (v1_tt - planck_tt) / planck_tt * 100
res_v2 = (v2_tt - planck_tt) / planck_tt * 100

print("\n" + "=" * 90)
print("RESIDUAL STATISTICS vs. PLANCK BEST-FIT")
print("=" * 90)

ranges = [
    ("Low-l (2-30)", 0, 29),
    ("First peak (150-300)", 148, 299),
    ("Second peak (400-650)", 398, 649),
    ("Third peak (700-900)", 698, 899),
    ("Damping tail (1500-2500)", 1498, min(2498, len(res_v1)-1)),
    ("All l (2-2500)", 0, min(2498, len(res_v1)-1)),
]

print(f"\n{'Range':<30} {'--- Framework v1 ---':<35} {'--- Framework v2 (derived) ---'}")
print(f"{'':30} {'Mean%':<10} {'RMS%':<10} {'Max|D|%':<10} {'Mean%':<10} {'RMS%':<10} {'Max|D|%':<10}")
print("-" * 110)

for name, lo, hi in ranges:
    r1 = res_v1[lo:hi+1]; r2 = res_v2[lo:hi+1]
    print(f"{name:<30} {np.mean(r1):<+10.3f} {np.sqrt(np.mean(r1**2)):<10.3f} {np.max(np.abs(r1)):<10.3f} "
          f"{np.mean(r2):<+10.3f} {np.sqrt(np.mean(r2**2)):<10.3f} {np.max(np.abs(r2)):<10.3f}")

# Improvement metric
rms_v1_all = np.sqrt(np.mean(res_v1**2))
rms_v2_all = np.sqrt(np.mean(res_v2**2))
print(f"\n{'OVERALL RMS RESIDUAL:':<30} {rms_v1_all:<10.4f}% {'':>25} {rms_v2_all:<10.4f}%")
print(f"{'CHANGE v2 vs v1:':<30} {100*(rms_v2_all - rms_v1_all)/rms_v1_all:<+.3f}%")
if rms_v2_all < rms_v1_all:
    print(">>> Framework v2 (derived Ob) IMPROVES the CMB fit <<<")
else:
    print(">>> Framework v2 (derived Ob) WORSENS the CMB fit <<<")

# ============================================================
# Odd/Even peak ratio (baryon loading test)
# ============================================================

print("\n" + "=" * 90)
print("ODD/EVEN PEAK RATIO (Baryon Loading Test)")
print("=" * 90)
print("The odd/even peak ratio R_{1/2} = D_l(peak1)/D_l(peak2) is sensitive to Omega_b h^2")
print("Higher Omega_b h^2 -> stronger odd-peak enhancement -> larger R_{1/2}")

if n_peaks >= 4:
    for m, tt, peaks in [
        ('Planck', planck_tt, peaks_p),
        ('v1', v1_tt, peaks_v1),
        ('v2', v2_tt, peaks_v2),
    ]:
        r12 = tt[peaks[0]] / tt[peaks[1]]
        r13 = tt[peaks[0]] / tt[peaks[2]]
        r23 = tt[peaks[2]] / tt[peaks[1]]
        r34 = tt[peaks[2]] / tt[peaks[3]]
        print(f"  {m:<15}: R_{{1/2}} = {r12:.4f}, R_{{1/3}} = {r13:.4f}, R_{{3/2}} = {r23:.4f}, R_{{3/4}} = {r34:.4f}")

# ============================================================
# Plotting
# ============================================================

fig = plt.figure(figsize=(16, 12))
gs = GridSpec(3, 1, height_ratios=[3, 1, 1], hspace=0.05)

# Panel 1: Power spectra
ax1 = fig.add_subplot(gs[0])
ax1.plot(ells, planck_tt, 'b-', lw=1.2, label='Planck 2018 (6 params)', alpha=0.8)
ax1.plot(ells, v1_tt, 'r--', lw=1.0, label=f'Framework v1 ($\\Omega_b h^2$={ombh2_planck}, borrowed)', alpha=0.7)
ax1.plot(ells, v2_tt, 'g-', lw=1.2, label=f'Framework v2 ($\\Omega_b h^2$={ombh2_derived}, derived)', alpha=0.8)
ax1.set_ylabel('$D_\\ell$ [$\\mu$K$^2$]', fontsize=12)
ax1.set_xlim(2, lmax)
ax1.set_title('CMB TT Power Spectrum: Effect of Framework-Derived $\\Omega_b h^2$', fontsize=14, fontweight='bold')
ax1.legend(fontsize=10, loc='upper right')
ax1.set_xticklabels([])
ax1.grid(True, alpha=0.3)

# Panel 2: v1 residual
ax2 = fig.add_subplot(gs[1], sharex=ax1)
ax2.plot(ells, res_v1, color='red', lw=0.5, alpha=0.5, label=f'v1 (RMS={rms_v1_all:.3f}%)')
ax2.plot(ells, res_v2, color='green', lw=0.5, alpha=0.7, label=f'v2 (RMS={rms_v2_all:.3f}%)')
ax2.axhline(0, color='gray', ls='--', lw=0.5)
ax2.fill_between(ells, -5, 5, alpha=0.08, color='blue')
ax2.set_ylabel('Residual [%]', fontsize=11)
ax2.set_ylim(-15, 15)
ax2.legend(fontsize=9, loc='upper right')
ax2.set_xticklabels([])
ax2.grid(True, alpha=0.3)

# Panel 3: Smoothed residuals
window = 50
s_v1 = np.convolve(res_v1, np.ones(window)/window, mode='valid')
s_v2 = np.convolve(res_v2, np.ones(window)/window, mode='valid')
ells_s = ells[window//2:window//2+len(s_v1)]

ax3 = fig.add_subplot(gs[2], sharex=ax1)
ax3.plot(ells_s, s_v1, 'r-', lw=1.5, alpha=0.7, label='v1 smoothed')
ax3.plot(ells_s, s_v2, 'g-', lw=1.5, alpha=0.9, label='v2 smoothed')
ax3.axhline(0, color='gray', ls='--', lw=0.5)
ax3.fill_between(ells_s, -2, 2, alpha=0.08, color='blue')
ax3.set_xlabel('Multipole $\\ell$', fontsize=12)
ax3.set_ylabel('Smoothed $\\Delta$%', fontsize=11)
ax3.set_ylim(-10, 10)
ax3.legend(fontsize=9, loc='upper right')
ax3.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig(f"{output_dir}/cmb_v2_comparison.png", dpi=150, bbox_inches='tight')
print(f"\nPlot saved to {output_dir}/cmb_v2_comparison.png")

# Detail: peak region
fig2, axes = plt.subplots(1, 3, figsize=(18, 5))

# Low-ell
ax = axes[0]
ax.plot(ells[:98], planck_tt[:98], 'b-', lw=2, label='Planck')
ax.plot(ells[:98], v1_tt[:98], 'r--', lw=1.5, label='v1')
ax.plot(ells[:98], v2_tt[:98], 'g-', lw=2, label='v2 (derived)')
ax.set_title('Low-$\\ell$ (ISW + SW)', fontweight='bold')
ax.set_xlabel('$\\ell$'); ax.set_ylabel('$D_\\ell$ [$\\mu$K$^2$]')
ax.legend(fontsize=9); ax.grid(True, alpha=0.3)

# First three peaks
ax = axes[1]
ax.plot(ells[98:898], planck_tt[98:898], 'b-', lw=1.5, label='Planck')
ax.plot(ells[98:898], v1_tt[98:898], 'r--', lw=1, label='v1')
ax.plot(ells[98:898], v2_tt[98:898], 'g-', lw=1.5, label='v2 (derived)')
ax.set_title('Acoustic Peaks 1-3', fontweight='bold')
ax.set_xlabel('$\\ell$'); ax.set_ylabel('$D_\\ell$ [$\\mu$K$^2$]')
ax.legend(fontsize=9); ax.grid(True, alpha=0.3)

# Damping tail
ax = axes[2]
ax.plot(ells[998:], planck_tt[998:], 'b-', lw=1.5, label='Planck')
ax.plot(ells[998:], v1_tt[998:], 'r--', lw=1, label='v1')
ax.plot(ells[998:], v2_tt[998:], 'g-', lw=1.5, label='v2 (derived)')
ax.set_title('Damping Tail ($\\ell > 1000$)', fontweight='bold')
ax.set_xlabel('$\\ell$'); ax.set_ylabel('$D_\\ell$ [$\\mu$K$^2$]')
ax.legend(fontsize=9); ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig(f"{output_dir}/cmb_v2_detail.png", dpi=150, bbox_inches='tight')
print(f"Detail plot saved to {output_dir}/cmb_v2_detail.png")

print("\n" + "=" * 90)
print("DONE")
print("=" * 90)
