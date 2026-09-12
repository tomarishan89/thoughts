"""
ISSUE-4.53: CMB Temperature as Cosmological Engine Exhaust
=============================================================

Question: Can the CMB temperature T_CMB = 2.725 K be derived from the
framework's 4-phase engine cycle rather than being treated as a measured input?

The CMB photon bath is the thermal waste product of the cosmic engine:
- Phase I (Radiation): fuel injection at T_rh ~ 10^15 GeV
- Phase II (Matter): partition/structure formation
- Phase III (Stellar/BH): localized sub-engine entropy production
- Phase IV (Dark Energy): equilibration/exhaust

The CMB photons were released at recombination (z_rec ~ 1089) when the
photon-baryon plasma decoupled. Today they have T_CMB = T_rec / (1 + z_rec).

The question is: can the framework fix T_rec and z_rec from first principles?
"""


import sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

import numpy as np

# ============================================================
# Constants
# ============================================================
G     = 6.67430e-11       # m^3/(kg s^2)
c     = 2.99792458e8      # m/s
hbar  = 1.054571817e-34   # J s
k_B   = 1.380649e-23      # J/K
sigma_T = 6.6524587e-29   # Thomson cross-section (m^2)
m_e   = 9.1093837e-31     # electron mass (kg)
m_p   = 1.67262192e-27    # proton mass (kg)
m_H   = 1.6737236e-27     # hydrogen atom mass (kg)
alpha_em = 1.0/137.036    # fine structure constant
a_rad = 4 * 5.670374419e-8 / c  # radiation constant (J/(m^3 K^4))
                                  # = 4*sigma_SB/c
GeV   = 1.602176634e-10   # 1 GeV in Joules

# Framework parameters
H_0   = 67.4e3 / (3.0857e22)  # Hubble constant in s^-1 (67.4 km/s/Mpc)
Omega_m = 1.0/3.0              # Framework prediction
Omega_Lambda = 2.0/3.0         # Framework prediction
Omega_b = 0.049                # Framework (derived from torsion baryogenesis)
Omega_r_obs = 9.15e-5          # Observed radiation density parameter

print("=" * 80)
print("ISSUE-4.53: CMB TEMPERATURE FROM FRAMEWORK PARAMETERS")
print("=" * 80)

# ============================================================
# APPROACH 1: Standard thermodynamic derivation
# ============================================================
# T_CMB today is related to T_rec by:
#   T_CMB = T_rec / (1 + z_rec)
#
# T_rec is the recombination temperature, ~3000 K, determined by
# the Saha equation: when the ionization fraction x_e drops below ~0.1
#
# The Saha equation for hydrogen recombination:
#   x_e^2 / (1-x_e) = (1/n_b) * (m_e k_B T / (2*pi*hbar^2))^{3/2} * exp(-E_I/(k_B T))
#
# where E_I = 13.6 eV is the hydrogen ionization energy
# and n_b is the baryon number density

print(f"\n{'='*80}")
print("APPROACH 1: T_CMB FROM RECOMBINATION PHYSICS")
print(f"{'='*80}")

# The recombination temperature depends on:
# 1. The hydrogen ionization energy E_I = 13.6 eV (atomic physics constant)
# 2. The baryon-to-photon ratio eta (framework-derived: 6.1e-10)
# 3. The photon number density n_gamma (proportional to T^3)

E_I = 13.6 * 1.602176634e-19  # 13.6 eV in Joules

# The condition for recombination (Saha equation) at x_e ~ 0.5:
# (1/n_b) * (m_e * k_B * T / (2*pi*hbar^2))^{3/2} * exp(-E_I/(k_B*T)) ~ 1
#
# n_b = eta * n_gamma = eta * (2*zeta(3)/pi^2) * (k_B*T/(hbar*c))^3
# where zeta(3) ~ 1.202

zeta3 = 1.20206
eta = 6.1e-10  # framework-derived baryon-to-photon ratio

# The recombination condition becomes (at x_e = 0.5):
# eta * (2*zeta(3)/pi^2) * (k_B*T/(hbar*c))^3 * [1/(m_e*k_B*T/(2*pi*hbar^2))^{3/2}]
#   * exp(E_I/(k_B*T)) ~ 4
#
# Simplifying:
# eta * (2*zeta(3)/pi^2) * (k_B*T)^3/(hbar*c)^3 * (2*pi*hbar^2)^{3/2}/(m_e*k_B*T)^{3/2}
#   * exp(E_I/(k_B*T)) ~ 4
#
# Let's solve this numerically:

def saha_equation(T, eta_val):
    """Returns x_e from the Saha equation at temperature T."""
    # Photon number density
    n_gamma = 2 * zeta3 / np.pi**2 * (k_B * T / (hbar * c))**3
    # Baryon number density
    n_b = eta_val * n_gamma
    # Thermal de Broglie factor
    lambda_th = np.sqrt(2 * np.pi * hbar**2 / (m_e * k_B * T))
    # Saha coefficient
    S = (1.0 / n_b) * (1.0 / lambda_th**3) * np.exp(-E_I / (k_B * T))
    # Solve x_e^2/(1-x_e) = S for x_e
    # x_e = (-S + sqrt(S^2 + 4*S)) / 2
    x_e = (-S + np.sqrt(S**2 + 4*S)) / 2.0
    return x_e

# Find T_rec where x_e = 0.1 (standard definition of "recombination")
from scipy.optimize import brentq

def recombination_condition(T, eta_val, x_target=0.1):
    return saha_equation(T, eta_val) - x_target

# Search between 2000 K and 5000 K
T_rec = brentq(recombination_condition, 2000, 5000, args=(eta, 0.1))
print(f"\nRecombination temperature (x_e = 0.1): T_rec = {T_rec:.1f} K")

# Also find T at x_e = 0.5 (50% ionized)
T_half = brentq(recombination_condition, 2000, 5000, args=(eta, 0.5))
print(f"50% ionization temperature: T_half = {T_half:.1f} K")

# The recombination redshift
# From the Friedmann equation in the matter-dominated era:
# T(z) = T_0 * (1 + z), so z_rec = T_rec / T_0 - 1
# But T_0 = T_CMB is what we're trying to derive!
# 
# This is circular unless we can derive T_0 independently.
# The key insight: T_0 is determined by the TOTAL photon energy density
# at the present epoch, which is determined by conservation of
# the photon number (after recombination, photons are free-streaming).

print(f"\n{'='*80}")
print("APPROACH 2: T_CMB FROM ENERGY CONSERVATION")
print(f"{'='*80}")

# The total energy in the universe is set by the critical density:
#   rho_crit = 3 H_0^2 / (8*pi*G)
rho_crit = 3 * H_0**2 / (8 * np.pi * G)
print(f"Critical density: rho_crit = {rho_crit:.4e} kg/m^3")

# The radiation energy density today:
#   rho_r = Omega_r * rho_crit
# For the framework, Omega_r is NOT an independent parameter — it's 
# determined by the baryon-to-photon ratio eta and the matter density:
#
# At matter-radiation equality (z_eq):
#   rho_r(z_eq) = rho_m(z_eq)
#   rho_r,0 * (1+z_eq)^4 = rho_m,0 * (1+z_eq)^3
#   rho_r,0 / rho_m,0 = 1 / (1+z_eq)
#
# The radiation-matter equality redshift is:
#   1 + z_eq = rho_m,0 / rho_r,0 = Omega_m / Omega_r
#
# The radiation density parameter is:
#   Omega_r = a_rad * T_CMB^4 / (rho_crit * c^2) * (1 + N_eff * 7/8 * (4/11)^{4/3})
# where N_eff = 3.046 (effective neutrino species)
#
# This seems circular again! T_CMB appears in Omega_r.
# 
# But the FRAMEWORK provides a non-circular path:
# 
# The photon number density is conserved after e+e- annihilation.
# The total comoving photon number N_gamma is fixed by:
#   n_gamma = (2*zeta(3)/pi^2) * (k_B * T_CMB)^3 / (hbar*c)^3
#   N_gamma = n_gamma * a^3 = const (after neutrino decoupling)
#
# The baryon number density is:
#   n_b = rho_b / m_p = Omega_b * rho_crit * c^2 / (m_p * c^2)
#   (using natural units properly)
#
# The baryon-to-photon ratio TODAY must equal eta:
#   eta = n_b / n_gamma
#
# Solving for T_CMB:
#   n_gamma = n_b / eta
#   (2*zeta(3)/pi^2) * (k_B * T_CMB / (hbar*c))^3 = n_b / eta
#
# n_b = Omega_b * rho_crit / m_H (number density of baryons)

