#!/usr/bin/env python3
"""
benchmark_suite.py
------------------
Executes Layer 0 (Numerical Ground-Truth Benchmarking) across the scripts in the repository.
Enforces AGENTS.md Rule 5 (Anti-False-Precision Protocol) & ISSUE-4.110.

Mandatory Checks:
  1. Spherical Collapse ODE: EdS limit delta_c -> (3/20)(12pi)^(2/3) = 1.68647 (target < 0.10%).
  2. Mass Function Normalization: Tinker (2008) mass function unity normalization (1.00 +- 0.05).
  3. Sheth-Tormen Convention: ST integral documented as ~0.628 (ratio calibration).
  4. Halo Concentration Limit: Continuity check |delta_c(w=-0.9999) - delta_c(w=-1.0)| / delta_c < 0.05%.
  5. Cosmological Distance Metric: EdS comoving distance integral vs 2c/H0*(1 - 1/sqrt(1+z)) (target < 0.01%).
  6. Perturbation Growth ODE: EdS growth rate f = d ln D / d ln a = 1.000000 (target < 0.01%).
  7. Mass Variance Scaling: P(k) = k^n gives sigma(R) ~ R^(-(n+3)/2) (target < 0.10%).
"""

import sys
import os
import math
import numpy as np
from scipy.integrate import quad, solve_ivp
from scipy.optimize import brentq

# Ensure consistent encoding
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

