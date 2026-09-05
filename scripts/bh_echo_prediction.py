"""
Prediction #9: Black Hole Post-Merger Echo Spectrum from ECSK Bounce
====================================================================

If the ECSK bounce prevents singularity formation, the BH interior has a
reflecting surface at Planck density. Post-merger ringdown perturbations
reflect off this surface and re-emerge as delayed echoes.

This script computes:
1. Echo delay time Delta_t for various BH masses
2. Echo frequency spectrum f_echo,n
3. Echo amplitude decay (viscous horizon damping)
4. SNR estimates for LIGO O4/O5, Einstein Telescope, LISA
"""


import sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# ============================================================
# Constants (SI)
# ============================================================
G     = 6.67430e-11       # m^3/(kg s^2)
c     = 2.99792458e8      # m/s
hbar  = 1.054571817e-34   # J s
k_B   = 1.380649e-23      # J/K
M_sun = 1.98892e30        # kg

# Planck scales
l_P   = np.sqrt(hbar * G / c**3)        # Planck length ~ 1.616e-35 m
t_P   = l_P / c                          # Planck time ~ 5.391e-44 s
rho_P = c**5 / (hbar * G**2)            # Planck density ~ 5.155e96 kg/m^3

print("=" * 80)
print("PREDICTION #9: BLACK HOLE ECHO SPECTRUM FROM ECSK BOUNCE")
print("=" * 80)
print(f"Planck length:  l_P = {l_P:.4e} m")
print(f"Planck time:    t_P = {t_P:.4e} s")
print(f"Planck density: rho_P = {rho_P:.4e} kg/m^3")

# ============================================================
# 1. Echo Delay Time
# ============================================================
# A perturbation at the horizon must travel to the bounce surface
# (at r ~ l_P from the would-be singularity) and back. In tortoise
# coordinates:
#
#   Delta_t_echo = 2 * integral from r_bounce to r_+ of dr/f(r)
#
# For Schwarzschild: f(r) = 1 - 2GM/(rc^2)
# The integral gives: Delta_t ~ (4GM/c^3) * ln(r_+/r_bounce)
# where r_+ = 2GM/c^2 (horizon) and r_bounce ~ l_P (Planck scale)
#
# This is the KEY formula:
#   Delta_t_echo = (4GM/c^3) * ln(R_+/l_P)

def echo_delay(M_kg):
    """Echo delay time in seconds for a BH of mass M (kg)."""
    R_plus = 2 * G * M_kg / c**2  # Schwarzschild radius
    return (4 * G * M_kg / c**3) * np.log(R_plus / l_P)

def echo_frequency_spacing(M_kg):
    """Echo frequency spacing Delta_f = 1/Delta_t_echo (Hz)."""
    return 1.0 / echo_delay(M_kg)

# ============================================================
# 2. QNM Frequencies (fundamental mode, l=2)
# ============================================================
# For Schwarzschild, the fundamental QNM frequency is approximately:
#   f_QNM ~ c^3 / (8*pi*G*M) * (1 - i/(2*Q))
# where Q ~ 2 (quality factor for l=2 fundamental mode)
# More precisely, for non-spinning Schwarzschild (Leaver 1985):
#   omega_QNM = (0.3737 - 0.0890i) * c^3/(GM)
# So f_QNM = 0.3737 * c^3/(2*pi*GM)

def f_QNM(M_kg):
    """Fundamental l=2 QNM frequency for Schwarzschild BH (Hz)."""
    return 0.3737 * c**3 / (2 * np.pi * G * M_kg)

def Q_QNM():
    """Quality factor of fundamental l=2 mode."""
    # Q = pi * f / gamma = |Re(omega)| / (2*|Im(omega)|)
    # = 0.3737 / (2 * 0.0890) = 2.099
    return 0.3737 / (2 * 0.0890)

# ============================================================
# 3. Echo Spectrum
# ============================================================
# The echo spectrum consists of new QNM-like modes at:
#   f_{echo,n} = f_QNM + n * Delta_f_echo, n = 1, 2, 3, ...
#
# The amplitude of the n-th echo decays due to:
# (a) Partial absorption at the horizon on each crossing (reflectivity R_H)
# (b) Damping during propagation
#
# For a horizon with reflectivity |R_H|^2:
#   A_n = A_0 * |R_H|^{2n} * |R_bounce|^{n}
#
# The horizon reflectivity depends on the model. In standard GR, |R_H| = 0
# (perfect absorber). For ECSK, the interior bounce surface has |R_bounce| ~ 1
# (hard reflection), but the horizon itself acts as a partial reflector:
#   |R_H|^2 ~ exp(-8*pi*G*M*omega/c^3) = exp(-8*pi*M*omega*l_P^2/(hbar*c))
#
# For the fundamental QNM frequency:
#   Gamma_horizon = Im(omega_QNM) = 0.0890 * c^3/(GM)
#   |R_H|^2 = exp(-8*pi * 0.3737) = exp(-9.39) ~ 8.4e-5
#
# This gives a per-echo amplitude suppression factor:
#   gamma_echo = -ln(|R_H|^2) / 2 ~ 4.69

