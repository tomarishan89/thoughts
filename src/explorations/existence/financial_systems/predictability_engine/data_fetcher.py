"""
data_fetcher.py
---------------
Automated fetching and local caching of:
1. SEC EDGAR XBRL company facts (10+ year balance sheets & income statements)
2. Daily market price history from Yahoo Finance API
3. Daily Gold benchmark price (GC=F)
"""

import os
import json
import time
import datetime
import requests
from config import (
    SEC_HEADERS, SEC_CACHE_DIR, PRICE_CACHE_DIR,
    UNIVERSE_VALIDATION, GOLD_SYMBOL, SP500_SYMBOL
)

def fetch_sec_facts(ticker: str, cik: int, force_refresh: bool = False) -> dict:
    """Fetch complete XBRL company facts from SEC EDGAR API with disk caching."""
    cache_path = os.path.join(SEC_CACHE_DIR, f"{ticker}_facts.json")
    if not force_refresh and os.path.exists(cache_path):
        print(f"[CACHE] Loaded SEC facts for {ticker} from {cache_path}")
        with open(cache_path, "r", encoding="utf-8") as f:
            return json.load(f)

    cik_padded = str(cik).zfill(10)
    url = f"https://data.sec.gov/api/xbrl/companyfacts/CIK{cik_padded}.json"
    print(f"[SEC EDGAR] Fetching XBRL facts for {ticker} (CIK: {cik_padded})...")
    
    # Respect SEC rate limit (max 10 requests/sec)
    time.sleep(0.2)
    response = requests.get(url, headers=SEC_HEADERS, timeout=30)
    
    if response.status_code != 200:
        raise RuntimeError(
            f"Failed to fetch SEC facts for {ticker} (CIK {cik_padded}): "
            f"HTTP {response.status_code} - {response.text[:200]}"
        )
        
    facts = response.json()
    with open(cache_path, "w", encoding="utf-8") as f:
        json.dump(facts, f)
    print(f"[SEC EDGAR] Cached facts for {ticker} to {cache_path}")
    return facts


def fetch_market_prices(symbol: str, force_refresh: bool = False) -> list:
    """Fetch 10-year daily adjusted close history from Yahoo Finance chart API."""
    safe_symbol = symbol.replace("=", "_").replace("^", "_")
    cache_path = os.path.join(PRICE_CACHE_DIR, f"{safe_symbol}_prices.json")
    
    if not force_refresh and os.path.exists(cache_path):
        print(f"[CACHE] Loaded price data for {symbol} from {cache_path}")
        with open(cache_path, "r", encoding="utf-8") as f:
            return json.load(f)

    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?interval=1d&range=10y"
    headers = {"User-Agent": "Mozilla/5.0"}
    print(f"[YAHOO] Fetching 10-year daily price history for {symbol}...")
    
    response = requests.get(url, headers=headers, timeout=30)
    if response.status_code != 200:
        raise RuntimeError(f"Failed to fetch market data for {symbol}: HTTP {response.status_code}")
        
    result = response.json()["chart"]["result"][0]
    timestamps = result.get("timestamp", [])
    quotes = result.get("indicators", {}).get("quote", [{}])[0]
    adjclose = result.get("indicators", {}).get("adjclose", [{}])[0].get("adjclose", [])
    
    closes = adjclose if adjclose else quotes.get("close", [])
    volumes = quotes.get("volume", [])
    
    clean_series = []
    for i, ts in enumerate(timestamps):
        c = closes[i] if i < len(closes) else None
        v = volumes[i] if i < len(volumes) else None
        if c is not None and not (isinstance(c, float) and (c != c)): # check for NaN
            dt_str = datetime.datetime.fromtimestamp(ts, datetime.timezone.utc).strftime("%Y-%m-%d")
            clean_series.append({
                "date": dt_str,
                "timestamp": ts,
                "close": float(c),
                "volume": int(v) if v is not None and v == v else 0
            })
            
    with open(cache_path, "w", encoding="utf-8") as f:
        json.dump(clean_series, f)
    print(f"[YAHOO] Cached {len(clean_series)} daily points for {symbol} to {cache_path}")
    return clean_series


def fetch_all_validation_data(force_refresh: bool = False):
    """Fetch complete SEC facts and price data for validation universe + benchmarks."""
    print("=" * 70)
    print("PREDICTABILITY ENGINE: DATA INGESTION PIPELINE")
    print("=" * 70)
    
    # 1. Benchmarks
    print("\n--- INGESTING BENCHMARK DATA ---")
    fetch_market_prices(GOLD_SYMBOL, force_refresh=force_refresh)
    fetch_market_prices(SP500_SYMBOL, force_refresh=force_refresh)
    
    # 2. Universe Companies
    print("\n--- INGESTING VALIDATION UNIVERSE DATA ---")
    for ticker, info in UNIVERSE_VALIDATION.items():
        print(f"\nProcessing {ticker} ({info['name']})...")
        fetch_sec_facts(ticker, info["cik"], force_refresh=force_refresh)
        fetch_market_prices(ticker, force_refresh=force_refresh)
        
    print("\n" + "=" * 70)
    print("DATA INGESTION COMPLETE: All universe files cached locally.")
    print("=" * 70)

if __name__ == "__main__":
    fetch_all_validation_data()
