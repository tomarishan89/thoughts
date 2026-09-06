"""
Sterile Neutrino Lyman-Alpha, Phase-Space, and Radiative Decay Confrontation
=============================================================================
Implementation of AGENTS.md Rule 5 / ISSUE-4.115 benchmark calculations.

This module evaluates the microphysical viability of Candidate A (Right-Handed
Sterile Neutrino nu_R produced at the non-singular ECSK torsion bounce) against:
  1. Lyman-alpha forest small-scale structure constraints (Irsic et al. 2017)
  2. Dwarf spheroidal galaxy phase-space density bounds (Tremaine & Gunn 1979)
  3. X-ray satellite radiative decay limits (NuSTAR, Chandra, XRISM)

Physical References:
--------------------
- Irsic, V. et al. (2017), "New Constraints on the Free-Streaming of Warm Dark
  Matter from Intermediate and Small Scale Lyman-alpha Forest Data",
  Phys. Rev. D 96, 023522 [arXiv:1702.01764].
- Boyarsky, A., Ruchayskiy, O. & Shaposhnikov, M. (2009), "The Role of Sterile
  Neutrinos in Cosmology and Astrophysics", Ann. Rev. Nucl. Part. Sci. 59, 191.
- Tremaine, S. & Gunn, J. E. (1979), "Dynamical Role of Light Neutral Leptons
  in Cosmology", Phys. Rev. Lett. 42, 407.
- Pal, P. B. & Wolfenstein, L. (1982), "Radiative Decays of Massive Neutrinos",
  Phys. Rev. D 25, 766.
- Roach, B. et al. (2020), "NuSTAR Constraints on Sterile Neutrino Dark Matter
  in the Milky Way", Phys. Rev. D 101, 103011.

Numerical Precision & Systematic Error Sources:
----------------------------------------------
- Analytical free-streaming formula carries ~5% systematic uncertainty from
  matter-radiation equality transfer function fitting (Boyarsky et al. 2009).
- Phase-space density bound Q_max assumes coarse-grained Fermi-Dirac profile
  diluted uniformly by out-of-equilibrium scalar/scalaron entropy dump D.
- Absolute vs. Ratio Claim Separation: The macroscopic envelope (Omega_m = 1/3,
  Omega_DM h^2 = 0.129, Omega_DM/Omega_b = 5.788) is an unconditional geometric
  prediction; the microscopic sterile neutrino benchmark (m_s = 7.1 keV, D = 21.4)
  is conditional on species identity across the Category Boundary.
"""

import numpy as np

# -----------------------------------------------------------------------------
# Fundamental Physical Constants (CODATA 2022 / SI & Natural)
# -----------------------------------------------------------------------------
C_LIGHT = 2.99792458e8         # m/s
HBAR_SI = 1.054571817e-34      # J s
HBAR_CGS = 1.054571817e-27     # erg s
EV_TO_J = 1.602176634e-19      # J/eV
M_SUN_G = 1.98847e33           # g
PC_TO_CM = 3.08567758e18       # cm
KM_TO_CM = 1.0e5               # cm
YEAR_TO_S = 3.15576e7          # s (Julian year)

# Standard Model / Cosmological Parameters
G_STAR_S_DEC = 106.75          # SM effective entropy degrees of freedom at T_dec > 100 GeV
G_STAR_S_0 = 3.91              # Modern effective entropy degrees of freedom (photons + active nu)
T_NU_RATIO_STANDARD = (10.75 / G_STAR_S_DEC)**(1.0 / 3.0) # ~0.4652 for early-decoupling species

# -----------------------------------------------------------------------------
# Core Physics Functions
# -----------------------------------------------------------------------------

def compute_temperature_ratio(D=1.0, g_star_dec=G_STAR_S_DEC):
    """
    Compute sterile neutrino to active neutrino temperature ratio T_nu_R / T_nu.
    
    Parameters:
        D (float): Entropy dilution factor from out-of-equilibrium decay
        g_star_dec (float): Effective degrees of freedom at decoupling
        
    Returns:
        float: Temperature ratio (T_nu_R / T_nu)
    """
    return ((10.75 / g_star_dec)**(1.0 / 3.0)) / (D**(1.0 / 3.0))


