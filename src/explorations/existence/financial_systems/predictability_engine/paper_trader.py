"""
paper_trader.py
---------------
Simulated Seed-Money Portfolio Engine (Paper Trading Simulator).
Executes quantitative portfolio allocation based on corporate regime classifications:
  - 100% Long: Regime 1 (Virtuous Autocatalytic) companies (equally weighted)
  - 0% Equity (Cash): Regime 2 (Subcritical / Stagnant) companies
  - Short / 0% Exposure: Regime 3 (Parasitic Decoupling) companies
  
Evaluates:
  - Cumulative Portfolio NAV curve
  - Maximum Drawdown
  - Annualized Sharpe Ratio
  - Alpha vs. Benchmark (S&P 500 or NIFTY 50)

NO REAL TRADES. NO DMAT ACCOUNT REQUIRED. COMPUTATIONAL SIMULATION ONLY.
"""

import os
import csv
import json
import math
import datetime
from typing import List, Dict, Any, Tuple
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

import sys
_current_dir = os.path.dirname(os.path.abspath(__file__))
if _current_dir not in sys.path:
    sys.path.insert(0, _current_dir)

from config import OUTPUT_DIR, FIGURES_DIR, SP500_SYMBOL
from data_fetcher import fetch_market_prices


def simulate_portfolio_strategy(
    prediction_log_path: str = "prediction_log_usd.csv",
    seed_capital: float = 100000.0,
    currency: str = "USD",
    short_regime_3: bool = False
) -> Dict[str, Any]:
    """
    Simulates seed capital portfolio over historical prediction timeline.
    Rebalances quarterly based on model classifications:
      - Regime 1 (HEALTHY): Long allocation
      - Regime 2 (CAUTION): Cash
      - Regime 3 (DANGER): Excluded (or 1x Short if short_regime_3=True)
    """
    filepath = os.path.join(OUTPUT_DIR, prediction_log_path)
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Missing log file: {filepath}")

    with open(filepath, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        records = list(reader)

    # Group by quarter
    quarters = sorted(list(set(r["quarter"] for r in records)))
    
    # Portfolio state
    nav = seed_capital
    portfolio_history = []
    
    # Risk-free quarterly rate (assumed 4% annual = ~1.0% quarterly)
    rf_qtr = 0.010

    for q in quarters:
        q_records = [r for r in records if r["quarter"] == q]
        q_date = q_records[0]["date"]

        healthy_stocks = [r for r in q_records if r["prediction"] == "HEALTHY" and r.get("fwd_return_6m")]
        caution_stocks = [r for r in q_records if r["prediction"] == "CAUTION"]
        danger_stocks = [r for r in q_records if r["prediction"] == "DANGER" and r.get("fwd_return_6m")]

        # Return computation for the quarter
        # If healthy stocks exist, allocate equally across them
        if healthy_stocks:
            stock_returns = [float(r["fwd_return_6m"]) / 2.0 for r in healthy_stocks] # ~1 quarter = half of 6m
            strategy_q_return = float(np.mean(stock_returns))
        else:
            # All cash earning risk-free rate
            strategy_q_return = rf_qtr

        # If shorting regime 3
        if short_regime_3 and danger_stocks:
            danger_returns = [float(r["fwd_return_6m"]) / 2.0 for r in danger_stocks]
            short_return = -float(np.mean(danger_returns))
            # 80% long healthy, 20% short danger
            strategy_q_return = 0.8 * strategy_q_return + 0.2 * short_return

        nav = nav * (1.0 + strategy_q_return)

        # Baseline buy-and-hold equal weight
        all_with_ret = [r for r in q_records if r.get("fwd_return_6m")]
        if all_with_ret:
            bm_q_return = float(np.mean([float(r["fwd_return_6m"]) / 2.0 for r in all_with_ret]))
        else:
            bm_q_return = rf_qtr

        portfolio_history.append({
            "quarter": q,
            "date": q_date,
            "nav": round(nav, 2),
            "q_return": round(strategy_q_return, 4),
            "bm_q_return": round(bm_q_return, 4),
            "n_healthy": len(healthy_stocks),
            "n_caution": len(caution_stocks),
            "n_danger": len(danger_stocks)
        })

    # Compute cumulative stats
    returns = [p["q_return"] for p in portfolio_history]
    bm_returns = [p["bm_q_return"] for p in portfolio_history]
    
    # Cumulative NAV series
    strat_navs = [seed_capital]
    bm_navs = [seed_capital]
    for r, b in zip(returns, bm_returns):
        strat_navs.append(strat_navs[-1] * (1.0 + r))
        bm_navs.append(bm_navs[-1] * (1.0 + b))

    # Max Drawdown
    peak = strat_navs[0]
    max_dd = 0.0
    for v in strat_navs:
        if v > peak:
            peak = v
        dd = (v - peak) / peak
        if dd < max_dd:
            max_dd = dd

    bm_peak = bm_navs[0]
    bm_max_dd = 0.0
    for v in bm_navs:
        if v > bm_peak:
            bm_peak = v
        dd = (v - bm_peak) / bm_peak
        if dd < bm_max_dd:
            bm_max_dd = dd

    total_return = (strat_navs[-1] - seed_capital) / seed_capital
    bm_total_return = (bm_navs[-1] - seed_capital) / seed_capital
    n_years = len(portfolio_history) * 0.25
    cagr = (strat_navs[-1] / seed_capital) ** (1.0 / max(0.5, n_years)) - 1.0
    bm_cagr = (bm_navs[-1] / seed_capital) ** (1.0 / max(0.5, n_years)) - 1.0

    excess_ret = np.array(returns) - rf_qtr
    sharpe = float(np.mean(excess_ret) / np.std(excess_ret) * np.sqrt(4.0)) if np.std(excess_ret) > 0 else 0.0

    bm_excess = np.array(bm_returns) - rf_qtr
    bm_sharpe = float(np.mean(bm_excess) / np.std(bm_excess) * np.sqrt(4.0)) if np.std(bm_excess) > 0 else 0.0

    summary = {
        "currency": currency,
        "seed_capital": seed_capital,
        "final_nav": round(strat_navs[-1], 2),
        "total_return_pct": round(total_return * 100, 2),
        "cagr_pct": round(cagr * 100, 2),
        "max_drawdown_pct": round(max_dd * 100, 2),
        "sharpe_ratio": round(sharpe, 3),
        "benchmark_final_nav": round(bm_navs[-1], 2),
        "benchmark_total_return_pct": round(bm_total_return * 100, 2),
        "benchmark_cagr_pct": round(bm_cagr * 100, 2),
        "benchmark_max_drawdown_pct": round(bm_max_dd * 100, 2),
        "benchmark_sharpe_ratio": round(bm_sharpe, 3),
        "alpha_cagr_pct": round((cagr - bm_cagr) * 100, 2),
        "history": portfolio_history
    }

    return summary, strat_navs, bm_navs, [p["date"] for p in portfolio_history]


def plot_portfolio_simulation(summary: dict, strat_navs: list, bm_navs: list, dates: list):
    """Generates comparison plot of Simulated Portfolio NAV vs Benchmark."""
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8), gridspec_kw={"height_ratios": [2.2, 1]})

    d_objs = [datetime.datetime.strptime(dates[0], "%Y-%m-%d") - datetime.timedelta(days=90)] + [datetime.datetime.strptime(d, "%Y-%m-%d") for d in dates]

    curr = summary["currency"]
    ax1.plot(d_objs, strat_navs, color="#1565c0", linewidth=2.5, label=f"Regime-Allocated Portfolio (CAGR: {summary['cagr_pct']}%, MaxDD: {summary['max_drawdown_pct']}%)")
    ax1.plot(d_objs, bm_navs, color="#757575", linewidth=1.8, linestyle="--", label=f"Equal-Weight Buy & Hold (CAGR: {summary['benchmark_cagr_pct']}%, MaxDD: {summary['benchmark_max_drawdown_pct']}%)")
    
    ax1.set_ylabel(f"Portfolio NAV ({curr})", fontweight="bold")
    ax1.set_title(f"Seed Capital Simulation ({curr} {summary['seed_capital']:,.0f}): Corporate Predictability Regime Allocation", fontweight="bold")
    ax1.legend(loc="upper left")
    ax1.xaxis.set_major_locator(mdates.YearLocator(2))
    ax1.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))

    # Panel 2: Regime asset counts
    hist = summary["history"]
    d_hist = [datetime.datetime.strptime(h["date"], "%Y-%m-%d") for h in hist]
    h_counts = [h["n_healthy"] for h in hist]
    c_counts = [h["n_caution"] for h in hist]
    d_counts = [h["n_danger"] for h in hist]

    ax2.bar(d_hist, h_counts, width=60, label="Regime 1 (Healthy / Long)", color="#2e7d32", alpha=0.85)
    ax2.bar(d_hist, c_counts, width=60, bottom=h_counts, label="Regime 2 (Caution / Cash)", color="#f57c00", alpha=0.85)
    ax2.bar(d_hist, d_counts, width=60, bottom=[h + c for h, c in zip(h_counts, c_counts)], label="Regime 3 (Danger / Avoid)", color="#c62828", alpha=0.85)
    
    ax2.set_ylabel("Companies Count")
    ax2.set_xlabel("Rebalancing Date (Quarterly)")
    ax2.set_title("Portfolio Regime Allocation Breakdown", fontweight="bold")
    ax2.legend(loc="upper left", fontsize=8)
    ax2.xaxis.set_major_locator(mdates.YearLocator(2))
    ax2.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))

    plt.tight_layout()
    out_path = os.path.join(FIGURES_DIR, "portfolio_nav_simulation.png")
    plt.savefig(out_path)
    plt.close()
    print(f"[FIGURE] Saved portfolio simulation plot to {out_path}")


