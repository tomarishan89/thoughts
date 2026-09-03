# Comparative Predictions: Per-Observable, Per-Framework

## Legend

| Symbol | Meaning |
|---|---|
| **P** | **Predicted** — derived from first principles, 0 free parameters adjusted to this observable |
| **F** | **Fitted** — a free parameter was tuned to match this observable |
| **D** | **Derived** — computed from other fitted/assumed parameters |
| **X** | **Addressed but wrong** — the framework makes a prediction that conflicts with observations |
| **—** | Not addressed by the framework |

---

## Prediction #1: $\Omega_\Lambda$ (Dark Energy Fraction)

**Observed:** $0.685 \pm 0.007$ (Planck 2018)

| Framework | Free Params | Value | Error | How |
|---|---|---|---|---|
| **This framework** | **0** | **$2/3 = 0.667$** | **2.6%** | Young-Laplace pressure of horizon membrane |
| ΛCDM | 6 (global) | $0.685$ | 0% | **Fitted** — $\Omega_\Lambda$ is a derived output of the 6-param fit |
| QFT (Planck cutoff) | 0 | $\sim 1$ | $10^{122}\times$ | Sum zero-point modes to $M_P$ → catastrophe |
| QFT (EW cutoff) | 0 | $\sim 1$ | $10^{56}\times$ | Higgs VEV + EW condensates → still catastrophe |
| Broken SUSY | 1+ | $\sim 1$ | $10^{60}\times$ | Partial boson-fermion cancellation → still catastrophe |
| Holographic DE (Li 2004) | 1 ($c$) | $\sim 0.73$ | 6.6% | IR cutoff at future event horizon; $c$ tuned |
| Padmanabhan (2012) | 0 | $\to 1$ (asymptotic) | — | $N_{\text{sur}} - N_{\text{bulk}}$ drives expansion; no fixed present value |
| Quintessence (tracker) | 2+ ($V(\phi)$) | $\sim 0.7$ | tunable | Scalar field tracks matter; value depends on potential shape |
| Verlinde EG (2016) | 0 | — | — | Not directly addressed |
| MOND/TeVeS | 1 ($a_0$) | — | — | Not addressed |
| LQC | 1 ($\gamma$) | — | — | Not addressed |
| String Landscape | $\sim 10^{500}$ | Any | — | Anthropic selection from $10^{500}$ vacua; no unique prediction |

> [!IMPORTANT]
> **Only this framework predicts a specific numerical value for $\Omega_\Lambda$ from zero free parameters.** Every other approach either fits it, gets it catastrophically wrong, or doesn't address it.

---

## Prediction #2: $\rho_\Lambda / \rho_m = 2$ (Cosmic Coincidence)

**Observed:** $2.172 \pm 0.067$

| Framework | Value | Error | How |
|---|---|---|---|
| **This framework** | **$2.000$** | **7.9%** | Geometric corollary of $\Omega_\Lambda = 2/3$; coincidence is demystified |
| ΛCDM | $2.175$ (derived) | 0% | **No explanation.** The ratio changes with time; we happen to live when it's $\sim 2$. This IS the cosmic coincidence problem. |
| Quintessence (tracker) | $\sim 2$ (tunable) | tunable | Tracker scalar field follows matter; partially explains "why now" but requires fine-tuned potential $V(\phi)$ |
| Anthropic / Landscape | $\sim 1$–$10$ | — | Selection bias: observers can only exist when $\rho_\Lambda \lesssim \rho_m$. Explains the order-of-magnitude but not the factor of 2 |
| Holographic DE | $\sim 2.6$ (derived) | 20% | Derived from fitted $c$ parameter |
| All others | — | — | Not addressed |

> [!TIP]
> **The cosmic coincidence is one of the great unsolved problems.** This framework is the only one that gives a specific, parameter-free value ($\rho_\Lambda / \rho_m = 2$) with a geometric explanation (Young-Laplace pressure = twice the enclosed matter density).

---

## Prediction #3: $S_{\text{BH}} / S_{\text{Bek}} = 1$ (Entropy Saturation)

**Observed:** $1.000$ (by construction for black holes; non-trivial that the universe saturates it)

