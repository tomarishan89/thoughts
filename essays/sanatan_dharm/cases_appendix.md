# Sandboxed Applied Test Cases: Framework Coverage

> **Editorial Note:** This file is strictly separated from the core axiomatic manuscript (`draft.md`). The following are **applied test cases** — empirical instantiations of the framework defined therein. They are not part of the core iterative development loop. Weaknesses discovered in test cases are logged here and promoted to `draft.md` Section 6 only if they expose a flaw in the core mathematical machinery (not merely in the approximations used to apply it).

---

## Case 1: The Star (Tier I Physical Engine)

### Framework Mapping

| Framework Primitive | Physical Instantiation |
| :--- | :--- |
| $E^i(t) = \langle D_{\mathfrak{Im}}^i, \mathcal{F}_{\mathbb{R}}^i \rangle$ | $D_{\mathfrak{Im}}^i =$ nuclear force laws (gravity + strong force); $\mathcal{F}_{\mathbb{R}}^i =$ plasma mass-energy |
| Front $f_k(t)$: zero-level set of $\phi_k = \|\mathbf{R}_k\| - \|\mathbf{C}_k\|$ | Stellar surface: hydrostatic equilibrium locus where radiation pressure $=$ gravitational compression |
| Challenge $\mathbf{C}_k$ | Gravitational self-compression: $\mathbf{C}_k = -\frac{Gm(r)}{r^2}\hat{r}$ |
| Resistance $\mathbf{R}_k$ | Radiation + thermal pressure: $\mathbf{R}_k = \nabla P_{\text{thermal}} + \nabla P_{\text{rad}}$ |
| Engine Cycle $\mathcal{E}^i$ | Fuel intake: H/He nuclear fuel; Conversion: $\mathcal{O}_k =$ nuclear fusion chain; Entropy rejection: photon emission ($\mathbf{J}_S = \mathbf{J}_{\text{photon}}$); Work output: $\dot{W} = L_{\odot}$ (stellar luminosity) |
| Viscosity $\nu_{\text{field}}$ | Radiation viscosity: $\nu_{\text{rad}} = \frac{4 a T^4}{15 c \kappa \rho}$ (radiation pressure tensor contribution) |
| Engine Efficiency $\eta$ | $\eta_{\odot} \approx 0.007$ (0.7% mass-energy conversion in H-burning); bounded by Curzon-Ahlborn: $\eta \le 1 - \sqrt{T_C/T_H}$ |
| Collapse Condition | Main sequence fuel exhaustion: $\mathcal{F}_{\text{fuel}} \to 0 \implies \mathbf{R}_k \to 0 \implies \phi_k < 0$ universally $\implies$ Front collapse |

### Prigogine Stability Ratio
$$\Lambda^{\odot} = \frac{\dot{S}_{\text{gen}}}{\dot{S}_{\text{export}}} = \frac{\dot{S}_{\text{nuclear}} + \dot{S}_{\text{viscous}}}{L_\odot / T_{\text{surface}}} \approx 1 \quad (\text{main sequence NESS})$$

The star operates at the NESS attractor ($\Lambda = 1$) during the main sequence. As hydrogen depletes, $\dot{S}_{\text{gen}}$ falls while $\dot{S}_{\text{export}}$ lags, driving $\Lambda < 1$ and triggering bifurcation into the red giant phase (Prigogine dissipative restructuring).

### Case-Specific Vulnerabilities
- **V-C1.1:** Rotation and magnetic fields generate anisotropic Maxwell Stress Tensor contributions to $\nu_{\text{field}}$ that are not captured by the scalar damping coefficient $\gamma_k$. The framework requires a tensorial generalization: $\gamma_k \to \boldsymbol{\nu}_{\text{field}}$ (full viscosity tensor).
- **V-C1.2:** The core-envelope interface during red giant evolution is a *moving* level-set front. The Hamilton-Jacobi PDE (SS1.2) requires boundary conditions at an internal rather than external interface. The framework's PDE may need extension to handle internal fronts.

---

## Case 2: The Atom (Tier I -- Tier II Boundary)

### Framework Mapping