n_b_0 = Omega_b * rho_crit / m_H  # baryons per m^3
print(f"Baryon number density: n_b = {n_b_0:.4e} m^-3")

n_gamma_0 = n_b_0 / eta  # photons per m^3
print(f"Photon number density: n_gamma = {n_gamma_0:.4e} m^-3")

# From n_gamma = (2*zeta(3)/pi^2) * (k_B * T / (hbar*c))^3:
T_CMB_derived = (n_gamma_0 * np.pi**2 / (2 * zeta3))**(1.0/3.0) * hbar * c / k_B
print(f"\nT_CMB (derived) = {T_CMB_derived:.4f} K")
print(f"T_CMB (observed) = 2.7255 K")
print(f"Discrepancy: {(T_CMB_derived - 2.7255)/2.7255 * 100:+.2f}%")

# Let's trace the dependencies:
print(f"\n--- Input dependencies ---")
print(f"  H_0 = 67.4 km/s/Mpc (measured)")
print(f"  Omega_b = {Omega_b} (framework-derived, §6.8.4)")
print(f"  eta = {eta:.2e} (framework-derived, §6.8.4)")
print(f"  m_H = {m_H:.4e} kg (atomic physics constant)")
print(f"  k_B, hbar, c (fundamental constants)")

# ============================================================
# APPROACH 3: Alternative — from matter-radiation equality
# ============================================================
print(f"\n{'='*80}")
print("APPROACH 3: T_CMB FROM MATTER-RADIATION EQUALITY")
print(f"{'='*80}")

# z_eq (radiation-matter equality) is observed to be ~3400
# In the framework: z_eq depends on eta (ISSUE-4.59 derived)
# 
# The radiation density at any redshift:
#   rho_r = (pi^2/15) * (k_B*T)^4 / (hbar*c)^3 * g_eff(T)
# where g_eff accounts for all relativistic species
#
# At T_CMB, only photons and (approximately) neutrinos contribute:
#   g_eff = 2 + 7/8 * 2 * 3 * (4/11)^{4/3} = 2 + 3.046 * 7/4 * (4/11)^{4/3}
# Actually, more precisely:
#   rho_r = rho_gamma * (1 + 7/8 * (4/11)^{4/3} * N_eff)
# where rho_gamma = a_rad * T^4 / c^2 (for T in the radiation constant)

N_eff = 3.046  # effective neutrino species

# The matter-radiation equality condition:
#   Omega_r * (1+z_eq)^4 = Omega_m * (1+z_eq)^3
#   Omega_r = Omega_m / (1+z_eq)
# 
# Also: Omega_r = rho_r / rho_crit
# where rho_r = (a_rad * T_CMB^4) * (1 + 7/8 * (4/11)^{4/3} * N_eff) / c^2
# (Note: a_rad = 4*sigma_SB/c has units J/(m^3 K^4))

# rho_r,0 in kg/m^3:
# rho_r = a_rad * T^4 / c^2 * (1 + factor_neutrino)
neutrino_factor = 1 + 7.0/8.0 * (4.0/11.0)**(4.0/3.0) * N_eff

# From Omega_r = Omega_m / (1 + z_eq):
z_eq_obs = 3402  # observed
Omega_r_from_zeq = Omega_m / (1 + z_eq_obs)
print(f"Omega_r from z_eq = {z_eq_obs}: {Omega_r_from_zeq:.6e}")

# Now get T_CMB from Omega_r:
# Omega_r = a_rad * T^4 * neutrino_factor / (c^2 * rho_crit)
# T^4 = Omega_r * c^2 * rho_crit / (a_rad * neutrino_factor)
T_CMB_from_zeq = (Omega_r_from_zeq * c**2 * rho_crit / (a_rad * neutrino_factor))**(1.0/4.0)
print(f"T_CMB from z_eq = {z_eq_obs}: {T_CMB_from_zeq:.4f} K")
print(f"Observed: 2.7255 K")
print(f"Discrepancy: {(T_CMB_from_zeq - 2.7255)/2.7255 * 100:+.2f}%")

# But z_eq is an observed quantity, not derived from the framework.
# Can the framework derive z_eq?
# 
# z_eq is determined by: rho_m / rho_r at early times
# rho_m/rho_r propto (1+z)^{-1} * (rho_m,0 / rho_r,0)
# 
# rho_m,0 = Omega_m * rho_crit (framework: Omega_m = 1/3)
# rho_r,0 = a_rad * T_CMB^4 * neutrino_factor / c^2
# 
# So z_eq = rho_m,0 / rho_r,0 - 1 depends on T_CMB.
# We're going in circles again!

