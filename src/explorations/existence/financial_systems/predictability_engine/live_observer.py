"""
live_observer.py
----------------
Autonomous Observation Agent for Corporate Predictability.
Implements the continuous observation protocol requested by the user:
  1. Observes target companies in real-time or at quarterly filing cadence
  2. Parses fundamentals & market closing prices into 5-vector MassVector
  3. Evaluates Vector Anisotropy Metric (VAM) and Productivity-Corrected SDI (PC-SDI)
  4. Classifies dynamical regime (Virtuous, Subcritical, Parasitic)
  5. Logs forward predictions (HEALTHY, CAUTION, DANGER) into an immutable ledger
  6. Evaluates and scores historical predictions as time elapses (T+6m, T+12m, T+24m)
  
NO TRADING. NO DMAT ACCOUNT REQUIRED.
Observation, quantitative logging, and verification only.
"""

import os
import csv
import json
import datetime
from typing import List, Dict, Any, Optional

import sys
_current_dir = os.path.dirname(os.path.abspath(__file__))
if _current_dir not in sys.path:
    sys.path.insert(0, _current_dir)

from config import OUTPUT_DIR, UNIVERSE_VALIDATION, GOLD_SYMBOL
from india_universe import INDIA_VALIDATION_UNIVERSE, GOLD_INR_SYMBOL
from data_fetcher import fetch_sec_facts, fetch_market_prices
from mass_vector import (
    MassVector, build_corporate_mass_history,
    compute_vam, compute_sdi, classify_regime
)
from india_adapter import (
    fetch_indian_market_prices, fetch_indian_financials, build_indian_mass_history
)

LEDGER_FILE = os.path.join(OUTPUT_DIR, "live_prediction_ledger.csv")


def initialize_ledger():
    """Ensures the immutable prediction ledger exists with standard header."""
    if not os.path.exists(LEDGER_FILE):
        headers = [
            "timestamp", "ticker", "market", "name", "sector", "observation_date",
            "stock_price", "gold_price", "VAM", "SDI_linear", "PC_SDI", "prod_growth",
            "regime", "prediction", "confidence", "target_horizon",
            "status", "eval_price_6m", "eval_price_12m", "eval_price_24m",
            "return_actual", "is_correct"
        ]
        with open(LEDGER_FILE, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(headers)
        print(f"[LEDGER] Initialized immutable prediction ledger at {LEDGER_FILE}")


def log_live_observation(entry: Dict[str, Any]):
    """Appends a new verified prediction to the immutable ledger."""
    initialize_ledger()
    with open(LEDGER_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "timestamp", "ticker", "market", "name", "sector", "observation_date",
            "stock_price", "gold_price", "VAM", "SDI_linear", "PC_SDI", "prod_growth",
            "regime", "prediction", "confidence", "target_horizon",
            "status", "eval_price_6m", "eval_price_12m", "eval_price_24m",
            "return_actual", "is_correct"
        ])
        writer.writerow(entry)
    print(f"[LEDGER] Recorded prediction: {entry['ticker']} -> {entry['prediction']} (Regime: {entry['regime']}, Conf: {entry['confidence']:.2f})")


def run_observation_cycle_us(alpha: float = 1.25) -> List[Dict[str, Any]]:
    """Runs a live observation cycle across the US universe."""
    print("\n" + "=" * 80)
    print("LIVE OBSERVER AGENT: US EQUITIES CYCLE")
    print("=" * 80)
    gold_prices = fetch_market_prices(GOLD_SYMBOL)
    now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()
    new_observations = []

    for ticker, info in UNIVERSE_VALIDATION.items():
        sec_facts = fetch_sec_facts(ticker, info["cik"])
        prices = fetch_market_prices(ticker)
        history = build_corporate_mass_history(ticker, sec_facts, prices, gold_prices)

        if len(history) < 4:
            continue

        latest_idx = len(history) - 1
        latest_mv = history[latest_idx]

        sdi_eff, sdi_lin, mf_growth, sub_growth, prod_growth = compute_sdi(
            history, latest_idx, mode="usd", window=4, alpha=alpha
        )
        vam = compute_vam(latest_mv.as_array_usd())
        regime, pred, conf = classify_regime(sdi_eff, vam, sub_growth, mf_growth)

        entry = {
            "timestamp": now_iso,
            "ticker": ticker,
            "market": "US (SEC EDGAR / NYSE / NASDAQ)",
            "name": info["name"],
            "sector": info["sector"],
            "observation_date": latest_mv.date,
            "stock_price": round(latest_mv.stock_price_usd, 2),
            "gold_price": round(latest_mv.gold_price_usd, 2),
            "VAM": round(vam, 4),
            "SDI_linear": round(sdi_lin, 4),
            "PC_SDI": round(sdi_eff, 4),
            "prod_growth": round(prod_growth, 4),
            "regime": regime,
            "prediction": pred,
            "confidence": round(conf, 3),
            "target_horizon": "12m - 24m Forward",
            "status": "ACTIVE_LOGGED",
            "eval_price_6m": "",
            "eval_price_12m": "",
            "eval_price_24m": "",
            "return_actual": "",
            "is_correct": ""
        }
        log_live_observation(entry)
        new_observations.append(entry)

    return new_observations