| Framework Primitive | Physical Instantiation |
| :--- | :--- |
| $E^i(t)$ | Atom: nucleus ($\mathcal{F}_{\mathbb{R}}^{\text{nucleus}}$) + electron cloud ($\mathcal{F}_{\mathbb{R}}^{\text{electrons}}$) |
| $D_{\mathfrak{Im}}^i$ | Quantum mechanical operators: Hamiltonian $\hat{H}$, angular momentum $\hat{L}$, spin $\hat{S}$ |
| Front $f_k(t)$ | Electron orbital shell boundary: $\phi_k = |\psi(r)|^2 - \rho_{\text{threshold}} = 0$ (probability density level-set) |
| Challenge $\mathbf{C}_k$ | Ionizing radiation, external electric field perturbation |
| Resistance $\mathbf{R}_k$ | Coulomb binding energy; orbital wavefunction coherence |
| Viscosity $\nu_{\text{field}}$ | Electron-electron correlation energy via EM stress tensor: $\nu_{\text{field}} = \frac{1}{Vk_BT}\int_0^\infty \langle T_{xy}^{\text{EM}}(0)T_{xy}^{\text{EM}}(\tau)\rangle d\tau$ |
| Engine Cycle | No thermodynamic engine in ground state (Tier I): $\dot{W} = 0$, $\mathbf{J}_S = 0$. Energy exchange only during photon emission/absorption |

### Imaginary Plane Note
The Dharmic operators $D_{\mathfrak{Im}}^i = \{\hat{H}, \hat{L}, \hat{S}\}$ reside in the imaginary subspace $i\Omega_{\mathbb{R}}$ as Hermitian operators on complex Hilbert space. The atom is the prototype Physical Carrier Projection Axiom instance: the abstract operator $\hat{H}$ is instantiated on the physical nuclear-electron configuration $\mathcal{F}_{\text{ledger}}^{\text{atom}} =$ spatial wavefunction amplitude.

### Case-Specific Vulnerabilities
- **V-C2.1 (Promote Candidate):** Quantum mechanics operates on a complex Hilbert space $\mathcal{H}$ fundamentally distinct from the complexified classical manifold $\Omega_{\mathbb{C}} = \Omega_{\mathbb{R}} \oplus i\Omega_{\mathbb{R}}$. The mapping $\hat{H} \in D_{\mathfrak{Im}}^i$ is suggestive but not formally proven. A rigorous isomorphism between the framework's imaginary subspace and quantum Hilbert space must be established before this case achieves mathematical closure.
- **V-C2.2:** Quantum entanglement creates non-local correlations across spatially separated entities. The framework's definition of $E^i$ as a *bounded subset* of $\Omega$ with $\partial E^i \neq \emptyset$ may be incompatible with non-local entangled states.

---

## Case 3: The Car Engine (Tier I Physical Engine, Engineered)

### Framework Mapping

| Framework Primitive | Physical Instantiation |
| :--- | :--- |
| $E^i(t)$ | Car engine: $D_{\mathfrak{Im}}^i =$ thermodynamic cycle laws (Otto/Diesel); $\mathcal{F}_{\mathbb{R}}^i =$ mechanical components + fuel |
| Front $f_k$ | Piston-cylinder interface: mechanical compression boundary |
| Challenge $\mathbf{C}_k$ | Atmospheric backpressure + mechanical load |
| Resistance $\mathbf{R}_k$ | Combustion expansion pressure |
| Engine Cycle $\mathcal{E}^i$ | Intake (fuel-air): $\mathbf{J}_{\text{fuel}}$; Compression: adiabatic $\mathcal{O}_k$; Combustion: conversion; Exhaust: $\mathbf{J}_S =$ hot exhaust gas |
| Efficiency | Otto: $\eta_{\text{Otto}} = 1 - r_c^{1-\gamma} \le 1 - \sqrt{T_C/T_H}$ (Curzon-Ahlborn at max power) |
| Viscosity | Oil film: $\gamma_k = \nu_{\text{oil}} \cdot A_{\text{piston}} / h_{\text{film}}$ |

### Collapse Conditions
Fuel cutoff ($\mathbf{J}_{\text{fuel}} \to 0$): Engine stalls. Lubrication failure ($\nu_{\text{oil}} \to 0$): $Re \to Re_{\text{critical}}$ at piston face, causing catastrophic metal contact (boundary shatter via turbulence constraint, SS2.4).

### Case-Specific Vulnerabilities
- **V-C3.1 (Promote Candidate):** The car engine is a Tier I entity with an external Tier III designer ($\mathcal{P}^{\text{engineer}} \neq \emptyset$). The framework must distinguish *endogenous* operators (self-generated by entity) from *exogenously imposed* operators (projected by an external existence). An engineered entity's $D_{\mathfrak{Im}}$ is not self-generated but is a projection from an external Tier III existence. This is an unresolved category in the taxonomy.

