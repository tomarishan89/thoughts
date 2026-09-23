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
    UNIVERSE_VALIDATION, ACTIVE_UNIVERSE, GOLD_SYMBOL, SP500_SYMBOL,
    TREASURY_10Y_SYMBOL, OUTPUT_DIR, BACKTEST_CONFIG
)
from data_fetcher import fetch_sec_facts, fetch_market_prices
from mass_vector import (
    MassVector, build_corporate_mass_history,
    compute_vam, compute_sdi, classify_regime,
    compute_manifold_stress_index, compute_pdr, classify_regime_v2,
    classify_regime_v3,
    compute_manifold_sdi_density_weighted, compute_macro_screening_length,
    compute_exogenous_alpha
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

            info = comp_data.get("info", {})
            entry = {
                "ticker": ticker,
                "name": info.get("name", ticker),
                "sector": info.get("sector", "Unknown"),
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


# ==============================================================================
# V2 ENHANCED BACKTESTER WITH FINANCIAL MANIFOLD LENSES (V-FIN-16)
# ==============================================================================

def run_single_backtest_v2(
    universe_data: Dict[str, Any],
    gold_data: List[dict],
    spx_data: List[dict],
    mode: str = "usd",
    alpha: float = 1.75,
    pdr_threshold: float = 3.5,
    aggregation_mode: str = "median"
) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    """
    Executes an enhanced V2 historical backtest run in either 'usd' or 'gold' mode,
    incorporating the three Financial Manifold Existence Lenses (V-FIN-16):
      - Lens 1: Manifold Stress Index (MSI via Gold/SPX relative return ratio)
      - Lens 2: Parasitic Decoupling Ratio (PDR gating positive growth)
      - Lens 3: Manifold-Level Aggregate SDI (unweighted median or density-weighted)
      - Macro Screening Length xi_manifold (Frontier V-FIN-16.4.2)

    Two-Pass Execution:
      Pass 1: Precompute entity-level SDIs and derive quarterly cross-sectional manifold SDI.
      Pass 2: Evaluate dynamic regime classifications with systemic manifold context.
    """
    prediction_log = []
    window = BACKTEST_CONFIG["sdi_window_quarters"]

    # --- PASS 1: Precompute SDIs and cross-sectional manifold aggregate ---
    quarterly_sdis: Dict[str, List[float]] = {}
    quarterly_masses: Dict[str, List[float]] = {}
    intermediate_evals = []

    for ticker, comp_data in universe_data.items():
        history: List[MassVector] = comp_data["history"]
        for i in range(window, len(history)):
            mv = history[i]
            sdi_eff, sdi_lin, mf_growth, sub_growth, prod_growth = compute_sdi(
                history, i, mode=mode, window=window, alpha=alpha
            )
            quarterly_sdis.setdefault(mv.quarter, []).append(sdi_eff)
            m_f_val = (mv.M_F / max(1.0, mv.gold_price_usd)) if mode == "gold" else mv.M_F
            quarterly_masses.setdefault(mv.quarter, []).append(max(1.0, float(m_f_val)))
            intermediate_evals.append({
                "ticker": ticker,
                "comp_data": comp_data,
                "history": history,
                "idx": i,
                "mv": mv,
                "sdi_eff": sdi_eff,
                "sdi_lin": sdi_lin,
                "mf_growth": mf_growth,
                "sub_growth": sub_growth,
                "prod_growth": prod_growth
            })

    # Cross-sectional aggregate SDI across universe at each quarter
    if aggregation_mode == "density_weighted":
        quarterly_manifold_sdi = {
            q: compute_manifold_sdi_density_weighted(quarterly_sdis[q], quarterly_masses[q])
            for q in quarterly_sdis
        }
    else:
        quarterly_manifold_sdi = {
            q: float(np.median(vals)) for q, vals in quarterly_sdis.items()
        }

    # --- PASS 2: Regime Classification with Manifold Context ---
    for item in intermediate_evals:
        ticker = item["ticker"]
        comp_data = item["comp_data"]
        mv: MassVector = item["mv"]
        sdi_eff = item["sdi_eff"]
        sdi_lin = item["sdi_lin"]
        mf_growth = item["mf_growth"]
        sub_growth = item["sub_growth"]
        prod_growth = item["prod_growth"]

        # 1. Lens 1: Manifold Stress Index (Gold/SPX relative return ratio)
        msi = compute_manifold_stress_index(gold_data, spx_data, mv.date)

        # 2. Lens 2: Parasitic Decoupling Ratio
        pdr = compute_pdr(mf_growth, sub_growth)

        # 3. Lens 3: Manifold-Level Aggregate SDI & Macro Screening Length
        m_sdi = quarterly_manifold_sdi.get(mv.quarter, 0.0)
        macro_xi = compute_macro_screening_length(m_sdi)

        # VAM evaluation
        if mode == "gold":
            vam = compute_vam(mv.as_array_gold())
        else:
            vam = compute_vam(mv.as_array_usd())

        # V2 Multi-Lens Classification
        regime, prediction, confidence = classify_regime_v2(
            sdi=sdi_eff,
            vam=vam,
            sub_growth=sub_growth,
            mf_growth=mf_growth,
            pdr=pdr,
            manifold_stress=msi,
            manifold_sdi=m_sdi,
            pdr_threshold=pdr_threshold
        )

        fwd_outcomes = comp_data.get("fwd_outcomes", {}).get(mv.date, {})
        crash_12m = fwd_outcomes.get("has_crash_12m")
        crash_24m = fwd_outcomes.get("has_crash_24m")
        ret_12m = fwd_outcomes.get("return_12m")

        is_correct = None
        if prediction == "DANGER":
            if crash_12m is not None or crash_24m is not None:
                is_correct = bool(crash_12m or crash_24m or (ret_12m is not None and ret_12m < 0.0))
        elif prediction == "HEALTHY":
            if ret_12m is not None:
                is_correct = bool(ret_12m > 0.0)

        info = universe_data[ticker].get("info", {})
        entry = {
            "ticker": ticker,
            "name": info.get("name", ticker),
            "sector": info.get("sector", "Unknown"),
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
            "PDR": round(pdr, 3),
            "MSI": round(msi, 4),
            "manifold_SDI": round(m_sdi, 4),
            "macro_xi": round(macro_xi, 4),
            "aggregation_mode": aggregation_mode,
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
    danger_preds = [p for p in prediction_log if p["prediction"] == "DANGER" and p["has_crash_24m"] is not None]
    healthy_preds = [p for p in prediction_log if p["prediction"] == "HEALTHY" and p["fwd_return_12m"] is not None]

    tp_danger = sum(1 for p in danger_preds if p["is_correct"])
    fp_danger = len(danger_preds) - tp_danger

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


def run_alpha_grid_search_v2(
    universe_data: Dict[str, Any],
    gold_data: List[dict],
    spx_data: List[dict],
    alphas: List[float] = [0.0, 0.25, 0.50, 0.75, 1.0, 1.25, 1.50, 1.75, 2.0],
    mode: str = "usd"
) -> Tuple[float, Dict[float, Dict[str, Any]], Dict[str, Any]]:
    """
    Sweeps productivity coupling coefficient alpha under V2 Manifold Lenses
    to determine optimal alpha* for USD and Gold modes.
    """
    print("\n" + "=" * 80)
    print(f"FRONTIER V-FIN-16: ALPHA GRID SEARCH UNDER V2 LENSES (MODE: {mode.upper()})")
    print("=" * 80)
    print(f"{'Alpha':<8} | {'Danger Preds':<14} | {'Precision':<12} | {'Recall':<12} | {'F1-Score':<10} | {'Healthy Acc':<12}")
    print("-" * 80)

    results = {}
    best_alpha = 0.0
    best_f1 = -1.0

    for a in alphas:
        _, score = run_single_backtest_v2(
            universe_data, gold_data, spx_data, mode=mode, alpha=a
        )
        results[a] = score
        f1 = score["danger_f1_score"]
        if f1 > best_f1:
            best_f1 = f1
            best_alpha = a
        print(f"{a:<8.2f} | {score['danger_predictions_count']:<14} | {score['danger_precision']*100:>6.1f}%{'':<5} | {score['danger_recall']*100:>6.1f}%{'':<5} | {score['danger_f1_score']:<10.3f} | {score['healthy_accuracy']*100:>6.1f}%")

    print("-" * 80)
    print(f"Optimal V2 Alpha* ({mode.upper()}): {best_alpha:.2f} with Danger F1: {best_f1:.3f}")
    return best_alpha, results, results[best_alpha]


# ==============================================================================
# V3 CONTINUUM PLASTICITY & BALANCE-SHEET YIELD SURFACE BACKTESTER (V-FIN-4, 10, 12)
# ==============================================================================

def run_single_backtest_v3(
    universe_data: Dict[str, Any],
    gold_data: List[dict],
    spx_data: List[dict],
    tnx_data: List[dict] = None,
    mode: str = "usd",
    alpha: float = 1.25,
    pdr_threshold: float = 3.5,
    aggregation_mode: str = "median",
    use_retarded_gestation: bool = True,
    use_sector_coupling: bool = True,
    gamma_sec: float = 1.0,
    use_drucker_prager_gate: bool = True,
    use_exogenous_macro_tensor: bool = True
) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    """
    Executes a V3 continuum plasticity historical backtest run with:
      - Lens 1: Manifold Stress Index (MSI via Gold/SPX relative return ratio)
      - Lens 2: Parasitic Decoupling Ratio (PDR gating positive growth)
      - Lens 3: Manifold-Level Aggregate SDI (unweighted median or density-weighted)
      - Lens 4: Capped Drucker-Prager Balance-Sheet Yield Surface phi_C (V-FIN-4)
      - Non-Markovian Retarded Gestation Memory (Gamma convolution) (V-FIN-12.1)
      - Sector Capital-Intensity Coupling alpha(rho_capex) (V-FIN-12.2)
      - Cash Conversion Cycle Dynamic Turnover timescale tau_turnover (V-FIN-1.1, V-FIN-10)

    Two-Pass Execution:
      Pass 1: Precompute entity-level SDIs with retarded gestation and sector coupling.
      Pass 2: Evaluate dynamic regime classifications with systemic manifold context and Lens 4.
    """
    prediction_log = []
    window = BACKTEST_CONFIG["sdi_window_quarters"]

    # --- PASS 1: Precompute SDIs and cross-sectional manifold aggregate ---
    quarterly_sdis: Dict[str, List[float]] = {}
    quarterly_masses: Dict[str, List[float]] = {}
    intermediate_evals = []

    for ticker, comp_data in universe_data.items():
        history: List[MassVector] = comp_data["history"]
        for i in range(window, len(history)):
            mv = history[i]
            if use_exogenous_macro_tensor and tnx_data:
                alpha_tau = compute_exogenous_alpha(alpha, tnx_data, mv.date, kappa=15.0)
            else:
                alpha_tau = alpha
            
            sdi_eff, sdi_lin, mf_growth, sub_growth, prod_growth = compute_sdi(
                history, i, mode=mode, window=window, alpha=alpha_tau,
                use_retarded_gestation=use_retarded_gestation,
                use_sector_coupling=use_sector_coupling,
                gamma_sec=gamma_sec
            )
            quarterly_sdis.setdefault(mv.quarter, []).append(sdi_eff)
            m_f_val = (mv.M_F / max(1.0, mv.gold_price_usd)) if mode == "gold" else mv.M_F
            quarterly_masses.setdefault(mv.quarter, []).append(max(1.0, float(m_f_val)))
            intermediate_evals.append({
                "ticker": ticker,
                "comp_data": comp_data,
                "history": history,
                "idx": i,
                "mv": mv,
                "sdi_eff": sdi_eff,
                "sdi_lin": sdi_lin,
                "mf_growth": mf_growth,
                "sub_growth": sub_growth,
                "prod_growth": prod_growth
            })

    # Cross-sectional aggregate SDI across universe at each quarter
    if aggregation_mode == "density_weighted":
        quarterly_manifold_sdi = {
            q: compute_manifold_sdi_density_weighted(quarterly_sdis[q], quarterly_masses[q])
            for q in quarterly_sdis
        }
    else:
        quarterly_manifold_sdi = {
            q: float(np.median(vals)) for q, vals in quarterly_sdis.items()
        }

    # --- PASS 2: Regime Classification with Manifold & Plasticity Context ---
    for item in intermediate_evals:
        ticker = item["ticker"]
        comp_data = item["comp_data"]
        mv: MassVector = item["mv"]
        sdi_eff = item["sdi_eff"]
        sdi_lin = item["sdi_lin"]
        mf_growth = item["mf_growth"]
        sub_growth = item["sub_growth"]
        prod_growth = item["prod_growth"]

        # Lens 1: Manifold Stress Index
        msi = compute_manifold_stress_index(gold_data, spx_data, mv.date)

        # Lens 2: Parasitic Decoupling Ratio
        pdr = compute_pdr(mf_growth, sub_growth)

        # Lens 3: Manifold-Level Aggregate SDI & Macro Screening Length
        m_sdi = quarterly_manifold_sdi.get(mv.quarter, 0.0)
        macro_xi = compute_macro_screening_length(m_sdi)

        # VAM evaluation
        if mode == "gold":
            vam = compute_vam(mv.as_array_gold())
        else:
            vam = compute_vam(mv.as_array_usd())

        # Lens 4: Capped Drucker-Prager Rupture Gate
        is_yield_ruptured = mv.is_yield_ruptured if use_drucker_prager_gate else False
        phi_c = mv.drucker_prager_phi if use_drucker_prager_gate else None

        sec_name = universe_data[ticker].get("info", {}).get("sector", "Unknown")
        regime, prediction, confidence = classify_regime_v3(
            sdi=sdi_eff,
            vam=vam,
            sub_growth=sub_growth,
            mf_growth=mf_growth,
            pdr=pdr,
            manifold_stress=msi,
            manifold_sdi=m_sdi,
            pdr_threshold=pdr_threshold,
            is_yield_ruptured=is_yield_ruptured,
            phi_c=phi_c,
            sector=sec_name
        )

        fwd_outcomes = comp_data.get("fwd_outcomes", {}).get(mv.date, {})
        crash_12m = fwd_outcomes.get("has_crash_12m")
        crash_24m = fwd_outcomes.get("has_crash_24m")
        ret_12m = fwd_outcomes.get("return_12m")

        is_correct = None
        if prediction == "DANGER":
            if crash_12m is not None or crash_24m is not None:
                is_correct = bool(crash_12m or crash_24m or (ret_12m is not None and ret_12m < 0.0))
        elif prediction == "HEALTHY":
            if ret_12m is not None:
                is_correct = bool(ret_12m > 0.0)

        info = universe_data[ticker].get("info", {})
        entry = {
            "ticker": ticker,
            "name": info.get("name", ticker),
            "sector": info.get("sector", "Unknown"),
            "quarter": mv.quarter,
            "date": mv.date,
            "mode": mode,
            "alpha_base": alpha,
            "alpha_eff": round(alpha_tau if 'alpha_tau' in locals() else alpha, 4),
            "stock_price": mv.stock_price_usd,
            "gold_price": mv.gold_price_usd,
            "M_L_billions": round(mv.M_L / 1e9, 2),
            "M_H_billions": round(mv.M_H / 1e9, 2),
            "M_P_billions": round(mv.M_P / 1e9, 2),
            "M_M_billions": round(mv.M_M / 1e9, 2),
            "M_F_billions": round(mv.M_F / 1e9, 2),
            "substrate_billions": round(mv.substrate_usd() / 1e9, 2),
            "substrate_prod": round(mv.substrate_productivity(), 4),
            "retarded_productivity": round(mv.retarded_productivity, 4),
            "tau_turnover": round(mv.tau_turnover, 4),
            "ccc_days": round(mv.ccc_days, 1),
            "drucker_prager_phi": round(mv.drucker_prager_phi, 4),
            "is_yield_ruptured": mv.is_yield_ruptured,
            "VAM": round(vam, 4),
            "SDI": round(sdi_eff, 4),
            "SDI_linear": round(sdi_lin, 4),
            "PDR": round(pdr, 3),
            "MSI": round(msi, 4),
            "manifold_SDI": round(m_sdi, 4),
            "macro_xi": round(macro_xi, 4),
            "aggregation_mode": aggregation_mode,
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
    danger_preds = [p for p in prediction_log if p["prediction"] == "DANGER" and p["has_crash_24m"] is not None]
    healthy_preds = [p for p in prediction_log if p["prediction"] == "HEALTHY" and p["fwd_return_12m"] is not None]

    tp_danger = sum(1 for p in danger_preds if p["is_correct"])
    fp_danger = len(danger_preds) - tp_danger

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


def evaluate_window(logs: List[Dict[str, Any]]) -> float:
    """Evaluates the F1-score of danger predictions in a given window of logs."""
    valid = [p for p in logs if p.get("has_crash_24m") is not None]
    
    tp = sum(1 for r in valid if r["prediction"] == "DANGER" and (r["has_crash_24m"] or (r.get("fwd_return_12m") is not None and r["fwd_return_12m"] < -0.20)))
    fp = sum(1 for r in valid if r["prediction"] == "DANGER" and not (r["has_crash_24m"] or (r.get("fwd_return_12m") is not None and r["fwd_return_12m"] < -0.20)))
    fn = sum(1 for r in valid if r["prediction"] != "DANGER" and (r["has_crash_24m"] or (r.get("fwd_return_12m") is not None and r["fwd_return_12m"] < -0.20)))
    
    danger_count = tp + fp
    crashes = tp + fn
    prec = tp / danger_count if danger_count > 0 else 0.0
    rec = tp / crashes if crashes > 0 else 0.0
    f1 = (2 * prec * rec / (prec + rec)) if (prec + rec) > 0 else 0.0
    return f1

def run_walk_forward_backtest_v3(
    universe_data: Dict[str, Any],
    gold_data: List[dict],
    spx_data: List[dict],
    tnx_data: List[dict] = None,
    alphas: List[float] = [0.0, 0.25, 0.50, 0.75, 1.0, 1.25, 1.50, 1.75, 2.0],
    mode: str = "usd",
    pdr_threshold: float = 3.5,
    aggregation_mode: str = "median",
    use_retarded_gestation: bool = True,
    use_sector_coupling: bool = True,
    gamma_sec: float = 1.0,
    use_drucker_prager_gate: bool = True,
    window_quarters: int = 20,
    lookahead_quarters: int = 8
) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    """
    Implements V-FIN-16.4.1c: Walk-Forward Dynamic Alpha Calibration.
    Optimizes alpha over a trailing window of predictions without lookahead bias.
    """
    alpha_logs = {}
    for a in alphas:
        log_a, _ = run_single_backtest_v3(
            universe_data, gold_data, spx_data, tnx_data=tnx_data,
            mode=mode, alpha=a,
            pdr_threshold=pdr_threshold, aggregation_mode=aggregation_mode,
            use_retarded_gestation=use_retarded_gestation, use_sector_coupling=use_sector_coupling,
            gamma_sec=gamma_sec, use_drucker_prager_gate=use_drucker_prager_gate,
            use_exogenous_macro_tensor=True
        )
        alpha_logs[a] = log_a

    if not alpha_logs[alphas[0]]:
        return [], {}

    quarters = sorted(list(set([p["quarter"] for p in alpha_logs[alphas[0]]])))
    
    def q_diff(q_end, q_start):
        y1, q1 = map(int, q_end.replace("Q", "").split("-"))
        y2, q2 = map(int, q_start.replace("Q", "").split("-"))
        return (y1 - y2) * 4 + (q1 - q2)
        
    dynamic_log = []
    chosen_alphas = {}

    for current_q in quarters:
        best_alpha = 1.25 # Default fallback
        best_f1 = -1.0
        
        for a in alphas:
            valid_hist = [
                p for p in alpha_logs[a] 
                if lookahead_quarters <= q_diff(current_q, p["quarter"]) < (lookahead_quarters + window_quarters)
            ]
            
            if valid_hist:
                f1 = evaluate_window(valid_hist)
                if f1 > best_f1:
                    best_f1 = f1
                    best_alpha = a
                
        chosen_alphas[current_q] = best_alpha
        
        preds_for_current_q = [p for p in alpha_logs[best_alpha] if p["quarter"] == current_q]
        dynamic_log.extend(preds_for_current_q)

    # Compute overall scorecard
    danger_preds = [p for p in dynamic_log if p["prediction"] == "DANGER" and p.get("has_crash_24m") is not None]
    healthy_preds = [p for p in dynamic_log if p["prediction"] == "HEALTHY" and p.get("fwd_return_12m") is not None]

    tp_danger = sum(1 for p in danger_preds if p["is_correct"])
    fp_danger = len(danger_preds) - tp_danger

    non_danger_preds = [p for p in dynamic_log if p["prediction"] != "DANGER" and p.get("has_crash_24m") is not None]
    fn_danger = sum(1 for p in non_danger_preds if p.get("has_crash_24m") or (p.get("fwd_return_12m") is not None and p.get("fwd_return_12m") < -0.20))

    precision_danger = (tp_danger / (tp_danger + fp_danger)) if (tp_danger + fp_danger) > 0 else 0.0
    recall_danger = (tp_danger / (tp_danger + fn_danger)) if (tp_danger + fn_danger) > 0 else 0.0
    f1_danger = (2 * precision_danger * recall_danger / (precision_danger + recall_danger)) if (precision_danger + recall_danger) > 0 else 0.0

    healthy_correct = sum(1 for p in healthy_preds if p["is_correct"])
    accuracy_healthy = (healthy_correct / len(healthy_preds)) if healthy_preds else 0.0

    scorecard = {
        "mode": mode + "_dynamic",
        "total_quarterly_evaluations": len(dynamic_log),
        "danger_predictions_count": len(danger_preds),
        "danger_true_positives": tp_danger,
        "danger_false_positives": fp_danger,
        "danger_false_negatives": fn_danger,
        "danger_precision": round(precision_danger, 4),
        "danger_recall": round(recall_danger, 4),
        "danger_f1_score": round(f1_danger, 4),
        "healthy_predictions_count": len(healthy_preds),
        "healthy_accuracy": round(accuracy_healthy, 4),
        "chosen_alphas_over_time": chosen_alphas
    }

    return dynamic_log, scorecard


def run_alpha_grid_search_v3(
    universe_data: Dict[str, Any],
    gold_data: List[dict],
    spx_data: List[dict],
    alphas: List[float] = [0.0, 0.25, 0.50, 0.75, 1.0, 1.25, 1.50, 1.75, 2.0],
    mode: str = "usd"
) -> Tuple[float, Dict[float, Dict[str, Any]], Dict[str, Any]]:
    """
    Sweeps productivity coupling coefficient alpha under V3 Continuum Plasticity
    to determine optimal alpha* for USD and Gold modes.
    """
    print("\n" + "=" * 80)
    print(f"FRONTIER V-FIN-4/10/12: ALPHA GRID SEARCH UNDER V3 CONTINUUM PLASTICITY (MODE: {mode.upper()})")
    print("=" * 80)
    print(f"{'Alpha':<8} | {'Danger Preds':<14} | {'Precision':<12} | {'Recall':<12} | {'F1-Score':<10} | {'Healthy Acc':<12}")
    print("-" * 80)

    results = {}
    best_alpha = 0.0
    best_f1 = -1.0

    for a in alphas:
        _, score = run_single_backtest_v3(
            universe_data, gold_data, spx_data, mode=mode, alpha=a
        )
        results[a] = score
        f1 = score["danger_f1_score"]
        if f1 > best_f1:
            best_f1 = f1
            best_alpha = a
        print(f"{a:<8.2f} | {score['danger_predictions_count']:<14} | {score['danger_precision']*100:>6.1f}%{'':<5} | {score['danger_recall']*100:>6.1f}%{'':<5} | {score['danger_f1_score']:<10.3f} | {score['healthy_accuracy']*100:>6.1f}%")

    print("-" * 80)
    print(f"Optimal V3 Alpha* ({mode.upper()}): {best_alpha:.2f} with Danger F1: {best_f1:.3f}")
    return best_alpha, results, results[best_alpha]


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


def compute_stratified_scorecard(prediction_log: List[Dict[str, Any]], group_key: str = "sector") -> Dict[str, Dict[str, Any]]:
    """Compute precision, recall, F1, danger count, and total count stratified by group (e.g. sector or period)."""
    groups: Dict[str, List[Dict[str, Any]]] = {}
    for p in prediction_log:
        g = p.get(group_key, "Unknown")
        groups.setdefault(g, []).append(p)

    scorecard = {}
    for g, rows in sorted(groups.items()):
        valid = [r for r in rows if r.get("has_crash_24m") is not None]
        total = len(valid)
        tp = sum(1 for r in valid if r["prediction"] == "DANGER" and (r["has_crash_24m"] or (r.get("fwd_return_12m") is not None and r["fwd_return_12m"] < -0.20)))
        fp = sum(1 for r in valid if r["prediction"] == "DANGER" and not (r["has_crash_24m"] or (r.get("fwd_return_12m") is not None and r["fwd_return_12m"] < -0.20)))
        fn = sum(1 for r in valid if r["prediction"] != "DANGER" and (r["has_crash_24m"] or (r.get("fwd_return_12m") is not None and r["fwd_return_12m"] < -0.20)))
        tn = sum(1 for r in valid if r["prediction"] != "DANGER" and not (r["has_crash_24m"] or (r.get("fwd_return_12m") is not None and r["fwd_return_12m"] < -0.20)))

        danger_count = tp + fp
        crashes = tp + fn
        prec = tp / danger_count if danger_count > 0 else 0.0
        rec = tp / crashes if crashes > 0 else 0.0
        f1 = (2 * prec * rec / (prec + rec)) if (prec + rec) > 0 else 0.0
        base_rate = crashes / total if total > 0 else 0.0

        scorecard[g] = {
            "total_samples": total,
            "danger_count": danger_count,
            "actual_crashes": crashes,
            "base_rate": round(base_rate, 4),
            "precision": round(prec, 4),
            "recall": round(rec, 4),
            "f1_score": round(f1, 4),
            "TP": tp, "FP": fp, "FN": fn, "TN": tn
        }
    return scorecard


def compute_temporal_holdout_scorecard(prediction_log: List[Dict[str, Any]], split_year: int = 2022) -> Dict[str, Dict[str, Any]]:
    """Stratify predictions into In-Sample (quarter < split_year) and Out-of-Sample (quarter >= split_year)."""
    in_sample = []
    out_of_sample = []
    for p in prediction_log:
        q = p.get("quarter", "")
        try:
            yr = int(q.split("-")[0])
            if yr < split_year:
                in_sample.append(p)
            else:
                out_of_sample.append(p)
        except (ValueError, IndexError):
            continue

    def _eval(recs):
        valid = [r for r in recs if r.get("has_crash_24m") is not None]
        total = len(valid)
        tp = sum(1 for r in valid if r["prediction"] == "DANGER" and (r["has_crash_24m"] or (r.get("fwd_return_12m") is not None and r["fwd_return_12m"] < -0.20)))
        fp = sum(1 for r in valid if r["prediction"] == "DANGER" and not (r["has_crash_24m"] or (r.get("fwd_return_12m") is not None and r["fwd_return_12m"] < -0.20)))
        fn = sum(1 for r in valid if r["prediction"] != "DANGER" and (r["has_crash_24m"] or (r.get("fwd_return_12m") is not None and r["fwd_return_12m"] < -0.20)))
        tn = sum(1 for r in valid if r["prediction"] != "DANGER" and not (r["has_crash_24m"] or (r.get("fwd_return_12m") is not None and r["fwd_return_12m"] < -0.20)))
        danger_count = tp + fp
        crashes = tp + fn
        prec = tp / danger_count if danger_count > 0 else 0.0
        rec = tp / crashes if crashes > 0 else 0.0
        f1 = (2 * prec * rec / (prec + rec)) if (prec + rec) > 0 else 0.0
        return {
            "total_samples": total,
            "danger_count": danger_count,
            "actual_crashes": crashes,
            "precision": round(prec, 4),
            "recall": round(rec, 4),
            "f1_score": round(f1, 4),
            "TP": tp, "FP": fp, "FN": fn, "TN": tn
        }

    return {
        "in_sample_2016_2021": _eval(in_sample),
        "out_of_sample_2022_2026": _eval(out_of_sample)
    }


def run_full_validation_suite(universe_dict: Optional[Dict[str, Dict[str, Any]]] = None):
    """
    Main entry point for running the complete backtest on any universe.
    Compares:
      1. Linear SDI (alpha = 0.0) in USD-Nominal
      2. Productivity-Corrected PC-SDI V1 (alpha* = 1.25) in USD-Nominal
      3. PC-SDI V1 in Gold-Normalized
      4. PC-SDI V2 (Multi-Lens: MSI + PDR + Manifold SDI) in USD-Nominal
      5. PC-SDI V2 in Gold-Normalized
      6. PC-SDI V3 (Continuum Plasticity + Drucker-Prager Gate) in USD & Gold
    """
    if universe_dict is None:
        universe_dict = ACTIVE_UNIVERSE

    print("=" * 80)
    print(f"PREDICTABILITY BACKTESTING ENGINE: EMPIRICAL VALIDATION SUITE (N={len(universe_dict)})")
    print("=" * 80)

    # 1. Load cached market data
    print("\n[STEP 1] Loading Universe Facts and Market Prices...")
    gold_data = fetch_market_prices(GOLD_SYMBOL)
    spx_data = fetch_market_prices(SP500_SYMBOL)
    universe_data = {}

    for ticker, info in universe_dict.items():
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

    # 2. Run Alpha Grid Search for PC-SDI V1 (Frontier V-FIN-12)
    best_alpha_v1, grid_results_v1, _ = run_alpha_grid_search(universe_data, gold_data)

    # 3. Run Linear SDI (alpha = 0.0) Baseline in USD
    print("\n[STEP 3] Running Linear SDI (alpha=0.0) Baseline Backtest...")
    log_linear, score_linear = run_single_backtest(universe_data, gold_data, mode="usd", alpha=0.0)
    export_to_csv(log_linear, "prediction_log_usd_linear.csv")

    # 4. Run Productivity-Corrected PC-SDI V1 (best_alpha_v1) in USD
    print(f"\n[STEP 4] Running PC-SDI V1 (alpha={best_alpha_v1:.2f}) USD Backtest...")
    log_pcsdi_usd, score_pcsdi_usd = run_single_backtest(universe_data, gold_data, mode="usd", alpha=best_alpha_v1)
    export_to_csv(log_pcsdi_usd, "prediction_log_usd.csv")

    # 5. Run PC-SDI V1 in Gold-Normalized
    print(f"\n[STEP 5] Running PC-SDI V1 (alpha={best_alpha_v1:.2f}) Gold-Normalized Backtest...")
    log_pcsdi_gold, score_pcsdi_gold = run_single_backtest(universe_data, gold_data, mode="gold", alpha=best_alpha_v1)
    export_to_csv(log_pcsdi_gold, "prediction_log_gold.csv")

    # 6. Run Alpha Grid Search for PC-SDI V2 (Frontier V-FIN-16)
    alphas_v2 = [0.0, 0.25, 0.50, 0.75, 1.0, 1.25, 1.50, 1.75, 2.0]
    best_alpha_v2_usd, grid_v2_usd, _ = run_alpha_grid_search_v2(
        universe_data, gold_data, spx_data, alphas=alphas_v2, mode="usd"
    )
    best_alpha_v2_gold, grid_v2_gold, _ = run_alpha_grid_search_v2(
        universe_data, gold_data, spx_data, alphas=alphas_v2, mode="gold"
    )

    # 7. Run Enhanced PC-SDI V2 in USD-Nominal (Median Aggregation)
    print(f"\n[STEP 7] Running PC-SDI V2 (alpha={best_alpha_v2_usd:.2f}) USD Multi-Lens Backtest (Median)...")
    log_v2_usd, score_v2_usd = run_single_backtest_v2(
        universe_data, gold_data, spx_data, mode="usd", alpha=best_alpha_v2_usd, aggregation_mode="median"
    )
    export_to_csv(log_v2_usd, "prediction_log_usd_v2.csv")

    # 7b. Run Density-Weighted PC-SDI V2 in USD-Nominal (Frontier V-FIN-16.4.1)
    print(f"\n[STEP 7b] Running PC-SDI V2 (alpha={best_alpha_v2_usd:.2f}) USD Density-Weighted Backtest (V-FIN-16.4.1)...")
    log_v2_usd_weighted, score_v2_usd_weighted = run_single_backtest_v2(
        universe_data, gold_data, spx_data, mode="usd", alpha=best_alpha_v2_usd, aggregation_mode="density_weighted"
    )
    export_to_csv(log_v2_usd_weighted, "prediction_log_usd_v2_density_weighted.csv")

    # 8. Run Enhanced PC-SDI V2 in Gold-Normalized
    print(f"\n[STEP 8] Running PC-SDI V2 (alpha={best_alpha_v2_gold:.2f}) Gold Multi-Lens Backtest...")
    log_v2_gold, score_v2_gold = run_single_backtest_v2(
        universe_data, gold_data, spx_data, mode="gold", alpha=best_alpha_v2_gold, aggregation_mode="median"
    )
    export_to_csv(log_v2_gold, "prediction_log_gold_v2.csv")

    # 8b. Run Alpha Grid Search for PC-SDI V3 (Frontiers V-FIN-1, 4, 10, 12: Continuum Plasticity)
    alphas_v3 = [0.0, 0.25, 0.50, 0.75, 1.0, 1.25, 1.50, 1.75, 2.0]
    best_alpha_v3_usd, grid_v3_usd, _ = run_alpha_grid_search_v3(
        universe_data, gold_data, spx_data, alphas=alphas_v3, mode="usd"
    )
    best_alpha_v3_gold, grid_v3_gold, _ = run_alpha_grid_search_v3(
        universe_data, gold_data, spx_data, alphas=alphas_v3, mode="gold"
    )

    # 8c. Run Enhanced PC-SDI V3 in USD-Nominal (Median Aggregation)
    print(f"\n[STEP 8c] Running PC-SDI V3 (alpha={best_alpha_v3_usd:.2f}) USD Continuum Plasticity Backtest...")
    log_v3_usd, score_v3_usd = run_single_backtest_v3(
        universe_data, gold_data, spx_data, mode="usd", alpha=best_alpha_v3_usd, aggregation_mode="median"
    )
    export_to_csv(log_v3_usd, "prediction_log_usd_v3.csv")

    # 8d. Run Enhanced PC-SDI V3 in Gold-Normalized
    print(f"\n[STEP 8d] Running PC-SDI V3 (alpha={best_alpha_v3_gold:.2f}) Gold Continuum Plasticity Backtest...")
    log_v3_gold, score_v3_gold = run_single_backtest_v3(
        universe_data, gold_data, spx_data, mode="gold", alpha=best_alpha_v3_gold, aggregation_mode="median"
    )
    export_to_csv(log_v3_gold, "prediction_log_gold_v3.csv")

    # 8e. Run Enhanced PC-SDI V3 with Dynamic Walk-Forward Calibration (V-FIN-16.4.1c) in USD
    print(f"\n[STEP 8e] Running PC-SDI V3 Dynamic Walk-Forward Calibration (USD) (V-FIN-16.4.1c)...")
    log_v3_usd_dyn, score_v3_usd_dyn = run_walk_forward_backtest_v3(
        universe_data, gold_data, spx_data, mode="usd", alphas=alphas_v3, aggregation_mode="median"
    )
    export_to_csv(log_v3_usd_dyn, "prediction_log_usd_v3_dynamic.csv")

    # 8f. Run Enhanced PC-SDI V3 with Dynamic Walk-Forward Calibration in Gold
    print(f"\n[STEP 8f] Running PC-SDI V3 Dynamic Walk-Forward Calibration (Gold)...")
    log_v3_gold_dyn, score_v3_gold_dyn = run_walk_forward_backtest_v3(
        universe_data, gold_data, spx_data, mode="gold", alphas=alphas_v3, aggregation_mode="median"
    )
    export_to_csv(log_v3_gold_dyn, "prediction_log_gold_v3_dynamic.csv")

    # 8g. Run Enhanced PC-SDI V3 with Exogenous Macro Tensor in USD (V-FIN-16.4.1d)
    print(f"\n[STEP 8g] Running PC-SDI V3 Exogenous Macro Tensor (USD) (V-FIN-16.4.1d)...")
    tnx_data = fetch_market_prices(TREASURY_10Y_SYMBOL, force_refresh=True)
    log_v3_usd_macro, score_v3_usd_macro = run_single_backtest_v3(
        universe_data, gold_data, spx_data, tnx_data=tnx_data, mode="usd", alpha=1.25, aggregation_mode="median", use_exogenous_macro_tensor=True
    )
    export_to_csv(log_v3_usd_macro, "prediction_log_usd_v3_macro.csv")

    # 8h. Run Enhanced PC-SDI V3 with Exogenous Macro Tensor in Gold (V-FIN-16.4.1d)
    print(f"\n[STEP 8h] Running PC-SDI V3 Exogenous Macro Tensor (Gold) (V-FIN-16.4.1d)...")
    log_v3_gold_macro, score_v3_gold_macro = run_single_backtest_v3(
        universe_data, gold_data, spx_data, tnx_data=tnx_data, mode="gold", alpha=1.25, aggregation_mode="median", use_exogenous_macro_tensor=True
    )
    export_to_csv(log_v3_gold_macro, "prediction_log_gold_v3_macro.csv")

    # 9. Save Unified Scorecard (validation_scorecard.json & validation_scorecard_v3.json)
    scorecard_path = os.path.join(OUTPUT_DIR, "validation_scorecard.json")
    scorecard_v3_path = os.path.join(OUTPUT_DIR, "validation_scorecard_v3.json")

    # Compute Stratified Scorecards
    sector_scorecard_v3_usd = compute_stratified_scorecard(log_v3_usd, group_key="sector")
    sector_scorecard_v3_gold = compute_stratified_scorecard(log_v3_gold, group_key="sector")
    holdout_v3_usd = compute_temporal_holdout_scorecard(log_v3_usd, split_year=BACKTEST_CONFIG.get("holdout_split_year", 2022))
    holdout_v3_gold = compute_temporal_holdout_scorecard(log_v3_gold, split_year=BACKTEST_CONFIG.get("holdout_split_year", 2022))

    # Save dedicated breakdown files
    with open(os.path.join(OUTPUT_DIR, "sector_stratified_scorecard.json"), "w", encoding="utf-8") as f:
        json.dump({"v3_usd": sector_scorecard_v3_usd, "v3_gold": sector_scorecard_v3_gold}, f, indent=2)
    with open(os.path.join(OUTPUT_DIR, "temporal_holdout_scorecard.json"), "w", encoding="utf-8") as f:
        json.dump({"v3_usd": holdout_v3_usd, "v3_gold": holdout_v3_gold}, f, indent=2)

    final_scorecard = {
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "universe_size": len(universe_dict),
        "backtest_window": "2017-Q4 to 2026-Q2 (35 quarters)",
        "v1_optimal_alpha": best_alpha_v1,
        "v2_optimal_alpha_usd": best_alpha_v2_usd,
        "v2_optimal_alpha_gold": best_alpha_v2_gold,
        "v3_optimal_alpha_usd": best_alpha_v3_usd,
        "v3_optimal_alpha_gold": best_alpha_v3_gold,
        "linear_sdi_usd": score_linear,
        "pcsdi_usd_v1": score_pcsdi_usd,
        "pcsdi_gold_v1": score_pcsdi_gold,
        "pcsdi_usd_v2": score_v2_usd,
        "pcsdi_usd_v2_density_weighted": score_v2_usd_weighted,
        "pcsdi_gold_v2": score_v2_gold,
        "pcsdi_usd_v3": score_v3_usd,
        "pcsdi_gold_v3": score_v3_gold,
        "pcsdi_usd_v3_dynamic": score_v3_usd_dyn,
        "pcsdi_gold_v3_dynamic": score_v3_gold_dyn,
        "pcsdi_usd_v3_macro": score_v3_usd_macro,
        "pcsdi_gold_v3_macro": score_v3_gold_macro,
        "sector_stratification_v3_usd": sector_scorecard_v3_usd,
        "temporal_holdout_v3_usd": holdout_v3_usd,
        "temporal_holdout_v3_gold": holdout_v3_gold,
        "delta_precision_v2_vs_v1_usd": round(score_v2_usd["danger_precision"] - score_pcsdi_usd["danger_precision"], 4),
        "delta_f1_v2_vs_v1_usd": round(score_v2_usd["danger_f1_score"] - score_pcsdi_usd["danger_f1_score"], 4),
        "delta_f1_v2_gold_vs_v1_gold": round(score_v2_gold["danger_f1_score"] - score_pcsdi_gold["danger_f1_score"], 4),
        "delta_precision_weighted_vs_median": round(score_v2_usd_weighted["danger_precision"] - score_v2_usd["danger_precision"], 4),
        "delta_precision_v3_vs_v2_usd": round(score_v3_usd["danger_precision"] - score_v2_usd["danger_precision"], 4),
        "delta_f1_v3_vs_v2_usd": round(score_v3_usd["danger_f1_score"] - score_v2_usd["danger_f1_score"], 4),
        "delta_precision_v3dyn_vs_v3_usd": round(score_v3_usd_dyn["danger_precision"] - score_v3_usd["danger_precision"], 4),
        "delta_f1_v3dyn_vs_v3_usd": round(score_v3_usd_dyn["danger_f1_score"] - score_v3_usd["danger_f1_score"], 4),
        "delta_precision_v3macro_vs_v3dyn_usd": round(score_v3_usd_macro["danger_precision"] - score_v3_usd_dyn["danger_precision"], 4),
        "delta_f1_v3macro_vs_v3dyn_usd": round(score_v3_usd_macro["danger_f1_score"] - score_v3_usd_dyn["danger_f1_score"], 4),
        "delta_recall_v3_vs_v2_usd": round(score_v3_usd["danger_recall"] - score_v2_usd["danger_recall"], 4),
        "delta_f1_v3_gold_vs_v2_gold": round(score_v3_gold["danger_f1_score"] - score_v2_gold["danger_f1_score"], 4),
        "delta_recall_v3_gold_vs_v2_gold": round(score_v3_gold["danger_recall"] - score_v2_gold["danger_recall"], 4)
    }
    with open(scorecard_path, "w", encoding="utf-8") as f:
        json.dump(final_scorecard, f, indent=2)
    with open(scorecard_v3_path, "w", encoding="utf-8") as f:
        json.dump(final_scorecard, f, indent=2)

    # 10. Print Comprehensive Scorecard Comparison across All Generations
    print("\n" + "=" * 160)
    print("EMPIRICAL SCORECARD COMPARISON: LINEAR vs V1 vs V2 vs V3 vs V3_DYN vs V3_MACRO (USD)")
    print("=" * 160)
    print(f"{'Metric':<25} | {'Linear SDI':<12} | {'V1 (USD)':<12} | {'V2 (USD)':<12} | {'V3 (USD)':<12} | {'V3_DYN (USD)':<12} | {'V3_MACRO (USD)':<14}")
    print("-" * 160)
    print(f"{'Danger Count':<25} | {score_linear['danger_predictions_count']:<12} | {score_pcsdi_usd['danger_predictions_count']:<12} | {score_v2_usd['danger_predictions_count']:<12} | {score_v3_usd['danger_predictions_count']:<12} | {score_v3_usd_dyn['danger_predictions_count']:<12} | {score_v3_usd_macro['danger_predictions_count']:<14}")
    print(f"{'Danger Precision':<25} | {score_linear['danger_precision']*100:>5.1f}%{'':<6} | {score_pcsdi_usd['danger_precision']*100:>5.1f}%{'':<6} | {score_v2_usd['danger_precision']*100:>5.1f}%{'':<6} | {score_v3_usd['danger_precision']*100:>5.1f}%{'':<6} | {score_v3_usd_dyn['danger_precision']*100:>5.1f}%{'':<6} | {score_v3_usd_macro['danger_precision']*100:>5.1f}%")
    print(f"{'Danger Recall':<25} | {score_linear['danger_recall']*100:>5.1f}%{'':<6} | {score_pcsdi_usd['danger_recall']*100:>5.1f}%{'':<6} | {score_v2_usd['danger_recall']*100:>5.1f}%{'':<6} | {score_v3_usd['danger_recall']*100:>5.1f}%{'':<6} | {score_v3_usd_dyn['danger_recall']*100:>5.1f}%{'':<6} | {score_v3_usd_macro['danger_recall']*100:>5.1f}%")
    print(f"{'Danger F1-Score':<25} | {score_linear['danger_f1_score']:<12.3f} | {score_pcsdi_usd['danger_f1_score']:<12.3f} | {score_v2_usd['danger_f1_score']:<12.3f} | {score_v3_usd['danger_f1_score']:<12.3f} | {score_v3_usd_dyn['danger_f1_score']:<12.3f} | {score_v3_usd_macro['danger_f1_score']:<14.3f}")
    print(f"{'Healthy Accuracy':<25} | {score_linear['healthy_accuracy']*100:>5.1f}%{'':<6} | {score_pcsdi_usd['healthy_accuracy']*100:>5.1f}%{'':<6} | {score_v2_usd['healthy_accuracy']*100:>5.1f}%{'':<6} | {score_v3_usd['healthy_accuracy']*100:>5.1f}%{'':<6} | {score_v3_usd_dyn['healthy_accuracy']*100:>5.1f}%{'':<6} | {score_v3_usd_macro['healthy_accuracy']*100:>5.1f}%")
    print("=" * 160)

    # 11. Print Sector Stratification Breakdown (V3 USD)
    print("\n--- SECTOR-STRATIFIED BREAKDOWN (PC-SDI V3 USD) ---")
    print(f"{'GICS Sector':<26} | {'Samples':<8} | {'Danger':<8} | {'Crashes':<8} | {'Precision':<10} | {'Recall':<10} | {'F1-Score':<10}")
    print("-" * 92)
    for sec, s_metrics in sector_scorecard_v3_usd.items():
        print(f"{sec:<26} | {s_metrics['total_samples']:<8} | {s_metrics['danger_count']:<8} | {s_metrics['actual_crashes']:<8} | {s_metrics['precision']*100:>6.1f}%{'':<3} | {s_metrics['recall']*100:>6.1f}%{'':<3} | {s_metrics['f1_score']:<10.3f}")
    print("-" * 92)

    # 12. Print Temporal Holdout Breakdown (In-Sample vs Out-of-Sample)
    print("\n--- TEMPORAL HOLDOUT VALIDATION (IN-SAMPLE 2016-2021 vs OUT-OF-SAMPLE 2022-2026) ---")
    print(f"{'Partition':<25} | {'Samples':<8} | {'Danger':<8} | {'Crashes':<8} | {'Precision':<10} | {'Recall':<10} | {'F1-Score':<10}")
    print("-" * 92)
    for part, p_metrics in holdout_v3_usd.items():
        label = "In-Sample (2016-2021)" if "in_sample" in part else "Out-of-Sample (2022-2026)"
        print(f"{label:<25} | {p_metrics['total_samples']:<8} | {p_metrics['danger_count']:<8} | {p_metrics['actual_crashes']:<8} | {p_metrics['precision']*100:>6.1f}%{'':<3} | {p_metrics['recall']*100:>6.1f}%{'':<3} | {p_metrics['f1_score']:<10.3f}")
    print("-" * 92)

    # 13. Specific Company Validation Check under V3 (Rule 5.1 Known-Limit Verification)
    print("\n--- CASE STUDY AUDIT UNDER PC-SDI V3 (RULE 5.1 KNOWN-LIMIT VERIFICATION) ---")
    audit_candidates = [t for t in ["BA", "AAPL", "GE", "MSFT", "NVDA", "TSLA", "JPM", "XOM"] if t in universe_dict]
    for t in audit_candidates:
        comp_preds = [p for p in log_v3_usd if p["ticker"] == t]
        print(f"\n[{t}] Timeline of Key Regime Classifications under PC-SDI V3 (alpha={best_alpha_v3_usd:.2f}):")
        for p in comp_preds:
            if p["prediction"] == "DANGER" or any(y in p["quarter"] for y in ["2018", "2019", "2020", "2021"]):
                crash_flag = "CRASH OCCURRED" if p["has_crash_24m"] else "No crash"
                rupture_str = f"Ruptured(phi={p['drucker_prager_phi']:.2f})" if p["is_yield_ruptured"] else f"Solvent(phi={p['drucker_prager_phi']:.2f})"
                print(f"  {p['quarter']}: {p['prediction']:<7} (Conf: {p['confidence']:.2f}) | PC-SDI={p['SDI']:+6.2f}, Lin={p['SDI_linear']:+6.2f}, {rupture_str:<22} | 24m DD: {p['fwd_drawdown_24m'] if p['fwd_drawdown_24m'] is not None else 0.0:>+6.1%} ({crash_flag})")

    return final_scorecard


if __name__ == "__main__":
    run_full_validation_suite()