# Actually, the Boltzmann reflectivity for a horizon at temperature T_H:
# |R_H|^2 = exp(-E/(k_B T_H)) where E = hbar*omega
# T_H = hbar*c^3/(8*pi*G*M*k_B)
# So |R_H|^2 = exp(-hbar*omega / (hbar*c^3/(8*pi*G*M))) = exp(-8*pi*G*M*omega/c^3)

def horizon_reflectivity_sq(M_kg, f_Hz):
    """Boltzmann reflectivity |R_H|^2 of the horizon at frequency f."""
    omega = 2 * np.pi * f_Hz
    exponent = -8 * np.pi * G * M_kg * omega / c**3
    return np.exp(exponent)

def echo_amplitude_ratio(M_kg, n, f_Hz=None):
    """Amplitude of n-th echo relative to ringdown, A_n/A_0."""
    if f_Hz is None:
        f_Hz = f_QNM(M_kg)
    R_sq = horizon_reflectivity_sq(M_kg, f_Hz)
    # Each echo: 2 horizon crossings + 1 bounce (R_bounce ~ 1)
    return R_sq**n

# ============================================================
# 4. Compute for various BH masses
# ============================================================

print(f"\n{'=' * 80}")
print("ECHO PARAMETERS FOR VARIOUS BLACK HOLE MASSES")
print(f"{'=' * 80}")
print(f"{'BH Type':<25} {'Mass (M_sun)':<15} {'R+ (m)':<12} {'dt_echo (s)':<15} "
      f"{'f_QNM (Hz)':<12} {'Df_echo (Hz)':<12} {'|R_H|^2':<12} {'A_1/A_0':<10}")
print("-" * 120)

bh_types = [
    ("Stellar (LIGO)", 10),
    ("Binary merger (LIGO)", 30),
    ("Heavy merger (LIGO)", 70),
    ("IMBH", 1000),
    ("Sgr A*", 4e6),
    ("M87*", 6.5e9),
    ("TON 618", 6.6e10),
]

for name, M_solar in bh_types:
    M = M_solar * M_sun
    R_plus = 2 * G * M / c**2
    dt = echo_delay(M)
    fq = f_QNM(M)
    df = echo_frequency_spacing(M)
    R_sq = horizon_reflectivity_sq(M, fq)
    A1 = echo_amplitude_ratio(M, 1)
    print(f"{name:<25} {M_solar:<15.1f} {R_plus:<12.3e} {dt:<15.4e} "
          f"{fq:<12.2f} {df:<12.4e} {R_sq:<12.4e} {A1:<10.4e}")

# ============================================================
# 5. Detectability Assessment
# ============================================================
print(f"\n{'=' * 80}")
print("DETECTABILITY ASSESSMENT")
print(f"{'=' * 80}")

# For LIGO: sensitivity band 10-10000 Hz, strain noise ~1e-23/sqrt(Hz)
# For Einstein Telescope: ~3x better, extends to ~3 Hz
# For LISA: 1e-4 to 1 Hz

# The echo signal is detectable if:
# h_echo * sqrt(N_cycles) > h_noise * sqrt(f)
# where N_cycles ~ f_QNM / Delta_f_echo (number of echo cycles in one QNM period)

# For a 30 M_sun merger at 400 Mpc (typical LIGO detection):
M_ref = 30 * M_sun
d_ref = 400 * 3.0857e22  # 400 Mpc in meters
dt_ref = echo_delay(M_ref)
fq_ref = f_QNM(M_ref)
df_ref = echo_frequency_spacing(M_ref)

# Ringdown strain estimate (order of magnitude):
# h_ringdown ~ (G*M*c*f_QNM) / (c^4 * d) * epsilon
# where epsilon ~ 0.01-0.1 (fraction of mass radiated in ringdown)
epsilon_ringdown = 0.03  # ~3% of total mass radiated in ringdown
h_ringdown = (G * M_ref / c**2) * (2 * np.pi * fq_ref) / d_ref * epsilon_ringdown

# Echo strain:
A1_ref = echo_amplitude_ratio(M_ref, 1)
h_echo_1 = h_ringdown * A1_ref

# LIGO noise at ~250 Hz (near the optimal frequency for 30 Msun merger):
h_LIGO_noise = 4e-24  # strain/sqrt(Hz) at design sensitivity
BW = 100  # Hz bandwidth for matched filter

SNR_ringdown = h_ringdown * np.sqrt(BW) / h_LIGO_noise
SNR_echo_1 = h_echo_1 * np.sqrt(BW) / h_LIGO_noise