---

## Case 4: The Biological Cell (Tier II Biological Engine)

### Framework Mapping

| Framework Primitive | Physical Instantiation |
| :--- | :--- |
| $E^i(t) = \langle D_{\mathfrak{Im}}^i, \mathcal{F}_{\mathbb{R}}^i \rangle$ | $D_{\mathfrak{Im}}^i =$ genetic regulatory network (encoded in $\mathcal{F}_{\text{ledger}}^{\text{DNA}}$); $\mathcal{F}_{\mathbb{R}}^i =$ cytoplasm, organelles, membrane lipids |
| Front $f_k$ | Plasma membrane: $\phi_k = V_{\text{membrane}} - \Pi_{\text{osmotic}} = 0$ |
| Challenge $\mathbf{C}_k$ | Osmotic pressure, pathogen attack, reactive oxygen species |
| Resistance $\mathbf{R}_k$ | Cytoskeletal tension, immune response, membrane potential |
| Engine Cycle | Oxidative phosphorylation: glucose $\to$ ATP $\to$ transmembrane ion pump work |
| Entropy Rejection $\mathbf{J}_S$ | Heat + metabolic waste (CO$_2$, H$_2$O, lactate) across membrane |
| Landauer Maintenance | DNA repair: $\dot{E}_{\text{maint}} \ge k_B T \ln 2 \cdot \dot{\mathcal{H}}_{\text{ledger}}^-$ |
| $\Lambda^{\text{cell}}$ | $\approx 1$ during homeostasis; apoptosis = programmed $\Lambda \gg 1$ bifurcation |

### Physical Carrier Projection Axiom -- Prototype Instance
$$D_{\mathfrak{Im}}^{\text{cell}} = \pi_{\mathfrak{Im}}(\mathcal{F}_{\text{ledger}}^{\text{DNA}}) \implies \text{genome destruction} \implies D_{\mathfrak{Im}} = \emptyset \implies \text{algorithmic paralysis}$$

### State-Trace Functional Applied: DNA as Viscoelastic Existence (§1.4 Instantiation)

The biological cell is the canonical applied prototype for the State-Trace Functional ($\Psi$, §1.4). The DNA molecule constitutes the ledger substrate $\mathcal{F}_{\text{ledger}}^{\text{DNA}} \subset \mathcal{F}_{\mathbb{R}}^{\text{cell}}$.

**Framework Mapping for State-Trace:**

| State-Trace Component | DNA/Cell Instantiation |
| :--- | :--- |
| Material substrate $\mathcal{F}_{\mathbb{R}}^i$ | Nucleotide polymer chain in cytoplasm ($\nu \gg 0$, $Re \ll 1$ at molecular scale) |
| Imaginary operator $D_{\mathfrak{Im}}^i = \pi_{\mathfrak{Im}}(\mathcal{F}_{\text{ledger}}^i)$ | Genetic regulatory operators encoded in DNA base sequence |
| Operations $\mathcal{O}_k(\tau)$ | Transcription, replication fork, UV damage, methyltransferase — each imposes a deformation on $E^{\text{DNA}}$ |
| Physical state trace | DNA sequence + methylation pattern + histone modification + chromatin conformation + telomere length |
| Memory kernel $G_k(t-\tau)$ | Epigenetic fidelity: recent methylation events dominate; ancient replication errors decay at rate $1/\tau_{\text{relax}}^{\text{DNA}}$ |

**State-Trace Equation for DNA:**
$$E^{\text{DNA}}(t) = \Psi\Big[E^{\text{DNA}}(0);\; \mathcal{O}^{\text{transcription}},\; \mathcal{O}^{\text{methylation}},\; \mathcal{O}^{\text{replication}},\; \ldots\Big]_0^t$$

The current genome state is not merely its base sequence — it is the complete path-history-encoded molecular configuration. What the DNA *is* now is the cumulative resultant of every operation performed upon it.

**Reversibility Demonstration (Yamanaka 2006):** Epigenetic reprogramming via defined transcription factors (Oct4, Sox2, Klf4, c-Myc) partially reverses the state-trace functional — re-inducing pluripotency by undoing the differentiation operations $\mathcal{O}_k^{\text{differentiation}}$. This is empirical evidence of state-trace traversal in reverse within the Stokes-flow regime ($Re \ll 1$ at cellular molecular scale).