def compute_free_streaming_length(m_s_eV, D=1.0):
    """
    Compute comoving free-streaming length lambda_FS [Mpc].
    
    Formula (Boyarsky et al. 2009, Lesgourgues & Pastor 2006):
        lambda_FS approx 1.2 Mpc * (1 keV / m_s) * (T_s / T_nu)
        
    Parameters:
        m_s_eV (float): Sterile neutrino mass in eV
        D (float): Entropy dilution factor
        
    Returns:
        float: Comoving free-streaming length in Mpc
    """
    t_ratio = compute_temperature_ratio(D=D)
    return 1.2 * (1000.0 / m_s_eV) * t_ratio


def compute_tremaine_gunn_q(m_s_eV, D=1.0, g_s=2):
    """
    Compute maximum phase-space density Q_max in astrophysical units:
        M_sun pc^-3 (km/s)^-3
        
    Formula (Tremaine & Gunn 1979):
        Q_max = (g_s * m_s^4) / ((2 pi hbar)^3 * 2 * D)
        
    Parameters:
        m_s_eV (float): Sterile neutrino mass in eV
        D (float): Entropy dilution factor
        g_s (int): Spin degrees of freedom (2 for Majorana / Weyl nu_R)
        
    Returns:
        tuple: (Q_max in g s^3 cm^-6, Q_max in M_sun pc^-3 (km/s)^-3)
    """
    # Mass in grams
    m_s_g = (m_s_eV * EV_TO_J / (C_LIGHT**2)) * 1000.0
    
    # Q in cgs: g s^3 cm^-6
    q_cgs = (g_s * m_s_g**4) / ((2.0 * np.pi * HBAR_CGS)**3 * 2.0 * D)
    
    # Conversion to astro units: M_sun / pc^3 / (km/s)^3
    unit_cgs = M_SUN_G / ((PC_TO_CM**3) * (KM_TO_CM**3))
    q_astro = q_cgs / unit_cgs
    
    return q_cgs, q_astro


def compute_xray_radiative_decay(m_s_eV, sin2_2theta=1.0e-11):
    """
    Compute sterile neutrino radiative decay rate Gamma_gamma [s^-1] and lifetime [s, yr].
    
    Formula (Pal & Wolfenstein 1982, Barger et al. 1995):
        Gamma_gamma = (9 alpha_EM G_F^2 / (1024 pi^4)) * sin^2(2 theta) * m_s^5
                    approx 1.38e-29 s^-1 * (sin^2(2 theta) / 10^-11) * (m_s / 7.1 keV)^5
                    
    Parameters:
        m_s_eV (float): Sterile neutrino mass in eV
        sin2_2theta (float): Active-sterile mixing angle parameter
        
    Returns:
        tuple: (Gamma_gamma [s^-1], lifetime [s], lifetime [yr])
    """
    m_s_ratio = m_s_eV / 7100.0
    gamma = 1.38e-29 * (sin2_2theta / 1.0e-11) * (m_s_ratio**5)
    lifetime_s = 1.0 / gamma if gamma > 0 else np.inf
    lifetime_yr = lifetime_s / YEAR_TO_S
    return gamma, lifetime_s, lifetime_yr


# -----------------------------------------------------------------------------
# Self-Test and Benchmarking Function (AGENTS.md Layer 0 Protocol)
# -----------------------------------------------------------------------------