print(f"\n{'='*80}")
print("KEY INSIGHT: THE NON-CIRCULAR DERIVATION")
print(f"{'='*80}")
print("""
The fundamental insight is that T_CMB is determined by CONSERVATION
of comoving entropy (photon number) combined with:
  1. The baryon-to-photon ratio eta (framework-derived: 6.1e-10)
  2. The baryon density Omega_b * rho_crit (framework: Omega_b = 0.049)
  3. The Hubble constant H_0 (measured: 67.4 km/s/Mpc)

The derivation chain is:
  eta (derived) + Omega_b (derived) + H_0 (measured)
  -> n_b = Omega_b * rho_crit / m_H
  -> n_gamma = n_b / eta
  -> T_CMB = [(n_gamma * pi^2) / (2 * zeta(3))]^{1/3} * (hbar*c/k_B)
""")

print(f"RESULT: T_CMB = {T_CMB_derived:.4f} K")
print(f"OBSERVED: T_CMB = 2.7255 K")
print(f"DISCREPANCY: {(T_CMB_derived - 2.7255)/2.7255 * 100:+.3f}%")

# ============================================================
# SENSITIVITY ANALYSIS
# ============================================================
print(f"\n{'='*80}")
print("SENSITIVITY ANALYSIS")
print(f"{'='*80}")

# T_CMB depends on (Omega_b * rho_crit / (eta * m_H))^{1/3}
# i.e., T_CMB propto (Omega_b * H_0^2 / eta)^{1/3}
# 
# Partial derivatives:
# dT/T = (1/3) * dOmega_b/Omega_b + (2/3) * dH_0/H_0 - (1/3) * deta/eta

print(f"T_CMB ∝ (Omega_b * H_0^2 / eta)^{{1/3}}")
print(f"Sensitivity:")
print(f"  dT/T = (1/3) * dOmega_b/Omega_b = (1/3) * (-0.40%) = -0.13%")
print(f"  dT/T = (2/3) * dH_0/H_0 (depends on H_0 measurement)")
print(f"  dT/T = -(1/3) * deta/eta")

# The key question: which framework parameters are derived vs measured?
# - eta: DERIVED (6.1e-10, from ECSK torsion baryogenesis, §6.8.4)
# - Omega_b: DERIVED (0.049, from eta and cosmological constraints)
# - H_0: MEASURED (67.4 km/s/Mpc)
# - m_H: CONSTANT (atomic physics)
# 
# So T_CMB is a PREDICTION given H_0 as the sole measured input.

print(f"\n{'='*80}")
print("FRAMEWORK PREDICTION STATUS")
print(f"{'='*80}")
print(f"  Inputs:")
print(f"    H_0 = 67.4 km/s/Mpc (measured)")
print(f"    eta = 6.1e-10 (derived, §6.8.4)")
print(f"    Omega_b = 0.049 (derived, §6.8.4)")
print(f"    m_H, k_B, hbar, c (constants)")
print(f"")
print(f"  Output:")
print(f"    T_CMB = {T_CMB_derived:.4f} K (predicted)")
print(f"    T_CMB = 2.7255 K (observed)")
print(f"    Error = {(T_CMB_derived - 2.7255)/2.7255 * 100:+.3f}%")

# ============================================================
# CRITICAL ASSESSMENT
# ============================================================
print(f"\n{'='*80}")
print("CRITICAL ASSESSMENT")
print(f"{'='*80}")
print("""
IS THIS A GENUINE PREDICTION?

The derivation T_CMB = f(eta, Omega_b, H_0) is standard cosmology.
Every textbook gives this relation. The question is whether the
framework ADDS anything beyond standard cosmology here.

The framework's contribution is:
1. eta is derived from ECSK torsion baryogenesis (not a free parameter)
2. Omega_b is derived from eta (not a free parameter)
3. The combination (eta, Omega_b) is self-consistent with T_CMB

But H_0 remains measured. So T_CMB is predicted ONLY in the sense
that eta and Omega_b are derived rather than fitted.

VERDICT: This is a COROLLARY of the baryogenesis derivation (§6.8.4),
not an independent prediction. The physics is standard; the framework's
contribution is fixing eta and Omega_b.

The more interesting question from ISSUE-4.53 is whether T_dS
(the de Sitter temperature) represents the ABSOLUTE lower limit
on measurement entropy. Let me address that separately.
""")