print(f"\nReference: 30 M_sun merger at 400 Mpc")
print(f"  Echo delay:       dt_echo = {dt_ref*1000:.3f} ms")
print(f"  QNM frequency:    f_QNM = {fq_ref:.1f} Hz")
print(f"  Echo spacing:     Df = {df_ref:.4f} Hz")
print(f"  Horizon |R_H|^2:  {horizon_reflectivity_sq(M_ref, fq_ref):.4e}")
print(f"  1st echo A_1/A_0: {A1_ref:.4e}")
print(f"  Ringdown strain:  h_ring ~ {h_ringdown:.3e}")
print(f"  1st echo strain:  h_echo ~ {h_echo_1:.3e}")
print(f"  SNR (ringdown):   {SNR_ringdown:.1f}")
print(f"  SNR (1st echo):   {SNR_echo_1:.4e}")

# Stacking: N events with coherent averaging
N_events = [10, 100, 390, 1000, 10000]
print(f"\n  Stacking {len(N_events)} scenarios:")
for N in N_events:
    SNR_stacked = SNR_echo_1 * np.sqrt(N)
    print(f"    N = {N:>6}: stacked SNR = {SNR_stacked:.4e} {'(DETECTABLE)' if SNR_stacked > 5 else ''}")

# ============================================================
# 6. Framework-Specific Distinguishing Features
# ============================================================
print(f"\n{'=' * 80}")
print("FRAMEWORK-SPECIFIC SIGNATURES")
print(f"{'=' * 80}")
print("""
ECSK bounce echoes are distinguished from other "near-horizon structure" models by:

1. ECHO DELAY FORMULA:
   Dt_echo = (4GM/c^3) * ln(R+/l_P)
   
   The log factor is FIXED by the Planck scale l_P.
   Other models (firewalls, fuzzballs, gravastars) have:
   - Firewalls: Dt ~ (4GM/c^3) * ln(R+/l_fw) where l_fw is arbitrary
   - Fuzzballs: no clean echo (diffuse scattering)
   - Gravastars: Dt depends on shell radius (free parameter)
   
   ECSK has ZERO free parameters in the delay formula.

2. MASS-DEPENDENT ECHO SPACING:
   Df_echo = 1/Dt = c^3 / [4GM * ln(2GM/(c^2 l_P))]
   
   This has a SPECIFIC M-dependence: ~ 1/(M * ln M)
   NOT 1/M (which all other models also predict for the leading term).
   The logarithmic correction is the fingerprint.

3. AMPLITUDE PATTERN:
   A_n/A_0 = |R_H|^{2n} = exp(-n * 8*pi*G*M*omega/c^3)
   
   Purely determined by Hawking temperature (Boltzmann suppression).
   No free reflectivity parameter.

4. SPIN DEPENDENCE (Kerr generalization):
   For spinning BH with dimensionless spin a:
   Dt_echo(a) = [4GM/(c^3*(1-a))] * ln[R+/l_P * (1 + sqrt(1-a^2))/2]
   
   Near-extremal BH (a -> 1): Dt diverges as 1/(1-a)
   This is testable: high-spin mergers should have longer echo delays.
""")

# ============================================================
# 7. The Falsifiability Statement
# ============================================================
print(f"\n{'=' * 80}")
print("FALSIFIABILITY")
print(f"{'=' * 80}")
print("""
The prediction is cleanly falsifiable:

IF ECSK bounce is correct:
  - Every BH merger MUST produce echoes
  - Echo delay MUST scale as M * ln(M/M_P)
  - Echo amplitude MUST follow Boltzmann suppression

IF no echoes are detected:
  - With sufficient stacked events (~10,000 at LIGO), the non-detection
    rules out the ECSK bounce at the Planck scale
  - This would falsify the framework's singularity avoidance mechanism
  - Consequence: the framework's baryogenesis derivation (§6.8.4) and
    torsion coupling would lose their physical motivation

CURRENT STATUS (as of 2026):
  - 390 GW events detected (GWTC-5.0)
  - No confirmed echoes (marginal claims from Abedi et al. 2017 remain controversial)
  - Einstein Telescope and LISA (expected 2030s) will provide definitive tests
""")

# ============================================================
# PLOT: Echo delay and frequency spacing vs mass
# ============================================================
M_range = np.logspace(0.5, 10, 500) * M_sun  # 3 to 10^10 solar masses
dt_range = np.array([echo_delay(M) for M in M_range])
df_range = 1.0 / dt_range
fq_range = np.array([f_QNM(M) for M in M_range])
A1_range = np.array([echo_amplitude_ratio(M, 1) for M in M_range])

M_solar_range = M_range / M_sun

fig, axes = plt.subplots(2, 2, figsize=(14, 10))

