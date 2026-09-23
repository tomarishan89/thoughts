"""
data_fetcher.py
---------------
Automated fetching and local caching of:
1. SEC EDGAR XBRL company facts (10+ year balance sheets & income statements)
2. Daily market price history from Yahoo Finance API
3. Daily Gold benchmark price (GC=F) & S&P 500 (^GSPC)

Features:
- Rate-limited SEC EDGAR fetching (compliant with 10 req/s limit)
- Robust exponential backoff and retry handling
- Disk caching for fast offline execution
- Universe-agnostic batch ingestion supporting both 55-firm S&P universe and legacy validation sets.
"""

import os
import json
import time
import datetime
from typing import Dict, Any, List, Optional
import requests

from config import (
    SEC_HEADERS, SEC_CACHE_DIR, PRICE_CACHE_DIR,
    UNIVERSE_VALIDATION, ACTIVE_UNIVERSE, GOLD_SYMBOL, SP500_SYMBOL, TREASURY_10Y_SYMBOL
)


def fetch_sec_facts(ticker: str, cik: int, force_refresh: bool = False, max_retries: int = 4) -> dict:
    """
    Fetch complete XBRL company facts from SEC EDGAR API with disk caching.
    Includes exponential backoff retry logic to handle rate-limiting or network glitches.
    """
    cache_path = os.path.join(SEC_CACHE_DIR, f"{ticker}_facts.json")
    if not force_refresh and os.path.exists(cache_path):
        with open(cache_path, "r", encoding="utf-8") as f:
            facts = json.load(f)
        sz_mb = os.path.getsize(cache_path) / (1024 * 1024)
        print(f"[CACHE] Loaded SEC facts for {ticker:6} from cache ({sz_mb:.2f} MB)")
        return facts

    cik_padded = str(cik).zfill(10)
    url = f"https://data.sec.gov/api/xbrl/companyfacts/CIK{cik_padded}.json"
    print(f"[SEC EDGAR] Fetching XBRL facts for {ticker:6} (CIK: {cik_padded})...")

    backoff = 1.0
    for attempt in range(1, max_retries + 1):
        # Respect SEC rate limit (max 10 req/sec; use 0.15s)
        time.sleep(0.15)
        try:
            response = requests.get(url, headers=SEC_HEADERS, timeout=30)
            if response.status_code == 200:
                facts = response.json()
                with open(cache_path, "w", encoding="utf-8") as f:
                    json.dump(facts, f)
                sz_mb = len(response.content) / (1024 * 1024)
                print(f"[SEC EDGAR] Cached facts for {ticker:6} ({sz_mb:.2f} MB) to {cache_path}")
                return facts
            elif response.status_code in [429, 500, 502, 503, 504]:
                print(f"[SEC EDGAR] HTTP {response.status_code} on attempt {attempt}/{max_retries} for {ticker}. Backing off {backoff:.1f}s...")
                time.sleep(backoff)
                backoff *= 2.0
            else:
                raise RuntimeError(
                    f"Failed to fetch SEC facts for {ticker} (CIK {cik_padded}): "
                    f"HTTP {response.status_code} - {response.text[:200]}"
                )
        except (requests.RequestException, TimeoutError) as e:
            print(f"[SEC EDGAR] Connection error on attempt {attempt}/{max_retries} for {ticker}: {e}. Retrying in {backoff:.1f}s...")
            time.sleep(backoff)
            backoff *= 2.0

    raise RuntimeError(f"Failed to fetch SEC facts for {ticker} after {max_retries} retries.")


