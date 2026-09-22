"""
config.py
---------
Configuration parameters, universe definitions, and SEC EDGAR XBRL tag mappings
for the Corporate Predictability & Transfer Operator Engine.
"""

import os

# Base paths
ENGINE_DIR = os.path.dirname(os.path.abspath(__file__))
CACHE_DIR = os.path.join(ENGINE_DIR, "cache")
SEC_CACHE_DIR = os.path.join(CACHE_DIR, "sec_facts")
PRICE_CACHE_DIR = os.path.join(CACHE_DIR, "market_prices")
OUTPUT_DIR = os.path.join(ENGINE_DIR, "output")
FIGURES_DIR = os.path.join(ENGINE_DIR, "figures")

# Ensure directories exist
for p in [CACHE_DIR, SEC_CACHE_DIR, PRICE_CACHE_DIR, OUTPUT_DIR, FIGURES_DIR]:
    os.makedirs(p, exist_ok=True)

# SEC EDGAR Request Headers (Fair Access compliant)
SEC_HEADERS = {
    "User-Agent": "VidyamanResearch admin@vidyaman.org"
}

# Initial Validation Set (8 Companies)
# Selected specifically to cover:
# - Tech Controls (AAPL, MSFT)
# - Known Regime 3 Collapses / Parasitic Decouplings (BA, GE, AIG)
# - Energy / Cyclical (XOM)
# - Financial Anchor (JPM)
# - Consumer Staples Anchor (WMT)
UNIVERSE_VALIDATION = {
    "AAPL": {
        "cik": 320193,
        "name": "Apple Inc.",
        "sector": "Technology",
        "expected_role": "Control: Main Sequence Virtuous Engine",
        "shares_tag": "CommonStockSharesOutstanding"
    },
    "MSFT": {
        "cik": 789019,
        "name": "Microsoft Corporation",
        "sector": "Technology",
        "expected_role": "Control: Cloud / Platform Engine",
        "shares_tag": "CommonStockSharesOutstanding"
    },
    "BA": {
        "cik": 12927,
        "name": "The Boeing Company",
        "sector": "Aerospace & Defense",
        "expected_role": "Regime 3 Validation: 2014-2019 Buybacks vs Engineering Attrition",
        "shares_tag": "CommonStockSharesOutstanding"
    },
    "GE": {
        "cik": 40545,
        "name": "General Electric Company",
        "sector": "Industrial Conglomerate",
        "expected_role": "Regime 3 Validation: 2012-2016 Financialization Decoupling",
        "shares_tag": "CommonStockSharesOutstanding"
    },
    "AIG": {
        "cik": 5272,
        "name": "American International Group",
        "sector": "Financial / Insurance",
        "expected_role": "Financial Collapse & Restructuring",
        "shares_tag": "CommonStockSharesOutstanding"
    },
    "XOM": {
        "cik": 34088,
        "name": "Exxon Mobil Corporation",
        "sector": "Energy",
        "expected_role": "Cyclical / Commodity Substrate Engine",
        "shares_tag": "CommonStockSharesOutstanding"
    },
    "JPM": {
        "cik": 19617,
        "name": "JPMorgan Chase & Co.",
        "sector": "Financial / Banking",
        "expected_role": "Fortress Balance Sheet Banking Engine",
        "shares_tag": "CommonStockSharesOutstanding"
    },
    "WMT": {
        "cik": 104169,
        "name": "Walmart Inc.",
        "sector": "Consumer Staples",
        "expected_role": "Defensive Substrate Anchor",
        "shares_tag": "CommonStockSharesOutstanding"
    }
}

# Gold Benchmark Symbol
GOLD_SYMBOL = "GC=F"
SP500_SYMBOL = "^GSPC"

# XBRL Tag Search Hierarchies (in priority order)
XBRL_TAG_MAP = {
    # Legal Mass (M_L): Intangible Assets + Goodwill
    "intangibles": [
        "IntangibleAssetsNetExcludingGoodwill",
        "FiniteLivedIntangibleAssetsNet",
        "GoodwillAndIntangibleAssetsNet",
        "OtherIntangibleAssetsNet"
    ],
    "goodwill": [
        "Goodwill"
    ],
    
    # Human Mass (M_H): R&D Expense + SG&A Expense
    "rd_expense": [
        "ResearchAndDevelopmentExpense",
        "ResearchAndDevelopmentExpenseExcludingAcquiredInProcessCost"
    ],
    "sga_expense": [
        "SellingGeneralAndAdministrativeExpense",
        "GeneralAndAdministrativeExpense",
        "OperatingExpenses"
    ],
    
    # Physical Mass (M_P): Net Property, Plant & Equipment
    "ppe_net": [
        "PropertyPlantAndEquipmentNet",
        "PropertyPlantAndEquipmentNetOfAccumulatedDepreciation"
    ],
    
    # Market Mass (M_M): Revenue and Gross Margin
    "revenue": [
        "Revenues",
        "RevenueFromContractWithCustomerExcludingAssessedTax",
        "SalesRevenueNet",
        "InterestAndDividendIncomeOperating",
        "TotalRevenuesAndOtherIncome"
    ],
    "gross_profit": [
        "GrossProfit",
        "OperatingIncomeLoss",
        "NetIncomeLoss"
    ],
    
    # Financial Mass (M_F): Cash, Debt, Market Cap
    "cash_equivalents": [
        "CashAndCashEquivalentsAtCarryingValue",
        "CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalents"
    ],
    "short_term_investments": [
        "AvailableForSaleSecuritiesCurrent",
        "MarketableSecuritiesCurrent",
        "ShortTermInvestments"
    ],
    "total_debt": [
        "LongTermDebtNoncurrent",
        "LongTermDebt",
        "DebtCurrent",
        "ShortTermBorrowings"
    ],
    "shares_outstanding": [
        "CommonStockSharesOutstanding",
        "EntityCommonStockSharesOutstanding"
    ]
}

# Backtesting Parameters
BACKTEST_CONFIG = {
    "start_year": 2016,
    "end_year": 2026,
    "sdi_window_quarters": 4,         # Rolling 4 quarters (1 year) for rate of change
    "drawdown_threshold": -0.20,       # -20% defines major structural drawdown
    "regime_thresholds": {
        "sdi_danger": 0.15,            # SDI > 0.15 -> Parasitic Warning
        "sdi_extreme": 0.35,           # SDI > 0.35 -> High Alert / Severe Decoupling
        "vam_distortion": 0.45,        # VAM > 0.45 indicates severe single-axis skew
    },
    "forward_horizons_quarters": [2, 4, 8]  # 6m, 12m, 24m
}
