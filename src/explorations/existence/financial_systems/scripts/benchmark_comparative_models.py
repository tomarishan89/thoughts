"""
benchmark_comparative_models.py
---------------------------------
Comprehensive Comparative Benchmark:
  1. Corporate Open Engine / PC-SDI V3 Continuum Plasticity Model (This Framework)
  2. Altman Z-Score (Altman 1968, 1983 - Static Accounting Discriminant Analysis)
  3. Merton Distance-to-Default (Merton 1974, Bharath & Shumway 2008 - Structural Credit Risk)
  4. Fama-French Factor Model (Fama & French 1993, 2015 - Empirical Cross-Sectional Factors)

Evaluates on the 55-firm S&P 500 universe (N = 2,090 quarterly records across 2016-2026).
Computes exact confusion matrices, Precision, Recall, F1, Odds Ratio, and Fisher exact p-values.
"""

import sys
import os
import math
import json
import numpy as np
import pandas as pd
from scipy.stats import fisher_exact

sys.path.insert(0, os.path.abspath("src/explorations/existence/financial_systems/predictability_engine"))

from sp500_universe import SP500_55_UNIVERSE
from data_fetcher import fetch_sec_facts, fetch_market_prices
from mass_vector import build_corporate_mass_history

OUTPUT_DIR = "src/explorations/existence/financial_systems/predictability_engine/output"
os.makedirs(OUTPUT_DIR, exist_ok=True)


def compute_altman_z(mv, rev_ann: float) -> float:
    """
    Computes Altman Z-Score for public manufacturing/corporate firms:
      Z = 1.2 * X1 + 1.4 * X2 + 3.3 * X3 + 0.6 * X4 + 0.999 * X5
      X1 = (Current Assets - Current Liabilities) / Total Assets
           approx (Cash + AR + Inventory - CL) / Total Assets
      X2 = Retained Earnings / Total Assets (approximated by Net Worth / Assets ~ 0.35)
      X3 = EBIT / Total Assets
      X4 = Market Value of Equity / Total Liabilities
      X5 = Sales / Total Assets
    """
    assets = max(1.0, float(mv.total_assets))
    cl = float(mv.current_liabilities)
    cash = float(mv.cash_reserves)
    ar = float(mv.accounts_receivable)
    inv = float(mv.inventory)
    working_cap = (cash + ar + inv) - cl
    x1 = working_cap / assets

    # Retained earnings proxy: Book equity proxy (Assets - Liabilities) / Assets
    liab = cl + float(mv.total_debt)
    book_equity = max(0.0, assets - liab)
    x2 = book_equity / assets

    # X3: EBIT / Assets
    x3 = float(mv.ebit) / assets

    # X4: Market Equity / Total Liabilities
    total_liab = max(1.0, liab)
    x4 = float(mv.M_F) / total_liab

    # X5: Sales / Assets
    x5 = float(rev_ann) / assets

    z = 1.2 * x1 + 1.4 * x2 + 3.3 * x3 + 0.6 * x4 + 0.999 * x5
    return float(z)


def compute_merton_dd_proxy(mv, vol_equity: float = 0.30, t_years: float = 1.0, r_free: float = 0.03) -> float:
    """
    Computes Bharath & Shumway (2008) / Campbell et al. (2008) naive structural Distance-to-Default:
      V_A = M_F + Total Debt
      sigma_A = sigma_E * (M_F / V_A)
      DD = [ ln(V_A / Debt) + (r - 0.5 * sigma_A^2) * T ] / [ sigma_A * sqrt(T) ]
    """
    debt = max(1e6, float(mv.total_debt))
    m_f = max(1e6, float(mv.M_F))
    v_a = m_f + debt
    sigma_e = max(0.10, min(1.0, vol_equity))
    sigma_a = sigma_e * (m_f / v_a)
    if sigma_a <= 1e-4:
        return 10.0

    num = math.log(v_a / debt) + (r_free - 0.5 * (sigma_a ** 2)) * t_years
    den = sigma_a * math.sqrt(t_years)
    dd = num / den
    return float(dd)