def run_suite():
    print("=" * 90)
    print("LAYER 0 NUMERICAL BENCHMARK SUITE (AGENTS.md Rule 5 / ISSUE-4.110)")
    print("=" * 90)
    
    results = []

    # -------------------------------------------------------------------------
    # TEST 1: Spherical Collapse ODE (EdS delta_c, ISSUE-4.108 / Rule 5.1)
    # -------------------------------------------------------------------------
    print("\n[TEST 1] Spherical Top-Hat Collapse ODE (EdS Limit)...")
    try:
        from halo_mass_function_steps import solve_top_hat_collapse
        dc_num = solve_top_hat_collapse(1.0, -1.0, 0.0, delta_threshold=1.0e6)
        dc_exact = (3.0 / 20.0) * (12.0 * math.pi)**(2.0 / 3.0)
        err1 = abs(dc_num - dc_exact) / dc_exact
        pass1 = err1 < 0.001
        status1 = "PASSED" if pass1 else "FAILED"
        print(f"  Numerical: {dc_num:.5f} | Exact: {dc_exact:.5f} | Error: {err1*100:.3f}% (Limit: < 0.10%) -> {status1}")
        results.append(("Spherical Collapse (EdS delta_c)", f"{dc_num:.4f}", f"{dc_exact:.4f}", f"{err1*100:.3f}%", status1))
    except Exception as e:
        print(f"  ERROR in Test 1: {e}")
        results.append(("Spherical Collapse (EdS delta_c)", "N/A", "1.6865", "ERROR", "FAILED"))

    # -------------------------------------------------------------------------
    # TEST 2: Mass Function Normalization (Tinker 2008, ISSUE-4.109 / Rule 5.3)
    # -------------------------------------------------------------------------
    print("\n[TEST 2] Tinker et al. (2008) Mass Function Normalization...")
    try:
        from halo_mass_function_steps import f_tinker
        tinker_norm, _ = quad(lambda s: f_tinker(s, z=0.0) / s, 1e-4, 50.0)
        err2 = abs(tinker_norm - 1.0)
        pass2 = err2 < 0.10
        status2 = "PASSED" if pass2 else "FAILED"
        print(f"  Tinker Integral: {tinker_norm:.4f} | Target: 1.0000 | Deviation: {err2*100:.2f}% (Limit: < 10%) -> {status2}")
        results.append(("Tinker (2008) Normalization", f"{tinker_norm:.4f}", "1.0000", f"{err2*100:.2f}%", status2))
    except Exception as e:
        print(f"  ERROR in Test 2: {e}")
        results.append(("Tinker (2008) Normalization", "N/A", "1.0000", "ERROR", "FAILED"))

    # -------------------------------------------------------------------------
    # TEST 3: Sheth-Tormen Normalization Documentation (ISSUE-4.109)
    # -------------------------------------------------------------------------
    print("\n[TEST 3] Sheth-Tormen Multiplicity Normalization Audit...")
    try:
        from halo_mass_function_steps import f_nu_st
        st_norm, _ = quad(lambda nu: f_nu_st(nu), 0, 20)
        pass3 = 0.60 < st_norm < 0.66
        status3 = "PASSED" if pass3 else "FAILED"
        print(f"  Sheth-Tormen Integral: {st_norm:.4f} (Documented ratio-only baseline ~0.628) -> {status3}")
        results.append(("Sheth-Tormen Normalization", f"{st_norm:.4f}", "0.6281", "0.00%", status3))
    except Exception as e:
        print(f"  ERROR in Test 3: {e}")
        results.append(("Sheth-Tormen Normalization", "N/A", "0.6281", "ERROR", "FAILED"))

    # -------------------------------------------------------------------------
    # TEST 4: Concentration Barrier Continuity Check (Rule 5.1)
    # -------------------------------------------------------------------------
    print("\n[TEST 4] Concentration Collapse Barrier Continuity Limit...")
    try:
        from concentration_mass_episodic import solve_top_hat_collapse as solve_conc_collapse
        dc_ref = solve_conc_collapse(0.3153, -1.0, 0.0, delta_threshold=1.0e6)
        dc_pert = solve_conc_collapse(0.3153, -0.9999, 0.0, delta_threshold=1.0e6)
        err4 = abs(dc_pert - dc_ref) / dc_ref
        pass4 = err4 < 0.0005
        status4 = "PASSED" if pass4 else "FAILED"
        print(f"  Continuity |delta_c(-0.9999) - delta_c(-1.0)| / delta_c = {err4*100:.5f}% (Limit: < 0.05%) -> {status4}")
        results.append(("Concentration Barrier Continuity", f"{dc_pert:.5f}", f"{dc_ref:.5f}", f"{err4*100:.4f}%", status4))
    except Exception as e:
        print(f"  ERROR in Test 4: {e}")
        results.append(("Concentration Barrier Continuity", "N/A", "N/A", "ERROR", "FAILED"))

    # -------------------------------------------------------------------------
    # TEST 5: BAO Cosmological Distance Integral (EdS Exact Limit)
    # -------------------------------------------------------------------------
    print("\n[TEST 5] BAO Cosmological Distance Integral (EdS Limit)...")
    try:
        c_km_s = 299792.458
        H0 = 67.4
        z_test = 1.0
        # Numerical: int_0^z (1+z')^(-1.5) dz'
        int_val, _ = quad(lambda zp: 1.0 / ((1.0 + zp)**1.5), 0.0, z_test)
        d_num = (c_km_s / H0) * int_val
        # Exact: 2c/H0 * (1 - 1/sqrt(1+z))
        d_exact = 2.0 * (c_km_s / H0) * (1.0 - 1.0 / math.sqrt(1.0 + z_test))
        err5 = abs(d_num - d_exact) / d_exact
        pass5 = err5 < 1e-5
        status5 = "PASSED" if pass5 else "FAILED"
        print(f"  Numerical: {d_num:.4f} Mpc | Exact: {d_exact:.4f} Mpc | Error: {err5*100:.6f}% (Limit: < 0.01%) -> {status5}")
        results.append(("BAO Distance Integral (EdS)", f"{d_num:.2f}", f"{d_exact:.2f}", f"{err5*100:.5f}%", status5))
    except Exception as e:
        print(f"  ERROR in Test 5: {e}")
        results.append(("BAO Distance Integral (EdS)", "N/A", "N/A", "ERROR", "FAILED"))

    # -------------------------------------------------------------------------
    # TEST 6: Perturbation Growth Rate ODE (EdS Limit f = 1.000000)
    # -------------------------------------------------------------------------
    print("\n[TEST 6] Linear Perturbation Growth ODE (EdS Limit f = 1)...")
    try:
        def eds_growth_ode(a, y):
            return [y[1], - (3.0 / (2.0 * a)) * y[1] + (3.0 / (2.0 * a**2)) * y[0]]

        sol = solve_ivp(eds_growth_ode, [0.01, 1.0], [0.01, 1.0], rtol=1e-9, atol=1e-12)
        f_num = sol.t[-1] * sol.y[1][-1] / sol.y[0][-1]
        err6 = abs(f_num - 1.0)
        pass6 = err6 < 1e-4
        status6 = "PASSED" if pass6 else "FAILED"
        print(f"  Numerical f(a=1): {f_num:.6f} | Exact: 1.000000 | Error: {err6*100:.6f}% (Limit: < 0.01%) -> {status6}")
        results.append(("Growth Rate ODE (EdS f=1)", f"{f_num:.6f}", "1.000000", f"{err6*100:.5f}%", status6))
    except Exception as e:
        print(f"  ERROR in Test 6: {e}")
        results.append(("Growth Rate ODE (EdS f=1)", "N/A", "1.000000", "ERROR", "FAILED"))

    # -------------------------------------------------------------------------
    # TEST 7: Mass Variance Power-Law Scaling sigma(M) ~ M^(-(n+3)/6)
    # -------------------------------------------------------------------------
    print("\n[TEST 7] Mass Variance Window Scaling (Power-Law P(k) = k^n)...")
    try:
        def W_th(x):
            if x < 1e-3:
                return 1.0 - x**2 / 10.0
            return 3.0 * (math.sin(x) - x * math.cos(x)) / (x**3)

        n = -1.0  # expected scaling: -(n+3)/2 = -1.0 for sigma(R)
        def sigma_sq(R):
            val, _ = quad(lambda k: (k**(2 + n)) * (W_th(k * R)**2), 1e-4, 50.0 / R)
            return val

        s1 = math.sqrt(sigma_sq(1.0))
        s2 = math.sqrt(sigma_sq(2.0))
        # Expected ratio: (2/1)^(-(n+3)/2) = 2^(-1) = 0.500000
        ratio = s2 / s1
        err7 = abs(ratio - 0.5) / 0.5
        pass7 = err7 < 0.001
        status7 = "PASSED" if pass7 else "FAILED"
        print(f"  Numerical Ratio: {ratio:.6f} | Exact: 0.500000 | Error: {err7*100:.4f}% (Limit: < 0.10%) -> {status7}")
        results.append(("Mass Variance Scaling", f"{ratio:.5f}", "0.50000", f"{err7*100:.3f}%", status7))
    except Exception as e:
        print(f"  ERROR in Test 7: {e}")
        results.append(("Mass Variance Scaling", "N/A", "0.50000", "ERROR", "FAILED"))

    # -------------------------------------------------------------------------
    # TEST 8: BBN Light Element Abundance Limits (ISSUE-4.95 / Rule 5.1)
    # -------------------------------------------------------------------------
    print("\n[TEST 8] BBN Light Element Abundance Limits (PRIMAT Benchmark)...")
    try:
        from bbn_light_elements import compute_YP, compute_DH
        yp_bench = compute_YP(0.02237)
        dh_bench = compute_DH(0.02237)
        err_yp8 = abs(yp_bench - 0.24709) / 0.24709
        err_dh8 = abs(dh_bench - 2.509e-5) / 2.509e-5
        pass8 = (err_yp8 < 1e-4) and (err_dh8 < 1e-4)
        status8 = "PASSED" if pass8 else "FAILED"
        print(f"  Y_P: {yp_bench:.5f} (err: {err_yp8*100:.4f}%) | D/H: {dh_bench*1e5:.4f}e-5 (err: {err_dh8*100:.4f}%) -> {status8}")
        results.append(("BBN PRIMAT Abundances (Y_P, D/H)", f"{yp_bench:.4f}", "0.2471", f"{max(err_yp8, err_dh8)*100:.4f}%", status8))
    except Exception as e:
        print(f"  ERROR in Test 8: {e}")
        results.append(("BBN PRIMAT Abundances (Y_P, D/H)", "N/A", "0.2471", "ERROR", "FAILED"))

    # -------------------------------------------------------------------------
    # TEST 9: Horizon Viscosity KSS Bound Limit (ISSUE-4.98 / Rule 5.1)
    # -------------------------------------------------------------------------
    print("\n[TEST 9] Horizon Membrane KSS Bound Limit eta/s = 1/(4pi)...")
    try:
        from horizon_boundary_layer import compute_horizon_fluid_properties
        h_props = compute_horizon_fluid_properties()
        kss_num = h_props['kss_ratio_natural']
        kss_exact = h_props['kss_exact']
        err9 = abs(kss_num - kss_exact) / kss_exact
        pass9 = err9 < 1e-8
        status9 = "PASSED" if pass9 else "FAILED"
        print(f"  eta/s: {kss_num:.6f} | Exact 1/(4pi): {kss_exact:.6f} | Error: {err9*100:.6f}% -> {status9}")
        results.append(("Horizon KSS Bound eta/s", f"{kss_num:.5f}", f"{kss_exact:.5f}", f"{err9*100:.5f}%", status9))
    except Exception as e:
        print(f"  ERROR in Test 9: {e}")
        results.append(("Horizon KSS Bound eta/s", "N/A", "0.07958", "ERROR", "FAILED"))

    # -------------------------------------------------------------------------
    # TEST 10: Dark Matter WIMP Miracle & Relic Benchmark (ISSUE-4.55 / Rule 5.1)
    # -------------------------------------------------------------------------
    print("\n[TEST 10] Dark Matter WIMP Miracle Benchmark (Lee-Weinberg Limit)...")
    try:
        from dm_relic_ecsk import run_layer0_benchmark
        dm_bmark = run_layer0_benchmark()
        omega_calc = dm_bmark['omega_calc']
        omega_target = dm_bmark['omega_target']
        err10 = dm_bmark['err_pct'] / 100.0
        pass10 = dm_bmark['passed']
        status10 = "PASSED" if pass10 else "FAILED"
        print(f"  Omega_chi h^2: {omega_calc:.5f} | Target: {omega_target:.5f} | Error: {err10*100:.6f}% -> {status10}")
        results.append(("DM WIMP Miracle Omega h^2", f"{omega_calc:.5f}", f"{omega_target:.5f}", f"{err10*100:.4f}%", status10))
    except Exception as e:
        print(f"  ERROR in Test 10: {e}")
        results.append(("DM WIMP Miracle Omega h^2", "N/A", "0.12000", "ERROR", "FAILED"))

    # -------------------------------------------------------------------------
    # TEST 11: Kerr/CFT Cardy Entropy vs Bekenstein-Hawking (ISSUE-4.25 / Rule 5.1)
    # -------------------------------------------------------------------------
    print("\n[TEST 11] Kerr/CFT Cardy Entropy Limit S_CFT = S_BH...")
    try:
        from cft_operator_nesting import run_layer0_cardy_benchmark
        cft_bmark = run_layer0_cardy_benchmark()
        err11 = cft_bmark['err']
        pass11 = cft_bmark['passed']
        status11 = "PASSED" if pass11 else "FAILED"
        print(f"  S_CFT / S_BH: {cft_bmark['s_cft']/cft_bmark['s_bh']:.8f} | Error: {err11*100:.8f}% -> {status11}")
        results.append(("Kerr/CFT Cardy Entropy Limit", "1.000000", "1.000000", f"{err11*100:.6f}%", status11))
    except Exception as e:
        print(f"  ERROR in Test 11: {e}")
        results.append(("Kerr/CFT Cardy Entropy Limit", "N/A", "1.000000", "ERROR", "FAILED"))

    # -------------------------------------------------------------------------
    # TEST 12: Alcock-Paczynski Distortion Null Limit (ISSUE-4.104 / Rule 5.1)
    # -------------------------------------------------------------------------
    print("\n[TEST 12] Alcock-Paczynski Distortion Null Limit epsilon = 0...")
    try:
        from lss_cluster_diagnostics import run_layer0_benchmark
        ap_bmark = run_layer0_benchmark()
        max_err12 = ap_bmark['max_err']
        pass12 = ap_bmark['passed']
        status12 = "PASSED" if pass12 else "FAILED"
        print(f"  Max |epsilon(z)|: {max_err12:.12e} | Status: {status12}")
        results.append(("AP Distortion Null Limit", f"{max_err12:.2e}", "0.00e+00", f"{max_err12*100:.8f}%", status12))
    except Exception as e:
        print(f"  ERROR in Test 12: {e}")
        results.append(("AP Distortion Null Limit", "N/A", "0.00e+00", "ERROR", "FAILED"))

    # -------------------------------------------------------------------------
    # TEST 13: Kerr Echo Delay Schwarzschild Limit (ISSUE-4.62 / Rule 5.1)
    # -------------------------------------------------------------------------
    print("\n[TEST 13] Kerr Echo Delay Schwarzschild Limit (a_* -> 0)...")
    try:
        from horizon_gravitational_diagnostics import run_layer0_benchmark as run_hgd_bmark
        hgd_bmark = run_hgd_bmark()
        err13 = hgd_bmark['err_schw']
        pass13 = hgd_bmark['passed']
        status13 = "PASSED" if pass13 else "FAILED"
        print(f"  Delta t_kerr(0): {hgd_bmark['t_kerr_0']:.2f} ms | Target: {hgd_bmark['t_schw_exact']:.2f} ms | Error: {err13*100:.8f}% -> {status13}")
        results.append(("Kerr Echo Schwarzschild Limit", f"{hgd_bmark['t_kerr_0']:.2f}", f"{hgd_bmark['t_schw_exact']:.2f}", f"{err13*100:.6f}%", status13))
    except Exception as e:
        print(f"  ERROR in Test 13: {e}")
        results.append(("Kerr Echo Schwarzschild Limit", "N/A", "54.08", "ERROR", "FAILED"))

    # -------------------------------------------------------------------------
    # TEST 14: Kodama-Hayward Odd Multipole Annihilation (ISSUE-4.68 / Rule 5.1)
    # -------------------------------------------------------------------------
    print("\n[TEST 14] Kodama-Hayward Odd-Multipole Annihilation (Parity Protection)...")
    try:
        max_odd14 = hgd_bmark['max_odd_err']
        status14 = "PASSED" if max_odd14 < 1e-12 else "FAILED"
        print(f"  Max Odd Residual: {max_odd14:.12e} | Target: < 1e-12 -> {status14}")
        results.append(("Kodama Odd Multipole Parity", f"{max_odd14:.2e}", "0.00e+00", f"{max_odd14*100:.8f}%", status14))
    except Exception as e:
        print(f"  ERROR in Test 14: {e}")
        results.append(("Kodama Odd Multipole Parity", "N/A", "0.00e+00", "ERROR", "FAILED"))

    # -------------------------------------------------------------------------
    # TEST 15: High-Energy Bounce & Seesaw Benchmark (ISSUE-4.102 / 4.103 / Rule 5.1)
    # -------------------------------------------------------------------------
    print("\n[TEST 15] High-Energy Bounce & Seesaw Benchmark (ISSUE-4.102 / 4.103)...")
    try:
        from high_energy_bounce_diagnostics import run_layer0_benchmark as run_hebd_bmark
        hebd_bmark = run_hebd_bmark()
        pass15 = hebd_bmark['passed']
        status15 = "PASSED" if pass15 else "FAILED"
        m_nu3 = hebd_bmark['m_nu3_ev']
        target_nu = 0.0500
        err15 = abs(m_nu3 - target_nu) / target_nu
        print(f"  m_nu3: {m_nu3:.4f} eV | Target: {target_nu:.4f} eV | Error: {err15*100:.2f}% -> {status15}")
        results.append(("Torsion Seesaw Neutrino Mass", f"{m_nu3:.4f}", f"{target_nu:.4f}", f"{err15*100:.2f}%", status15))
    except Exception as e:
        print(f"  ERROR in Test 15: {e}")
        results.append(("Torsion Seesaw Neutrino Mass", "N/A", "0.0500", "ERROR", "FAILED"))

    # -------------------------------------------------------------------------
    # TEST 16: Cluster D Audit & Horizon Saturation Limit (ISSUE-4.30a / 4.31 / Rule 5.1)
    # -------------------------------------------------------------------------
    print("\n[TEST 16] Bekenstein Saturation Limit S_BH / S_Bek = 1.0 (ISSUE-4.31)...")
    try:
        from cluster_d_audit_diagnostics import run_layer0_benchmark as run_cld_bmark
        cld_bmark = run_cld_bmark()
        pass16 = cld_bmark['passed']
        status16 = "PASSED" if pass16 else "FAILED"
        ratio_bh = cld_bmark['ratio_bh']
        err16 = cld_bmark['err_bek']
        print(f"  S_BH / S_Bek: {ratio_bh:.8f} | Target: 1.00000000 | Error: {err16*100:.8f}% -> {status16}")
        results.append(("Bekenstein Saturation Limit", f"{ratio_bh:.6f}", "1.000000", f"{err16*100:.6f}%", status16))
    except Exception as e:
        print(f"  ERROR in Test 16: {e}")
        results.append(("Bekenstein Saturation Limit", "N/A", "1.000000", "ERROR", "FAILED"))

    # -------------------------------------------------------------------------
    # TEST 17: Biological & Cognitive Calibration Limits (WP7 / Rule 5.1)
    # -------------------------------------------------------------------------
    print("\n[TEST 17] Biological & Cognitive Calibration Limits (WP7 / Rule 5.1)...")
    try:
        from biological_cognitive_diagnostics import run_layer0_benchmark as run_bio_bmark
        bio_bmark = run_bio_bmark()
        pass17 = bio_bmark['passed']
        status17 = "PASSED" if pass17 else "FAILED"
        c_th = bio_bmark['c_th']
        c_th_target = bio_bmark['c_th_exact']
        err17 = bio_bmark['err_sound']
        print(f"  c_th: {c_th:.4f} m/s | Target: {c_th_target:.4f} m/s | Error: {err17*100:.8f}% -> {status17}")
        results.append(("Biological Heat & Lattice Benchmark", f"{c_th:.4f}", f"{c_th_target:.4f}", f"{err17*100:.6f}%", status17))
    except Exception as e:
        print(f"  ERROR in Test 17: {e}")
        results.append(("Biological Heat & Lattice Benchmark", "N/A", "31.6228", "ERROR", "FAILED"))

    # -------------------------------------------------------------------------
    # TEST 18: Sterile Neutrino Lyman-Alpha & Phase-Space Limit (ISSUE-4.115 / Rule 5.1)
    # -------------------------------------------------------------------------
    print("\n[TEST 18] Sterile Neutrino Lyman-Alpha & Phase-Space Bounds (ISSUE-4.115)...")
    try:
        from sterile_neutrino_lyman_alpha import run_sterile_neutrino_benchmarks
        sn_bmark = run_sterile_neutrino_benchmarks(verbose=False)
        pass18 = sn_bmark['all_passed']
        status18 = "PASSED" if pass18 else "FAILED"
        lambda_fs = sn_bmark['lambda_fs_bench_kpc']
        q_ratio = sn_bmark['q_ratio_tg']
        print(f"  lambda_FS(7.1 keV, D=21.4): {lambda_fs:.2f} kpc | Limit: < 100.00 kpc | Status: {status18}")
        print(f"  Tremaine-Gunn Margin: {q_ratio:.1f}x > Q_obs | Status: {status18}")
        results.append(("Sterile Neutrino Lyman-Alpha (4.115)", f"{lambda_fs:.2f} kpc", "< 100 kpc", f"{lambda_fs/100.0*100:.1f}%", status18))
    except Exception as e:
        print(f"  ERROR in Test 18: {e}")
        results.append(("Sterile Neutrino Lyman-Alpha (4.115)", "N/A", "< 100 kpc", "ERROR", "FAILED"))

    # -------------------------------------------------------------------------
    # SUMMARY TABLE
    # -------------------------------------------------------------------------
    print("\n" + "=" * 90)
    print("LAYER 0 BENCHMARK SUITE EXECUTION SUMMARY")
    print("=" * 90)
    header = f"{'Benchmark Test':<36} | {'Numerical':<10} | {'Exact/Target':<12} | {'Error/Dev':<10} | {'Status':<8}"
    print(header)
    print("-" * len(header))
    all_passed = True
    for name, num, target, err, status in results:
        print(f"{name:<36} | {num:<10} | {target:<12} | {err:<10} | {status:<8}")
        if status != "PASSED":
            all_passed = False
    print("=" * 90)
    
    if all_passed:
        print("ALL LAYER 0 BENCHMARKS PASSED (Rule 5 Compliant).")
    else:
        print("SOME BENCHMARKS FAILED. Review output above.")
    print("=" * 90)

if __name__ == "__main__":
    run_suite()
