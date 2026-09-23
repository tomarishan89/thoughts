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

# S&P 500 55-Firm Expanded Universe (Option C)
from sp500_universe import SP500_55_UNIVERSE, GICS_SECTORS, get_universe

# Active Universe Selection: 'sp55' (default) or 'validation_8'
UNIVERSE_MODE = "sp55"
ACTIVE_UNIVERSE = SP500_55_UNIVERSE if UNIVERSE_MODE == "sp55" else UNIVERSE_VALIDATION

# Gold Benchmark Symbol
GOLD_SYMBOL = "GC=F"
SP500_SYMBOL = "^GSPC"
TREASURY_10Y_SYMBOL = "^TNX"

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
        "OperatingExpenses",
        "NoninterestExpense",
        "OperatingCostsAndExpenses",
        "OtherOperatingIncomeExpenseNet",
        "CostsAndExpenses",
        "LaborAndRelatedExpenses"
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
        "RegulatedAndUnregulatedOperatingRevenue",
        "ElectricUtilityRevenue",
        "InterestAndDividendIncomeOperating",
        "TotalRevenuesAndOtherIncome",
        "ElectricOperatingRevenue",
        "RegulatedOperatingRevenue"
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
    "short_term_debt": [
        "DebtCurrent",
        "ShortTermBorrowings",
        "CommercialPaper",
        "LongTermDebtCurrent"
    ],
    "shares_outstanding": [
        "CommonStockSharesOutstanding",
        "EntityCommonStockSharesOutstanding",
        "WeightedAverageNumberOfDilutedSharesOutstanding",
        "WeightedAverageNumberOfSharesOutstandingBasic",
        "CommonStockSharesIssued"
    ],

    # Working Capital & Continuum Plasticity (V-FIN-1.1, V-FIN-4, V-FIN-10)
    "inventory": [
        "InventoryNet",
        "InventoryGross",
        "Inventories",
        "InventoryNetOfAllowancesCustomerAdvancesAndProgressBillings",
        "InventoryFinishedGoods"
    ],
    "accounts_receivable": [
        "AccountsReceivableNetCurrent",
        "ReceivablesNetCurrent",
        "AccountsAndOtherReceivablesNetCurrent"
    ],
    "accounts_payable": [
        "AccountsPayableCurrent",
        "AccountsPayableAndAccruedLiabilitiesCurrent",
        "AccountsPayableOtherCurrent"
    ],
    "cost_of_goods_sold": [
        "CostOfGoodsAndServicesSold",
        "CostOfRevenue",
        "CostOfGoodsSold",
        "CostsAndExpenses",
        "OperatingCostsAndExpenses"
    ],
    "total_assets": [
        "Assets",
        "AssetsCurrent"
    ],
    "current_liabilities": [
        "LiabilitiesCurrent",
        "OtherLiabilitiesCurrent",
        "Liabilities"
    ],
    "ebit": [
        "OperatingIncomeLoss",
        "GrossProfit",
        "NetIncomeLoss"
    ],
    "interest_expense": [
        "InterestExpense",
        "InterestAndDebtExpense",
        "FinancingInterestExpense",
        "InterestExpenseDebt"
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
    "forward_horizons_quarters": [2, 4, 8],  # 6m, 12m, 24m
    "holdout_split_year": 2022,              # Boundary: Train <= 2021, Out-of-Sample >= 2022
    "in_sample_range": (2016, 2021),         # 6 years in-sample calibration
    "out_of_sample_range": (2022, 2026),     # 4.5 years out-of-sample holdout validation

    # Continuum Plasticity & Mechanical Parameters (Option B / V-FIN-1, 4, 10, 12)
    "continuum_plasticity": {
        "alpha_dp": 0.25,               # Drucker-Prager friction angle coefficient
        "alpha_0": 1.25,                # Base productivity coupling coefficient
        "gamma_sec": 1.0,               # Sector capital intensity scaling exponent
        "tau_bar_gestation": 2.5,       # Mean capital gestation delay (years = 10 quarters)
        "use_retarded_gestation": True, # Non-Markovian Gamma memory convolution
        "use_sector_coupling": True,    # Sector-adaptive alpha(rho_capex)
        "use_drucker_prager_gate": True # Balance-sheet plastic rupture gate
    }
}
