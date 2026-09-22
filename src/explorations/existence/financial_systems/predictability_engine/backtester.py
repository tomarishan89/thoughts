"""
backtester.py
-------------
Core Backtesting and Forward-Scoring Engine.
Evaluates the SDI/VAM Corporate Predictability framework across the validation universe:
  1. Computes quarterly MassVector histories (2016-2026)
  2. Runs parallel backtests: USD-Nominal vs. Gold-Normalized
  3. Generates forward predictions (HEALTHY, CAUTION, DANGER)
  4. Computes actual 6m, 12m, and 24m forward returns and max drawdowns
  5. Scores precision, recall, F1, and lead-time metrics for known collapses
"""

import sys
import os
import json
import csv
import math
import datetime
from typing import List, Dict, Any, Tuple
import numpy as np

# Ensure local package directory is on sys.path
_current_dir = os.path.dirname(os.path.abspath(__file__))
if _current_dir not in sys.path:
    sys.path.insert(0, _current_dir)

from config import (
    UNIVERSE_VALIDATION, GOLD_SYMBOL, SP500_SYMBOL,
    OUTPUT_DIR, BACKTEST_CONFIG
)
from data_fetcher import fetch_sec_facts, fetch_market_prices
from mass_vector import (
    MassVector, build_corporate_mass_history,
    compute_vam, compute_sdi, classify_regime
)


def precompute_company_forward_outcomes(
    prices: List[dict],
    quarter_dates: List[str],
    horizons_months: List[int] = [6, 12, 24]
) -> Dict[str, Dict[str, Any]]:
    """
    Precomputes forward returns and drawdowns for all quarter dates in a single pass.
    Avoids millions of redundant string parsing operations.
    """
    # Parse dates once
    parsed_prices = []
    for p in prices:
        try:
            dt = datetime.datetime.strptime(p["date"], "%Y-%m-%d").date()
            parsed_prices.append((dt, float(p["close"])))
        except (ValueError, KeyError):
            continue

    parsed_prices.sort(key=lambda x: x[0])
    dates_only = [p[0] for p in parsed_prices]
    closes_only = [p[1] for p in parsed_prices]
    n_prices = len(parsed_prices)

    outcomes_by_date = {}

    for q_date_str in quarter_dates:
        curr_dt = datetime.datetime.strptime(q_date_str, "%Y-%m-%d").date()
        
        # Binary search for start index
        import bisect
        start_idx = bisect.bisect_left(dates_only, curr_dt)
        if start_idx >= n_prices:
            outcomes_by_date[q_date_str] = {
                f"return_{m}m": None for m in horizons_months
            }
            continue

        base_price = closes_only[start_idx]
        outcomes = {}

        for m in horizons_months:
            target_dt = curr_dt + datetime.timedelta(days=int(m * 30.4375))
            end_idx = bisect.bisect_right(dates_only, target_dt)
            window_closes = closes_only[start_idx:end_idx]

            if len(window_closes) > 1 and base_price > 0:
                end_price = window_closes[-1]
                fwd_return = (end_price - base_price) / base_price
                min_close = min(window_closes)
                max_drawdown = (min_close - base_price) / base_price

                outcomes[f"return_{m}m"] = float(fwd_return)
                outcomes[f"drawdown_{m}m"] = float(max_drawdown)
                outcomes[f"has_crash_{m}m"] = bool(max_drawdown <= BACKTEST_CONFIG["drawdown_threshold"])
            else:
                outcomes[f"return_{m}m"] = None
                outcomes[f"drawdown_{m}m"] = None
                outcomes[f"has_crash_{m}m"] = None

        outcomes_by_date[q_date_str] = outcomes

    return outcomes_by_date


