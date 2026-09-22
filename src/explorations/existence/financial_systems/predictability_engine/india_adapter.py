"""
india_adapter.py
----------------
Data Adapter and MassVector Parser for Indian Equities (NSE/BSE).
Fetches market prices and quarterly financial statements via yfinance for Indian tickers.
Constructs 5-vector corporate mass histories in INR and Gold-INR coordinates:
  M_C = (M_L, M_H, M_P, M_M, M_F)^T
Evaluates VAM, SDI, and PC-SDI on Indian equities.
"""

import os
import json
import time
import datetime
from typing import List, Dict, Any, Tuple
import numpy as np
import yfinance as yf

import sys
_current_dir = os.path.dirname(os.path.abspath(__file__))
if _current_dir not in sys.path:
    sys.path.insert(0, _current_dir)

from config import PRICE_CACHE_DIR, CACHE_DIR, OUTPUT_DIR
from india_universe import INDIA_VALIDATION_UNIVERSE, NIFTY_50_SYMBOL, GOLD_INR_SYMBOL
from mass_vector import (
    MassVector, compute_vam, compute_sdi, classify_regime
)
from backtester import precompute_company_forward_outcomes, export_to_csv

INDIA_CACHE_DIR = os.path.join(CACHE_DIR, "india_facts")
os.makedirs(INDIA_CACHE_DIR, exist_ok=True)


def fetch_indian_market_prices(symbol: str, force_refresh: bool = False) -> List[dict]:
    """Fetch 5-year daily close history for Indian ticker."""
    safe_symbol = symbol.replace(".", "_").replace("^", "_").replace("=", "_")
    cache_path = os.path.join(PRICE_CACHE_DIR, f"{safe_symbol}_prices.json")

    if not force_refresh and os.path.exists(cache_path):
        print(f"[CACHE] Loaded price data for {symbol} from {cache_path}")
        with open(cache_path, "r", encoding="utf-8") as f:
            return json.load(f)

    print(f"[YFINANCE] Fetching daily prices for {symbol}...")
    ticker = yf.Ticker(symbol)
    df = ticker.history(period="10y", interval="1d")
    
    clean_series = []
    for idx, row in df.iterrows():
        dt_str = idx.strftime("%Y-%m-%d")
        close_val = float(row["Close"])
        vol_val = int(row["Volume"]) if not np.isnan(row["Volume"]) else 0
        if not np.isnan(close_val) and close_val > 0:
            clean_series.append({
                "date": dt_str,
                "timestamp": int(idx.timestamp()),
                "close": close_val,
                "volume": vol_val
            })

    with open(cache_path, "w", encoding="utf-8") as f:
        json.dump(clean_series, f)
    print(f"[YFINANCE] Cached {len(clean_series)} daily points for {symbol}")
    return clean_series


def fetch_indian_financials(symbol: str, force_refresh: bool = False) -> dict:
    """Fetch quarterly income statement and balance sheet via yfinance."""
    safe_symbol = symbol.replace(".", "_")
    cache_path = os.path.join(INDIA_CACHE_DIR, f"{safe_symbol}_financials.json")

    if not force_refresh and os.path.exists(cache_path):
        print(f"[CACHE] Loaded Indian financials for {symbol}")
        with open(cache_path, "r", encoding="utf-8") as f:
            return json.load(f)

    print(f"[YFINANCE] Fetching quarterly balance sheet and income statement for {symbol}...")
    ticker = yf.Ticker(symbol)
    
    try:
        q_bs = ticker.quarterly_balance_sheet
        q_is = ticker.quarterly_income_stmt
    except Exception as e:
        print(f"[WARN] Error fetching statements for {symbol}: {e}")
        q_bs = None
        q_is = None

    data = {
        "dates": [],
        "balance_sheet": {},
        "income_statement": {}
    }

    if q_bs is not None and not q_bs.empty:
        for col in q_bs.columns:
            d_str = col.strftime("%Y-%m-%d")
            data["dates"].append(d_str)
            col_data = {str(k): (float(v) if not np.isnan(v) else 0.0) for k, v in q_bs[col].items()}
            data["balance_sheet"][d_str] = col_data

    if q_is is not None and not q_is.empty:
        for col in q_is.columns:
            d_str = col.strftime("%Y-%m-%d")
            if d_str not in data["dates"]:
                data["dates"].append(d_str)
            col_data = {str(k): (float(v) if not np.isnan(v) else 0.0) for k, v in q_is[col].items()}
            data["income_statement"][d_str] = col_data

    data["dates"] = sorted(list(set(data["dates"])))
    with open(cache_path, "w", encoding="utf-8") as f:
        json.dump(data, f)
    print(f"[YFINANCE] Cached {len(data['dates'])} quarters for {symbol}")
    return data


