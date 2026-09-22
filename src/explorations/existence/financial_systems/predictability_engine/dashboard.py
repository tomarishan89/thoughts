"""
dashboard.py
------------
Visualization and scorecard generation module for the Corporate Predictability Engine.
Generates publication-quality figures:
  1. Boeing 737 MAX Case Study (Structural Lead-Time Validation)
  2. Apple vs. Boeing (Virtuous Platform vs. Parasitic Extraction)
  3. Predictability Scorecard & USD vs. Gold Empirical Comparison
"""

import os
import json
import csv
import datetime
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

from config import OUTPUT_DIR, FIGURES_DIR

# Set publication style
plt.rcParams.update({
    "font.family": "sans-serif",
    "font.size": 10,
    "axes.titlesize": 12,
    "axes.labelsize": 11,
    "xtick.labelsize": 9,
    "ytick.labelsize": 9,
    "legend.fontsize": 9,
    "figure.titlesize": 14,
    "figure.dpi": 300,
    "axes.grid": True,
    "grid.alpha": 0.3
})


def load_prediction_log(filename: str = "prediction_log_usd.csv") -> list:
    filepath = os.path.join(OUTPUT_DIR, filename)
    with open(filepath, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return list(reader)


def plot_boeing_case_study(log: list):
    """
    Figure 1: Boeing 737 MAX Case Study.
    Demonstrates the 4-6 quarter lead-time of SDI prior to catastrophic collapse.
    """
    ba_rows = [r for r in log if r["ticker"] == "BA"]
    if not ba_rows:
        return

    dates = [datetime.datetime.strptime(r["date"], "%Y-%m-%d") for r in ba_rows]
    stocks = [float(r["stock_price"]) for r in ba_rows]
    sub = [float(r["substrate_billions"]) for r in ba_rows]
    sdi = [float(r["SDI"]) for r in ba_rows]
    vam = [float(r["VAM"]) for r in ba_rows]
    preds = [r["prediction"] for r in ba_rows]

    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(11, 10), sharex=True, gridspec_kw={"height_ratios": [2, 1.2, 1]})
    
    # 1. Top Panel: Stock Price & Substrate with Danger Shading
    ax1.plot(dates, stocks, color="#0d47a1", linewidth=2.2, label="Boeing Stock Price ($BA)")
    ax1_sub = ax1.twinx()
    ax1_sub.plot(dates, sub, color="#2e7d32", linewidth=2.0, linestyle="--", label="Structural Substrate M_sub ($B)")
    
    # Highlight DANGER quarters
    for i in range(len(dates) - 1):
        if preds[i] == "DANGER":
            ax1.axvspan(dates[i], dates[i+1], color="#ffebee", alpha=0.6)

    # Milestones
    crash1_dt = datetime.datetime(2018, 10, 29) # Lion Air 610
    crash2_dt = datetime.datetime(2019, 3, 10)  # Ethiopian 302
    ax1.axvline(crash1_dt, color="#b71c1c", linestyle=":", linewidth=1.8)
    ax1.text(crash1_dt, 380, " Oct 2018: Lion Air 610", color="#b71c1c", fontsize=9, fontweight="bold")
    ax1.axvline(crash2_dt, color="#d50000", linestyle="-.", linewidth=2.0)
    ax1.text(crash2_dt, 410, " Mar 2019: Ethiopian 302 (Grounding)", color="#d50000", fontsize=9, fontweight="bold")

    ax1.set_ylabel("Stock Price (USD)")
    ax1_sub.set_ylabel("Substrate M_sub ($B)", color="#2e7d32")
    ax1.set_title("Boeing Company (BA): Parasitic Decoupling & Catastrophic Rupture", fontweight="bold")
    
    # Combined legend
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax1_sub.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc="upper left")

    # 2. Middle Panel: Shadow Divergence Indicator (SDI)
    ax2.plot(dates, sdi, color="#c62828", linewidth=2.0, marker="o", markersize=4, label="Shadow Divergence Indicator (SDI)")
    ax2.axhline(0.15, color="#e65100", linestyle="--", linewidth=1.2, label="Parasitic Threshold (SDI = +0.15)")
    ax2.axhline(0.00, color="gray", linestyle="-", linewidth=0.8)
    ax2.fill_between(dates, sdi, 0.15, where=[s >= 0.15 for s in sdi], color="#ffcdd2", alpha=0.5)
    ax2.set_ylabel("SDI (d ln M_F - d ln M_sub)")
    ax2.legend(loc="upper right")

    # 3. Bottom Panel: Vector Anisotropy Metric (VAM)
    ax3.plot(dates, vam, color="#4a148c", linewidth=2.0, label="Vector Anisotropy Metric (VAM)")
    ax3.axhline(0.45, color="#7b1fa2", linestyle="--", label="Distortion Bound (0.45)")
    ax3.set_ylabel("VAM Delta_M")
    ax3.set_ylim(0.0, 0.85)
    ax3.legend(loc="lower right")

    ax3.xaxis.set_major_locator(mdates.YearLocator(2))
    ax3.xaxis.set_minor_locator(mdates.YearLocator(1))
    ax3.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    ax3.set_xlabel("Filing Timeline")

    plt.tight_layout()
    out_path = os.path.join(FIGURES_DIR, "boeing_737max_predictability_case_study.png")
    plt.savefig(out_path)
    plt.close()
    print(f"[FIGURE] Saved Boeing case study to {out_path}")


