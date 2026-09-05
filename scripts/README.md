# Vidyaman Scripts Directory

This directory houses two complementary suites of tools:
1. **Theoretical Derivation & Numerical Simulation Scripts (`*.py`)**: First-principles physical computations, cosmological models, and observational confrontation scripts developed during manuscript verification.
2. **Repository Toolchain & Automation Scripts**: Markdown sanitization, LaTeX conversion, MathJax PDF generation, and git hook infrastructure.

---

## 1. Theoretical Physics & Numerical Computations

These 13 scripts formulate and evaluate the framework's mathematical proofs, physical conservation bounds, and observational predictions against empirical data (Planck 2018, GWTC-3/5.0, CODATA 2018).

| Script | Issue / Section | Core Physics / Equations | Primary Output | Dependencies |
|---|---|---|---|---|
| [derive_lambda.py](derive_lambda.py) | §6.7.2 / Lemma 3 | $\kappa_{\text{dS}} = 2\kappa_S$, geometric holographic bound $\Omega_\Lambda = 2/3$ | $\Omega_\Lambda = 0.6667$ vs $0.6847$ ( -2.6% ) | `math` |
| [derive_parent_bh.py](derive_parent_bh.py) | §6.7.1 / Prediction #2 | Non-circular forward propagation: initial bounce conditions $\rho_P \to$ parent black hole mass | $M_H \approx 3.2 \times 10^{22}\,M_\odot$, $R_H \approx 13.8\text{ Gly}$ | `math` |
| [derive_baryon_density.py](derive_baryon_density.py) | ISSUE-4.59 / §6.8.4 | ECSK Hehl-Datta four-fermion torsion interaction, $\varepsilon_{CP}(T) = \frac{3\pi}{2}(T/M_P)^2$, Sakharov conditions | $\eta = 6.104 \times 10^{-10}$, $\Omega_b h^2 = 0.02228$ ( -0.40% ) | `numpy`, `matplotlib` |
| [cmb_comparison.py](cmb_comparison.py) | ISSUE-4.57 / §6.9.6 | Boltzmann solver (CAMB) for CMB $TT$ power spectrum with $\Omega_\Lambda=2/3$, $\Omega_m=1/3$, borrowed $\Omega_b$ | Acoustic peaks $\ell_1, \ell_2, \ell_3$; RMS residual $4.01\%$ | `numpy`, `scipy`, `matplotlib`, `camb` |
| [cmb_v2_comparison.py](cmb_v2_comparison.py) | ISSUE-4.57 / §6.9.6 | CMB $TT$ comparison with framework-derived $\Omega_b h^2 = 0.02228$ from torsion baryogenesis | Direct comparison: v1 ( $4.01\%$ ) vs v2 ( $3.98\%$ RMS residual ) | `numpy`, `scipy`, `matplotlib`, `camb` |
| [bh_echo_prediction.py](bh_echo_prediction.py) | ISSUE-4.60 / §6.10 | Post-merger gravitational wave echoes from Planck bounce surface: $\Delta t_{\text{echo}} = \frac{4GM}{c^3}\ln(\frac{2GM}{c^2 \ell_P})$ | $\Delta t_{30M_\odot} = 54.10\text{ ms}$, $A_1/A_0 = 8.34 \times 10^{-5}$ | `numpy`, `matplotlib` |
| [echo_confrontation.py](echo_confrontation.py) | ISSUE-4.63 / §6.10.3 | Confrontation with LVK GWTC-3/5.0 coherentWaveBurst searches; SNR stacking requirements | Current upper limits ( $h_{\text{rss}} \sim 10^{-23}$ ) vs predicted ( $10^{-25}$ ); 10,000 events | `numpy` |
| [primordial_spectrum.py](primordial_spectrum.py) | ISSUE-4.58 / §6.11 | Mukhanov-Sasaki curvature perturbations through ECSK torsion bounce; slow-roll trajectory | $n_s = 0.9667$, $r = 0.0031$ | `numpy` |
| [cmb_temperature.py](cmb_temperature.py) | ISSUE-4.53 / §6.12 | $T_{\text{CMB}}$ as cosmic engine exhaust: entropy conservation from $\eta$ and $\Omega_b$ | $T_{\text{CMB}} = 2.7228\text{ K}$ vs $2.7255\text{ K}$ ( -0.10% ) | `numpy`, `scipy` |
| [test_theorem11.py](test_theorem11.py) | ISSUE-4.52 / §6.7.7 | Theorem 11 ( $T_{\text{dS}} = 2T_H$ ) and parent black hole evaporation timescale | Evaporation timescale $t_{\text{evap}} \sim 10^{135}\text{ yr}$, $S_{\text{BH}}/k_B \sim 10^{122}$ | `math` |
| [verify_lambda_strengthening.py](verify_lambda_strengthening.py) | §6.7.2 / Lemma 3 | Kodama-Hayward surface gravity on FRW apparent horizon vs de Sitter Gibbons-Hawking | $\kappa_{\text{dS}}/\kappa_S = 2.000000$, $\Omega_\Lambda = 2/3$ bounds | `math` |
| [test_session_aug28.py](test_session_aug28.py) | §6.7 & §6.8 | Comprehensive regression test suite for Session Aug 28 derivations (bounce, horizon, entropy) | 48 unit tests covering early framework milestones | `math` |
| [test_session_aug31.py](test_session_aug31.py) | §2.4, §6.7, §6.8 | Extended regression test suite for Session Aug 31 (Influence Field $\psi$, Theorem 9, Theorem 10) | 56 unit tests verifying ontology-physics bridge | `math` |