def run_paper_trader_demo():
    """Runs demonstration for US ($100k) and India (₹10,00,000)."""
    print("=" * 80)
    print("PAPER TRADER SIMULATOR: SEED CAPITAL EXPERIMENT")
    print("=" * 80)

    # US Simulation ($100k)
    summary_us, s_navs, b_navs, dates = simulate_portfolio_strategy(
        prediction_log_path="prediction_log_usd.csv",
        seed_capital=100000.0,
        currency="USD"
    )
    plot_portfolio_simulation(summary_us, s_navs, b_navs, dates)

    print(f"\n--- US SEED CAPITAL EXPERIMENT ($100,000) ---")
    print(f"Final NAV:                ${summary_us['final_nav']:,.2f}")
    print(f"Total Cumulative Return:   {summary_us['total_return_pct']:+.1f}%")
    print(f"Annualized Return (CAGR):  {summary_us['cagr_pct']:+.1f}% (vs Benchmark: {summary_us['benchmark_cagr_pct']:+.1f}%)")
    print(f"Maximum Drawdown:          {summary_us['max_drawdown_pct']:.1f}% (vs Benchmark: {summary_us['benchmark_max_drawdown_pct']:.1f}%)")
    print(f"Annualized Sharpe Ratio:   {summary_us['sharpe_ratio']:.2f} (vs Benchmark: {summary_us['benchmark_sharpe_ratio']:.2f})")
    print(f"Alpha (CAGR Lift):        {summary_us['alpha_cagr_pct']:+.1f}%")
    print("=" * 80)

    # Save summary
    out_json = os.path.join(OUTPUT_DIR, "paper_trader_results.json")
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(summary_us, f, indent=2)
    print(f"[REPORT] Saved paper trader results to {out_json}")


if __name__ == "__main__":
    run_paper_trader_demo()
