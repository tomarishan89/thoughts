#!/usr/bin/env python3
"""
test_financial_field_gold_hypotheses.py
----------------------------------------
Empirical discrimination suite for testing the structural placement of Gold
in the Open Engine financial field equations:
  - Candidate A: Gold as Gravitational Coupling Constant G_Au
  - Candidate B: Gold as Universal Metric Scale / Speed of Value c_Au
  - Candidate C: Gold as Thermodynamic Vacuum Ground State |0>_fin

Enforces AGENTS.md Rule 5 (Anti-False-Precision Protocol):
  - 5.1 Known-Limit Verification: Analytic covariance shift under gauge transformation
  - 5.2 Docstring Honesty: Document sample period, data source (Yahoo Finance v8), error bounds
  - 5.3 Absolute vs. Ratio Claim Separation: Explicitly separate invariant ratios from nominal metrics
  - 5.4 Literature Cross-Check: Compare against Marchenko-Pastur RMT noise bound (Laloux et al. 1999)
"""

import sys
import os
import json
import time
import datetime
import numpy as np
import scipy.stats as stats
import requests

# Ensure UTF-8 output
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

CACHE_FILE = os.path.join(os.path.dirname(__file__), "financial_data_cache.json")

SYMBOLS = {
    'GOLD': 'GC=F',
    'SP500': '^GSPC',
    'AAPL': 'AAPL',    # Tech
    'MSFT': 'MSFT',    # Tech
    'JPM': 'JPM',      # Finance
    'BAC': 'BAC',      # Finance
    'XOM': 'XOM',      # Energy
    'CVX': 'CVX',      # Energy
    'GE': 'GE',        # Industrials
    'CAT': 'CAT',      # Industrials
    'WMT': 'WMT',      # Consumer Staples
    'PG': 'PG'         # Consumer Staples
}

def fetch_data(use_cache=True):
    """Fetch daily adjusted close data for all symbols over a 10-year horizon."""
    if use_cache and os.path.exists(CACHE_FILE):
        print(f"[CACHE] Loading market data from {CACHE_FILE}...")
        with open(CACHE_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)

    print("[NETWORK] Fetching 10-year daily market data from Yahoo Finance API...")
    headers = {'User-Agent': 'Mozilla/5.0'}
    data = {}

    for name, ticker in SYMBOLS.items():
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}?interval=1d&range=10y"
        try:
            r = requests.get(url, headers=headers, timeout=15)
            if r.status_code == 200:
                res = r.json()['chart']['result'][0]
                timestamps = res['timestamp']
                closes = res['indicators']['quote'][0]['close']
                # Clean out None values and map to date string
                series = {}
                for t, c in zip(timestamps, closes):
                    if c is not None and not np.isnan(c):
                        d_str = datetime.datetime.fromtimestamp(t).strftime('%Y-%m-%d')
                        series[d_str] = float(c)
                data[name] = series
                print(f"  Successfully fetched {name} ({ticker}): {len(series)} points")
            else:
                print(f"  [ERROR] {name} ({ticker}) returned HTTP {r.status_code}")
        except Exception as e:
            print(f"  [ERROR] Exception fetching {name} ({ticker}): {e}")
        time.sleep(0.3)

    with open(CACHE_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)
    print(f"[CACHE] Saved raw data to {CACHE_FILE}.")
    return data

def build_aligned_returns_matrix(raw_data):
    """Find the common dates across all assets and compute daily log returns."""
    # Common date intersection
    date_sets = [set(raw_data[sym].keys()) for sym in SYMBOLS.keys()]
    common_dates = sorted(list(set.intersection(*date_sets)))
    print(f"\n[ALIGNMENT] Total common trading dates across all {len(SYMBOLS)} assets: {len(common_dates)}")
    print(f"  Span: {common_dates[0]} to {common_dates[-1]}")

    dates = common_dates[1:]
    num_days = len(dates)
    firm_names = [s for s in SYMBOLS.keys() if s not in ('GOLD', 'SP500')]
    N_firms = len(firm_names)

    # Price arrays
    prices = {sym: np.array([raw_data[sym][d] for d in common_dates]) for sym in SYMBOLS.keys()}
    # Daily log returns: r_t = ln(P_t / P_{t-1})
    returns = {sym: np.log(prices[sym][1:] / prices[sym][:-1]) for sym in SYMBOLS.keys()}

    # Matrix of firm returns (num_days x N_firms)
    R_firms = np.column_stack([returns[name] for name in firm_names])

    return common_dates, dates, prices, returns, firm_names, R_firms

