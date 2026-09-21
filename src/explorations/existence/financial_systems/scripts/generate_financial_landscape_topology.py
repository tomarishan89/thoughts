#!/usr/bin/env python3
"""
generate_financial_landscape_topology.py
-----------------------------------------
Computes and renders the 2D Financial Potential Landscape and Corporate Trajectories
derived from the Screened Poisson Field Equation:
  (\\nabla^2 - \\xi_Au^{-2}) \\Phi_fin = -4\\pi G_Au \\rho_capital

Outputs:
  1. financial_potential_landscape_tranquil_vs_crisis.png
  2. corporate_trajectories_on_landscape.png
  3. effective_potential_radial_and_phase_portrait.png
"""

import sys
import os
import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors

# Ensure UTF-8 output
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

ARTIFACT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CACHE_FILE = os.path.join(ARTIFACT_DIR, "scratch", "financial_data_cache.json")

# Sector color map and market cap weights (in Trillions USD, representative 2024-2026)
SECTOR_INFO = {
    'AAPL': {'sector': 'Tech',       'color': '#00d2ff', 'mass': 3.2},
    'MSFT': {'sector': 'Tech',       'color': '#0099ff', 'mass': 3.1},
    'JPM':  {'sector': 'Finance',    'color': '#ffb703', 'mass': 0.65},
    'BAC':  {'sector': 'Finance',    'color': '#fb8500', 'mass': 0.35},
    'XOM':  {'sector': 'Energy',     'color': '#d62828', 'mass': 0.48},
    'CVX':  {'sector': 'Energy',     'color': '#e63946', 'mass': 0.28},
    'GE':   {'sector': 'Industrial', 'color': '#a8dadc', 'mass': 0.20},
    'CAT':  {'sector': 'Industrial', 'color': '#457b9d', 'mass': 0.18},
    'WMT':  {'sector': 'Staples',    'color': '#2a9d8f', 'mass': 0.62},
    'PG':   {'sector': 'Staples',    'color': '#588157', 'mass': 0.38}
}