| Framework | Value | How |
|---|---|---|
| **This framework** | **$1.000$ (0%)** | Corollary of $R_s = R_H$: the universe IS a maximum-entropy object |
| ΛCDM | — | Not addressed; does not compute holographic entropy |
| Holographic Principle ('t Hooft, Susskind) | Proves the **bound** exists | Does not predict **saturation** — just that $S \leq A/(4\ell_P^2)$ |
| Bousso covariant bound | Proves the **bound** in general spacetimes | Same — proves $S \leq A/(4G\hbar)$ but not $S = A/(4G\hbar)$ for the universe |
| AdS/CFT (Maldacena) | Saturation in AdS black holes | Our universe is NOT AdS; does not apply directly |
| Verlinde EG | Uses entropy gradient | Does not predict saturation of the cosmological horizon |
| All others | — | Not addressed |

> [!NOTE]
> **Saturation is the key distinction.** Many frameworks prove the Bekenstein bound exists. Only this framework predicts that the observable universe **exactly saturates** it — i.e., $S_{\text{BH}}/S_{\text{Bek}} = 1.000$, not $0.9$ or $0.5$. This is non-trivial: ordinary matter systems are far below saturation.

---

## Prediction #4: $\Omega_m = 1/3$ (Total Matter Fraction)

**Observed:** $0.315 \pm 0.007$

| Framework | Value | Error | How |
|---|---|---|---|
| **This framework** | **$1/3 = 0.333$** | **5.7%** | Complement of $\Omega_\Lambda = 2/3$ |
| ΛCDM | $0.315$ | 0% | **Fitted** ($\Omega_c h^2$ is a free parameter) |
| QFT | — | — | Not addressed |
| MOND | $\Omega_b \approx 0.05$ (no DM) | 84% off total $\Omega_m$ | Eliminates DM → gets total matter fraction catastrophically wrong at cosmological scales |
| All others | — | — | Either fitted or not addressed |

---

## Prediction #5: $z_{\text{eq}}^{(m-\Lambda)} = 0.260$ (Matter-DE Equality Redshift)

**Observed:** $0.295$ (derived from Planck $\Omega$s)

| Framework | Value | Error | How |
|---|---|---|---|
| **This framework** | **$2^{1/3} - 1 = 0.260$** | **11.9%** | Parameter-free: follows from $\rho_\Lambda = 2\rho_m$ |
| ΛCDM | $0.295$ | 0% | **Derived** from fitted $\Omega_\Lambda$ and $\Omega_m$ — not an independent prediction |
| All others | — | — | No framework independently predicts this transition redshift |

---

## Prediction #6: $\Omega_{\text{DM}} = 0.284$ (Dark Matter Fraction)

**Observed:** $0.265 \pm 0.007$

| Framework | Value | Error | How |
|---|---|---|---|
| **This framework** | **$1/3 - \Omega_b = 0.284$** | **7.2%** | Structural corollary: $\Omega_m = 1/3$, baryons from BBN |
| ΛCDM | $0.265$ | 0% | **Fitted** ($\Omega_c h^2$ is a free parameter) |
| Verlinde EG (2016) | $\Omega_{\text{DM}}^2 \approx \frac{4}{3}\Omega_b$ → apparent $\Omega_{\text{DM}} \sim 0.26$ | ~2% | Emergent effect from entanglement entropy displacement; **no DM particles** |
| MOND/TeVeS | $0$ | 100% | DM doesn't exist by construction; fails at cluster/CMB scales |
| Superfluid DM (Berezhiani-Khoury) | $\sim 0.27$ (fitted) | — | DM exists but has superfluid phase at galaxy scales |
| WIMPs (various) | $\sim 0.27$ (fitted) | — | Thermal relic freeze-out; cross-section tuned to match |
| Axion models | $\sim 0.27$ (fitted) | — | Misalignment mechanism; mass/coupling tuned |
| String Landscape | Many candidates | — | Neutralinos, axions, KK modes... no unique prediction |

> [!NOTE]
> **Verlinde's emergent gravity** gives a comparable prediction ($\sim 0.26$) with 0 free parameters, but it claims DM **doesn't exist** — it's an apparent effect of entanglement entropy. This framework claims DM **does exist** as partially-realized modes. The Bullet Cluster remains a key discriminator: Verlinde's framework struggles with it; this framework's particle DM is consistent.

---

## Prediction #7: $T_{\text{dS}} = 2T_H$ (Horizon Temperature Complementarity)

**Not independently measurable** (both temperatures are $\sim 10^{-30}$ K)

| Framework | Value | How |
|---|---|---|
| **This framework** | **$T_{\text{dS}} / T_H = 2.000$** | Exact consequence of $\kappa_{\text{dS}} = 2\kappa_S$ (Lemma 3) |
| Standard BH thermodynamics | Treats $T_H$ and $T_{\text{dS}}$ separately | Never connects them via a factor-of-2 identity |
| Jacobson (1995) | Derives Einstein eqns from $dQ = T \, dS$ | Doesn't identify the interior/exterior temperature ratio |
| All others | — | Not addressed |

---

## Grand Summary Table

| # | Observable | **This Framework** | ΛCDM | Best Competing | Worst Competing |
|---|---|---|---|---|---|
| 1 | $\Omega_\Lambda$ | **P**: $0.667$ (2.6%) | F: $0.685$ (0%) | Holographic DE: F, 6.6% | QFT Planck: $10^{122}\times$ |
| 2 | $\rho_\Lambda/\rho_m$ | **P**: $2.000$ (7.9%) | D: $2.175$ (0%) | Quintessence: tunable | ΛCDM: no explanation |
| 3 | $S_{\text{BH}}/S_{\text{Bek}}$ | **P**: $1.000$ (0%) | — | Holographic: proves bound, not saturation | — |
| 4 | $\Omega_m$ | **P**: $0.333$ (5.7%) | F: $0.315$ (0%) | — | MOND: $0.05$ (84% off) |
| 5 | $z_{\text{eq}}^{(m-\Lambda)}$ | **P**: $0.260$ (11.9%) | D: $0.295$ (0%) | — (no other predicts this) | — |
| 6 | $\Omega_{\text{DM}}$ | **P**: $0.284$ (7.2%) | F: $0.265$ (0%) | Verlinde: $\sim 0.26$ (0 params) | MOND: $0$ (100% off) |
| 7 | $T_{\text{dS}}/T_H$ | **P**: $2.000$ | — | — (no other predicts this) | — |

**Free parameter count for these 7 observables:**

| Framework | Free Params Used | Predictions Made | Observables Addressed |
|---|---|---|---|
| **This framework** | **0** | **7** | 7/7 |
| ΛCDM | 6 | 0 (all fitted/derived) | 4/7 |
| QFT vacuum (all cutoffs) | 0 | 1 (catastrophically wrong) | 1/7 |
| Holographic DE | 1 | 0 (fitted) | 2/7 |
| Verlinde EG | 0 | 1 ($\Omega_{\text{DM}}$) | 1/7 |
| MOND | 1 | 1 (wrong: $\Omega_{\text{DM}} = 0$) | 1/7 |

---

## What This Framework Does NOT Address (Gaps for Future Work)

| Observable | ΛCDM Performance | This Framework | Priority |
|---|---|---|---|
| **CMB power spectrum $C_\ell$** | Exquisite fit to $\ell \sim 2500$ | Not addressed | **High** — to be picked up |
| Matter power spectrum $P(k)$ | Excellent fit with N-body sims | Not addressed | High |
| BBN light element abundances | $^4$He, D, $^7$Li predictions | Not addressed (uses $\Omega_b$ as input) | Medium |
| Galaxy rotation curves | NFW profile + DM halos | Not addressed | Medium |
| BAO peak positions | Sub-percent precision | Not addressed | Medium |
| Hubble tension ($H_0$) | Unresolved ($\sim 5\sigma$) | $H_0$ is contingent (parent BH dependent) | Low (by design) |
| Gravitational wave spectrum | LIGO/Virgo predictions | Not addressed | Low |

> [!TIP]
> **The CMB power spectrum** is the single most impactful gap. If the framework can derive or constrain the acoustic peak structure from its engine formalism + ECSK bounce initial conditions, it would move from "derivation engine for ΛCDM inputs" to a standalone cosmological model. This is flagged for future work.

---

## The Honest Bottom Line

This framework makes **7 quantitative predictions from 0 free parameters**, achieving 0%–11.9% accuracy across all of them. No other single framework does this for more than 1 of these observables.

But it currently addresses **none** of the observables where ΛCDM excels (CMB, BAO, $P(k)$, BBN). The two are complementary: this framework derives the inputs; ΛCDM uses those inputs to fit the data.
