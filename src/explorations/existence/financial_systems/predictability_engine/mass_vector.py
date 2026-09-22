"""
mass_vector.py
--------------
Mathematical formulation and extraction of the 5-component Corporate Mass Vector:
  M_C = (M_L, M_H, M_P, M_M, M_F)^T
and associated diagnostics:
  - Vector Anisotropy Metric (VAM): Delta_M in [0, 0.8]
  - Shadow Divergence Indicator (SDI): Sigma_shadow (rolling rate of decoupling)
  - Regime Classification (Regime 1 Virtuous, Regime 2 Subcritical, Regime 3 Parasitic)

Supports parallel evaluation in:
  1. USD-Nominal coordinates
  2. Gold-Normalized coordinates (M_alpha / P_Au)
"""

import math
import datetime
from dataclasses import dataclass
from typing import List, Dict, Optional, Tuple
import numpy as np

import sys
import os

# Ensure local package directory is on sys.path
_current_dir = os.path.dirname(os.path.abspath(__file__))
if _current_dir not in sys.path:
    sys.path.insert(0, _current_dir)

from config import XBRL_TAG_MAP, BACKTEST_CONFIG

@dataclass
class MassVector:
    """Represents a corporate mass vector at a specific quarter."""
    date: str                  # ISO date YYYY-MM-DD
    quarter: str               # YYYY-Q#
    ticker: str
    M_L: float                 # Legal Mass (Goodwill + Intangibles) [$]
    M_H: float                 # Human Mass (Annualized R&D + SG&A) [$]
    M_P: float                 # Physical Mass (Net PP&E) [$]
    M_M: float                 # Market Mass (TTM Revenue x Margin) [$]
    M_F: float                 # Financial Mass (Market Capitalization) [$]
    gold_price_usd: float      # Contemporaneous Gold Price [$/oz]
    stock_price_usd: float     # Stock Closing Price [$]
    shares_outstanding: float  # Diluted shares count

    def as_array_usd(self) -> np.ndarray:
        """Return 5-vector in USD nominal coordinates."""
        return np.array([self.M_L, self.M_H, self.M_P, self.M_M, self.M_F], dtype=float)

    def as_array_gold(self) -> np.ndarray:
        """Return 5-vector denominated in Gold Structural Ounces."""
        p_au = max(1.0, self.gold_price_usd)
        return self.as_array_usd() / p_au

    def substrate_usd(self) -> float:
        """Mean non-financial structural substrate: (M_L + M_H + M_P + M_M) / 4 in USD."""
        return (self.M_L + self.M_H + self.M_P + self.M_M) / 4.0

    def substrate_gold(self) -> float:
        """Mean non-financial structural substrate denominated in Gold Ounces."""
        p_au = max(1.0, self.gold_price_usd)
        return self.substrate_usd() / p_au

    def substrate_productivity(self) -> float:
        """
        Substrate productivity: eta_sub = M_M / (M_H + M_P).
        Market output (Revenue x Margin) generated per unit of
        combined human talent and physical equipment.
        Dimensionless ratio of output flow to structural capacity.
        Gauge-invariant under gold normalization:
          eta_sub^(Au) = (M_M/P_Au) / ((M_H+M_P)/P_Au) = eta_sub^(USD).
        """
        denom = max(1.0, self.M_H + self.M_P)
        return float(max(1.0, self.M_M) / denom)

    def total_mass_usd(self) -> float:
        """Euclidean norm of corporate mass vector in USD."""
        return float(np.linalg.norm(self.as_array_usd()))

    def total_mass_gold(self) -> float:
        """Euclidean norm of corporate mass vector in Gold Ounces."""
        return float(np.linalg.norm(self.as_array_gold()))