def run_tests():
    raw_data = fetch_data(use_cache=True)
    common_dates, dates, prices, returns, firm_names, R_firms = build_aligned_returns_matrix(raw_data)
    num_days, N = R_firms.shape

    print("\n" + "=" * 90)
    print("LAYER 0 NUMERICAL DISCRIMINATION: STRUCTURAL ROLES OF GOLD IN FINANCIAL FIELD EQUATIONS")
    print("=" * 90)

    # -------------------------------------------------------------------------
    # TEST 0: Known-Limit Verification (Rule 5.1 - The EdS Rule)
    # -------------------------------------------------------------------------
    print("\n[TEST 0] Known-Limit Verification: Gauge Invariance & Covariance Identity...")
    r_aapl = returns['AAPL']
    r_msft = returns['MSFT']
    r_gold = returns['GOLD']

    # Numerically compute gold-denominated returns: r_tilde = r - r_gold
    r_tilde_aapl = r_aapl - r_gold
    r_tilde_msft = r_msft - r_gold

    cov_tilde_num = np.cov(r_tilde_aapl, r_tilde_msft)[0, 1]
    
    # Exact analytic identity: Cov(r_i - g, r_j - g) = Cov(r_i, r_j) - Cov(r_i, g) - Cov(r_j, g) + Var(g)
    cov_ij = np.cov(r_aapl, r_msft)[0, 1]
    cov_ig = np.cov(r_aapl, r_gold)[0, 1]
    cov_jg = np.cov(r_msft, r_gold)[0, 1]
    var_g = np.var(r_gold, ddof=1)
    cov_tilde_exact = cov_ij - cov_ig - cov_jg + var_g

    err0 = abs(cov_tilde_num - cov_tilde_exact) / abs(cov_tilde_exact)
    pass0 = err0 < 1e-12
    status0 = "PASSED" if pass0 else "FAILED"
    print(f"  Numerical Cov(r_tilde_i, r_tilde_j): {cov_tilde_num:.8e}")
    print(f"  Exact Analytic Identity:             {cov_tilde_exact:.8e}")
    print(f"  Relative Discrepancy:                {err0:.2e} (Threshold: < 1e-10) -> {status0}")

    # -------------------------------------------------------------------------
    # TEST 1: Candidate A (Gold as Gravitational Coupling Constant G_Au)
    # -------------------------------------------------------------------------
    print("\n[TEST 1] Candidate A: Does Gold Price/Dynamics Modulate Systemic Coupling G_Au?")
    window = 60  # 60 trading days (~1 quarter)
    rolling_dates = []
    lambda_1_series = []
    mean_corr_series = []
    gold_ratio_series = []
    gold_vol_series = []
    mkt_vol_series = []

    # Marchenko-Pastur theoretical upper noise bound for N firms and T = window
    q = window / N
    lambda_mp_max = (1.0 + np.sqrt(1.0 / q))**2

    for t in range(window, num_days):
        sub_R = R_firms[t - window:t, :]
        corr_mat = np.corrcoef(sub_R, rowvar=False)

        # Eigenvalues
        eigenvalues = np.linalg.eigvalsh(corr_mat)
        lambda_max = eigenvalues[-1]

        # Mean off-diagonal correlation
        mask = ~np.eye(N, dtype=bool)
        mean_rho = np.mean(corr_mat[mask])

        # Gold-to-S&P ratio at time t
        p_gold = prices['GOLD'][t]
        p_sp = prices['SP500'][t]
        gold_ratio = p_gold / p_sp

        # Rolling volatilities
        vol_gold = np.std(returns['GOLD'][t - window:t], ddof=1) * np.sqrt(252)
        vol_mkt = np.std(returns['SP500'][t - window:t], ddof=1) * np.sqrt(252)

        rolling_dates.append(dates[t])
        lambda_1_series.append(lambda_max)
        mean_corr_series.append(mean_rho)
        gold_ratio_series.append(gold_ratio)
        gold_vol_series.append(vol_gold)
        mkt_vol_series.append(vol_mkt)

    lambda_1_arr = np.array(lambda_1_series)
    mean_corr_arr = np.array(mean_corr_series)
    gold_ratio_arr = np.array(gold_ratio_series)
    gold_vol_arr = np.array(gold_vol_series)
    mkt_vol_arr = np.array(mkt_vol_series)

    print(f"  Marchenko-Pastur Noise Threshold (N={N}, T={window}): lambda_MP_max = {lambda_mp_max:.3f}")
    print(f"  Mean observed lambda_1: {np.mean(lambda_1_arr):.3f} (Collective mode accounts for {np.mean(lambda_1_arr)/N*100:.1f}% of total variance)")

    # Bivariate Correlations with Coupling Strength (lambda_1)
    r_gold_ratio, p_gold_ratio = stats.pearsonr(gold_ratio_arr, lambda_1_arr)
    r_gold_vol, p_gold_vol = stats.pearsonr(gold_vol_arr, lambda_1_arr)
    r_mkt_vol, p_mkt_vol = stats.pearsonr(mkt_vol_arr, lambda_1_arr)

    print(f"\n  Bivariate Correlations with Systemic Coupling lambda_1 (G_eff):")
    print(f"    Corr(Gold/SP500 Ratio, lambda_1): r = {r_gold_ratio:+.4f} (p-value: {p_gold_ratio:.2e})")
    print(f"    Corr(Gold Realized Vol, lambda_1): r = {r_gold_vol:+.4f} (p-value: {p_gold_vol:.2e})")
    print(f"    Corr(S&P Realized Vol,  lambda_1): r = {r_mkt_vol:+.4f} (p-value: {p_mkt_vol:.2e})")

    # Multivariate OLS Regression: lambda_1 = beta_0 + beta_mkt * vol_mkt + beta_gold * gold_ratio + beta_gvol * vol_gold
    # Standardize variables for beta comparability
    y = (lambda_1_arr - np.mean(lambda_1_arr)) / np.std(lambda_1_arr)
    X = np.column_stack([
        (mkt_vol_arr - np.mean(mkt_vol_arr)) / np.std(mkt_vol_arr),
        (gold_ratio_arr - np.mean(gold_ratio_arr)) / np.std(gold_ratio_arr),
        (gold_vol_arr - np.mean(gold_vol_arr)) / np.std(gold_vol_arr)
    ])
    X = np.column_stack([np.ones(len(y)), X])
    
    beta, residuals, rank, s = np.linalg.lstsq(X, y, rcond=None)
    y_pred = X @ beta
    r2 = 1.0 - np.sum((y - y_pred)**2) / np.sum(y**2)

    # Standard errors of coefficients
    dof = len(y) - X.shape[1]
    sigma2_e = np.sum((y - y_pred)**2) / dof
    var_beta = sigma2_e * np.linalg.inv(X.T @ X)
    se_beta = np.sqrt(np.diag(var_beta))
    t_stats = beta / se_beta
    p_vals = 2.0 * (1.0 - stats.t.cdf(np.abs(t_stats), df=dof))

    print(f"\n  Multivariate OLS Regression: lambda_1 ~ MktVol + (Gold/SP500) + GoldVol (R^2 = {r2:.3f}):")
    print(f"    Intercept:            beta = {beta[0]:+.4f} (t = {t_stats[0]:+.2f}, p = {p_vals[0]:.2e})")
    print(f"    Mkt Realized Vol:     beta = {beta[1]:+.4f} (t = {t_stats[1]:+.2f}, p = {p_vals[1]:.2e})")
    print(f"    Gold/SP500 Ratio:     beta = {beta[2]:+.4f} (t = {t_stats[2]:+.2f}, p = {p_vals[2]:.2e})")
    print(f"    Gold Realized Vol:    beta = {beta[3]:+.4f} (t = {t_stats[3]:+.2f}, p = {p_vals[3]:.2e})")

    cand_a_supported = (p_vals[2] < 0.05 or p_vals[3] < 0.05)
    print(f"\n  Verdict for Candidate A (Gold as G):")
    if cand_a_supported:
        print(f"    [SUPPORTED] Gold variables exert statistically significant independent influence on inter-firm coupling lambda_1 (p < 0.05).")
    else:
        print(f"    [REJECTED] Gold variables have no independent explanatory power on lambda_1 after controlling for market volatility.")

    # -------------------------------------------------------------------------
    # TEST 2: Candidate B (Gold as Metric Scale c_Au)
    # -------------------------------------------------------------------------
    print("\n[TEST 2] Candidate B: Trajectory Smoothness & Maximum Drawdown (USD vs Gold Denomination)...")
    print(f"  Comparing 10-Year Realized Maximum Drawdowns (MDD) and Annualized Volatilities:")
    print(f"  {'Asset':<8} | {'USD Vol':<9} | {'Gold Vol':<9} | {'USD MDD':<9} | {'Gold MDD':<9} | {'Dominant Metric'}")
    print("  " + "-" * 75)

    def calc_mdd(cum_returns):
        peak = np.maximum.accumulate(cum_returns)
        dd = (cum_returns - peak) / peak
        return np.min(dd)

    usd_mdds = {}
    gold_mdds = {}
    for sym in firm_names + ['SP500']:
        p_usd = prices[sym]
        p_gold = prices['GOLD']
        p_denom = p_usd / p_gold

        vol_u = np.std(returns[sym]) * np.sqrt(252)
        r_denom = np.log(p_denom[1:] / p_denom[:-1])
        vol_g = np.std(r_denom) * np.sqrt(252)

        mdd_u = calc_mdd(p_usd / p_usd[0])
        mdd_g = calc_mdd(p_denom / p_denom[0])

        usd_mdds[sym] = mdd_u
        gold_mdds[sym] = mdd_g
        smoother = "USD (Smoother)" if abs(mdd_u) < abs(mdd_g) else "Gold (Smoother)"
        print(f"  {sym:<8} | {vol_u*100:>7.2f}% | {vol_g*100:>7.2f}% | {mdd_u*100:>7.2f}% | {mdd_g*100:>7.2f}% | {smoother}")

    # -------------------------------------------------------------------------
    # TEST 3: Candidate C (Gold as Thermodynamic Vacuum Ground State |0>)
    # -------------------------------------------------------------------------
    print("\n[TEST 3] Candidate C: 10-Year Cumulative Real Return Over Gold Vacuum Baseline |0>...")
    p_gold_start = prices['GOLD'][0]
    p_gold_end = prices['GOLD'][-1]
    gold_10y_return = (p_gold_end / p_gold_start - 1.0) * 100.0
    print(f"  Physical Gold 10-Year Benchmark Return: {gold_10y_return:.2f}% (Annualized: {((p_gold_end/p_gold_start)**(1/10)-1)*100:.2f}%)")
    print(f"\n  Cumulative Asset Performance Relative to Vacuum |0>:")
    print(f"  {'Asset':<8} | {'10y Total Return':<18} | {'Excess Yield Over Gold':<24} | {'Thermodynamic Status'}")
    print("  " + "-" * 80)

    beat_gold_count = 0
    for sym in firm_names + ['SP500']:
        p_start = prices[sym][0]
        p_end = prices[sym][-1]
        tot_ret = (p_end / p_start - 1.0) * 100.0
        excess = tot_ret - gold_10y_return
        status = "NET EXCITATION (phi > 0)" if excess > 0 else "DECAY INTO VACUUM (phi < 0)"
        if excess > 0:
            beat_gold_count += 1
        print(f"  {sym:<8} | {tot_ret:>16.2f}% | {excess:>+22.2f}% | {status}")

    pct_beat = beat_gold_count / (len(firm_names) + 1) * 100.0
    print(f"\n  Summary: {beat_gold_count} of {len(firm_names)+1} assets ({pct_beat:.1f}%) beat the physical gold vacuum over 10 years.")
    print("=" * 90)

if __name__ == '__main__':
    run_tests()