def run_single_backtest(
    universe_data: Dict[str, Any],
    gold_data: List[dict],
    mode: str = "usd",
    alpha: float = 0.0
) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    """
    Executes a complete historical backtest run in either 'usd' or 'gold' mode,
    with optional productivity correction coefficient alpha.
    """
    prediction_log = []
    window = BACKTEST_CONFIG["sdi_window_quarters"]

    # Gold price map for vacuum drift benchmark
    gold_price_by_date = {g["date"]: g["close"] for g in gold_data}
    sorted_gold_dates = sorted(gold_price_by_date.keys())

    for ticker, comp_data in universe_data.items():
        history: List[MassVector] = comp_data["history"]
        prices: List[dict] = comp_data["prices"]

        for i in range(window, len(history)):
            mv = history[i]
            sdi_eff, sdi_lin, mf_growth, sub_growth, prod_growth = compute_sdi(
                history, i, mode=mode, window=window, alpha=alpha
            )
            
            # In gold mode, evaluate real thermodynamic substrate decay
            if mode == "gold":
                vam = compute_vam(mv.as_array_gold())
            else:
                vam = compute_vam(mv.as_array_usd())

            regime, prediction, confidence = classify_regime(sdi_eff, vam, sub_growth, mf_growth)
            fwd_outcomes = comp_data.get("fwd_outcomes", {}).get(mv.date, {})

            # Determine if prediction was successful
            # DANGER prediction succeeds if drawdown <= -20% or negative return in 12m or 24m
            is_correct = None
            crash_12m = fwd_outcomes.get("has_crash_12m")
            crash_24m = fwd_outcomes.get("has_crash_24m")
            ret_12m = fwd_outcomes.get("return_12m")

            if prediction == "DANGER":
                if crash_12m is not None or crash_24m is not None:
                    # True Positive if crash occurred or return was negative
                    is_correct = bool(crash_12m or crash_24m or (ret_12m is not None and ret_12m < 0.0))
            elif prediction == "HEALTHY":
                if ret_12m is not None:
                    # True Positive if return was positive
                    is_correct = bool(ret_12m > 0.0)

            entry = {
                "ticker": ticker,
                "name": UNIVERSE_VALIDATION[ticker]["name"],
                "sector": UNIVERSE_VALIDATION[ticker]["sector"],
                "quarter": mv.quarter,
                "date": mv.date,
                "mode": mode,
                "alpha": alpha,
                "stock_price": mv.stock_price_usd,
                "gold_price": mv.gold_price_usd,
                "M_L_billions": round(mv.M_L / 1e9, 2),
                "M_H_billions": round(mv.M_H / 1e9, 2),
                "M_P_billions": round(mv.M_P / 1e9, 2),
                "M_M_billions": round(mv.M_M / 1e9, 2),
                "M_F_billions": round(mv.M_F / 1e9, 2),
                "substrate_billions": round(mv.substrate_usd() / 1e9, 2),
                "substrate_prod": round(mv.substrate_productivity(), 4),
                "VAM": round(vam, 4),
                "SDI": round(sdi_eff, 4),
                "SDI_linear": round(sdi_lin, 4),
                "prod_growth": round(prod_growth, 4),
                "mf_growth": round(mf_growth, 4),
                "sub_growth": round(sub_growth, 4),
                "regime": regime,
                "prediction": prediction,
                "confidence": round(confidence, 3),
                "fwd_return_6m": round(fwd_outcomes.get("return_6m") or 0.0, 4) if fwd_outcomes.get("return_6m") is not None else None,
                "fwd_return_12m": round(fwd_outcomes.get("return_12m") or 0.0, 4) if fwd_outcomes.get("return_12m") is not None else None,
                "fwd_return_24m": round(fwd_outcomes.get("return_24m") or 0.0, 4) if fwd_outcomes.get("return_24m") is not None else None,
                "fwd_drawdown_12m": round(fwd_outcomes.get("drawdown_12m") or 0.0, 4) if fwd_outcomes.get("drawdown_12m") is not None else None,
                "fwd_drawdown_24m": round(fwd_outcomes.get("drawdown_24m") or 0.0, 4) if fwd_outcomes.get("drawdown_24m") is not None else None,
                "has_crash_12m": crash_12m,
                "has_crash_24m": crash_24m,
                "is_correct": is_correct
            }
            prediction_log.append(entry)

    # Compute aggregate scorecard metrics
    # Danger evaluation:
    danger_preds = [p for p in prediction_log if p["prediction"] == "DANGER" and p["has_crash_24m"] is not None]
    healthy_preds = [p for p in prediction_log if p["prediction"] == "HEALTHY" and p["fwd_return_12m"] is not None]
    
    tp_danger = sum(1 for p in danger_preds if p["is_correct"])
    fp_danger = len(danger_preds) - tp_danger
    
    # Crashes that occurred when not flagged DANGER
    non_danger_preds = [p for p in prediction_log if p["prediction"] != "DANGER" and p["has_crash_24m"] is not None]
    fn_danger = sum(1 for p in non_danger_preds if p["has_crash_24m"] or (p["fwd_return_12m"] is not None and p["fwd_return_12m"] < -0.20))
    tn_danger = len(non_danger_preds) - fn_danger

    precision_danger = (tp_danger / (tp_danger + fp_danger)) if (tp_danger + fp_danger) > 0 else 0.0
    recall_danger = (tp_danger / (tp_danger + fn_danger)) if (tp_danger + fn_danger) > 0 else 0.0
    f1_danger = (2 * precision_danger * recall_danger / (precision_danger + recall_danger)) if (precision_danger + recall_danger) > 0 else 0.0

    healthy_correct = sum(1 for p in healthy_preds if p["is_correct"])
    accuracy_healthy = (healthy_correct / len(healthy_preds)) if healthy_preds else 0.0

    scorecard = {
        "mode": mode,
        "total_quarterly_evaluations": len(prediction_log),
        "danger_predictions_count": len(danger_preds),
        "danger_true_positives": tp_danger,
        "danger_false_positives": fp_danger,
        "danger_false_negatives": fn_danger,
        "danger_precision": round(precision_danger, 4),
        "danger_recall": round(recall_danger, 4),
        "danger_f1_score": round(f1_danger, 4),
        "healthy_predictions_count": len(healthy_preds),
        "healthy_accuracy": round(accuracy_healthy, 4)
    }

    return prediction_log, scorecard