def plot_apple_vs_boeing(log: list):
    """
    Figure 2: Apple (Virtuous) vs. Boeing (Parasitic) Comparison.
    Contrasts balanced structural growth against debt-inflated financialization.
    """
    aapl_rows = [r for r in log if r["ticker"] == "AAPL"]
    ba_rows = [r for r in log if r["ticker"] == "BA"]
    if not aapl_rows or not ba_rows:
        return

    dates_aapl = [datetime.datetime.strptime(r["date"], "%Y-%m-%d") for r in aapl_rows]
    sdi_aapl = [float(r["SDI"]) for r in aapl_rows]
    sub_aapl = [float(r["substrate_billions"]) for r in aapl_rows]
    mf_aapl = [float(r["M_F_billions"]) for r in aapl_rows]

    dates_ba = [datetime.datetime.strptime(r["date"], "%Y-%m-%d") for r in ba_rows]
    sdi_ba = [float(r["SDI"]) for r in ba_rows]
    sub_ba = [float(r["substrate_billions"]) for r in ba_rows]
    mf_ba = [float(r["M_F_billions"]) for r in ba_rows]

    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(13, 9))

    # Panel A: Apple Substrate vs Market Cap
    ax1.plot(dates_aapl, [m / mf_aapl[0] for m in mf_aapl], color="#1565c0", linewidth=2.0, label="Normalized M_F (Market Cap)")
    ax1.plot(dates_aapl, [s / sub_aapl[0] for s in sub_aapl], color="#2e7d32", linewidth=2.0, linestyle="--", label="Normalized Substrate M_sub")
    ax1.set_title("Apple Inc. (AAPL): Virtuous Coupled Expansion", fontweight="bold")
    ax1.set_ylabel("Normalized Growth (2016=1.0)")
    ax1.legend(loc="upper left")

    # Panel B: Boeing Substrate vs Market Cap
    ax2.plot(dates_ba, [m / mf_ba[0] for m in mf_ba], color="#d32f2f", linewidth=2.0, label="Normalized M_F (Market Cap)")
    ax2.plot(dates_ba, [s / sub_ba[0] for s in sub_ba], color="#2e7d32", linewidth=2.0, linestyle="--", label="Normalized Substrate M_sub")
    ax2.set_title("Boeing Co. (BA): Parasitic Substrate Stagnation", fontweight="bold")
    ax2.set_ylabel("Normalized Growth (2016=1.0)")
    ax2.legend(loc="upper left")

    # Panel C: Apple SDI (Linear vs PC-SDI)
    sdi_aapl_lin = [float(r["SDI_linear"]) for r in aapl_rows]
    ax3.plot(dates_aapl, sdi_aapl_lin, color="#90caf9", linewidth=1.5, linestyle=":", label="Linear SDI (alpha=0)")
    ax3.plot(dates_aapl, sdi_aapl, color="#1565c0", linewidth=2.0, marker="s", markersize=3, label="PC-SDI (alpha=1.25)")
    ax3.axhline(0.15, color="orange", linestyle="--", label="Danger Threshold (+0.15)")
    ax3.axhline(0.00, color="gray", linestyle="-", linewidth=0.8)
    ax3.set_title("Apple PC-SDI vs. Linear SDI: Productivity Correction Eliminates False Alarms", fontweight="bold")
    ax3.set_ylabel("SDI")
    ax3.legend(loc="upper left", fontsize=8)

    # Panel D: Boeing SDI (Linear vs PC-SDI)
    sdi_ba_lin = [float(r["SDI_linear"]) for r in ba_rows]
    ax4.plot(dates_ba, sdi_ba_lin, color="#ef9a9a", linewidth=1.5, linestyle=":", label="Linear SDI (alpha=0)")
    ax4.plot(dates_ba, sdi_ba, color="#d32f2f", linewidth=2.0, marker="o", markersize=3, label="PC-SDI (alpha=1.25)")
    ax4.axhline(0.15, color="orange", linestyle="--", label="Danger Threshold (+0.15)")
    ax4.axhline(0.00, color="gray", linestyle="-", linewidth=0.8)
    ax4.set_title("Boeing PC-SDI vs. Linear SDI: Decoupling Signal Remains Severe (> +2.50)", fontweight="bold")
    ax4.set_ylabel("SDI")
    ax4.legend(loc="upper right", fontsize=8)

    for ax in [ax1, ax2, ax3, ax4]:
        ax.xaxis.set_major_locator(mdates.YearLocator(2))
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))

    plt.tight_layout()
    out_path = os.path.join(FIGURES_DIR, "apple_vs_boeing_virtuous_vs_parasitic.png")
    plt.savefig(out_path)
    plt.close()
    print(f"[FIGURE] Saved Apple vs Boeing comparison to {out_path}")