# ============================================================
# THE DE SITTER TEMPERATURE AS MEASUREMENT FLOOR
# ============================================================
print(f"\n{'='*80}")
print("DE SITTER TEMPERATURE AS MEASUREMENT ENTROPY FLOOR")
print(f"{'='*80}")

# Framework result (Theorem 11): T_dS = 2 * T_H
# where T_H = hbar * c^3 / (8*pi*k_B*G*M_H) is the parent BH Hawking temp
# 
# For our universe: M_H ~ 3.2e22 M_sun (derived in §6.7.1)

M_sun = 1.98892e30
M_H = 3.2e22 * M_sun
T_H = hbar * c**3 / (8 * np.pi * k_B * G * M_H)
T_dS = 2 * T_H

print(f"Parent BH mass: M_H = {M_H:.3e} kg = {M_H/M_sun:.3e} M_sun")
print(f"Hawking temperature: T_H = {T_H:.3e} K")
print(f"de Sitter temperature: T_dS = 2*T_H = {T_dS:.3e} K")
print(f"CMB temperature: T_CMB = 2.7255 K")
print(f"Ratio: T_CMB / T_dS = {2.7255/T_dS:.3e}")
print(f"The CMB is {2.7255/T_dS:.3e} times hotter than the de Sitter floor.")

# The Bekenstein bound on minimum temperature resolution:
# The minimum energy distinguishable in a de Sitter spacetime is:
# E_min = k_B * T_dS
# 
# Any measurement process must produce entropy >= k_B * ln(2) (Landauer),
# requiring energy >= k_B * T_env * ln(2)
# 
# In de Sitter spacetime, the environmental temperature IS T_dS,
# so the minimum measurement energy is k_B * T_dS * ln(2)
# 
# This means:
# 1. No sub-ego can measure a temperature below T_dS
# 2. T_dS is the absolute thermodynamic floor of the child universe
# 3. The CMB is the PRACTICAL electromagnetic floor (currently)
# 4. As the universe expands, T_CMB -> 0, but T_dS is constant
# 5. Eventually T_CMB < T_dS, and the de Sitter horizon becomes
#    the dominant noise source

# When does T_CMB = T_dS?
# T_CMB(a) = T_CMB,0 / a = T_CMB,0 * (1+z)
# At z = 0: T_CMB = 2.7255 K >> T_dS
# T_CMB = T_dS when a = T_CMB,0 / T_dS

a_crossover = 2.7255 / T_dS
z_crossover = -(1 - 1/a_crossover)  # this will be negative (in the future)

print(f"\nCMB-dS crossover scale factor: a = T_CMB/T_dS = {a_crossover:.3e}")
print(f"This is {np.log10(a_crossover):.1f} orders of magnitude in the future")

# In terms of time (assuming de Sitter expansion a = a_0 * exp(H_dS * t)):
H_dS = H_0 * np.sqrt(Omega_Lambda)
t_crossover = np.log(a_crossover) / H_dS
t_crossover_yr = t_crossover / (3.156e7)
print(f"Time to crossover: t ~ {t_crossover_yr:.3e} years")
print(f"(assuming de Sitter expansion from now)")

print(f"\n{'='*80}")
print("SUMMARY")
print(f"{'='*80}")
print(f"""
RESULT 1: T_CMB DERIVATION
  T_CMB = [Omega_b * rho_crit / (eta * m_H)]^{{1/3}} * [pi^2/(2*zeta(3))]^{{1/3}} * hbar*c/k_B
  T_CMB = {T_CMB_derived:.4f} K (predicted) vs 2.7255 K (observed)
  Error: {(T_CMB_derived - 2.7255)/2.7255 * 100:+.3f}%
  Status: COROLLARY of baryogenesis (§6.8.4), not independent prediction
  Dependencies: H_0 (measured), eta and Omega_b (derived)

RESULT 2: T_dS AS MEASUREMENT FLOOR
  T_dS = 2*T_H = {T_dS:.3e} K
  T_CMB/T_dS = {2.7255/T_dS:.3e} (CMB is currently the practical EM noise floor)
  The de Sitter temperature is the ABSOLUTE thermodynamic floor (Landauer bound)
  CMB cools below T_dS at a ~ {a_crossover:.1e} (far future, ~{t_crossover_yr:.1e} yr)
""")
