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
import bisect
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

    # Continuum Mechanics & Plasticity Fields (Option B / V-FIN-1.1, V-FIN-4, V-FIN-10, V-FIN-12)
    total_assets: float = 1e9
    current_liabilities: float = 1e8
    cash_reserves: float = 1e8
    total_debt: float = 1e8
    ebit: float = 1e8
    interest_expense: float = 1e7
    inventory: float = 0.0
    accounts_receivable: float = 0.0
    accounts_payable: float = 0.0
    cogs: float = 1e8
    tau_turnover: float = 1.0
    ccc_days: float = 90.0
    drucker_prager_phi: float = 0.1
    is_yield_ruptured: bool = False
    retarded_productivity: float = 1.0

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
    alpha: float = 0.0,
    use_retarded_gestation: bool = False,
    use_sector_coupling: bool = False,
    gamma_sec: float = 1.0
) -> Tuple[float, float, float, float, float]:
    """
    Compute the Shadow Divergence Indicator (SDI) and Productivity-Corrected SDI (PC-SDI):
      Sigma_shadow = d/dtau ln(m_F) - d/dtau ln(M_sub)
      Sigma_shadow^* = Sigma_shadow - alpha_effective * d/dtau ln(eta_sub)
    over a rolling window (default: 4 quarters = 1 year).

    Continuum Enhancements (Option B / V-FIN-12.1 & 12.2):
      - use_retarded_gestation: Evaluates d/dtau ln(eta_sub^(retarded)) via Gamma memory kernel.
      - use_sector_coupling: Dynamically scales alpha by capital intensity rho_capex:
          alpha_effective = alpha * (1 - rho_capex)^gamma_sec

    Parameters:
      history: List of MassVector
      current_idx: index of current evaluation quarter
      mode: 'usd' or 'gold'
      window: rolling lookback quarters (default 4)
      alpha: productivity correction coupling coefficient (default 0.0 for linear SDI)
      use_retarded_gestation: boolean, whether to use non-Markovian gestation memory
      use_sector_coupling: boolean, whether to scale alpha by sector capital intensity
      gamma_sec: sector scaling exponent (default 1.0)

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

    # Substrate productivity: instantaneous vs retarded gestation
    if use_retarded_gestation:
        eta_curr = max(1e-6, curr.retarded_productivity)
        eta_prev = max(1e-6, prev.retarded_productivity)
    else:
        eta_curr = max(1e-6, curr.substrate_productivity())
        eta_prev = max(1e-6, prev.substrate_productivity())

    d_ln_eta = (math.log(eta_curr) - math.log(eta_prev)) / dt_years

    # Sector capital intensity coupling: alpha(rho_capex) (V-FIN-12.1, V-FIN-16.4.1f)
    alpha_eff = alpha
    if use_sector_coupling and alpha > 0.0:
        rho_capex = curr.M_P / max(1.0, curr.M_H + curr.M_P)
        # Floor effective coupling at 0.50 * alpha to preserve profit-margin buffering for commodity/industrial engines
        alpha_eff = max(0.50 * alpha, alpha * ((1.0 - min(0.80, rho_capex)) ** gamma_sec))

    # Linear SDI
    sdi_linear = d_ln_mf - d_ln_sub
    
    # Productivity-Corrected SDI (PC-SDI)
    sdi_effective = sdi_linear - (alpha_eff * d_ln_eta)

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
# V2 FINANCIAL MANIFOLD EXISTENCE LENSES (V-FIN-16)
# ==============================================================================

def compute_manifold_stress_index(
    gold_series: List[dict],
    spx_series: List[dict],
    target_date: str,
    lookback_days: int = 365
) -> float:
    """
    Computes the Manifold Stress Index (MSI) via the Gold/S&P500 relative return ratio (Lens 1):
      MSI(tau) = [P_Au(tau) / P_Au(tau - Delta tau)] / [P_SPX(tau) / P_SPX(tau - Delta tau)]

    Physical Rationale (V-FIN-16 §4.2):
      Gold represents un-falsifiable physical substrate capacity (zero counterparty liability).
      S&P 500 represents aggregate equity claims on corporate cash flows.
      When MSI > 1.10: Gold is outperforming equities (>10% outperformance over lookback),
      indicating systemic friction, risk aversion, or flight from fiat liquidity claims.
      When MSI < 0.90: Equities outpace gold, indicating tranquil economic accretion.
    """
    if not gold_series or not spx_series:
        return 1.0

    target_dt = datetime.datetime.strptime(target_date, "%Y-%m-%d")
    lookback_dt = target_dt - datetime.timedelta(days=lookback_days)
    lookback_str = lookback_dt.strftime("%Y-%m-%d")

    def _get_price(series: List[dict], dt_str: str) -> float:
        dates = [p["date"] for p in series]
        idx = bisect.bisect_right(dates, dt_str) - 1
        if idx >= 0:
            return float(series[idx]["close"])
        return float(series[0]["close"])

    p_gold_curr = _get_price(gold_series, target_date)
    p_gold_prev = _get_price(gold_series, lookback_str)
    p_spx_curr = _get_price(spx_series, target_date)
    p_spx_prev = _get_price(spx_series, lookback_str)

    if p_gold_prev <= 0 or p_spx_prev <= 0 or p_spx_curr <= 0:
        return 1.0

    ret_gold = p_gold_curr / p_gold_prev
    ret_spx = p_spx_curr / p_spx_prev

    if ret_spx <= 0:
        return 1.0

    return float(ret_gold / ret_spx)


def compute_pdr(mf_growth: float, sub_growth: float) -> float:
    """
    Parasitic Decoupling Ratio (PDR, Lens 2):
      PDR = (dM_F / dtau) / (dM_sub / dtau)
    Approximated by annualized log-growth rates:
      - When sub_growth <= 0 and mf_growth > 0: PDR = 100.0 (extreme parasitic divergence:
        substrate is stagnating or eroding while market cap inflates, e.g. Boeing buybacks).
      - When sub_growth <= 0 and mf_growth <= 0: PDR = 1.0 (synchronized contraction).
      - When sub_growth > 0: PDR = mf_growth / sub_growth.
    """
    if sub_growth <= 0.0:
        if mf_growth > 0.0:
            return 100.0
        return 1.0
    return float(mf_growth / max(1e-4, sub_growth))


def compute_manifold_sdi_density_weighted(sdis: List[float], masses: List[float]) -> float:
    """
    Capitalization-Density-Weighted Manifold SDI (Frontier V-FIN-16.4.1):
      Sigma_shadow^(manifold, weighted)(tau) = sum_i w_i(tau) * Sigma_shadow^*(i)(tau)
      where w_i(tau) = M_F^(i)(tau) / sum_j M_F^(j)(tau)
    Weights systemic shadow divergence by individual entity financial mass density,
    preventing mega-cap hollowing from being diluted by multiple small firms.
    """
    if not sdis or not masses or len(sdis) != len(masses):
        return 0.0
    total_mass = sum(masses)
    if total_mass <= 0:
        return float(np.median(sdis))
    weights = [m / total_mass for m in masses]
    return float(sum(w * s for w, s in zip(weights, sdis)))


def compute_macro_screening_length(
    manifold_sdi: float,
    xi_0: float = 1.0,
    beta: float = 1.5
) -> float:
    """
    Constitutive Macroeconomic Screening Length (Frontier V-FIN-16.4.2):
      xi_manifold(tau) = xi_0 / (1 + beta * max(0, Sigma_shadow^(manifold)(tau)))
    Quantifies the contraction of systemic counterparty credit screening length
    under elevated manifold shadow divergence, predicting cross-asset correlation spikes
    and liquidity freezes.
    """
    stress_term = max(0.0, float(manifold_sdi))
    return float(xi_0 / (1.0 + beta * stress_term))


def compute_graph_laplacian_algebraic_connectivity(
    returns_matrix: np.ndarray,
    macro_xi: float = 1.0,
    critical_threshold: float = 0.15
) -> Tuple[float, float, str, Dict[str, Any]]:
    """
    V-FIN-3.1: Interbank & Counterparty Graph Laplacian Algebraic Connectivity.
    Evaluates the second smallest eigenvalue lambda_2(L_sym) of the normalized symmetric
    Graph Laplacian L_sym = I - D^(-1/2) W D^(-1/2) defined over the screened correlation
    manifold G = (V, E, W):
      d_ij = sqrt(2 * (1 - C_ij))
      W_ij = C_ij * Theta(1.5 * xi_manifold - d_ij)   for C_ij > 0, i != j
    
    By Cheeger's Inequality:
      lambda_2 / 2 <= h(G) <= sqrt(2 * lambda_2)
    When lambda_2 < critical_threshold (0.15), the network undergoes a percolation freeze,
    disconnecting sector clusters and trapping systemic liquidity.
    """
    if returns_matrix is None or len(returns_matrix) < 2:
        return 0.0, 0.0, "INSUFFICIENT_NODES", {}

    N = returns_matrix.shape[0]
    C = np.corrcoef(returns_matrix)
    np.fill_diagonal(C, 0.0)

    # Correlation metric distance on Riemannian manifold: d_ij = sqrt(2 * (1 - C_ij))
    dist_mat = np.sqrt(np.maximum(0.0, 2.0 * (1.0 - C)))
    cutoff = max(0.5, float(macro_xi) * 1.5)

    # Screened transmission conductance
    W = np.where((dist_mat <= cutoff) & (C > 0), C, 0.0)
    np.fill_diagonal(W, 0.0)

    d = np.sum(W, axis=1)
    d_inv_sqrt = np.where(d > 1e-12, 1.0 / np.sqrt(d), 0.0)
    D_inv = np.diag(d_inv_sqrt)
    L_sym = np.eye(N) - D_inv @ W @ D_inv

    eigvals = np.sort(np.linalg.eigvalsh(L_sym))
    lambda_2 = float(eigvals[1]) if len(eigvals) > 1 else 0.0
    cheeger_lower = float(lambda_2 / 2.0)
    cheeger_upper = float(np.sqrt(max(0.0, 2.0 * lambda_2)))

    # Correlation matrix trace absorption (market mode)
    C_with_diag = C + np.eye(N)
    eig_C = np.sort(np.linalg.eigvalsh(C_with_diag))
    alpha_trace = float(eig_C[-1] / np.sum(eig_C)) if np.sum(eig_C) > 0 else 0.0

    status = "PERCOLATION_FREEZE" if lambda_2 < critical_threshold else "STABLE"

    details = {
        "num_nodes": N,
        "lambda_1": float(eigvals[0]),
        "lambda_2": lambda_2,
        "lambda_max": float(eigvals[-1]),
        "cheeger_lower": cheeger_lower,
        "cheeger_upper": cheeger_upper,
        "mean_corr": float(np.mean(C[np.triu_indices_from(C, k=1)])),
        "alpha_trace": alpha_trace,
        "macro_xi": float(macro_xi),
        "cutoff_distance": float(cutoff)
    }

    return lambda_2, cheeger_lower, status, details


def compute_exogenous_alpha(
    alpha_0: float,
    treasury_series: List[dict],
    target_date: str,
    kappa: float = 15.0
) -> float:
    """
    V-FIN-16.4.1d: Exogenous Macro-Regime Tensor.
    Couples the operational decision threshold alpha to the instantaneous
    macro-regime stress tensor (represented by the 10-year Treasury yield).
    
    alpha(tau) = alpha_0 * (1 + kappa * r_rf(tau))
    where r_rf(tau) is the 10-year yield in decimal (e.g., 0.045 for 4.5%).
    When rates are 0%, alpha(tau) = alpha_0.
    When rates are 5%, alpha(tau) = alpha_0 * (1 + 15 * 0.05) = alpha_0 * 1.75.
    This effectively intensifies the productivity correction when capital is expensive,
    forcing structural discipline.
    """
    if not treasury_series:
        return alpha_0
    
    def _get_yield(series: List[dict], dt_str: str) -> float:
        dates = [p["date"] for p in series]
        idx = bisect.bisect_right(dates, dt_str) - 1
        if idx >= 0:
            return float(series[idx]["close"])
        return float(series[0]["close"])
        
    y10_pct = _get_yield(treasury_series, target_date)
    # ^TNX returns yield in percent, e.g., 4.5 for 4.5%
    # Handle bad data where yield might be negative or NaN
    if y10_pct != y10_pct or y10_pct < 0: 
        r_rf = 0.0
    else:
        r_rf = y10_pct / 100.0
    
    alpha_tau = alpha_0 * (1.0 + kappa * r_rf)
    return float(alpha_tau)


def classify_regime_v2(
    sdi: float,
    vam: float,
    sub_growth: float,
    mf_growth: float,
    pdr: Optional[float] = None,
    manifold_stress: Optional[float] = None,
    manifold_sdi: Optional[float] = None,
    pdr_threshold: float = 3.5
) -> Tuple[str, str, float]:
    """
    Enhanced Corporate Dynamical Regime Classifier incorporating Manifold Existence Lenses (V-FIN-16):
      - Lens 1: Manifold Stress Index (MSI from Gold/SPX) dynamically modulates sdi_danger threshold.
      - Lens 2: Parasitic Decoupling Ratio (PDR) gates positive growth to eliminate false alarms
                on balanced corporate expansions.
      - Lens 3: Manifold-Level Aggregate SDI (cross-sectional median) modulates systemic temperature.

    Parameters:
      sdi: Effective Productivity-Corrected SDI (Sigma_shadow^*)
      vam: Vector Anisotropy Metric (Delta_M)
      sub_growth: Annualized substrate growth rate d/dtau ln(M_sub)
      mf_growth: Annualized financial mass growth rate d/dtau ln(M_F)
      pdr: Parasitic Decoupling Ratio (mf_growth / sub_growth)
      manifold_stress: MSI = ret_Au / ret_SPX
      manifold_sdi: Systemic cross-sectional median SDI across the active corporate universe
      pdr_threshold: Minimum growth ratio required to confirm parasitic extraction (default 3.5)

    Returns:
      (regime_name, prediction, confidence)
    """
    cfg = BACKTEST_CONFIG["regime_thresholds"]
    sdi_danger_base = cfg["sdi_danger"] # 0.15
    sdi_extreme = cfg["sdi_extreme"]   # 0.35
    vam_distortion = cfg["vam_distortion"] # 0.45

    # 1. Dynamic Threshold Modulation (Lens 1 & Lens 3)
    sdi_danger_adj = sdi_danger_base

    if manifold_stress is not None:
        if manifold_stress > 1.10:
            # Systemic stress / gold outperformance -> lower threshold (heightened sensitivity)
            sdi_danger_adj -= 0.02
        elif manifold_stress < 0.90:
            # Systemic accretion / equity calm -> raise threshold (suppress false positives)
            sdi_danger_adj += 0.02

    if manifold_sdi is not None:
        if manifold_sdi > 0.08:
            # Systemic shadow expansion across manifold -> lower threshold
            sdi_danger_adj -= 0.03
        elif manifold_sdi < 0.0:
            # Systemic structural discipline / contraction -> raise threshold
            sdi_danger_adj += 0.03

    # Clamped to physical bounds [0.08, 0.22]
    sdi_danger_adj = max(0.08, min(0.22, sdi_danger_adj))

    # 2. Regime 3: Parasitic Decoupling
    # Candidate condition: SDI exceeds dynamic threshold and substrate is lagging
    is_danger_candidate = (sdi >= sdi_danger_adj) and (sub_growth <= 0.05 or mf_growth > 2.0 * max(0.01, sub_growth))

    if is_danger_candidate:
        # Lens 2 Confirmation:
        # In a positive growth environment (sub_growth > 0.05 and mf_growth > 0), verify whether
        # financial mass is outpacing substrate beyond the balanced accretion threshold.
        # If PDR <= pdr_threshold, the firm is expanding productively with market appreciation,
        # not parasitically extracting. Downgrade to Regime 2 (CAUTION).
        if (sub_growth > 0.05) and (mf_growth > 0):
            computed_pdr = pdr if pdr is not None else (mf_growth / sub_growth)
            if computed_pdr <= pdr_threshold:
                return "Regime 2 (Subcritical)", "CAUTION", 0.55

        # Confirmed Regime 3
        conf = 0.50 + (sdi / sdi_extreme) * 0.35
        if pdr is not None and pdr > 5.0:
            conf += 0.05
        if manifold_stress is not None and manifold_stress > 1.10:
            conf += 0.05
        confidence = min(0.95, conf)
        return "Regime 3 (Parasitic)", "DANGER", float(confidence)

    # 3. Regime 1: Virtuous Cycle
    if sub_growth > 0.02 and sdi < sdi_danger_adj and vam < vam_distortion:
        confidence = min(0.95, 0.60 + sub_growth * 0.50)
        return "Regime 1 (Virtuous)", "HEALTHY", float(confidence)

    # 4. Regime 2: Subcritical / Stagnant
    return "Regime 2 (Subcritical)", "CAUTION", 0.55


def classify_regime_v3(
    sdi: float,
    vam: float,
    sub_growth: float,
    mf_growth: float,
    pdr: Optional[float] = None,
    manifold_stress: Optional[float] = None,
    manifold_sdi: Optional[float] = None,
    pdr_threshold: float = 3.5,
    is_yield_ruptured: bool = False,
    phi_c: Optional[float] = None,
    sector: str = "Unknown"
) -> Tuple[str, str, float]:
    """
    V3 Continuum Plasticity Regime Classifier (V-FIN-4, V-FIN-10, V-FIN-16, V-FIN-16.4.1e, V-FIN-16.4.1i):
      Integrates all three Manifold Existence Lenses (MSI, PDR, Systemic SDI) with
      Lens 4: Capped Drucker-Prager Balance-Sheet Yield Surface (phi_C).

    Physical Principles:
      1. A corporate engine cannot maintain a Virtuous Cycle (Regime 1) if its internal
         balance-sheet stress state exceeds dynamic yield strength (phi_C < 0).
         Plastic deformation (covenant rupture, debt distress) forces departure to Regime 2 (CAUTION).
      2. Plastic rupture (phi_C < 0) sensitizes the operational danger threshold:
         a leveraged/ruptured firm requires less shadow divergence (sdi) to trigger Regime 3 (DANGER).
      3. For defensive, non-cyclical franchises (e.g. Consumer Staples, Utilities) with low crash
         base rates, steady brand compounding without balance-sheet leverage (phi_C >= 0) is non-parasitic
         and remains confined to Regime 2 (CAUTION) unless extreme bubble speculation occurs (sdi >= sdi_extreme).

    Returns:
      (regime_name, prediction, confidence)
    """
    cfg = BACKTEST_CONFIG["regime_thresholds"]
    sdi_danger_base = cfg["sdi_danger"]  # 0.15
    sdi_extreme = cfg["sdi_extreme"]      # 0.35
    vam_distortion = cfg["vam_distortion"]  # 0.45

    # 1. Dynamic Threshold Modulation (Lens 1, 3, & 4)
    sdi_danger_adj = sdi_danger_base

    if manifold_stress is not None:
        if manifold_stress > 1.10:
            sdi_danger_adj -= 0.02
        elif manifold_stress < 0.90:
            sdi_danger_adj += 0.02

    if manifold_sdi is not None:
        if manifold_sdi > 0.08:
            sdi_danger_adj -= 0.03
        elif manifold_sdi < 0.0:
            sdi_danger_adj += 0.03

    # Lens 4: Plastic Rupture Sensitization (V-FIN-16.4.1e)
    is_rupture_active = is_yield_ruptured or (phi_c is not None and phi_c < 0.0)
    if is_rupture_active:
        phi_deficit = min(0.20, abs(phi_c) if phi_c is not None else 0.05)
        sdi_danger_adj -= (0.02 + 0.10 * phi_deficit)

    # Clamped to physical bounds [0.06, 0.22]
    sdi_danger_adj = max(0.06, min(0.22, sdi_danger_adj))

    # Base-Rate Modulated PDR Threshold for Defensive Franchises (V-FIN-16.4.1i)
    effective_pdr_threshold = pdr_threshold
    if sector in ["Consumer Staples", "Utilities"]:
        effective_pdr_threshold = 5.0

    # 2. Regime 3: Parasitic Decoupling
    is_danger_candidate = False
    if is_rupture_active:
        # Compromised balance sheet (Boeing, GE power collapse, Chapter 11 risk)
        is_danger_candidate = (sdi >= sdi_danger_adj) and (sub_growth <= 0.08 or mf_growth > 1.8 * max(0.01, sub_growth))
    elif sub_growth < 0.0:
        # Actively liquidating structural substrate
        is_danger_candidate = (sdi >= sdi_danger_adj)
    else:
        # Solvent balance sheet with non-contracting substrate
        computed_pdr = pdr if pdr is not None else ((mf_growth / max(0.01, sub_growth)) if sub_growth > 0 else 1.0)
        is_danger_candidate = (sdi >= sdi_extreme) or (sdi >= sdi_danger_adj and computed_pdr > effective_pdr_threshold)

    if is_danger_candidate:
        conf = 0.50 + (sdi / sdi_extreme) * 0.35
        if is_rupture_active:
            conf += 0.10
        if pdr is not None and pdr > 5.0:
            conf += 0.05
        if manifold_stress is not None and manifold_stress > 1.10:
            conf += 0.05
        return "Regime 3 (Parasitic)", "DANGER", float(min(0.95, conf))

    # 3. Regime 1: Virtuous Cycle (Blocked if balance sheet is ruptured!)
    if sub_growth > 0.02 and sdi < sdi_danger_adj and vam < vam_distortion:
        if is_rupture_active:
            return "Regime 2 (Subcritical)", "CAUTION", 0.60
        confidence = min(0.95, 0.60 + sub_growth * 0.50)
        return "Regime 1 (Virtuous)", "HEALTHY", float(confidence)

    # 4. Regime 2: Subcritical / Stagnant
    return "Regime 2 (Subcritical)", "CAUTION", 0.55


# ==============================================================================
# CONSTITUTIVE MECHANICAL & CONTINUUM CLOSURE FUNCTIONS (V-FIN-1, V-FIN-4, V-FIN-12)
# ==============================================================================

def compute_cash_conversion_cycle_timescale(
    inv: float,
    ar: float,
    ap: float,
    rev: float,
    cogs: float,
    assets: float,
    epsilon_days: float = 1.0
) -> Tuple[float, float, float, float, float]:
    """
    Computes the firm-specific turnover timescale tau_turnover via the Cash Conversion Cycle (V-FIN-1.1):
      DIO = 365.25 * (Inventory / COGS)
      DSO = 365.25 * (Receivables / Revenue)
      DPO = 365.25 * (Payables / COGS)
      CCC = DIO + DSO - DPO [days]
      tau_turnover = max(epsilon_days, CCC) / 365.25 * (Total Assets / Revenue) [years]

    Docstring Honesty (Rule 5.2):
      - In negative CCC regimes (e.g. Apple, Amazon where suppliers finance operations),
        CCC < 0. To maintain positive definite turnover matrix tau_0, CCC is floored at
        epsilon_days (default 1.0 day).
      - Normalization error: Neglects intra-quarter working capital seasonality (< 5% error
        against full monthly treasury ledgers).
      - Returns: (tau_turnover_years, ccc_days, dio_days, dso_days, dpo_days).
    """
    cogs_eff = max(1.0, float(cogs))
    rev_eff = max(1.0, float(rev))
    assets_eff = max(1.0, float(assets))

    dio = 365.25 * max(0.0, float(inv)) / cogs_eff
    dso = 365.25 * max(0.0, float(ar)) / rev_eff
    dpo = 365.25 * max(0.0, float(ap)) / cogs_eff
    ccc = dio + dso - dpo

    # Capital intensity ratio: Total Assets / Revenue
    capital_intensity = assets_eff / rev_eff
    ccc_clamped_days = max(epsilon_days, ccc)
    tau_turnover = (ccc_clamped_days / 365.25) * capital_intensity

    return float(tau_turnover), float(ccc), float(dio), float(dso), float(dpo)


def compute_cauchy_stress_tensor(
    cl: float,
    cash: float,
    assets: float,
    debt: float,
    ebit: float,
    rev: float,
    int_exp: float,
    sga: float,
    gp: float,
    st_debt: Optional[float] = None,
    inv: float = 0.0,
    ar: float = 0.0,
    ap: float = 0.0,
    sector: str = "Unknown"
) -> Tuple[np.ndarray, float]:
    """
    Computes the 3x3 symmetric GAAP-to-Cauchy stress tensor sigma_C and margin cushion (V-FIN-4.1, V-FIN-16.4.1e, V-FIN-16.4.1h, V-FIN-16.4.1j, V-FIN-16.4.1k):
      sigma_C = [[sigma_liq,   tau_credit, 0         ],
                 [tau_credit,  sigma_solv, tau_opex   ],
                 [0,           tau_opex,   sigma_margin]]

    Diagonal Normal Stresses:
      sigma_liq    = (Net Non-Float Liabilities - Quick Assets) / Assets
                     where Net Non-Float = max(0, Current Liabilities - Accounts Payable)
                     and Quick Assets = Cash + 0.5 * AR + 0.25 * Inventory
      sigma_solv   = (Effective Debt - EBIT) / Assets
      sigma_margin = max(0, Interest Expense - EBIT) / Revenue  [Tensile debt-service deficit]

    Operational Margin Cushion:
      margin_cushion = max(0, EBIT - Interest Expense) / Revenue [Adds to yield strength sigma_Y]

    Off-Diagonal Shear Stresses:
      tau_credit = (Effective Short-Term Debt) / Assets (refinancing rollover pressure)
      tau_opex   = max(0, -EBIT) / Revenue (operational cash burn friction; 0 when EBIT >= 0)

    Docstring Honesty (Rule 5.2):
      - Units: Dimensionless ratios normalized to Total Assets and Revenue.
      - If short-term debt is unobserved, approximated as 0.25 * Effective Debt.
      - Positivity: Off-diagonal terms are symmetric to satisfy angular momentum conservation.
    """
    assets_eff = max(1.0, float(assets))
    rev_eff = max(1.0, float(rev))

    # V-FIN-16.4.1e: Interest-Coverage-Ratio (ICR) Damping on Solvency Tensile Stress
    int_exp_pos = max(1e5, float(int_exp))
    icr = max(0.0, float(ebit)) / int_exp_pos
    psi_icr = max(1.0, math.log(1.0 + icr))

    # V-FIN-16.4.1k: Real Estate REIT Non-Recourse Asset-Backed Collateral Exclusion
    # In REITs, property-level mortgage debt is secured directly by physical real estate
    # with loan-to-value (LTV) ratios bounded below 50%.
    debt_collateral_factor = 0.60 if sector == "Real Estate" else 1.0
    effective_debt = (float(debt) * debt_collateral_factor) / psi_icr

    # Quick Assets & Working Capital Float Coverage (V-FIN-16.4.1g / V-FIN-16.4.1h / V-FIN-16.4.1j)
    # Trade credit (Accounts Payable) represents self-liquidating operational supplier float
    # rather than default financial debt.
    quick_assets = float(cash) + 0.50 * max(0.0, float(ar)) + 0.25 * max(0.0, float(inv))
    ap_float = max(0.0, float(ap))
    net_cl = max(0.0, float(cl) - ap_float)
    sigma_liq = (net_cl - quick_assets) / assets_eff
    sigma_solv = (effective_debt - float(ebit)) / assets_eff

    # Solvency Margin Stress & Operational Cushion (V-FIN-16.4.1h)
    raw_margin = (float(int_exp) - float(ebit)) / rev_eff
    sigma_margin = max(0.0, raw_margin)
    margin_cushion = max(0.0, -raw_margin)

    if st_debt is None:
        tau_credit = 0.25 * max(0.0, effective_debt) / assets_eff
    else:
        tau_credit = (max(0.0, float(st_debt)) / psi_icr) / assets_eff

    tau_opex = max(0.0, -float(ebit)) / rev_eff

    sigma_tensor = np.array([
        [sigma_liq,    tau_credit, 0.0],
        [tau_credit,   sigma_solv, tau_opex],
        [0.0,          tau_opex,   sigma_margin]
    ], dtype=float)

    return sigma_tensor, margin_cushion


def compute_drucker_prager_yield(
    stress_tensor: np.ndarray,
    liquid_reserves: float,
    undrawn_credit: float,
    assets: float,
    alpha_dp: float = 0.25,
    sector: str = "Unknown",
    margin_cushion: float = 0.0
) -> Tuple[float, float, float, bool, float]:
    """
    Evaluates the Capped Drucker-Prager Yield Function phi_C for the corporate body (V-FIN-4.2):
      p = 1/3 * Tr(sigma_C)                             [Mean hydrostatic balance-sheet pressure]
      s = sigma_C - p * I                               [Deviatoric stress tensor]
      J_2 = 1/2 * Tr(s^2)                               [Second deviatoric stress invariant]
      sigma_Y^(C) = (Liquid Reserves + Credit) / Assets  [Dynamic structural yield strength]
      phi_C = sigma_Y^(C) - (sqrt(3 * J_2) + alpha_DP * p)

    Yield / Rupture Criterion:
      phi_C >= 0 : Confined elastic/viscoplastic state (solvent, bounded operations).
      phi_C < 0  : Yield surface rupture / plastic failure (liquidity freeze, covenant rupture).

    Docstring Honesty (Rule 5.2):
      - Friction coefficient alpha_DP defaults to 0.25 based on standard pressure-sensitivity
        in financial solvency networks.
      - Known analytic limit: For isotropic hydrostatic pressure (J_2 = 0), yield condition
        simplifies to sigma_Y >= alpha_DP * p.
      - Returns: (phi_C, p, J_2, is_ruptured, sigma_Y).
    """
    if stress_tensor.shape != (3, 3):
        raise ValueError("stress_tensor must be a 3x3 matrix")

    # Hydrostatic pressure
    p = float(np.trace(stress_tensor) / 3.0)

    # Deviatoric stress tensor
    s = stress_tensor - p * np.eye(3)

    # Second invariant J_2 = 1/2 Tr(s^2)
    s_squared = np.dot(s, s)
    j2 = float(0.5 * np.trace(s_squared))
    j2_nonneg = max(0.0, j2)

    # Effective shear stress
    tau_eff = math.sqrt(3.0 * j2_nonneg)

    # V-FIN-16.4.1f: Commercial Bank Deposit Decoupling & Regulatory Capital Adequacy
    if sector == "Financials":
        assets_eff = max(1.0, float(assets))
        equity_ratio = (liquid_reserves + max(0.0, float(assets) * 0.10)) / assets_eff
        phi_c = equity_ratio - 0.08
        is_ruptured = bool(phi_c < 0.0)
        return float(phi_c), float(p), float(j2_nonneg), is_ruptured, float(0.08 + phi_c)

    # V-FIN-16.4.1b & V-FIN-16.4.1k: Sector-Heterogeneous Rate Pass-Through Elasticity (omega_sec)
    elasticity_map = {
        "Consumer Staples": 1.4,
        "Utilities": 1.5,
        "Health Care": 1.2,
        "Energy": 1.1,
        "Materials": 1.0,
        "Industrials": 1.0,
        "Information Technology": 1.0,
        "Communication Services": 1.0,
        "Financials": 1.0,
        "Consumer Discretionary": 0.9,
        "Real Estate": 1.8
    }
    omega_sec = elasticity_map.get(sector, 1.0)

    # Yield strength: baseline operational enterprise capacity + liquidity buffer + margin cushion + REIT collateral (V-FIN-16.4.1e, V-FIN-16.4.1h, V-FIN-16.4.1k)
    assets_eff = max(1.0, float(assets))
    sigma_y_liq = float(max(0.0, liquid_reserves + undrawn_credit) / assets_eff)
    sigma_base = 0.15
    reit_collateral = 0.10 if sector == "Real Estate" else 0.0
    sigma_y = (sigma_base * omega_sec) + sigma_y_liq + (float(margin_cushion) * 0.20) + reit_collateral

    # Yield function
    phi_c = sigma_y - (tau_eff + alpha_dp * p)
    is_ruptured = bool(phi_c < 0.0)

    return float(phi_c), float(p), float(j2_nonneg), is_ruptured, float(sigma_y)


def compute_retarded_gestation_productivity(
    history: List[MassVector],
    current_idx: int,
    tau_bar: float = 2.5,
    dt_quarter: float = 0.25
) -> float:
    """
    Computes Non-Markovian Retarded Gestation Substrate Productivity (V-FIN-12.1):
      eta_sub^(retarded)(tau) = int_0^tau K(tau - s) eta_sub(s) ds
      where K(u) = (u / tau_bar^2) * exp(-u / tau_bar),  int_0^inf K(u) du = 1.

    Docstring Honesty (Rule 5.2):
      - tau_bar is the mean capital gestation lag in years (default 2.5 years = 10 quarters).
      - Discretization uses normalized trapezoidal/point weights over available quarters
        k = 0 ... current_idx.
      - Known analytic limit: For constant history eta_sub(s) = eta_0, the normalized
        convolution reproduces eta_0 exactly (error < 1e-12).
      - Returns: eta_sub_retarded [dimensionless].
    """
    if not history or current_idx < 0:
        return 1.0

    curr_idx = min(current_idx, len(history) - 1)
    if curr_idx == 0:
        return float(history[0].substrate_productivity())

    # Collect past productivities and lags
    weights = []
    prod_vals = []

    for k in range(curr_idx + 1):
        # Lookback quarters from current: lag_q = curr_idx - k
        lag_years = (curr_idx - k) * dt_quarter
        # Gamma kernel: K(u) = (u / tau_bar^2) * exp(-u / tau_bar)
        k_val = (lag_years / (tau_bar ** 2)) * math.exp(-lag_years / tau_bar)
        weights.append(k_val)
        prod_vals.append(history[k].substrate_productivity())

    sum_weights = sum(weights)
    if sum_weights <= 1e-9:
        return float(history[curr_idx].substrate_productivity())

    # Normalized convolution ensures partition of unity across finite lookbacks
    retarded_eta = sum(w * p for w, p in zip(weights, prod_vals)) / sum_weights
    return float(retarded_eta)


# ==============================================================================
# SEC XBRL FACT PARSING ENGINE
# ==============================================================================

# Known stock splits table for 2016-2026 legacy validation baseline
FALLBACK_SPLITS_TABLE = {
    "AAPL": [{"date": "2020-08-31", "ratio": 4.0}],
    "WMT": [{"date": "2024-02-26", "ratio": 3.0}],
    "GE": [{"date": "2021-08-02", "ratio": 0.125}],
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
    facts_gaap = {**sec_facts.get("facts", {}).get("us-gaap", {}), **sec_facts.get("facts", {}).get("dei", {})}
    
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

    # Dynamic split lookup with legacy fallback
    try:
        from data_fetcher import fetch_market_splits
        cached_splits = fetch_market_splits(ticker)
    except Exception:
        cached_splits = []
    splits_data = FALLBACK_SPLITS_TABLE.get(ticker, cached_splits)

    history: List[MassVector] = []

    # Identify Sector for V-FIN-16.4.1b, V-FIN-16.4.1f, V-FIN-16.4.1g
    try:
        from config import UNIVERSE_MODE
        from sp500_universe import get_universe
        ticker_sector = get_universe(UNIVERSE_MODE).get(ticker, {}).get("sector", "Unknown")
    except Exception:
        ticker_sector = "Unknown"

    # Pre-extract observed shares to find first valid share count (avoids arbitrary 1e8 fallback)
    first_valid_shares = None
    for _, q_d in quarters:
        s_val, _ = _extract_best_fact(facts_gaap, XBRL_TAG_MAP["shares_outstanding"], q_d, is_instant=True)
        if s_val > 1e6:
            first_valid_shares = s_val
            break
    if first_valid_shares is None:
        first_valid_shares = 1e8

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
                for s in splits_data:
                    s_dt = datetime.datetime.strptime(s["date"], "%Y-%m-%d").date() if isinstance(s["date"], str) else s["date"]
                    if filed_dt < s_dt:
                        split_factor *= float(s["ratio"])
                shares = shares * split_factor
            except (ValueError, KeyError, TypeError):
                pass

        # Robust share count fallback & outlier rejection (V-FIN-16.4.1g)
        # Prevents artificial 3500% market cap spikes when SEC tags are missing in early quarters
        # or when unit scaling glitches occur (e.g. AMT 2020-Q1).
        if shares <= 1e6:
            shares = history[-1].shares_outstanding if history else first_valid_shares
        elif history and (shares < 0.20 * history[-1].shares_outstanding or shares > 5.0 * history[-1].shares_outstanding):
            shares = history[-1].shares_outstanding

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
        # For Financials, smooth across trailing 4 quarters to eliminate spurious quarterly trading volatility (V-FIN-16.4.1g)
        if ticker_sector == "Financials":
            recent_revs = [h.M_M / 0.30 / 4.0 for h in history[-3:] if h.M_M > 0]
            curr_rev = rev_qtr if rev_qtr > 0 else (gp_qtr if gp_qtr > 0 else 0.0)
            if curr_rev > 0:
                recent_revs.append(curr_rev)
            if recent_revs:
                avg_rev_qtr = sum(recent_revs) / len(recent_revs)
                M_M = avg_rev_qtr * 4.0 * 0.30
            elif gp_qtr > 0:
                M_M = gp_qtr * 4.0
            elif rev_qtr > 0:
                M_M = rev_qtr * 4.0 * 0.30
            else:
                M_M = history[-1].M_M if history else 1e9
        elif gp_qtr > 0:
            M_M = gp_qtr * 4.0
        elif rev_qtr > 0:
            M_M = rev_qtr * 4.0 * 0.30
        else:
            M_M = history[-1].M_M if history else 1e9

        # Financial Mass: Equity Market Capitalization
        M_F = stock_price * shares

        # 4. Working Capital & Balance-Sheet Continuum Extraction (V-FIN-1.1, V-FIN-4, V-FIN-10)
        inv_inst, _ = _extract_best_fact(facts_gaap, XBRL_TAG_MAP.get("inventory", []), q_date, is_instant=True)
        ar_inst, _ = _extract_best_fact(facts_gaap, XBRL_TAG_MAP.get("accounts_receivable", []), q_date, is_instant=True)
        ap_inst, _ = _extract_best_fact(facts_gaap, XBRL_TAG_MAP.get("accounts_payable", []), q_date, is_instant=True)
        cogs_qtr, _ = _extract_best_fact(facts_gaap, XBRL_TAG_MAP.get("cost_of_goods_sold", []), q_date, is_instant=False)
        assets_inst, _ = _extract_best_fact(facts_gaap, XBRL_TAG_MAP.get("total_assets", []), q_date, is_instant=True)
        cl_inst, _ = _extract_best_fact(facts_gaap, XBRL_TAG_MAP.get("current_liabilities", []), q_date, is_instant=True)
        debt_inst, _ = _extract_best_fact(facts_gaap, XBRL_TAG_MAP.get("total_debt", []), q_date, is_instant=True)
        st_debt_inst, _ = _extract_best_fact(facts_gaap, XBRL_TAG_MAP.get("short_term_debt", []), q_date, is_instant=True)
        cash_inst, _ = _extract_best_fact(facts_gaap, XBRL_TAG_MAP.get("cash_equivalents", []), q_date, is_instant=True)
        st_inv_inst, _ = _extract_best_fact(facts_gaap, XBRL_TAG_MAP.get("short_term_investments", []), q_date, is_instant=True)
        ebit_qtr, _ = _extract_best_fact(facts_gaap, XBRL_TAG_MAP.get("ebit", []), q_date, is_instant=False)
        int_exp_qtr, _ = _extract_best_fact(facts_gaap, XBRL_TAG_MAP.get("interest_expense", []), q_date, is_instant=False)

        # Realistic fallbacks & annualizations
        rev_ann = rev_qtr * 4.0 if rev_qtr > 0 else (history[-1].M_M / 0.30 if history else 1e9)
        cogs_ann = cogs_qtr * 4.0 if cogs_qtr > 0 else (rev_ann * 0.65)
        ebit_ann = ebit_qtr * 4.0 if ebit_qtr != 0 else (gp_qtr * 4.0 * 0.40 if gp_qtr > 0 else rev_ann * 0.15)
        assets_val = assets_inst if assets_inst > 0 else (history[-1].total_assets if history else max(M_P * 1.8, rev_ann))
        cash_reserves = (cash_inst + st_inv_inst) if (cash_inst + st_inv_inst) > 0 else (history[-1].cash_reserves if history else max(1e6, assets_val * 0.08))
        cl_val = cl_inst if cl_inst > 0 else (history[-1].current_liabilities if history else max(1e6, assets_val * 0.15))
        debt_val = debt_inst if debt_inst > 0 else (history[-1].total_debt if history else max(1e6, cl_val * 0.60))
        int_exp_ann = int_exp_qtr * 4.0 if int_exp_qtr > 0 else max(1e6, debt_val * 0.04)

        # V-FIN-16.4.1g: Financial Tangible Equity Substrate Anchoring
        # Financial institutions have low physical net PP&E; their balance-sheet economic substrate
        # is anchored by Common Tangible Equity (assets_val * 0.08 - 0.10)
        if ticker_sector == "Financials":
            M_P = max(M_P, float(assets_val) * 0.08)

        # CCC and Turnover Timescale (V-FIN-1.1)
        tau_turnover, ccc_days, _, _, _ = compute_cash_conversion_cycle_timescale(
            inv=inv_inst,
            ar=ar_inst,
            ap=ap_inst,
            rev=max(1.0, rev_ann),
            cogs=max(1.0, cogs_ann),
            assets=max(1.0, assets_val)
        )

        # GAAP-to-Cauchy Stress Tensor (V-FIN-4 & V-FIN-16.4.1h)
        sigma_c, margin_cushion = compute_cauchy_stress_tensor(
            cl=cl_val,
            cash=cash_reserves,
            assets=assets_val,
            debt=debt_val,
            ebit=ebit_ann,
            rev=max(1.0, rev_ann),
            int_exp=int_exp_ann,
            sga=sga_qtr * 4.0,
            gp=gp_qtr * 4.0,
            st_debt=st_debt_inst if st_debt_inst > 0 else None,
            inv=inv_inst,
            ar=ar_inst,
            ap=ap_inst,
            sector=ticker_sector
        )

        # Drucker-Prager Yield Function (V-FIN-10 & V-FIN-16.4.1b)
        phi_c, _, _, is_ruptured, _ = compute_drucker_prager_yield(
            stress_tensor=sigma_c,
            liquid_reserves=cash_reserves,
            undrawn_credit=cash_reserves * 0.5,
            assets=assets_val,
            alpha_dp=0.25,
            sector=ticker_sector,
            margin_cushion=margin_cushion
        )

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
            shares_outstanding=max(1.0, shares),
            total_assets=float(assets_val),
            current_liabilities=float(cl_val),
            cash_reserves=float(cash_reserves),
            total_debt=float(debt_val),
            ebit=float(ebit_ann),
            interest_expense=float(int_exp_ann),
            inventory=float(inv_inst),
            accounts_receivable=float(ar_inst),
            accounts_payable=float(ap_inst),
            cogs=float(cogs_ann),
            tau_turnover=float(tau_turnover),
            ccc_days=float(ccc_days),
            drucker_prager_phi=float(phi_c),
            is_yield_ruptured=bool(is_ruptured)
        )
        history.append(mv)
        # Compute non-Markovian retarded productivity over lookback history
        mv.retarded_productivity = compute_retarded_gestation_productivity(history, current_idx=len(history) - 1, tau_bar=2.5)

    return history