def build_indian_mass_history(
    symbol: str,
    fin_data: dict,
    prices: List[dict],
    gold_prices: List[dict]
) -> List[MassVector]:
    """Constructs MassVector sequence in INR and Gold-INR."""
    price_by_date = {p["date"]: p["close"] for p in prices}
    sorted_price_dates = sorted(price_by_date.keys())
    
    gold_by_date = {g["date"]: g["close"] for g in gold_prices}
    sorted_gold_dates = sorted(gold_by_date.keys())

    def get_price(d: str, p_map: dict, s_dates: list) -> float:
        if d in p_map:
            return p_map[d]
        valid = [dt for dt in s_dates if dt <= d]
        return p_map[valid[-1]] if valid else (p_map[s_dates[0]] if s_dates else 1.0)

    dates = fin_data.get("dates", [])
    history = []

    for d_str in dates:
        dt = datetime.datetime.strptime(d_str, "%Y-%m-%d").date()
        q_num = (dt.month - 1) // 3 + 1
        q_label = f"{dt.year}-Q{q_num}"

        bs = fin_data["balance_sheet"].get(d_str, {})
        inc = fin_data["income_statement"].get(d_str, {})

        stock_price = get_price(d_str, price_by_date, sorted_price_dates)
        gold_price = get_price(d_str, gold_by_date, sorted_gold_dates)

        # 1. Physical Mass: Net PP&E / Tangible Assets
        ppe = bs.get("Net PPE") or bs.get("Property Plant Equipment Net") or bs.get("Net Tangible Assets") or 1e8

        # 2. Legal Mass: Goodwill and Intangible Assets
        goodwill = bs.get("Goodwill") or 0.0
        intangibles = bs.get("Other Intangible Assets") or bs.get("Goodwill And Other Intangible Assets") or (ppe * 0.15)
        M_L = goodwill + intangibles

        # 3. Human Mass: SG&A + Employee Benefits / R&D
        sga = inc.get("Selling General And Administration") or inc.get("Operating Expense") or 1e8
        rd = inc.get("Research And Development") or 0.0
        M_H = (rd + sga) * 4.0

        # 4. Market Mass: Revenue x Margin
        rev = inc.get("Total Revenue") or inc.get("Operating Revenue") or 1e8
        gp = inc.get("Gross Profit") or inc.get("Operating Income") or (rev * 0.25)
        M_M = gp * 4.0

        # 5. Financial Mass: Market Capitalization
        shares = bs.get("Share Issued") or bs.get("Ordinary Shares Number") or 1e7
        M_F = stock_price * shares

        mv = MassVector(
            date=d_str,
            quarter=q_label,
            ticker=symbol,
            M_L=max(1e6, float(M_L)),
            M_H=max(1e6, float(M_H)),
            M_P=max(1e6, float(ppe)),
            M_M=max(1e6, float(M_M)),
            M_F=max(1e6, float(M_F)),
            gold_price_usd=max(1.0, float(gold_price)),
            stock_price_usd=max(0.01, float(stock_price)),
            shares_outstanding=max(1.0, float(shares))
        )
        history.append(mv)

    return history