def load_and_embed():
    with open(CACHE_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
    dates = sorted(list(set.intersection(*[set(data[k].keys()) for k in data.keys()])))
    firms = [k for k in data.keys() if k not in ('GOLD', 'SP500')]
    N = len(firms)

    # Returns matrix
    rets = np.column_stack([
        np.log(np.array([data[f][d] for d in dates[1:]]) / np.array([data[f][d] for d in dates[:-1]]))
        for f in firms
    ])

    # Full sample correlation & Mantegna distance
    corr_full = np.corrcoef(rets, rowvar=False)
    D_full = np.sqrt(np.maximum(0, 2 * (1 - corr_full)))

    # Classical MDS embedding
    H = np.eye(N) - np.ones((N, N)) / N
    K_full = -0.5 * H @ (D_full**2) @ H
    vals, vecs = np.linalg.eigh(K_full)
    idx = np.argsort(vals)[::-1]
    X_ref = vecs[:, idx[:2]] * np.sqrt(np.maximum(0, vals[idx[:2]]))

    # Rolling trajectories with Procrustes alignment
    w = 250
    step = 40
    traj = {f: [] for f in firms}
    traj_dates = []

    for t in range(w, len(dates)-1, step):
        sub_r = rets[t-w:t, :]
        c_mat = np.corrcoef(sub_r, rowvar=False)
        D_sub = np.sqrt(np.maximum(0, 2 * (1 - c_mat)))
        K_sub = -0.5 * H @ (D_sub**2) @ H
        v, u = np.linalg.eigh(K_sub)
        i_s = np.argsort(v)[::-1]
        X_sub = u[:, i_s[:2]] * np.sqrt(np.maximum(0, v[i_s[:2]]))
        
        # Procrustes alignment
        U_p, _, Vt_p = np.linalg.svd(X_sub.T @ X_ref)
        R_opt = U_p @ Vt_p
        X_aligned = X_sub @ R_opt
        
        traj_dates.append(dates[t])
        for i, f in enumerate(firms):
            traj[f].append(X_aligned[i].tolist())

    return firms, X_ref, traj, traj_dates, data, dates

def compute_potential_field(X_firms, masses, xi, G, grid_res=200, extent=(-1.0, 0.8, -0.9, 0.8)):
    x = np.linspace(extent[0], extent[1], grid_res)
    y = np.linspace(extent[2], extent[3], grid_res)
    XX, YY = np.meshgrid(x, y)
    Phi = np.zeros_like(XX)
    softening = 0.08  # Plummer core radius

    for i in range(len(masses)):
        xf, yf = X_firms[i]
        r = np.sqrt((XX - xf)**2 + (YY - yf)**2 + softening**2)
        Phi += - G * masses[i] * np.exp(-r / xi) / r

    # Compute gradient field (Force = - grad Phi)
    dPhi_dy, dPhi_dx = np.gradient(Phi, y[1]-y[0], x[1]-x[0])
    Fx = -dPhi_dx
    Fy = -dPhi_dy

    return XX, YY, Phi, Fx, Fy

def render_figure_1(firms, X_ref):
    """Figure 1: Tranquil vs. Crisis Financial Potential Landscape."""
    masses = [SECTOR_INFO[f]['mass'] for f in firms]
    
    # Tranquil: Low Gold vol -> High G, long screening length xi
    XX, YY, Phi_tranquil, Fx_t, Fy_t = compute_potential_field(X_ref, masses, xi=3.0, G=1.0)
    
    # Crisis: High Gold vol -> Reduced G, short screening length xi
    _, _, Phi_crisis, Fx_c, Fy_c = compute_potential_field(X_ref, masses, xi=0.35, G=0.6)

    fig, axes = plt.subplots(1, 2, figsize=(18, 8), facecolor='#0d1117')
    
    titles = [
        "A. Tranquil Regime (Low Gold Volatility, $\\sigma_{\\mathrm{Au}} = 10\\%$\nScreening Length $\\xi = 3.0$: Global Gravitational Coupling",
        "B. Crisis Regime (Spiking Gold Volatility, $\\sigma_{\\mathrm{Au}} = 35\\%$\nScreening Length $\\xi = 0.35$: Decoupled Localized Wells"
    ]
    fields = [(Phi_tranquil, Fx_t, Fy_t), (Phi_crisis, Fx_c, Fy_c)]

    for ax, title, (Phi, Fx, Fy) in zip(axes, titles, fields):
        ax.set_facecolor('#0d1117')
        # Equipotential contour fill
        levels = np.linspace(np.min(Phi_tranquil), np.max(Phi_crisis) + 0.5, 40)
        cf = ax.contourf(XX, YY, Phi, levels=levels, cmap='plasma', alpha=0.85)
        cs = ax.contour(XX, YY, Phi, levels=15, colors='#ffffff', alpha=0.25, linewidths=0.7)
        
        # Streamlines / vector arrows
        skip = (slice(None, None, 12), slice(None, None, 12))
        ax.quiver(XX[skip], YY[skip], Fx[skip], Fy[skip], color='#ffffff', alpha=0.4, scale=40, width=0.003)

        # Plot corporate entities
        for i, f in enumerate(firms):
            xf, yf = X_ref[i]
            color = SECTOR_INFO[f]['color']
            m = SECTOR_INFO[f]['mass']
            size = 80 + m * 55
            ax.scatter(xf, yf, s=size, color=color, edgecolors='#ffffff', linewidth=1.5, zorder=5)
            # Label
            offset_y = 0.045 if yf > 0 else -0.055
            ax.text(xf, yf + offset_y, f, color='#ffffff', fontsize=10, fontweight='bold',
                    ha='center', va='center', zorder=6,
                    bbox=dict(boxstyle='round,pad=0.2', facecolor='#161b22', edgecolor=color, alpha=0.85))

        ax.set_title(title, color='#ffffff', fontsize=12, pad=12, fontweight='bold')
        ax.set_xlabel("MDS Correlation Dimension 1 ($x$)", color='#8b949e', fontsize=10)
        ax.set_ylabel("MDS Correlation Dimension 2 ($y$)", color='#8b949e', fontsize=10)
        ax.tick_params(colors='#8b949e')
        for spine in ax.spines.values():
            spine.set_color('#30363d')
        ax.grid(True, color='#21262d', linestyle='--', alpha=0.5)

    cbar_ax = fig.add_axes([0.92, 0.15, 0.015, 0.7])
    cbar = fig.colorbar(cf, cax=cbar_ax)
    cbar.set_label("Financial Potential $\\Phi_{\\mathrm{fin}}(\\mathbf{x})$ [Gravitational Attraction]", color='#ffffff', fontsize=10)
    cbar.ax.tick_params(colors='#8b949e')

    out_path = os.path.join(ARTIFACT_DIR, "financial_potential_landscape_tranquil_vs_crisis.png")
    plt.savefig(out_path, dpi=200, bbox_inches='tight', facecolor='#0d1117')
    plt.close()
    print(f"[RENDER] Saved Figure 1: {out_path}")

def render_figure_2(firms, X_ref, traj, traj_dates):
    """Figure 2: Corporate Historical Trajectories (2017-2026) Across the Landscape."""
    masses = [SECTOR_INFO[f]['mass'] for f in firms]
    XX, YY, Phi_base, _, _ = compute_potential_field(X_ref, masses, xi=1.8, G=0.9)

    fig, ax = plt.subplots(figsize=(12, 10), facecolor='#0d1117')
    ax.set_facecolor('#0d1117')

    # Background potential contours
    ax.contourf(XX, YY, Phi_base, levels=30, cmap='inferno', alpha=0.6)
    ax.contour(XX, YY, Phi_base, levels=12, colors='#ffffff', alpha=0.15, linewidths=0.6)

    # Plot trajectories
    for f in firms:
        pts = np.array(traj[f])
        color = SECTOR_INFO[f]['color']
        
        # Trajectory line
        ax.plot(pts[:, 0], pts[:, 1], color=color, linewidth=2.0, alpha=0.85, zorder=4)
        
        # Start marker (circle) & End marker (star)
        ax.scatter(pts[0, 0], pts[0, 1], s=40, color=color, marker='o', edgecolors='#ffffff', zorder=5)
        ax.scatter(pts[-1, 0], pts[-1, 1], s=120, color=color, marker='*', edgecolors='#ffffff', linewidth=1.2, zorder=6)
        
        # Label at endpoint
        ax.text(pts[-1, 0] + 0.03, pts[-1, 1] + 0.02, f, color='#ffffff', fontsize=9, fontweight='bold',
                bbox=dict(boxstyle='round,pad=0.2', facecolor='#161b22', edgecolor=color, alpha=0.85), zorder=7)

    # Highlight GE restructure and Energy cycle
    ax.annotate("GE Restructuring & Turnaround\n(Migrating out of debt basin into Aero)", 
                xy=(traj['GE'][-1][0], traj['GE'][-1][1]), xytext=(-0.35, 0.72),
                arrowprops=dict(facecolor='#a8dadc', shrink=0.08, width=1.5, headwidth=6),
                color='#a8dadc', fontsize=9, fontweight='bold', bbox=dict(boxstyle='round', facecolor='#161b22', edgecolor='#a8dadc'))

    ax.annotate("Energy Commodity Cycle\n(2020 Oil Shock -> 2022 Inflation Surge)", 
                xy=(traj['XOM'][-1][0], traj['XOM'][-1][1]), xytext=(0.15, -0.75),
                arrowprops=dict(facecolor='#e63946', shrink=0.08, width=1.5, headwidth=6),
                color='#e63946', fontsize=9, fontweight='bold', bbox=dict(boxstyle='round', facecolor='#161b22', edgecolor='#e63946'))

    ax.set_title("Corporate Geodesics on the Financial Potential Landscape (2017–2026)\n"
                 "Trajectories in Correlation Metric Space $\\mathbf{x}(\\tau)$ [Circle = 2017, Star = 2026]",
                 color='#ffffff', fontsize=13, pad=15, fontweight='bold')
    ax.set_xlabel("MDS Correlation Coordinate 1 ($x$)", color='#8b949e', fontsize=11)
    ax.set_ylabel("MDS Correlation Coordinate 2 ($y$)", color='#8b949e', fontsize=11)
    ax.tick_params(colors='#8b949e')
    for spine in ax.spines.values():
        spine.set_color('#30363d')
    ax.grid(True, color='#21262d', linestyle='--', alpha=0.4)

    out_path = os.path.join(ARTIFACT_DIR, "corporate_trajectories_on_landscape.png")
    plt.savefig(out_path, dpi=200, bbox_inches='tight', facecolor='#0d1117')
    plt.close()
    print(f"[RENDER] Saved Figure 2: {out_path}")

def render_figure_3(firms, X_ref):
    """Figure 3: Radial Screened Potential Well and Corporate Phase Portrait."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(18, 7), facecolor='#0d1117')

    # Subplot 1: Radial Screened Yukawa Potential Profiles
    r = np.linspace(0.01, 1.8, 300)
    G = 1.0
    M_tech = 3.2 # AAPL
    soft = 0.08

    xi_values = [3.0, 1.2, 0.6, 0.3]
    labels = [
        "$\\xi = 3.0$ (Tranquil Market, $\\sigma_{\\mathrm{Au}} = 8\\%$)",
        "$\\xi = 1.2$ (Normal Regime, $\\sigma_{\\mathrm{Au}} = 14\\%$)",
        "$\\xi = 0.6$ (Elevated Stress, $\\sigma_{\\mathrm{Au}} = 22\\%$)",
        "$\\xi = 0.3$ (Severe Crisis / Gold Spike, $\\sigma_{\\mathrm{Au}} = 38\\%$)"
    ]
    colors = ['#00d2ff', '#2a9d8f', '#f4a261', '#e76f51']

    ax1.set_facecolor('#0d1117')
    for xi, label, col in zip(xi_values, labels, colors):
        phi_r = - G * M_tech * np.exp(-r / xi) / np.sqrt(r**2 + soft**2)
        ax1.plot(r, phi_r, color=col, linewidth=2.5, label=label)

    # Screening horizon mark
    ax1.axvline(0.3, color='#e76f51', linestyle=':', alpha=0.7)
    ax1.text(0.32, -18, "Crisis Horizon $r \\approx \\xi_{\\mathrm{crisis}}$\n(Coupling cuts off)", color='#e76f51', fontsize=9)

    ax1.set_title("A. Radial Potential Well $\\Phi(r)$ Sourced by Mega-Cap Platform\nModulated by Gold Volatility Screening $\\xi(\\sigma_{\\mathrm{Au}})$", 
                  color='#ffffff', fontsize=11, fontweight='bold', pad=12)
    ax1.set_xlabel("Metric Distance from Mega-Cap Core $r = \\|\\mathbf{x} - \\mathbf{x}_{\\mathrm{tech}}\\|$", color='#8b949e', fontsize=10)
    ax1.set_ylabel("Gravitational Potential $\\Phi(r)$", color='#8b949e', fontsize=10)
    ax1.legend(facecolor='#161b22', edgecolor='#30363d', labelcolor='#ffffff', fontsize=9)
    ax1.tick_params(colors='#8b949e')
    ax1.grid(True, color='#21262d', linestyle='--', alpha=0.4)
    for spine in ax1.spines.values():
        spine.set_color('#30363d')

    # Subplot 2: Phase Portrait (Valuation Velocity dV/dtau vs Gap Acceleration)
    ax2.set_facecolor('#0d1117')
    
    # Load prices to compute real phase portrait
    with open(CACHE_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
    dates = sorted(list(set.intersection(*[set(data[k].keys()) for k in data.keys()])))
    
    # Compute 60-day velocity (1st diff) and 60-day acceleration (2nd diff) of normalized price
    for f in ['AAPL', 'JPM', 'GE', 'XOM', 'WMT']:
        p = np.array([data[f][d] for d in dates])
        p_norm = p / p[0]
        # Smooth with 30-day convolution
        p_smooth = np.convolve(p_norm, np.ones(30)/30, mode='valid')
        # Velocity and Acceleration
        vel = np.gradient(p_smooth) * 252.0 # Annualized velocity
        acc = np.gradient(vel) * 252.0       # Annualized acceleration
        
        color = SECTOR_INFO[f]['color']
        ax2.plot(p_smooth[::20], vel[::20], color=color, alpha=0.7, linewidth=1.5, label=f"{f} ({SECTOR_INFO[f]['sector']})")
        ax2.scatter(p_smooth[-1], vel[-1], color=color, s=80, marker='*', edgecolors='#ffffff', zorder=5)

    ax2.set_title("B. Corporate Phase Portrait: Valuation Rate $\\dot{V}$ vs State $V$\nShowing Limit Cycles and Expansion Geodesics", 
                  color='#ffffff', fontsize=11, fontweight='bold', pad=12)
    ax2.set_xlabel("Normalized Valuation State $V(\\tau) / V_0$", color='#8b949e', fontsize=10)
    ax2.set_ylabel("Valuation Velocity $\\dot{V}(\\tau)$ [Annualized]", color='#8b949e', fontsize=10)
    ax2.legend(facecolor='#161b22', edgecolor='#30363d', labelcolor='#ffffff', fontsize=9)
    ax2.tick_params(colors='#8b949e')
    ax2.grid(True, color='#21262d', linestyle='--', alpha=0.4)
    for spine in ax2.spines.values():
        spine.set_color('#30363d')

    out_path = os.path.join(ARTIFACT_DIR, "effective_potential_radial_and_phase_portrait.png")
    plt.savefig(out_path, dpi=200, bbox_inches='tight', facecolor='#0d1117')
    plt.close()
    print(f"[RENDER] Saved Figure 3: {out_path}")

def main():
    firms, X_ref, traj, traj_dates, data, dates = load_and_embed()
    render_figure_1(firms, X_ref)
    render_figure_2(firms, X_ref, traj, traj_dates)
    render_figure_3(firms, X_ref)
    print("[SUCCESS] All 3 landscape visualization figures successfully generated.")

if __name__ == '__main__':
    main()