def export_to_csv(prediction_log: List[dict], filename: str):
    """Exports prediction log to clean CSV."""
    if not prediction_log:
        return
    keys = list(prediction_log[0].keys())
    filepath = os.path.join(OUTPUT_DIR, filename)
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        writer.writerows(prediction_log)
    print(f"[EXPORT] Wrote {len(prediction_log)} prediction records to {filepath}")


def run_alpha_grid_search(
    universe_data: Dict[str, Any],
    gold_data: List[dict],
    alphas: List[float] = [0.0, 0.25, 0.50, 0.75, 1.0, 1.25, 1.50]
) -> Tuple[float, Dict[float, Dict[str, Any]], Dict[str, Any]]:
    """
    Sweeps productivity coupling coefficient alpha to optimize Danger F1 score
    and eliminate the growth-stock false positive problem (Frontier V-FIN-12).
    """
    print("\n" + "=" * 80)
    print("FRONTIER V-FIN-12: ALPHA GRID SEARCH (PRODUCTIVITY-CORRECTED SDI)")
    print("=" * 80)
    print(f"{'Alpha':<8} | {'Danger Preds':<14} | {'Precision':<12} | {'Recall':<12} | {'F1-Score':<10} | {'Healthy Acc':<12}")
    print("-" * 80)

    results = {}
    best_alpha = 0.0
    best_f1 = -1.0

    for a in alphas:
        _, score = run_single_backtest(universe_data, gold_data, mode="usd", alpha=a)
        results[a] = score
        f1 = score["danger_f1_score"]
        if f1 > best_f1:
            best_f1 = f1
            best_alpha = a
        print(f"{a:<8.2f} | {score['danger_predictions_count']:<14} | {score['danger_precision']*100:>6.1f}%{'':<5} | {score['danger_recall']*100:>6.1f}%{'':<5} | {score['danger_f1_score']:<10.3f} | {score['healthy_accuracy']*100:>6.1f}%")

    print("-" * 80)
    print(f"Optimal Alpha*: {best_alpha:.2f} with Danger F1: {best_f1:.3f}")
    return best_alpha, results, results[best_alpha]