def run_indian_validation_backtest(alpha: float = 1.25) -> Dict[str, Any]:
    """Runs complete predictability backtest across Indian validation universe."""
    print("=" * 80)
    print("INDIAN EQUITY PREDICTABILITY BACKTEST: NIFTY VALIDATION UNIVERSE")
    print("=" * 80)

    # 1. Fetch Indian Gold proxy (GOLDBEES.NS)
    gold_data = fetch_indian_market_prices(GOLD_INR_SYMBOL)
    universe_data = {}

    for symbol, meta in INDIA_VALIDATION_UNIVERSE.items():
        prices = fetch_indian_market_prices(symbol)
        fin = fetch_indian_financials(symbol)
        history = build_indian_mass_history(symbol, fin, prices, gold_data)

        if len(history) >= 4:
            fwd_outcomes = precompute_company_forward_outcomes(prices, [mv.date for mv in history], [6, 12, 24])
            universe_data[symbol] = {
                "meta": meta,
                "prices": prices,
                "history": history,
                "fwd_outcomes": fwd_outcomes
            }
            print(f"  Loaded {symbol} ({meta['name']}): {len(history)} quarters available.")
        else:
            print(f"  [SKIP] {symbol}: Insufficient quarterly history ({len(history)} quarters).")

    # 2. Run Backtest
    prediction_log = []
    window = 3 # 3 quarters lookback due to 4-year API depth

    for symbol, comp in universe_data.items():
        history = comp["history"]
        fwd_map = comp["fwd_outcomes"]

        for i in range(window, len(history)):
            mv = history[i]
            sdi_eff, sdi_lin, mf_growth, sub_growth, prod_growth = compute_sdi(
                history, i, mode="usd", window=window, alpha=alpha
            )
            vam = compute_vam(mv.as_array_usd())
            regime, pred, conf = classify_regime(sdi_eff, vam, sub_growth, mf_growth)
            fwd = fwd_map.get(mv.date, {})

            crash_12m = fwd.get("has_crash_12m")
            crash_24m = fwd.get("has_crash_24m")
            ret_12m = fwd.get("return_12m")

            is_correct = None
            if pred == "DANGER":
                if crash_12m is not None or crash_24m is not None:
                    is_correct = bool(crash_12m or crash_24m or (ret_12m is not None and ret_12m < 0.0))
            elif pred == "HEALTHY":
                if ret_12m is not None:
                    is_correct = bool(ret_12m > 0.0)

            entry = {
                "ticker": symbol,
                "name": comp["meta"]["name"],
                "sector": comp["meta"]["sector"],
                "quarter": mv.quarter,
                "date": mv.date,
                "stock_price_inr": mv.stock_price_usd,
                "VAM": round(vam, 4),
                "SDI": round(sdi_eff, 4),
                "SDI_linear": round(sdi_lin, 4),
                "prod_growth": round(prod_growth, 4),
                "mf_growth": round(mf_growth, 4),
                "sub_growth": round(sub_growth, 4),
                "regime": regime,
                "prediction": pred,
                "confidence": round(conf, 3),
                "fwd_return_12m": round(ret_12m, 4) if ret_12m is not None else None,
                "fwd_drawdown_24m": round(fwd.get("drawdown_24m") or 0.0, 4) if fwd.get("drawdown_24m") is not None else None,
                "has_crash_24m": crash_24m,
                "is_correct": is_correct
            }
            prediction_log.append(entry)

    # Export Indian predictions
    export_to_csv(prediction_log, "prediction_log_india.csv")

    danger_preds = [p for p in prediction_log if p["prediction"] == "DANGER" and p["has_crash_24m"] is not None]
    healthy_preds = [p for p in prediction_log if p["prediction"] == "HEALTHY" and p["fwd_return_12m"] is not None]

    tp_danger = sum(1 for p in danger_preds if p["is_correct"])
    fp_danger = len(danger_preds) - tp_danger
    precision_danger = (tp_danger / len(danger_preds)) if danger_preds else 0.0
    healthy_acc = (sum(1 for p in healthy_preds if p["is_correct"]) / len(healthy_preds)) if healthy_preds else 0.0

    scorecard = {
        "market": "NSE/BSE (India)",
        "total_evaluations": len(prediction_log),
        "danger_predictions": len(danger_preds),
        "danger_true_positives": tp_danger,
        "danger_false_positives": fp_danger,
        "danger_precision": round(precision_danger, 4),
        "healthy_predictions": len(healthy_preds),
        "healthy_accuracy": round(healthy_acc, 4)
    }

    out_json = os.path.join(OUTPUT_DIR, "validation_scorecard_india.json")
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(scorecard, f, indent=2)

    print("\n" + "=" * 80)
    print("INDIAN MARKET PREDICTABILITY SCORECARD:")
    print("=" * 80)
    print(f"Total Quarterly Evaluations: {len(prediction_log)}")
    print(f"Danger Predictions:          {len(danger_preds)}")
    print(f"Danger Precision:            {precision_danger * 100:.1f}%")
    print(f"Healthy Accuracy:            {healthy_acc * 100:.1f}%")
    print("=" * 80)
    
    return scorecard


if __name__ == "__main__":
    run_indian_validation_backtest()