def compute_vam(M_array: np.ndarray) -> float:
    """
    Vector Anisotropy Metric (VAM):
      Delta_M = 1 - (sum_alpha M_alpha)^2 / (5 * sum_alpha M_alpha^2)
    Properties:
      Delta_M = 0 when all 5 components are identical (complete balance)
      Delta_M -> 0.8 when mass is concentrated entirely in a single axis
    """
    pos_M = np.maximum(M_array, 1.0) # floor to avoid division by zero
    sum_M = np.sum(pos_M)
    sum_sq = np.sum(pos_M ** 2)
    
    if sum_sq <= 0:
        return 0.0
        
    ratio = (sum_M ** 2) / (5.0 * sum_sq)
    vam = 1.0 - ratio
    # Clamp to theoretical bounds [0, 0.8]
    return float(np.clip(vam, 0.0, 0.8))


def compute_sdi(
    history: List[MassVector],
    current_idx: int,
    mode: str = "usd",
    window: int = 4,
    alpha: float = 0.0
) -> Tuple[float, float, float, float, float]:
    """
    Compute the Shadow Divergence Indicator (SDI) and Productivity-Corrected SDI (PC-SDI):
      Sigma_shadow = d/dtau ln(m_F) - d/dtau ln(M_sub)
      Sigma_shadow^* = Sigma_shadow - alpha * d/dtau ln(eta_sub)
    over a rolling window (default: 4 quarters = 1 year).

    Parameters:
      history: List of MassVector
      current_idx: index of current evaluation quarter
      mode: 'usd' or 'gold'
      window: rolling lookback quarters (default 4)
      alpha: productivity correction coupling coefficient (default 0.0 for linear SDI)

    Returns:
      (sdi_effective, sdi_linear, mf_annual_growth, sub_annual_growth, prod_annual_growth)
    """
    if current_idx < window:
        lookback = max(1, current_idx)
    else:
        lookback = window

    curr = history[current_idx]
    prev = history[current_idx - lookback]
    dt_years = lookback * 0.25 # quarters to years

    if mode == "usd":
        mf_curr = max(1.0, curr.M_F)
        mf_prev = max(1.0, prev.M_F)
        sub_curr = max(1.0, curr.substrate_usd())
        sub_prev = max(1.0, prev.substrate_usd())
    else: # gold mode
        mf_curr = max(1e-6, curr.M_F / max(1.0, curr.gold_price_usd))
        mf_prev = max(1e-6, prev.M_F / max(1.0, prev.gold_price_usd))
        sub_curr = max(1e-6, curr.substrate_gold())
        sub_prev = max(1e-6, prev.substrate_gold())

    d_ln_mf = (math.log(mf_curr) - math.log(mf_prev)) / dt_years
    d_ln_sub = (math.log(sub_curr) - math.log(sub_prev)) / dt_years

    # Substrate productivity growth rate: d/dtau ln(eta_sub)
    eta_curr = max(1e-6, curr.substrate_productivity())
    eta_prev = max(1e-6, prev.substrate_productivity())
    d_ln_eta = (math.log(eta_curr) - math.log(eta_prev)) / dt_years

    # Linear SDI
    sdi_linear = d_ln_mf - d_ln_sub
    
    # Productivity-Corrected SDI (PC-SDI)
    sdi_effective = sdi_linear - (alpha * d_ln_eta)

    return float(sdi_effective), float(sdi_linear), float(d_ln_mf), float(d_ln_sub), float(d_ln_eta)


def classify_regime(
    sdi: float,
    vam: float,
    sub_growth: float,
    mf_growth: float
) -> Tuple[str, str, float]:
    """
    Classifies corporate dynamical regime and generates forward prediction:
      - Regime 1: Virtuous Autocatalytic Cycle -> Prediction: HEALTHY
      - Regime 2: Subcritical Dissipative Regime -> Prediction: CAUTION / NEUTRAL
      - Regime 3: Parasitic Extraction Regime -> Prediction: DANGER

    Returns:
      (regime_name, prediction, confidence)
    """
    cfg = BACKTEST_CONFIG["regime_thresholds"]
    sdi_danger = cfg["sdi_danger"]
    sdi_extreme = cfg["sdi_extreme"]
    vam_distortion = cfg["vam_distortion"]

    # Regime 3: Parasitic Decoupling
    # Condition: Financial shadow growing significantly faster than substrate,
    # and substrate is either stagnating/eroding or severely outpaced
    if sdi >= sdi_danger and (sub_growth <= 0.05 or mf_growth > 2.0 * max(0.01, sub_growth)):
        confidence = min(0.95, 0.50 + (sdi / sdi_extreme) * 0.40)
        return "Regime 3 (Parasitic)", "DANGER", float(confidence)

    # Regime 1: Virtuous Cycle
    # Condition: Substrate is growing, SDI is low/balanced, VAM is healthy
    if sub_growth > 0.02 and sdi < sdi_danger and vam < vam_distortion:
        confidence = min(0.95, 0.60 + sub_growth * 0.50)
        return "Regime 1 (Virtuous)", "HEALTHY", float(confidence)

    # Regime 2: Subcritical / Stagnant
    # Substrate growth is flat or negative, but market is not hyping (SDI not spiking)
    confidence = 0.55
    return "Regime 2 (Subcritical)", "CAUTION", float(confidence)