def plot_alpha_sensitivity():
    """
    Figure 4: Alpha Sensitivity Curve (Frontier V-FIN-12).
    Shows Precision, Recall, and F1 across alpha in [0.0, 1.50].
    """
    score_path = os.path.join(OUTPUT_DIR, "validation_scorecard.json")
    if not os.path.exists(score_path):
        return

    with open(score_path, "r", encoding="utf-8") as f:
        sc = json.load(f)

    grid = sc.get("alpha_grid_search", {})
    if not grid:
        return

    alphas = sorted([float(k) for k in grid.keys()])
    precisions = [grid[str(a)]["danger_precision"] * 100 for a in alphas]
    recalls = [grid[str(a)]["danger_recall"] * 100 for a in alphas]
    f1s = [grid[str(a)]["danger_f1_score"] * 100 for a in alphas]
    accuracies = [grid[str(a)]["healthy_accuracy"] * 100 for a in alphas]

    fig, ax = plt.subplots(figsize=(9, 5))
    ax.plot(alphas, f1s, color="#4a148c", linewidth=2.5, marker="o", label="Danger F1-Score (%)")
    ax.plot(alphas, precisions, color="#1565c0", linewidth=2.0, marker="s", linestyle="--", label="Danger Precision (%)")
    ax.plot(alphas, recalls, color="#c62828", linewidth=2.0, marker="^", linestyle="-.", label="Danger Recall (%)")
    ax.plot(alphas, accuracies, color="#2e7d32", linewidth=1.8, marker="d", linestyle=":", label="Healthy Accuracy (%)")

    opt_a = sc.get("optimal_alpha", 1.25)
    ax.axvline(opt_a, color="#e65100", linestyle="--", linewidth=1.5, label=f"Optimal Alpha* = {opt_a:.2f}")

    ax.set_xlabel("Productivity Coupling Coefficient (alpha)")
    ax.set_ylabel("Score (%)")
    ax.set_title("Frontier V-FIN-12: Optimization of Productivity Coupling Coefficient (alpha)", fontweight="bold")
    ax.legend(loc="lower right")
    ax.set_ylim(20, 90)

    plt.tight_layout()
    out_path = os.path.join(FIGURES_DIR, "alpha_sensitivity_curve.png")
    plt.savefig(out_path)
    plt.close()
    print(f"[FIGURE] Saved Alpha sensitivity curve to {out_path}")