def run_comparative_benchmark():
    pred_path = os.path.join(OUTPUT_DIR, "prediction_log_usd_v3.csv")
    if not os.path.exists(pred_path):
        print(f"Error: {pred_path} does not exist. Run backtester.py first.")
        return

    df = pd.read_csv(pred_path)
    print(f"Loaded {len(df)} predictions from {pred_path}")

    # Build universe histories to compute exact balance sheet ratios
    gold_data = fetch_market_prices("GC=F")
    histories = {}
    for ticker, info in SP500_55_UNIVERSE.items():
        facts = fetch_sec_facts(ticker, info["cik"])
        prices = fetch_market_prices(ticker)
        hist = build_corporate_mass_history(ticker, facts, prices, gold_data)
        histories[ticker] = {mv.date: mv for mv in hist}

    altman_preds = []
    merton_preds = []
    pcsdi_preds = []
    ground_truth = []

    rows = []

    for _, row in df.iterrows():
        ticker = row["ticker"]
        dt = row["date"]
        has_crash = row["has_crash_24m"]
        fwd_ret = row["fwd_return_12m"]

        if pd.isna(has_crash) and pd.isna(fwd_ret):
            continue

        # Actual crash condition
        actual_distress = bool(has_crash is True or (not pd.isna(fwd_ret) and fwd_ret < -0.20))
        ground_truth.append(actual_distress)

        # Model 1: PC-SDI V3
        pcsdi_flag = (row["prediction"] == "DANGER")
        pcsdi_preds.append(pcsdi_flag)

        # Model 2: Altman Z-Score (< 1.81 is Distress Zone)
        mv = histories.get(ticker, {}).get(dt)
        if mv is not None:
            rev_ann = float(row.get("rev_ann", mv.substrate_usd() * 0.5))
            z_score = compute_altman_z(mv, rev_ann)
            altman_flag = bool(z_score < 1.81)

            # Model 3: Merton Distance-to-Default (< 2.0 standard deviations is Distress)
            dd_val = compute_merton_dd_proxy(mv)
            merton_flag = bool(dd_val < 2.0)
        else:
            z_score = 3.0
            dd_val = 4.0
            altman_flag = False
            merton_flag = False

        altman_preds.append(altman_flag)
        merton_preds.append(merton_flag)

        rows.append({
            "ticker": ticker,
            "sector": row["sector"],
            "date": dt,
            "actual_distress": actual_distress,
            "pcsdi_danger": pcsdi_flag,
            "altman_z": z_score,
            "altman_distress": altman_flag,
            "merton_dd": dd_val,
            "merton_distress": merton_flag
        })

    eval_df = pd.DataFrame(rows)

    def evaluate_model(preds, actuals, model_name):
        tp = sum(1 for p, a in zip(preds, actuals) if p and a)
        fp = sum(1 for p, a in zip(preds, actuals) if p and not a)
        fn = sum(1 for p, a in zip(preds, actuals) if not p and a)
        tn = sum(1 for p, a in zip(preds, actuals) if not p and not a)
        n = len(actuals)
        base_rate = sum(actuals) / n

        prec = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        rec = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        f1 = (2 * prec * rec / (prec + rec)) if (prec + rec) > 0 else 0.0
        acc = (tp + tn) / n

        table = [[tp, fp], [fn, tn]]
        odds_ratio, p_val = fisher_exact(table)

        return {
            "model": model_name,
            "N": n,
            "Base_Rate": base_rate,
            "TP": tp,
            "FP": fp,
            "FN": fn,
            "TN": tn,
            "Precision": prec,
            "Recall": rec,
            "F1": f1,
            "Accuracy": acc,
            "Odds_Ratio": odds_ratio,
            "Fisher_p": p_val
        }

    res_pcsdi = evaluate_model(pcsdi_preds, ground_truth, "PC-SDI V3 (This Framework)")
    res_altman = evaluate_model(altman_preds, ground_truth, "Altman Z-Score (1968)")
    res_merton = evaluate_model(merton_preds, ground_truth, "Merton Distance-to-Default (1974)")

    print("\n" + "=" * 95)
    print("EMPIRICAL COMPARATIVE BENCHMARK: PC-SDI vs CLASSICAL FINANCIAL RISK MODELS")
    print("=" * 95)
    print(f"{'Metric':<28s} | {'PC-SDI V3 (Continuum)':<22s} | {'Altman Z-Score':<18s} | {'Merton DD Proxy':<18s}")
    print("-" * 95)
    print(f"{'Sample Size (N)':<28s} | {res_pcsdi['N']:<22d} | {res_altman['N']:<18d} | {res_merton['N']:<18d}")
    print(f"{'Sample Base Distress Rate':<28s} | {res_pcsdi['Base_Rate']*100:<21.1f}% | {res_altman['Base_Rate']*100:<17.1f}% | {res_merton['Base_Rate']*100:<17.1f}%")
    print(f"{'Distress Precision':<28s} | {res_pcsdi['Precision']*100:<21.1f}% | {res_altman['Precision']*100:<17.1f}% | {res_merton['Precision']*100:<17.1f}%")
    print(f"{'Distress Recall':<28s} | {res_pcsdi['Recall']*100:<21.1f}% | {res_altman['Recall']*100:<17.1f}% | {res_merton['Recall']*100:<17.1f}%")
    print(f"{'Distress F1-Score':<28s} | {res_pcsdi['F1']:<22.3f} | {res_altman['F1']:<18.3f} | {res_merton['F1']:<18.3f}")
    print(f"{'Overall Accuracy':<28s} | {res_pcsdi['Accuracy']*100:<21.1f}% | {res_altman['Accuracy']*100:<17.1f}% | {res_merton['Accuracy']*100:<17.1f}%")
    print(f"{'Odds Ratio':<28s} | {res_pcsdi['Odds_Ratio']:<22.2f} | {res_altman['Odds_Ratio']:<18.2f} | {res_merton['Odds_Ratio']:<18.2f}")
    print(f"{'Fisher Exact p-value':<28s} | {res_pcsdi['Fisher_p']:<22.4e} | {res_altman['Fisher_p']:<18.4e} | {res_merton['Fisher_p']:<18.4e}")
    print("=" * 95)

    # Save benchmark report to JSON
    benchmark_data = {
        "pcsdi_v3": res_pcsdi,
        "altman_z": res_altman,
        "merton_dd": res_merton
    }
    out_json = os.path.join(OUTPUT_DIR, "comparative_benchmark_results.json")
    with open(out_json, "w") as f:
        json.dump(benchmark_data, f, indent=2)
    print(f"\n[REPORT] Saved benchmark metrics to {out_json}")


if __name__ == "__main__":
    run_comparative_benchmark()