# ==============================================================================
# SEC XBRL FACT PARSING ENGINE
# ==============================================================================

# Known stock splits table for 2016-2026
# (split_date, adjustment_factor_for_pre_split_filings)
SPLITS_TABLE = {
    "AAPL": [(datetime.date(2020, 8, 31), 4.0)],
    "WMT": [(datetime.date(2024, 2, 26), 3.0)],
    "GE": [(datetime.date(2021, 8, 2), 0.125)],
}

def _extract_best_fact(
    facts_gaap: dict,
    tag_candidates: List[str],
    target_date: str,
    is_instant: bool = True,
    max_day_diff: int = 60,
    ticker: str = ""
) -> Tuple[float, str]:
    """
    Extract best matching XBRL value for target calendar date from tag priority list.
    Returns (value, filed_date_str)
    """
    target_dt = datetime.datetime.strptime(target_date, "%Y-%m-%d").date()
    
    for tag in tag_candidates:
        if tag not in facts_gaap:
            continue
        units_dict = facts_gaap[tag].get("units", {})
        units = units_dict.get("USD", []) or units_dict.get("shares", [])
        if not units:
            continue

        best_val = None
        best_filed = ""
        min_diff = 9999

        for item in units:
            form = item.get("form", "")
            if not any(f in form for f in ["10-K", "10-Q"]):
                continue

            end_str = item.get("end")
            if not end_str:
                continue

            try:
                end_dt = datetime.datetime.strptime(end_str, "%Y-%m-%d").date()
            except ValueError:
                continue

            diff = abs((end_dt - target_dt).days)
            if diff > max_day_diff:
                continue

            if is_instant:
                if diff < min_diff:
                    min_diff = diff
                    best_val = float(item["val"])
                    best_filed = item.get("filed", "")
            else:
                start_str = item.get("start")
                if not start_str:
                    continue
                try:
                    start_dt = datetime.datetime.strptime(start_str, "%Y-%m-%d").date()
                except ValueError:
                    continue
                duration = (end_dt - start_dt).days
                if 60 <= duration <= 120:
                    if diff < min_diff:
                        min_diff = diff
                        best_val = float(item["val"])
                        best_filed = item.get("filed", "")

        if best_val is not None:
            return best_val, best_filed

    return 0.0, ""