def fetch_market_prices(symbol: str, force_refresh: bool = False, max_retries: int = 4) -> list:
    """
    Fetch 10-year daily adjusted close history from Yahoo Finance chart API with disk caching.
    """
    safe_symbol = symbol.replace("=", "_").replace("^", "_").replace("-", "_")
    cache_path = os.path.join(PRICE_CACHE_DIR, f"{safe_symbol}_prices.json")

    if not force_refresh and os.path.exists(cache_path):
        with open(cache_path, "r", encoding="utf-8") as f:
            clean_series = json.load(f)
        print(f"[CACHE] Loaded {len(clean_series)} daily price points for {symbol:6} from cache")
        return clean_series

    # Format for Yahoo Finance (e.g. BRK-B is BRK-B) with split events
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?interval=1d&range=10y&events=splits"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    print(f"[YAHOO] Fetching 10-year daily price history & splits for {symbol:6}...")

    backoff = 1.0
    for attempt in range(1, max_retries + 1):
        time.sleep(0.15)
        try:
            response = requests.get(url, headers=headers, timeout=30)
            if response.status_code == 200:
                res_data = response.json()
                chart = res_data.get("chart", {})
                result = chart.get("result")
                if not result:
                    raise RuntimeError(f"No chart result returned for {symbol}: {res_data}")

                res_obj = result[0]
                timestamps = res_obj.get("timestamp", [])
                quotes = res_obj.get("indicators", {}).get("quote", [{}])[0]
                adjclose = res_obj.get("indicators", {}).get("adjclose", [{}])[0].get("adjclose", [])

                closes = adjclose if adjclose else quotes.get("close", [])
                volumes = quotes.get("volume", [])

                clean_series = []
                for i, ts in enumerate(timestamps):
                    c = closes[i] if i < len(closes) else None
                    v = volumes[i] if i < len(volumes) else None
                    if c is not None and not (isinstance(c, float) and (c != c)):  # check for NaN
                        dt_str = datetime.datetime.fromtimestamp(ts, datetime.timezone.utc).strftime("%Y-%m-%d")
                        clean_series.append({
                            "date": dt_str,
                            "timestamp": ts,
                            "close": float(c),
                            "volume": int(v) if v is not None and v == v else 0
                        })

                with open(cache_path, "w", encoding="utf-8") as f:
                    json.dump(clean_series, f)

                # Extract and cache split events
                splits_dict = res_obj.get("events", {}).get("splits", {})
                splits_list = []
                for k, v in splits_dict.items():
                    s_dt = datetime.datetime.fromtimestamp(v["date"], datetime.timezone.utc).strftime("%Y-%m-%d")
                    num = float(v.get("numerator", 1.0))
                    den = float(v.get("denominator", 1.0))
                    ratio = num / den if den != 0 else 1.0
                    splits_list.append({"date": s_dt, "ratio": ratio})
                splits_list.sort(key=lambda x: x["date"])

                splits_path = os.path.join(PRICE_CACHE_DIR, f"{safe_symbol}_splits.json")
                with open(splits_path, "w", encoding="utf-8") as f:
                    json.dump(splits_list, f)

                print(f"[YAHOO] Cached {len(clean_series)} daily points & {len(splits_list)} splits for {symbol:6} to {cache_path}")
                return clean_series
            elif response.status_code in [429, 500, 502, 503]:
                print(f"[YAHOO] HTTP {response.status_code} on attempt {attempt}/{max_retries} for {symbol}. Backing off {backoff:.1f}s...")
                time.sleep(backoff)
                backoff *= 2.0
            else:
                raise RuntimeError(f"Failed to fetch market data for {symbol}: HTTP {response.status_code}")
        except (requests.RequestException, TimeoutError) as e:
            print(f"[YAHOO] Network error on attempt {attempt}/{max_retries} for {symbol}: {e}. Retrying in {backoff:.1f}s...")
            time.sleep(backoff)
            backoff *= 2.0

    raise RuntimeError(f"Failed to fetch market data for {symbol} after {max_retries} retries.")


def fetch_market_splits(symbol: str) -> List[Dict[str, Any]]:
    """Fetch cached split events for a symbol or empty list if none."""
    safe_symbol = symbol.replace("=", "_").replace("^", "_").replace("-", "_")
    splits_path = os.path.join(PRICE_CACHE_DIR, f"{safe_symbol}_splits.json")
    if os.path.exists(splits_path):
        try:
            with open(splits_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return []


def fetch_all_universe_data(universe: Optional[Dict[str, Dict[str, Any]]] = None, force_refresh: bool = False):
    """
    Fetch complete SEC facts and price data for any given universe + benchmarks.
    Defaults to ACTIVE_UNIVERSE (Option C 55-firm universe).
    """
    if universe is None:
        universe = ACTIVE_UNIVERSE

    total_companies = len(universe)
    print("=" * 80)
    print(f"PREDICTABILITY ENGINE: DATA INGESTION PIPELINE ({total_companies} COMPANIES)")
    print("=" * 80)

    # 1. Benchmarks
    print("\n--- INGESTING BENCHMARK DATA ---")
    fetch_market_prices(GOLD_SYMBOL, force_refresh=force_refresh)
    fetch_market_prices(SP500_SYMBOL, force_refresh=force_refresh)
    fetch_market_prices(TREASURY_10Y_SYMBOL, force_refresh=force_refresh)

    # 2. Universe Companies
    print(f"\n--- INGESTING UNIVERSE DATA ({total_companies} CONSTITUENTS) ---")
    start_time = time.time()
    for idx, (ticker, info) in enumerate(universe.items(), start=1):
        sec_name = info.get("sector", "N/A")
        comp_name = info.get("name", ticker)
        print(f"\n[{idx:2d}/{total_companies:2d}] Ingesting {ticker:6} | {comp_name} ({sec_name})...")
        fetch_sec_facts(ticker, info["cik"], force_refresh=force_refresh)
        fetch_market_prices(ticker, force_refresh=force_refresh)

    elapsed = time.time() - start_time
    print("\n" + "=" * 80)
    print(f"DATA INGESTION COMPLETE: All {total_companies} universe files cached locally in {elapsed:.1f}s.")
    print("=" * 80)


def fetch_all_validation_data(force_refresh: bool = False):
    """Backwards-compatible entry point for the legacy 8-firm validation set."""
    fetch_all_universe_data(universe=UNIVERSE_VALIDATION, force_refresh=force_refresh)


if __name__ == "__main__":
    import sys
    # If '--legacy' or '--8' passed in args, fetch legacy 8 firms
    if any(arg in sys.argv for arg in ["--legacy", "--8"]):
        fetch_all_validation_data()
    else:
        fetch_all_universe_data()