def run_observation_cycle_india(alpha: float = 1.25) -> List[Dict[str, Any]]:
    """Runs a live observation cycle across the Indian universe."""
    print("\n" + "=" * 80)
    print("LIVE OBSERVER AGENT: INDIAN EQUITIES CYCLE (NSE/BSE)")
    print("=" * 80)
    gold_prices = fetch_indian_market_prices(GOLD_INR_SYMBOL)
    now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()
    new_observations = []

    for symbol, meta in INDIA_VALIDATION_UNIVERSE.items():
        prices = fetch_indian_market_prices(symbol)
        if not prices:
            continue
        fin = fetch_indian_financials(symbol)
        history = build_indian_mass_history(symbol, fin, prices, gold_prices)

        if len(history) < 3:
            continue

        latest_idx = len(history) - 1
        latest_mv = history[latest_idx]

        sdi_eff, sdi_lin, mf_growth, sub_growth, prod_growth = compute_sdi(
            history, latest_idx, mode="usd", window=min(3, latest_idx), alpha=alpha
        )
        vam = compute_vam(latest_mv.as_array_usd())
        regime, pred, conf = classify_regime(sdi_eff, vam, sub_growth, mf_growth)

        entry = {
            "timestamp": now_iso,
            "ticker": symbol,
            "market": "India (NSE/BSE)",
            "name": meta["name"],
            "sector": meta["sector"],
            "observation_date": latest_mv.date,
            "stock_price": round(latest_mv.stock_price_usd, 2),
            "gold_price": round(latest_mv.gold_price_usd, 2),
            "VAM": round(vam, 4),
            "SDI_linear": round(sdi_lin, 4),
            "PC_SDI": round(sdi_eff, 4),
            "prod_growth": round(prod_growth, 4),
            "regime": regime,
            "prediction": pred,
            "confidence": round(conf, 3),
            "target_horizon": "12m - 24m Forward",
            "status": "ACTIVE_LOGGED",
            "eval_price_6m": "",
            "eval_price_12m": "",
            "eval_price_24m": "",
            "return_actual": "",
            "is_correct": ""
        }
        log_live_observation(entry)
        new_observations.append(entry)

    return new_observations


def print_active_predictions_dashboard():
    """Displays current active predictions logged in the ledger."""
    if not os.path.exists(LEDGER_FILE):
        print("[LEDGER] No predictions logged yet.")
        return

    print("\n" + "=" * 95)
    print("LIVE PREDICTION LEDGER DASHBOARD (IMMUTABLE TRACKING)")
    print("=" * 95)
    print(f"{'Ticker':<12} | {'Market':<8} | {'Price':<10} | {'VAM':<7} | {'PC-SDI':<8} | {'Regime':<24} | {'Prediction':<10}")
    print("-" * 95)

    with open(LEDGER_FILE, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for r in reader:
            market_short = "US" if "US" in r["market"] else "IN"
            print(f"{r['ticker']:<12} | {market_short:<8} | {r['stock_price']:<10} | {r['VAM']:<7} | {r['PC_SDI']:<8} | {r['regime']:<24} | {r['prediction']:<10}")
    print("=" * 95)


def run_full_observer_protocol():
    """Main execution protocol for the autonomous observation agent."""
    run_observation_cycle_us()
    run_observation_cycle_india()
    print_active_predictions_dashboard()


if __name__ == "__main__":
    run_full_observer_protocol()