---

## 2. Notebook Conversion Roadmap (`.ipynb` Planning)

The scripts are structured modularly to allow direct conversion into interactive Jupyter Notebooks. The proposed notebook architecture maps the problem domains as follows:

```
notebooks/
├── 01_cosmological_constant_and_horizons.ipynb   (from derive_lambda.py, verify_lambda_strengthening.py, test_theorem11.py)
├── 02_ecsk_torsion_baryogenesis.ipynb           (from derive_baryon_density.py)
├── 03_cmb_boltzmann_acoustic_peaks.ipynb        (from cmb_comparison.py, cmb_v2_comparison.py)
├── 04_primordial_perturbations_ns_r.ipynb       (from primordial_spectrum.py)
├── 05_black_hole_gw_echoes_lvk.ipynb           (from bh_echo_prediction.py, echo_confrontation.py)
├── 06_engine_thermodynamics_t_cmb.ipynb         (from cmb_temperature.py, derive_parent_bh.py)
└── 07_framework_full_regression_suite.ipynb     (from test_session_aug28.py, test_session_aug31.py)
```

### Standard Cell-by-Cell Structure for Each Notebook
1. **Markdown Cell: Mathematical Physics Context**: Formal statement of the theorem/prediction, citations (Planck 2018, Hehl-Datta 1971, Poplawski 2010), and LaTeX equations.
2. **Code Cell: Fundamental Constants & Parameters**: SI & natural units with exact CODATA 2018 / Planck 2018 constants.
3. **Code Cell: Analytic/Numerical Model**: Execution of differential equations, integrals, or CAMB Boltzmann codes.
4. **Code Cell: Interactive Visualizations**: Matplotlib plots showing parameter scans, residuals, and observational exclusion bounds.
5. **Markdown Cell: Confrontation & Falsifiability Analysis**: Comparison against experimental bounds and explicit criteria for theoretical falsification.

---

## 3. Running the Computation Scripts

All scripts can be executed directly from the repository root:

```bash
# Run baryon density derivation
python scripts/derive_baryon_density.py

# Run CMB power spectrum comparison (requires CAMB)
python scripts/cmb_v2_comparison.py

# Run black hole echo spectrum and generate plots
python scripts/bh_echo_prediction.py

# Run full cosmological temperature derivation
python scripts/cmb_temperature.py

# Run regression test suites
python scripts/test_theorem11.py
python scripts/test_session_aug31.py
```

### Environment Variables
- `OUTPUT_DIR`: Specify directory where output plots (`*.png`) are saved. Defaults to the directory containing the script (`scripts/`).
  ```bash
  OUTPUT_DIR=plots python scripts/bh_echo_prediction.py
  ```

---

## 4. Repository Toolchain & Markdown/LaTeX Automation

The repository also includes 23 maintenance and publishing utilities:

- **`generate_pdf.py`**: Compiles publication-grade PDFs of the essays using headless Chromium and MathJax 3 with custom academic typography.
- **`md_to_latex.py`**: Transpiles GitHub-Flavored Markdown essays into LaTeX documents for arXiv/journal submission.
- **`lint_markdown.py`**: Validates Markdown files for broken cross-links, unwrapped LaTeX formulas, unescaped characters, and GFM math collisions.
- **`pipeline.py`**: Multi-stage documentation workflow manager.
- **`sanitize_math.py`**, **`harden_gfm_math.py`**: Fixes common formatting issues in mathematical notation.
- **`install_git_hooks.py`**: Configures `.git/hooks/pre-commit` to prevent committing invalid LaTeX or broken links.