**Ledger Hierarchy (from V-C4.1):** The complete cell ledger is hierarchical:
$$\mathcal{F}_{\text{ledger}}^{\text{cell}} = \mathcal{F}_{\text{ledger}}^{\text{DNA}} \cup \mathcal{F}_{\text{ledger}}^{\text{epigenetic}} \cup \mathcal{F}_{\text{ledger}}^{\text{chromatin}} \cup \ldots$$
Each level carries a distinct $G_k(t-\tau)$ with distinct $\tau_{\text{relax}}$: DNA sequence changes at evolutionary timescale ($\tau_{\text{relax}} \sim 10^9$ years), histone modifications at developmental timescale ($\tau_{\text{relax}} \sim$ hours–years), RNA expression at metabolic timescale ($\tau_{\text{relax}} \sim$ minutes).

### Case-Specific Vulnerabilities
- **V-C4.1:** Epigenetic operators modify gene expression without altering the DNA ledger sequence. The Physical Carrier Projection Axiom maps $D_{\mathfrak{Im}} \leftrightarrow \mathcal{F}_{\text{ledger}}^{\text{DNA}}$, but epigenetic modifications constitute additional operators $D_{\mathfrak{Im}}^{\text{epigenetic}}$ encoded in chromatin configuration $\mathcal{F}_{\text{ledger}}^{\text{chromatin}}$. The framework must accommodate a **hierarchical ledger**: $\mathcal{F}_{\text{ledger}} = \mathcal{F}_{\text{ledger}}^{\text{DNA}} \cup \mathcal{F}_{\text{ledger}}^{\text{epigenetic}} \cup \ldots$
- **V-C4.2:** The memory kernel $G_k^{\text{DNA}}(t-\tau)$ for epigenetic modifications spans multiple biological timescales. The single Maxwell-model form $G_0 e^{-(t-\tau)/\tau_{\text{relax}}}$ cannot accommodate this multi-scale structure without a sum of exponentials (generalized Maxwell model): $G_k = \sum_j G_j e^{-(t-\tau)/\tau_j}$. The number of Maxwell elements $j$ is unspecified — a free parameter.


---

## Case 5: The Universe as a Form of Existence (Cosmological Limit)

> **Status:** Exploratory. Mathematical closure is partial. See vulnerabilities below.

### Hypothesis
The Universe $\mathcal{U}$ is modeled as a Form of Existence $E^{\mathcal{U}}(t)$ with:
- $\mathcal{F}_{\mathbb{R}}^{\mathcal{U}} =$ all mass-energy within the cosmological horizon $R_H = c/H_0$
- $D_{\mathfrak{Im}}^{\mathcal{U}} =$ physical laws (Standard Model, General Relativity), mathematical constants
- Front $f^{\mathcal{U}}(t)$ = cosmological horizon (Hubble sphere): $\phi = R_H - r = 0$

### Black Hole Universe Sub-Hypothesis
$$R_H = \frac{c}{H_0} \approx 1.3 \times 10^{26} \text{ m} \approx \frac{2G M_{\text{observable}}}{c^2} = R_S$$

At critical cosmological density, the Hubble radius equals the Schwarzschild radius. This equivalence (Pathria 1972; Smolin 1992; Popławski 2010) maps:

| BHU Concept | Framework Mapping |
| :--- | :--- |
| Cosmological horizon as causal boundary | Front $f^{\mathcal{U}}$: level-set of causal connectivity |
| Dark energy ($\rho_\Lambda$) | Challenge $\mathbf{C}^{\mathcal{U}}$: accelerating horizon expansion |
| Gravitational self-binding | Resistance $\mathbf{R}^{\mathcal{U}}$: gravitational potential energy opposing dispersal |
| Hawking radiation at horizon | Entropy rejection $\mathbf{J}_S$: $T_H = \frac{\hbar c^3}{8\pi G M k_B}$ |
| Big Bang | Engine ignition: fuel intake onset |
| Heat death / Big Rip | Collapse condition: $\phi^{\mathcal{U}} < 0$ universally |

### Challenge as Gravity -- Reaction Space
Per session submission: *"In the Reaction Space, Challenge is exerted by Existence over other existence (fuel). Hence Challenge can be defined as a component of this engine when defining a front."*

