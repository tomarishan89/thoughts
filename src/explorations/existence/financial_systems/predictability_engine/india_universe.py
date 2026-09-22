"""
india_universe.py
-----------------
Universe definitions and corporate profiles for the Indian equity market (NSE/BSE).
Defines:
  1. 10-Company Initial Validation Universe (IT, Banking, Industrials, Auto, Pharma, FMCG)
     Includes deliberate Regime 3 entity: YESBANK.NS (2018-2020 NPA concealment & collapse)
  2. Full NIFTY 50 benchmark universe
"""

# Benchmark symbols
NIFTY_50_SYMBOL = "^NSEI"
GOLD_INR_SYMBOL = "GOLDBEES.NS"   # Nippon India ETF Gold BeES (Liquid Indian Gold proxy)
USDINR_SYMBOL = "INR=X"

# Initial 10-Company Validation Set
INDIA_VALIDATION_UNIVERSE = {
    "TCS.NS": {
        "name": "Tata Consultancy Services",
        "sector": "Information Technology",
        "expected_role": "Control: Virtuous Autocatalytic Software/Human Substrate",
    },
    "INFY.NS": {
        "name": "Infosys Limited",
        "sector": "Information Technology",
        "expected_role": "Control: Platform Engine",
    },
    "RELIANCE.NS": {
        "name": "Reliance Industries",
        "sector": "Conglomerate (Oil / Telecom / Retail)",
        "expected_role": "High Capex Physical Substrate Expansion",
    },
    "HDFCBANK.NS": {
        "name": "HDFC Bank",
        "sector": "Financial / Banking",
        "expected_role": "Fortress Balance Sheet Banking Engine",
    },
    "YESBANK.NS": {
        "name": "Yes Bank Limited",
        "sector": "Financial / Banking",
        "expected_role": "Regime 3 Validation: 2018-2020 Hidden NPA Decoupling & Crash",
    },
    "LT.NS": {
        "name": "Larsen & Toubro",
        "sector": "Engineering & Construction",
        "expected_role": "Physical Infrastructure Substrate Anchor",
    },
    "SUNPHARMA.NS": {
        "name": "Sun Pharmaceutical Industries",
        "sector": "Healthcare / Pharmaceuticals",
        "expected_role": "High Margin R&D / IP Substrate Engine",
    },
    "ITC.NS": {
        "name": "ITC Limited",
        "sector": "Consumer Goods / Tobacco",
        "expected_role": "High-ROIC Defensive Cash Cow Substrate",
    },
    "TATAMOTORS.NS": {
        "name": "Tata Motors",
        "sector": "Automotive",
        "expected_role": "Cyclical / Turnaround Substrate Engine",
    },
    "ADANIENT.NS": {
        "name": "Adani Enterprises",
        "sector": "Infrastructure Conglomerate",
        "expected_role": "High-Leverage Capital Expenditure Engine",
    }
}

# Full NIFTY 50 Constituents (Sector Breakdown)
NIFTY_50_UNIVERSE = [
    # Information Technology
    "TCS.NS", "INFY.NS", "HCLTECH.NS", "WIPRO.NS", "TECHM.NS",
    # Financial Services / Banks
    "HDFCBANK.NS", "ICICIBANK.NS", "SBIN.NS", "KOTAKBANK.NS", "AXISBANK.NS", "BAJFINANCE.NS", "BAJAJFINSV.NS",
    # Oil, Gas & Consumable Fuels
    "RELIANCE.NS", "ONGC.NS", "BPCL.NS", "COALINDIA.NS",
    # Fast Moving Consumer Goods
    "HINDUNILVR.NS", "ITC.NS", "NESTLEIND.NS", "BRITANNIA.NS", "TATACONSUM.NS",
    # Automobile
    "MARUTI.NS", "M&M.NS", "TATAMOTORS.NS", "BAJAJ-AUTO.NS", "EICHERMOT.NS", "HEROMOTOCO.NS",
    # Construction & Metals
    "LT.NS", "ULTRACEMCO.NS", "GRASIM.NS", "TATASTEEL.NS", "JSWSTEEL.NS", "HINDALCO.NS",
    # Healthcare
    "SUNPHARMA.NS", "DRREDDY.NS", "CIPLA.NS", "APOLLOHOSP.NS",
    # Power & Telecom
    "NTPC.NS", "POWERGRID.NS", "BHARTIARTL.NS", "ADANIPORTS.NS", "ADANIENT.NS",
    # Consumer Discretionary & Retail
    "TITAN.NS", "TRENT.NS", "BEL.NS", "SHRIRAMFIN.NS"
]
