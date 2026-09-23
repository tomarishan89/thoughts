"""
sp500_universe.py
-----------------
Expanded S&P 500 Constituent Universe for the Predictability Engine (Option C).
Contains 55 companies: exactly 5 representative firms across all 11 GICS sectors.

Includes:
- Official SEC CIK numbers
- GICS Sector classifications
- Expected roles (Controls, Cyclicals, Capital-Intensive, Financials, Real Estate)
- Sector groupings for stratified backtesting and scorecard generation.
"""

from typing import Dict, Any, List

# 11 Official GICS Sectors
GICS_SECTORS: List[str] = [
    "Information Technology",
    "Health Care",
    "Financials",
    "Consumer Discretionary",
    "Communication Services",
    "Industrials",
    "Consumer Staples",
    "Energy",
    "Utilities",
    "Real Estate",
    "Materials"
]

# 55-Firm Universe Definition: 5 per GICS Sector
SP500_55_UNIVERSE: Dict[str, Dict[str, Any]] = {
    # --------------------------------------------------------------------------
    # 1. Information Technology
    # --------------------------------------------------------------------------
    "AAPL": {
        "cik": 320193,
        "name": "Apple Inc.",
        "sector": "Information Technology",
        "expected_role": "Control: Main Sequence Virtuous Engine",
        "shares_tag": "CommonStockSharesOutstanding"
    },
    "MSFT": {
        "cik": 789019,
        "name": "Microsoft Corporation",
        "sector": "Information Technology",
        "expected_role": "Control: Enterprise Cloud & Software Platform",
        "shares_tag": "CommonStockSharesOutstanding"
    },
    "NVDA": {
        "cik": 1045810,
        "name": "NVIDIA Corporation",
        "sector": "Information Technology",
        "expected_role": "High-Growth Hardware / Accelerated Computing",
        "shares_tag": "CommonStockSharesOutstanding"
    },
    "AVGO": {
        "cik": 1730168,
        "name": "Broadcom Inc.",
        "sector": "Information Technology",
        "expected_role": "Acquisitive Semiconductor & Infrastructure Software",
        "shares_tag": "CommonStockSharesOutstanding"
    },
    "CRM": {
        "cik": 1108524,
        "name": "Salesforce, Inc.",
        "sector": "Information Technology",
        "expected_role": "Enterprise SaaS Platform",
        "shares_tag": "CommonStockSharesOutstanding"
    },

    # --------------------------------------------------------------------------
    # 2. Health Care
    # --------------------------------------------------------------------------
    "JNJ": {
        "cik": 200406,
        "name": "Johnson & Johnson",
        "sector": "Health Care",
        "expected_role": "Diversified Pharma & MedTech Defensive Anchor",
        "shares_tag": "CommonStockSharesOutstanding"
    },
    "UNH": {
        "cik": 731766,
        "name": "UnitedHealth Group Inc.",
        "sector": "Health Care",
        "expected_role": "Managed Care & Health Services Provider",
        "shares_tag": "CommonStockSharesOutstanding"
    },
    "PFE": {
        "cik": 78003,
        "name": "Pfizer Inc.",
        "sector": "Health Care",
        "expected_role": "Biopharma / Post-Pandemic Pipeline Realignment",
        "shares_tag": "CommonStockSharesOutstanding"
    },
    "ABT": {
        "cik": 1800,
        "name": "Abbott Laboratories",
        "sector": "Health Care",
        "expected_role": "Medical Devices & Diagnostics",
        "shares_tag": "CommonStockSharesOutstanding"
    },
    "TMO": {
        "cik": 97745,
        "name": "Thermo Fisher Scientific Inc.",
        "sector": "Health Care",
        "expected_role": "Life Sciences Tools & Lab Instruments",
        "shares_tag": "CommonStockSharesOutstanding"
    },

    # --------------------------------------------------------------------------
    # 3. Financials
    # --------------------------------------------------------------------------
    "JPM": {
        "cik": 19617,
        "name": "JPMorgan Chase & Co.",
        "sector": "Financials",
        "expected_role": "Fortress Balance Sheet Banking Anchor",
        "shares_tag": "CommonStockSharesOutstanding"
    },
    "BAC": {
        "cik": 70858,
        "name": "Bank of America Corp.",
        "sector": "Financials",
        "expected_role": "Commercial & Retail Banking Anchor",
        "shares_tag": "CommonStockSharesOutstanding"
    },
    "GS": {
        "cik": 886982,
        "name": "Goldman Sachs Group Inc.",
        "sector": "Financials",
        "expected_role": "Investment Banking & Capital Markets",
        "shares_tag": "CommonStockSharesOutstanding"
    },
    "BRK-B": {
        "cik": 1067983,
        "name": "Berkshire Hathaway Inc.",
        "sector": "Financials",
        "expected_role": "Diversified Insurance & Operating Conglomerate",
        "shares_tag": "CommonStockSharesOutstanding"
    },
    "AIG": {
        "cik": 5272,
        "name": "American International Group, Inc.",
        "sector": "Financials",
        "expected_role": "Global Insurance & Legacy Restructuring",
        "shares_tag": "CommonStockSharesOutstanding"
    },

    # --------------------------------------------------------------------------
    # 4. Consumer Discretionary
    # --------------------------------------------------------------------------
    "AMZN": {
        "cik": 1018724,
        "name": "Amazon.com, Inc.",
        "sector": "Consumer Discretionary",
        "expected_role": "E-Commerce & Cloud Infrastructure Platform",
        "shares_tag": "CommonStockSharesOutstanding"
    },
    "TSLA": {
        "cik": 1318605,
        "name": "Tesla, Inc.",
        "sector": "Consumer Discretionary",
        "expected_role": "High-Beta EV & Clean Energy / Volatility Stress Test",
        "shares_tag": "CommonStockSharesOutstanding"
    },
    "HD": {
        "cik": 354950,
        "name": "The Home Depot, Inc.",
        "sector": "Consumer Discretionary",
        "expected_role": "Housing & Home Improvement Retail Anchor",
        "shares_tag": "CommonStockSharesOutstanding"
    },
    "NKE": {
        "cik": 320187,
        "name": "NIKE, Inc.",
        "sector": "Consumer Discretionary",
        "expected_role": "Consumer Apparel & Direct-to-Consumer Transition",
        "shares_tag": "CommonStockSharesOutstanding"
    },
    "BA": {
        "cik": 12927,
        "name": "The Boeing Company",
        "sector": "Consumer Discretionary",
        "expected_role": "Regime 3 Validation: 2014-2019 Buybacks vs Engineering Attrition",
        "shares_tag": "CommonStockSharesOutstanding"
    },

    # --------------------------------------------------------------------------
    # 5. Communication Services
    # --------------------------------------------------------------------------
    "GOOGL": {
        "cik": 1652044,
        "name": "Alphabet Inc.",
        "sector": "Communication Services",
        "expected_role": "Digital Advertising & Search / Platform Anchor",
        "shares_tag": "CommonStockSharesOutstanding"
    },
    "META": {
        "cik": 1326801,
        "name": "Meta Platforms, Inc.",
        "sector": "Communication Services",
        "expected_role": "Social Media Ecosystem & Reality Labs Pivot",
        "shares_tag": "CommonStockSharesOutstanding"
    },
    "DIS": {
        "cik": 1744489,
        "name": "The Walt Disney Company",
        "sector": "Communication Services",
        "expected_role": "Media, Entertainment & Theme Parks / Streaming Transition",
        "shares_tag": "CommonStockSharesOutstanding"
    },
    "NFLX": {
        "cik": 1065280,
        "name": "Netflix, Inc.",
        "sector": "Communication Services",
        "expected_role": "Subscription Video Streaming Engine",
        "shares_tag": "CommonStockSharesOutstanding"
    },
    "T": {
        "cik": 732717,
        "name": "AT&T Inc.",
        "sector": "Communication Services",
        "expected_role": "Capital-Intensive Telecom / Debt & Dividend Restructuring",
        "shares_tag": "CommonStockSharesOutstanding"
    },

    # --------------------------------------------------------------------------
    # 6. Industrials
    # --------------------------------------------------------------------------
    "HON": {
        "cik": 773840,
        "name": "Honeywell International Inc.",
        "sector": "Industrials",
        "expected_role": "Diversified Multi-Industry Technology & Aerospace",
        "shares_tag": "CommonStockSharesOutstanding"
    },
    "CAT": {
        "cik": 18230,
        "name": "Caterpillar Inc.",
        "sector": "Industrials",
        "expected_role": "Heavy Construction & Mining Machinery Cyclical Anchor",
        "shares_tag": "CommonStockSharesOutstanding"
    },
    "GE": {
        "cik": 40545,
        "name": "General Electric Company",
        "sector": "Industrials",
        "expected_role": "Regime 3 Validation: Financialization Decoupling & Spinoffs",
        "shares_tag": "CommonStockSharesOutstanding"
    },
    "RTX": {
        "cik": 101829,
        "name": "RTX Corporation",
        "sector": "Industrials",
        "expected_role": "Defense Prime & Commercial Aerospace",
        "shares_tag": "CommonStockSharesOutstanding"
    },
    "UPS": {
        "cik": 1090727,
        "name": "United Parcel Service, Inc.",
        "sector": "Industrials",
        "expected_role": "Logistics & Global Freight Network Substrate",
        "shares_tag": "CommonStockSharesOutstanding"
    },

    # --------------------------------------------------------------------------
    # 7. Consumer Staples
    # --------------------------------------------------------------------------
    "WMT": {
        "cik": 104169,
        "name": "Walmart Inc.",
        "sector": "Consumer Staples",
        "expected_role": "Defensive Retail & Physical Supply-Chain Anchor",
        "shares_tag": "CommonStockSharesOutstanding"
    },
    "PG": {
        "cik": 80424,
        "name": "The Procter & Gamble Company",
        "sector": "Consumer Staples",
        "expected_role": "Branded Consumer Goods Compounding Anchor",
        "shares_tag": "CommonStockSharesOutstanding"
    },
    "KO": {
        "cik": 21344,
        "name": "The Coca-Cola Company",
        "sector": "Consumer Staples",
        "expected_role": "Global Beverage Distribution Franchise",
        "shares_tag": "CommonStockSharesOutstanding"
    },
    "PEP": {
        "cik": 77476,
        "name": "PepsiCo, Inc.",
        "sector": "Consumer Staples",
        "expected_role": "Beverages & Convenience Foods Compounding Anchor",
        "shares_tag": "CommonStockSharesOutstanding"
    },
    "COST": {
        "cik": 909832,
        "name": "Costco Wholesale Corporation",
        "sector": "Consumer Staples",
        "expected_role": "Membership Warehouse & High-Turnover Physical Retail",
        "shares_tag": "CommonStockSharesOutstanding"
    },

    # --------------------------------------------------------------------------
    # 8. Energy
    # --------------------------------------------------------------------------
    "XOM": {
        "cik": 34088,
        "name": "Exxon Mobil Corporation",
        "sector": "Energy",
        "expected_role": "Integrated Upstream/Downstream Energy Major",
        "shares_tag": "CommonStockSharesOutstanding"
    },
    "CVX": {
        "cik": 93410,
        "name": "Chevron Corporation",
        "sector": "Energy",
        "expected_role": "Integrated Global Energy Major",
        "shares_tag": "CommonStockSharesOutstanding"
    },
    "COP": {
        "cik": 1163165,
        "name": "ConocoPhillips",
        "sector": "Energy",
        "expected_role": "Pure-Play E&P Commodity Exposure",
        "shares_tag": "CommonStockSharesOutstanding"
    },
    "SLB": {
        "cik": 87347,
        "name": "SLB (Schlumberger Limited)",
        "sector": "Energy",
        "expected_role": "Oilfield Services & Technology Cyclical",
        "shares_tag": "CommonStockSharesOutstanding"
    },
    "EOG": {
        "cik": 821189,
        "name": "EOG Resources, Inc.",
        "sector": "Energy",
        "expected_role": "Unconventional Shale E&P",
        "shares_tag": "CommonStockSharesOutstanding"
    },

    # --------------------------------------------------------------------------
    # 9. Utilities
    # --------------------------------------------------------------------------
    "NEE": {
        "cik": 753308,
        "name": "NextEra Energy, Inc.",
        "sector": "Utilities",
        "expected_role": "Regulated Utility & Clean Energy Transition",
        "shares_tag": "CommonStockSharesOutstanding"
    },
    "DUK": {
        "cik": 1326160,
        "name": "Duke Energy Corporation",
        "sector": "Utilities",
        "expected_role": "Regulated Electric & Gas Infrastructure",
        "shares_tag": "CommonStockSharesOutstanding"
    },
    "SO": {
        "cik": 92122,
        "name": "The Southern Company",
        "sector": "Utilities",
        "expected_role": "Regulated Nuclear & Thermal Electric Utility",
        "shares_tag": "CommonStockSharesOutstanding"
    },
    "D": {
        "cik": 715957,
        "name": "Dominion Energy, Inc.",
        "sector": "Utilities",
        "expected_role": "Regulated Electric Utility & Offshore Wind",
        "shares_tag": "CommonStockSharesOutstanding"
    },
    "AEP": {
        "cik": 4904,
        "name": "American Electric Power Company, Inc.",
        "sector": "Utilities",
        "expected_role": "Electric Transmission & Distribution Substrate",
        "shares_tag": "CommonStockSharesOutstanding"
    },

    # --------------------------------------------------------------------------
    # 10. Real Estate
    # --------------------------------------------------------------------------
    "AMT": {
        "cik": 1053507,
        "name": "American Tower Corporation",
        "sector": "Real Estate",
        "expected_role": "Telecom Infrastructure REIT",
        "shares_tag": "CommonStockSharesOutstanding"
    },
    "PLD": {
        "cik": 1045609,
        "name": "Prologis, Inc.",
        "sector": "Real Estate",
        "expected_role": "Industrial Logistics & Warehouse REIT",
        "shares_tag": "CommonStockSharesOutstanding"
    },
    "CCI": {
        "cik": 1051470,
        "name": "Crown Castle Inc.",
        "sector": "Real Estate",
        "expected_role": "Cell Tower & Small Cell REIT",
        "shares_tag": "CommonStockSharesOutstanding"
    },
    "EQIX": {
        "cik": 1101239,
        "name": "Equinix, Inc.",
        "sector": "Real Estate",
        "expected_role": "Data Center & Interconnection REIT",
        "shares_tag": "CommonStockSharesOutstanding"
    },
    "SPG": {
        "cik": 1063761,
        "name": "Simon Property Group, Inc.",
        "sector": "Real Estate",
        "expected_role": "Regional Retail Mall & Premium Outlet REIT",
        "shares_tag": "CommonStockSharesOutstanding"
    },

    # --------------------------------------------------------------------------
    # 11. Materials
    # --------------------------------------------------------------------------
    "LIN": {
        "cik": 1707925,
        "name": "Linde plc",
        "sector": "Materials",
        "expected_role": "Industrial Gases Compounding Moat",
        "shares_tag": "CommonStockSharesOutstanding"
    },
    "APD": {
        "cik": 2969,
        "name": "Air Products and Chemicals, Inc.",
        "sector": "Materials",
        "expected_role": "Industrial Gases & Hydrogen Infrastructure",
        "shares_tag": "CommonStockSharesOutstanding"
    },
    "SHW": {
        "cik": 89800,
        "name": "The Sherwin-Williams Company",
        "sector": "Materials",
        "expected_role": "Paints & Coatings Manufacturing & Distribution",
        "shares_tag": "CommonStockSharesOutstanding"
    },
    "ECL": {
        "cik": 31462,
        "name": "Ecolab Inc.",
        "sector": "Materials",
        "expected_role": "Water, Hygiene & Infection Prevention Solutions",
        "shares_tag": "CommonStockSharesOutstanding"
    },
    "NEM": {
        "cik": 1164727,
        "name": "Newmont Corporation",
        "sector": "Materials",
        "expected_role": "Gold Mining Major / Direct Commodity Anchor",
        "shares_tag": "CommonStockSharesOutstanding"
    }
}

# Sector to Tickers Lookup
SECTOR_TICKERS: Dict[str, List[str]] = {}
for _ticker, _info in SP500_55_UNIVERSE.items():
    _sec = _info["sector"]
    SECTOR_TICKERS.setdefault(_sec, []).append(_ticker)

# Helper function
def get_universe(mode: str = "sp55") -> Dict[str, Dict[str, Any]]:
    """Return dictionary of universe constituents based on mode."""
    if mode == "sp55":
        return SP500_55_UNIVERSE
    elif mode == "validation_8":
        from config import UNIVERSE_VALIDATION
        return UNIVERSE_VALIDATION
    else:
        raise ValueError(f"Unknown universe mode: {mode}. Expected 'sp55' or 'validation_8'.")