def run_sterile_neutrino_benchmarks(verbose=True):
    """
    Execute Layer 0 benchmarks for Sterile Neutrino DM Microphysics.
    
    Returns:
        dict: Test results with numerical and status fields.
    """
    results = {}
    
    # Case 1: Known Limit (Thermal Relic, D = 1.0, m_s = 331 eV)
    # Physical expectation: lambda_FS >> 0.1 Mpc (excluded by Lyman-alpha)
    # Q_max << Q_obs (violates Tremaine-Gunn bound in dwarf spheroidal galaxies)
    m_s_therm = 331.0
    d_therm = 1.0
    lambda_fs_therm = compute_free_streaming_length(m_s_therm, d_therm)
    _, q_astro_therm = compute_tremaine_gunn_q(m_s_therm, d_therm)
    
    # Case 2: Non-Thermal Diluted Benchmark (m_s = 7100 eV = 7.1 keV, D = 21.4)
    # Physical expectation: lambda_FS < 0.1 Mpc (satisfies Lyman-alpha forest)
    # Q_max >> Q_obs ~ 1e-4 M_sun pc^-3 (km/s)^-3 (satisfies Tremaine-Gunn)
    # Radiative decay lifetime >> age of universe (t_0 ~ 1.38e10 yr)
    m_s_bench = 7100.0
    d_bench = 21.4
    lambda_fs_bench = compute_free_streaming_length(m_s_bench, d_bench)
    _, q_astro_bench = compute_tremaine_gunn_q(m_s_bench, d_bench)
    gamma_bench, tau_s_bench, tau_yr_bench = compute_xray_radiative_decay(m_s_bench, sin2_2theta=1.0e-11)
    
    # Dwarf spheroidal typical central core phase-space density (Draco, Fornax)
    q_dsph_obs = 1.0e-4
    
    # Lyman-alpha comoving free-streaming cut-off bound (Irsic et al. 2017)
    lambda_fs_lyman_limit = 0.10 # Mpc (corresponding to m_WDM^thermal > 3.5 - 5.3 keV)
    
    # Evaluated status
    pass_thermal_exclusion = (lambda_fs_therm > lambda_fs_lyman_limit) and (q_astro_therm < q_dsph_obs)
    pass_bench_lyman = (lambda_fs_bench < lambda_fs_lyman_limit)
    pass_bench_tg = (q_astro_bench > q_dsph_obs)
    pass_bench_xray = (tau_yr_bench > 1.38e10 * 1.0e8) # > 10^8 times universe age
    
    all_passed = pass_thermal_exclusion and pass_bench_lyman and pass_bench_tg and pass_bench_xray
    
    results['lambda_fs_therm_Mpc'] = lambda_fs_therm
    results['q_astro_therm'] = q_astro_therm
    results['pass_thermal_exclusion'] = pass_thermal_exclusion
    
    results['lambda_fs_bench_kpc'] = lambda_fs_bench * 1000.0
    results['lambda_fs_bench_Mpc'] = lambda_fs_bench
    results['pass_bench_lyman'] = pass_bench_lyman
    
    results['q_astro_bench'] = q_astro_bench
    results['q_ratio_tg'] = q_astro_bench / q_dsph_obs
    results['pass_bench_tg'] = pass_bench_tg
    
    results['gamma_xray_s'] = gamma_bench
    results['tau_xray_yr'] = tau_yr_bench
    results['pass_bench_xray'] = pass_bench_xray
    
    results['all_passed'] = all_passed
    
    if verbose:
        print("=" * 80)
        print("STERILE NEUTRINO LYMAN-ALPHA & PHASE-SPACE CONFRONTATION (ISSUE-4.115)")
        print("=" * 80)
        print(f"[LIMIT 1: Thermal Relic] m_s = {m_s_therm:.1f} eV, D = 1.0")
        print(f"  lambda_FS : {lambda_fs_therm:.4f} Mpc (Cut-off bound < 0.100 Mpc)")
        print(f"  Q_max     : {q_astro_therm:.3e} M_sun pc^-3 (km/s)^-3 vs dSph Q_obs = {q_dsph_obs:.1e}")
        print(f"  Status    : {'EXCLUDED AS EXPECTED (PASS)' if pass_thermal_exclusion else 'FAIL'}")
        print("-" * 80)
        print(f"[BENCHMARK: Non-Thermal Diluted] m_s = {m_s_bench/1000.0:.1f} keV, D = {d_bench:.1f}")
        print(f"  lambda_FS : {lambda_fs_bench*1000.0:.2f} kpc ({lambda_fs_bench:.4f} Mpc)")
        print(f"  Lyman-alpha Limit Check: {lambda_fs_bench:.4f} < 0.100 Mpc -> {'PASSED' if pass_bench_lyman else 'FAILED'}")
        print(f"  Q_max     : {q_astro_bench:.4f} M_sun pc^-3 (km/s)^-3 (Margin: {q_astro_bench/q_dsph_obs:.1f}x > Q_obs)")
        print(f"  Tremaine-Gunn Check     : {'PASSED' if pass_bench_tg else 'FAILED'}")
        print(f"  X-Ray tau : {tau_yr_bench:.3e} yr (NuSTAR/XRISM limit sin^2(2th) <= 1e-11)")
        print(f"  Radiative Decay Check   : {'PASSED' if pass_bench_xray else 'FAILED'}")
        print("=" * 80)
        print(f"OVERALL CONFRONTATION STATUS: {'ALL CHECKS PASSED' if all_passed else 'FAILED'}")
        print("=" * 80)
        
    return results


if __name__ == "__main__":
    res = run_sterile_neutrino_benchmarks(verbose=True)
    assert res['all_passed'], "Sterile neutrino benchmark validation failure"