def build_corporate_mass_history(
    ticker: str,
    sec_facts: dict,
    price_series: List[dict],
    gold_series: List[dict],
    start_year: int = 2016,
    end_year: int = 2026
) -> List[MassVector]:
    """
    Constructs quarterly MassVector sequence for a company from 2016 to 2026.
    """
    facts_gaap = sec_facts.get("facts", {}).get("us-gaap", {})
    
    # Map price series by date for fast lookup
    price_by_date = {p["date"]: p["close"] for p in price_series}
    gold_by_date = {g["date"]: g["close"] for g in gold_series}
    sorted_price_dates = sorted(price_by_date.keys())
    sorted_gold_dates = sorted(gold_by_date.keys())

    def get_nearest_price(target_date: str, price_map: dict, sorted_dates: list) -> float:
        if target_date in price_map:
            return price_map[target_date]
        # Find latest trading day <= target_date
        valid = [d for d in sorted_dates if d <= target_date]
        if valid:
            return price_map[valid[-1]]
        return price_map[sorted_dates[0]]

    # Generate standard calendar quarters: Q1 (03-31), Q2 (06-30), Q3 (09-30), Q4 (12-31)
    quarters = []
    for y in range(start_year, end_year + 1):
        for q, md in [(1, "03-31"), (2, "06-30"), (3, "09-30"), (4, "12-31")]:
            q_date = f"{y}-{md}"
            if y == end_year and q > 2: # up to Q2 2026
                continue
            quarters.append((f"{y}-Q{q}", q_date))

    history: List[MassVector] = []

    for q_label, q_date in quarters:
        # 1. Market Price & Gold Price
        stock_price = get_nearest_price(q_date, price_by_date, sorted_price_dates)
        gold_price = get_nearest_price(q_date, gold_by_date, sorted_gold_dates)

        # 2. Balance Sheet Items (Instantaneous)
        ppe_net, _ = _extract_best_fact(facts_gaap, XBRL_TAG_MAP["ppe_net"], q_date, is_instant=True)
        goodwill, _ = _extract_best_fact(facts_gaap, XBRL_TAG_MAP["goodwill"], q_date, is_instant=True)
        intangibles, _ = _extract_best_fact(facts_gaap, XBRL_TAG_MAP["intangibles"], q_date, is_instant=True)
        shares, shares_filed = _extract_best_fact(facts_gaap, XBRL_TAG_MAP["shares_outstanding"], q_date, is_instant=True)

        # 3. Income Statement Items (Flows)
        rd_qtr, _ = _extract_best_fact(facts_gaap, XBRL_TAG_MAP["rd_expense"], q_date, is_instant=False)
        sga_qtr, _ = _extract_best_fact(facts_gaap, XBRL_TAG_MAP["sga_expense"], q_date, is_instant=False)
        rev_qtr, _ = _extract_best_fact(facts_gaap, XBRL_TAG_MAP["revenue"], q_date, is_instant=False)
        gp_qtr, _ = _extract_best_fact(facts_gaap, XBRL_TAG_MAP["gross_profit"], q_date, is_instant=False)

        # Apply stock split normalization to shares
        if shares > 0 and shares_filed:
            try:
                filed_dt = datetime.datetime.strptime(shares_filed, "%Y-%m-%d").date()
                split_factor = 1.0
                for s_dt, factor in SPLITS_TABLE.get(ticker, []):
                    if filed_dt < s_dt:
                        split_factor *= factor
                shares = shares * split_factor
            except ValueError:
                pass

        # Fallbacks & Annualizations
        if shares <= 0:
            # Fallback to nearest previous shares if available
            shares = history[-1].shares_outstanding if history else 1e8

        # Human Mass: Annualized R&D + SG&A (4x quarterly flow)
        M_H = (rd_qtr * 4.0) + (sga_qtr * 4.0)
        if M_H <= 0:
            M_H = history[-1].M_H if history else 1e9

        # Physical Mass: Net PP&E
        M_P = ppe_net
        if M_P <= 0:
            M_P = history[-1].M_P if history else 1e9

        # Legal Mass: Goodwill + Intangible Assets
        M_L = goodwill + intangibles
        if M_L <= 0:
            M_L = history[-1].M_L if history else (M_P * 0.15)

        # Market Mass: Annualized Revenue x Margin (or Annualized Gross Profit)
        if gp_qtr > 0:
            M_M = gp_qtr * 4.0
        elif rev_qtr > 0:
            M_M = rev_qtr * 4.0 * 0.30
        else:
            M_M = history[-1].M_M if history else 1e9

        # Financial Mass: Equity Market Capitalization
        M_F = stock_price * shares

        mv = MassVector(
            date=q_date,
            quarter=q_label,
            ticker=ticker,
            M_L=max(1e6, M_L),
            M_H=max(1e6, M_H),
            M_P=max(1e6, M_P),
            M_M=max(1e6, M_M),
            M_F=max(1e6, M_F),
            gold_price_usd=max(1.0, gold_price),
            stock_price_usd=max(0.01, stock_price),
            shares_outstanding=max(1.0, shares)
        )
        history.append(mv)

    return history