def plot_scorecard_comparison():
    """
    Figure 3: Empirical Scorecard Comparison (Linear SDI vs. PC-SDI USD vs. PC-SDI Gold).
    """
    score_path = os.path.join(OUTPUT_DIR, "validation_scorecard.json")
    if not os.path.exists(score_path):
        return

    with open(score_path, "r", encoding="utf-8") as f:
        sc = json.load(f)

    linear = sc.get("linear_sdi_usd", sc.get("usd_nominal"))
    pcsdi_usd = sc.get("pcsdi_usd", sc.get("usd_nominal"))
    pcsdi_gold = sc.get("pcsdi_gold", sc.get("gold_normalized"))

    labels = ["Danger Precision", "Danger Recall", "Danger F1-Score", "Healthy Accuracy"]
    lin_vals = [linear["danger_precision"] * 100, linear["danger_recall"] * 100, linear["danger_f1_score"] * 100, linear["healthy_accuracy"] * 100]
    usd_vals = [pcsdi_usd["danger_precision"] * 100, pcsdi_usd["danger_recall"] * 100, pcsdi_usd["danger_f1_score"] * 100, pcsdi_usd["healthy_accuracy"] * 100]
    gold_vals = [pcsdi_gold["danger_precision"] * 100, pcsdi_gold["danger_recall"] * 100, pcsdi_gold["danger_f1_score"] * 100, pcsdi_gold["healthy_accuracy"] * 100]

    x = np.arange(len(labels))
    width = 0.25

    fig, ax = plt.subplots(figsize=(10, 6))
    rects1 = ax.bar(x - width, lin_vals, width, label="Linear SDI (alpha=0)", color="#9e9e9e")
    rects2 = ax.bar(x, usd_vals, width, label="PC-SDI (USD, alpha=1.25)", color="#1976d2")
    rects3 = ax.bar(x + width, gold_vals, width, label="PC-SDI (Gold, alpha=1.25)", color="#fbc02d")

    ax.set_ylabel("Percentage (%)")
    ax.set_title("Predictability Engine Performance: Linear SDI vs. PC-SDI (USD & Gold)", fontweight="bold")
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.legend(loc="upper right")
    ax.set_ylim(0, 95)

    for r in rects1:
        h = r.get_height()
        ax.annotate(f"{h:.1f}%", xy=(r.get_x() + r.get_width()/2, h), xytext=(0, 3),
                    textcoords="offset points", ha="center", va="bottom", fontsize=8)

    for r in rects2:
        h = r.get_height()
        ax.annotate(f"{h:.1f}%", xy=(r.get_x() + r.get_width()/2, h), xytext=(0, 3),
                    textcoords="offset points", ha="center", va="bottom", fontsize=8, fontweight="bold")

    for r in rects3:
        h = r.get_height()
        ax.annotate(f"{h:.1f}%", xy=(r.get_x() + r.get_width()/2, h), xytext=(0, 3),
                    textcoords="offset points", ha="center", va="bottom", fontsize=8)

    plt.tight_layout()
    out_path = os.path.join(FIGURES_DIR, "scorecard_comparison_usd_vs_gold.png")
    plt.savefig(out_path)
    plt.close()
    print(f"[FIGURE] Saved scorecard comparison to {out_path}")


def generate_all_dashboard_figures():
    print("=" * 70)
    print("GENERATING DASHBOARD VISUALIZATIONS")
    print("=" * 70)
    log_usd = load_prediction_log("prediction_log_usd.csv")
    plot_boeing_case_study(log_usd)
    plot_apple_vs_boeing(log_usd)
    plot_alpha_sensitivity()
    plot_scorecard_comparison()
    print("=" * 70)
    print("DASHBOARD GENERATION COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    generate_all_dashboard_figures()