Instantiation: The Universe (as $E^{\mathcal{U}}$) exerts gravitational challenge $\mathbf{C}_k = -\frac{Gm}{r^2}\hat{r}$ upon all sub-entities (stellar fuel). Sub-entities resist with internal pressure (stellar $\mathbf{R}_k$), with the zero-level set of $\phi_k$ defining each stellar surface. Stars are fuel entities consumed by the Universe-engine's gravitational challenge field. Each star's entropy rejection flux (photon emission) constitutes the Universe-engine's outward entropy export $\mathbf{J}_S^{\mathcal{U}}$.

### Entropy Dynamics
The Bekenstein-Hawking horizon entropy:
$$S_{\mathcal{U}} = \frac{k_B c^3 A_H}{4 G \hbar}, \quad A_H = 4\pi R_H^2$$
As $R_H$ grows (dark energy), $S_{\mathcal{U}}$ increases monotonically. Consistent with the framework: dissolution of sub-entities ($\phi < 0$) and subsequent spreading of their microstates into $\Omega$ maximizes $S_{\mathcal{U}}$.

### Prigogine Stability
$$\Lambda^{\mathcal{U}} = \frac{\dot{S}_{\text{gen}}^{\text{stellar}} + \dot{S}_{\text{gen}}^{\text{BH formation}}}{\dot{S}_{\text{Hawking radiation}}} \gg 1$$

**The Universe is not at NESS. It is in sustained entropic explosion.** This is not a framework failure: it correctly predicts the cosmological arrow of time. It implies the Universe as $E^{\mathcal{U}}$ is a *decaying, non-stable* existence trending toward heat death (global equilibrium).

### Case-Specific Vulnerabilities
- **V-C5.1 (Critical -- Promote Candidate):** The Physical Carrier Projection Axiom requires $D_{\mathfrak{Im}}^{\mathcal{U}} = \pi_{\mathfrak{Im}}(\mathcal{F}_{\text{ledger}}^{\mathcal{U}})$. Physical laws as imaginary operators must be encoded in a real physical ledger. The holographic principle (Bekenstein bound) suggests all physical information within $R_H$ is encoded on the 2D horizon surface. The isomorphism between horizon surface $\mathcal{F}_{\text{ledger}}^{\mathcal{U}}$ and physical laws $D_{\mathfrak{Im}}^{\mathcal{U}}$ is not formally established. This is an unpublishable gap.
- **V-C5.2:** For the Universe, there is no external heat bath $T_{\text{ambient}}$ to receive entropy. Hawking temperature $T_H \sim 10^{-30}$ K at cosmological scale makes entropy export effectively zero while $\dot{S}_{\text{gen}}$ is enormous. The framework's entropy rejection inequality $\int_{\partial E^i}\mathbf{J}_S \cdot \hat{n}\,dA \ge \dot{S}_{\text{gen}}$ is violated for the Universe as a whole. This is consistent with $\Lambda^{\mathcal{U}} \gg 1$: the Universe is NOT a sustainable dissipative structure.
- **V-C5.3:** Popławski's torsion mechanism avoids the Big Bang singularity but requires the level-set PDE to remain well-defined at Planck density. Near Planck density, spacetime topology is uncertain, and the manifold $\mathcal{M}$ may be ill-defined. The Hamilton-Jacobi PDE requires a well-defined smooth manifold.

---

## Cross-Case Summary Table

| Case | Tier | $\Lambda^i$ at steady state | Primary Failure Mode | Core Vulnerability Exposed |
| :--- | :--- | :--- | :--- | :--- |
| Star | I | $\approx 1$ (main sequence NESS) | Fuel exhaustion $\to$ Tier drop / bifurcation | Tensorial $\boldsymbol{\nu}_{\text{field}}$ needed for anisotropic cases |
| Atom | I | $0$ (ground state) | Ionization: Challenge $>$ Resistance | Hilbert space vs $\Omega_{\mathbb{C}}$ mapping unproven |
| Car Engine | I (engineered) | $\approx 1$ (throttle NESS) | Fuel cutoff / lubrication failure | Exogenous vs endogenous $D_{\mathfrak{Im}}$ undistinguished |
| Cell | II | $\approx 1$ (homeostasis) | Substrate starvation / DNA damage | Hierarchical ledger structure required |
| Universe | I (cosmological) | $\gg 1$ (entropic explosion) | Heat death (no external bath) | Holographic $D_{\mathfrak{Im}}$ projection unproven |

---

*Last updated: 2026-08-14. Promote candidates: V-C2.1 (Hilbert space isomorphism) and V-C5.1 (holographic ledger projection) pending sufficient mathematical development in the core manuscript.*