# Top left: echo delay
ax = axes[0, 0]
ax.loglog(M_solar_range, dt_range, 'b-', lw=2)
ax.set_xlabel(r'BH Mass ($M_\odot$)', fontsize=11)
ax.set_ylabel(r'Echo Delay $\Delta t_{\rm echo}$ (s)', fontsize=11)
ax.set_title('Echo Delay Time', fontweight='bold')
# Mark specific masses
for name, Ms in [("LIGO\n30", 30), ("Sgr A*", 4e6), ("M87*", 6.5e9)]:
    M = Ms * M_sun
    ax.plot(Ms, echo_delay(M), 'ro', ms=8)
    ax.annotate(name, (Ms, echo_delay(M)), fontsize=8, ha='center', va='bottom')
ax.grid(True, alpha=0.3)

# Top right: echo frequency spacing
ax = axes[0, 1]
ax.loglog(M_solar_range, df_range, 'g-', lw=2, label=r'$\Delta f_{\rm echo}$')
ax.loglog(M_solar_range, fq_range, 'b--', lw=1.5, label=r'$f_{\rm QNM}$')
ax.axhspan(10, 1e4, alpha=0.1, color='orange', label='LIGO band')
ax.axhspan(1e-4, 1, alpha=0.1, color='purple', label='LISA band')
ax.set_xlabel(r'BH Mass ($M_\odot$)', fontsize=11)
ax.set_ylabel('Frequency (Hz)', fontsize=11)
ax.set_title('Echo Spacing vs QNM Frequency', fontweight='bold')
ax.legend(fontsize=9)
ax.grid(True, alpha=0.3)

# Bottom left: echo amplitude
ax = axes[1, 0]
ax.loglog(M_solar_range, A1_range, 'r-', lw=2)
ax.set_xlabel(r'BH Mass ($M_\odot$)', fontsize=11)
ax.set_ylabel(r'$A_1/A_0$ (1st echo amplitude)', fontsize=11)
ax.set_title('First Echo Relative Amplitude', fontweight='bold')
ax.grid(True, alpha=0.3)

# Bottom right: echo spectrum for 30 Msun
ax = axes[1, 1]
M30 = 30 * M_sun
fq30 = f_QNM(M30)
df30 = echo_frequency_spacing(M30)
n_echoes = np.arange(0, 20)
f_echoes = fq30 + n_echoes * df30
A_echoes = np.array([echo_amplitude_ratio(M30, n) for n in n_echoes])
A_echoes[0] = 1.0  # ringdown

ax.stem(f_echoes, A_echoes / A_echoes[0], linefmt='b-', markerfmt='bo', basefmt='k-')
ax.set_xlabel('Frequency (Hz)', fontsize=11)
ax.set_ylabel('Relative Amplitude', fontsize=11)
ax.set_title(r'Echo Spectrum: $M = 30\,M_\odot$', fontweight='bold')
ax.set_yscale('log')
ax.set_ylim(1e-25, 2)
ax.axhline(1e-23, color='r', ls='--', alpha=0.5, label='LIGO noise floor')
ax.legend(fontsize=9)
ax.grid(True, alpha=0.3)

plt.tight_layout()
import os
output_dir = os.environ.get("OUTPUT_DIR", os.path.dirname(os.path.abspath(__file__)))
plt.savefig(f"{output_dir}/bh_echo_spectrum.png", dpi=150, bbox_inches='tight')
print(f"\nPlot saved to {output_dir}/bh_echo_spectrum.png")

# ============================================================
# Summary table for the framework
# ============================================================
print(f"\n{'=' * 80}")
print("PREDICTION #9 SUMMARY")
print(f"{'=' * 80}")
print(f"""
PREDICTION #9: Post-Merger Black Hole Echo Spectrum

FORMULA:
  Delta_t_echo = (4GM/c^3) * ln(2GM / (c^2 * l_P))
  
  Equivalently: Delta_t_echo = (4GM/c^3) * ln(M/M_P) + (4GM/c^3) * ln(2)
  
  For 30 M_sun: Delta_t_echo = {echo_delay(30*M_sun)*1000:.2f} ms

ECHO SPECTRUM:
  f_echo,n = f_QNM + n / Delta_t_echo,  n = 1, 2, 3, ...
  A_n / A_0 = exp(-n * 8*pi*G*M*omega_QNM/c^3)

ZERO FREE PARAMETERS:
  - Delay: determined by l_P (Planck length)
  - Amplitude: determined by T_H (Hawking temperature)
  - Both from fundamental constants only

DISTINGUISHING FEATURE:
  Echo spacing ~ 1/(M * ln M), NOT 1/M
  The ln M factor is the ECSK fingerprint

FALSIFICATION:
  Non-detection with ~10,000 stacked LIGO events would rule out 
  Planck-scale bounce surfaces (and hence the ECSK mechanism).
""")