def run_full_validation_suite():
    """
    Main entry point for running the complete backtest on the validation universe.
    Compares:
      1. Linear SDI (alpha = 0.0) in USD-Nominal
      2. Productivity-Corrected PC-SDI (optimal alpha*) in USD-Nominal
      3. PC-SDI in Gold-Normalized
    """
    print("=" * 80)
    print("PREDICTABILITY BACKTESTING ENGINE: EMPIRICAL VALIDATION SUITE")
    print("=" * 80)

    # 1. Load cached market data
    print("\n[STEP 1] Loading Universe Facts and Market Prices...")
    gold_data = fetch_market_prices(GOLD_SYMBOL)
    universe_data = {}

    for ticker, info in UNIVERSE_VALIDATION.items():
        sec_facts = fetch_sec_facts(ticker, info["cik"])
        prices = fetch_market_prices(ticker)
        history = build_corporate_mass_history(ticker, sec_facts, prices, gold_data)
        fwd_outcomes = precompute_company_forward_outcomes(prices, [mv.date for mv in history], [6, 12, 24])
        universe_data[ticker] = {
            "info": info,
            "sec_facts": sec_facts,
            "prices": prices,
            "history": history,
            "fwd_outcomes": fwd_outcomes
        }
        print(f"  Loaded {ticker}: {len(history)} quarterly mass vectors constructed.")

    # 2. Run Alpha Grid Search for PC-SDI (Frontier V-FIN-12)
    best_alpha, grid_results, best_score = run_alpha_grid_search(universe_data, gold_data)

    # 3. Run Linear SDI (alpha = 0.0) Baseline in USD
    print("\n[STEP 3] Running Linear SDI (alpha=0.0) Baseline Backtest...")
    log_linear, score_linear = run_single_backtest(universe_data, gold_data, mode="usd", alpha=0.0)
    export_to_csv(log_linear, "prediction_log_usd_linear.csv")

    # 4. Run Productivity-Corrected PC-SDI (best_alpha) in USD
    print(f"\n[STEP 4] Running PC-SDI (alpha={best_alpha:.2f}) USD Backtest...")
    log_pcsdi_usd, score_pcsdi_usd = run_single_backtest(universe_data, gold_data, mode="usd", alpha=best_alpha)
    export_to_csv(log_pcsdi_usd, "prediction_log_usd.csv")

    # 5. Run PC-SDI in Gold-Normalized
    print(f"\n[STEP 5] Running PC-SDI (alpha={best_alpha:.2f}) Gold-Normalized Backtest...")
    log_pcsdi_gold, score_pcsdi_gold = run_single_backtest(universe_data, gold_data, mode="gold", alpha=best_alpha)
    export_to_csv(log_pcsdi_gold, "prediction_log_gold.csv")

    # 6. Save Scorecard
    scorecard_path = os.path.join(OUTPUT_DIR, "validation_scorecard.json")
    final_scorecard = {
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "universe_size": len(UNIVERSE_VALIDATION),
        "backtest_window": "2017-Q4 to 2026-Q2 (35 quarters)",
        "optimal_alpha": best_alpha,
        "alpha_grid_search": {str(k): v for k, v in grid_results.items()},
        "linear_sdi_usd": score_linear,
        "pcsdi_usd": score_pcsdi_usd,
        "pcsdi_gold": score_pcsdi_gold,
        "delta_precision_pcsdi_vs_linear": round(score_pcsdi_usd["danger_precision"] - score_linear["danger_precision"], 4),
        "delta_f1_pcsdi_vs_linear": round(score_pcsdi_usd["danger_f1_score"] - score_linear["danger_f1_score"], 4),
        "delta_precision_gold_vs_usd": round(score_pcsdi_gold["danger_precision"] - score_pcsdi_usd["danger_precision"], 4)
    }
    with open(scorecard_path, "w", encoding="utf-8") as f:
        json.dump(final_scorecard, f, indent=2)

    # 7. Print Scorecard Comparison
    print("\n" + "=" * 95)
    print("EMPIRICAL SCORECARD COMPARISON: LINEAR SDI vs. PC-SDI vs. GOLD-NORMALIZED")
    print("=" * 95)
    print(f"{'Metric':<32} | {'Linear SDI (USD)':<16} | {'PC-SDI (USD)':<16} | {'PC-SDI (Gold)':<16} | {'PC-SDI Lift':<10}")
    print("-" * 100)
    print(f"{'Danger (Regime 3) Predictions':<32} | {score_linear['danger_predictions_count']:<16} | {score_pcsdi_usd['danger_predictions_count']:<16} | {score_pcsdi_gold['danger_predictions_count']:<16} | {score_pcsdi_usd['danger_predictions_count'] - score_linear['danger_predictions_count']:<+10}")
    print(f"{'Danger Precision (Drawdowns)':<32} | {score_linear['danger_precision']*100:>6.1f}%{'':<9} | {score_pcsdi_usd['danger_precision']*100:>6.1f}%{'':<9} | {score_pcsdi_gold['danger_precision']*100:>6.1f}%{'':<9} | {(score_pcsdi_usd['danger_precision'] - score_linear['danger_precision'])*100:>+6.1f}%")
    print(f"{'Danger Recall (Crashes)':<32} | {score_linear['danger_recall']*100:>6.1f}%{'':<9} | {score_pcsdi_usd['danger_recall']*100:>6.1f}%{'':<9} | {score_pcsdi_gold['danger_recall']*100:>6.1f}%{'':<9} | {(score_pcsdi_usd['danger_recall'] - score_linear['danger_recall'])*100:>+6.1f}%")
    print(f"{'Danger F1-Score':<32} | {score_linear['danger_f1_score']:<16.3f} | {score_pcsdi_usd['danger_f1_score']:<16.3f} | {score_pcsdi_gold['danger_f1_score']:<16.3f} | {score_pcsdi_usd['danger_f1_score'] - score_linear['danger_f1_score']:<+10.3f}")
    print(f"{'Healthy (Regime 1) Accuracy':<32} | {score_linear['healthy_accuracy']*100:>6.1f}%{'':<9} | {score_pcsdi_usd['healthy_accuracy']*100:>6.1f}%{'':<9} | {score_pcsdi_gold['healthy_accuracy']*100:>6.1f}%{'':<9} | {(score_pcsdi_usd['healthy_accuracy'] - score_linear['healthy_accuracy'])*100:>+6.1f}%")
    print("=" * 95)

    # 8. Specific Company Validation Check (Boeing, Apple, GE)
    print("\n--- CASE STUDY AUDIT (RULE 5.1 KNOWN-LIMIT VERIFICATION) ---")
    for t in ["BA", "AAPL", "GE"]:
        comp_preds = [p for p in log_pcsdi_usd if p["ticker"] == t]
        print(f"\n[{t}] Timeline of Key Regime Classifications under PC-SDI (alpha={best_alpha:.2f}):")
        for p in comp_preds:
            if p["prediction"] == "DANGER" or "2018" in p["quarter"] or "2019" in p["quarter"] or "2020" in p["quarter"]:
                crash_flag = "CRASH OCCURRED" if p["has_crash_24m"] else "No crash"
                print(f"  {p['quarter']}: {p['prediction']:<7} (Conf: {p['confidence']:.2f}) | PC-SDI={p['SDI']:+6.2f}, Lin={p['SDI_linear']:+6.2f}, Prod={p['substrate_prod']:.2f} | 24m Drawdown: {p['fwd_drawdown_24m'] if p['fwd_drawdown_24m'] is not None else 0.0:>+6.1%} ({crash_flag})")

    return final_scorecard


if __name__ == "__main__":
    run_full_validation_suite()
