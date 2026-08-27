import re

def main():
    with open('essays/existence/draft.md', 'r', encoding='utf-8') as f:
        text = f.read()

    sec7_marker = '## Section 7: Discussion — Cosmological Scale and Philosophical Correspondences'
    ref_marker = '## References'

    parts_before_7 = text.split(sec7_marker)
    tier1_body = parts_before_7[0].strip()

    sec7_and_refs = parts_before_7[1]
    parts_7_ref = sec7_and_refs.split(ref_marker)
    tier2_body = parts_7_ref[0].strip()
    refs = '## References\n\n' + parts_7_ref[1].strip()

    tier1_abstract_note = """
> **Note on Mathematical and Physical Nomenclature:** In this framework, "Real Space" ($\Omega_{\\mathbb{R}}$) denotes the spatial support of localized physical mass-energy and stress tensors, while "Imaginary Space" ($\Omega_{\\mathfrak{Im}}$) denotes the formal information-theoretic Hilbert/state space of internal carrier ledgers, gauge projections, predictive models, and sub-ego representations. It carries strictly physical and thermodynamic meaning (Landauer dissipation, Bekenstein-Hawking horizon capacity, Shannon-von Neumann entropy) with zero metaphysical connotation.
"""

    # Insert note after Executive overview or title
    tier1_lines = tier1_body.split('\n')
    # Find after title or executive overview
    tier1_custom_body = tier1_body

    sec64_addition = """

### 6.4 Cosmological Horizon Limits, Hierarchical Nesting, and Holographic Consistency

Extending the framework's Bekenstein-bounded thermodynamic ledger recursively to cosmological horizons yields a natural black-hole interior embedding without requiring metaphysical assumptions. In standard FLRW cosmology, the observable universe is bounded by a cosmological horizon $R_{\\text{Hubble}} \\approx c/H_0$ with Bekenstein-Hawking entropy $S_{\\text{max}}(\\mathcal{D}_T) = \\frac{|\\partial \\mathcal{D}_T| c^3}{4 G \\hbar \\ln 2} \\approx 10^{122} \\text{ bits}$.

**Theorem (Hierarchical Nesting, Nesting Map, and Holographic Consistency):** Let $\\mathcal{L} = \\{L_0, L_1, \\ldots, L_n\\}$ be a finite hierarchy of entity levels where $L_0 = \\Omega_\\mathbb{R}^{\\text{cosmos}}$ is the physical vacuum (ground floor) and entities at level $L_{i+1}$ are bounded systems embedded in the state space of level $L_i$.

1. **The Nesting Map ($\\iota_i$):**
For any adjacent levels $L_i$ and $L_{i+1}$, the embedding of the child state space $\\Omega_\\mathbb{C}^{L_{i+1}}$ into the structured carrier ledger $\\Omega_{\\mathfrak{Im}}^{L_i}$ of the parent entity is given by an injective, measure-preserving map:
$$\\boxed{\\iota_i: \\Omega_\\mathbb{C}^{L_{i+1}} \\hookrightarrow \\Omega_{\\mathfrak{Im}}^{L_i}}$$
such that the child real space $\\Omega_\\mathbb{R}^{L_{i+1}}$ is physically realized as a structured relational sub-configuration within the parent's internal state space.

2. **Information Monotonicity & Bekenstein Capacity Hierarchy:**
At each nesting transition $L_i \\to L_{i+1}$, the maximum information capacity of the child is strictly bounded by the Bekenstein-Hawking area entropy of the enclosing parent boundary horizon:
$$\\boxed{S_{\\text{max}}(\\Omega_\\mathbb{C}^{L_{i+1}}) \\le S_{\\text{BH}}(L_{i+1}) \\equiv \\frac{c_{i+1}^3 \\cdot \\mathrm{Area}(\\partial \\Omega_\\mathbb{R}^{L_{i+1}})}{4 G_{i+1} \\hbar_{i+1} \\ln 2} \\le S_{\\text{max}}(\\Omega_\\mathbb{C}^{L_i})}$$
Since $\\partial \\Omega_\\mathbb{R}^{L_{i+1}} \\subset \\Omega^{L_i}$, the hierarchy exhibits strict monotonic capacity contraction: $S_{\\text{BH}}^{(i+1)} < S_{\\text{BH}}^{(i)}$, terminating unconditionally at the cosmological ground floor $L_0$.

3. **Holographic Consistency Condition Across Nesting Levels:**
Let $\\ell_P^{(i)} \\equiv \\sqrt{\\frac{G_i \\hbar_i}{c_i^3}}$ denote the Planck length at level $L_i$.
- From the interior observer frame at level $L_{i+1}$: $\\mathcal{N}_{\\text{inside}}^{(i+1)} \\equiv \\frac{\\mathrm{Area}(\\partial \\Omega_\\mathbb{R}^{L_{i+1}})}{4 (\\ell_P^{(i+1)})^2 \\ln 2}$.
- From the parent exterior frame at level $L_i$: $\\mathcal{N}_{\\text{outside}}^{(i)} \\equiv \\frac{\\mathrm{Area}(\\partial \\Omega_\\mathbb{R}^{L_{i+1}})}{4 (\\ell_P^{(i)})^2 \\ln 2}$.
Holographic consistency requires $\\mathcal{N}_{\\text{inside}}^{(i+1)} \\le \\mathcal{N}_{\\text{outside}}^{(i)}$. If fundamental dimensionless coupling parameters drift across levels ($\\ell_P^{(i+1)} \\neq \\ell_P^{(i)}$), the horizon scaling must satisfy the **Holographic Compensation Inequality**:
$$\\boxed{\\frac{\\mathrm{Area}^{(i+1)}}{\\mathrm{Area}^{(i)}} \\le \\left(\\frac{\\ell_P^{(i+1)}}{\\ell_P^{(i)}}\\right)^2}$$

4. **Observational Status of Physical Constants & The Cosmological Constant:**
- *Empirical Invariance within Level $L_0$:* High-precision astrophysical observations of quasar absorption spectra and molecular transitions constrain variations of fundamental dimensionless constants across cosmological lookback times ($z \\sim 0.89 - 3$):
$$|\\Delta \\alpha / \\alpha| < 10^{-6}, \\quad |\\Delta \\mu / \\mu| < 10^{-7} \\quad (\\mu \\equiv m_p / m_e), \\quad |\\dot{G}/G| < 10^{-12} \\text{ yr}^{-1}$$
No empirical drift in dimensionless physical constants is detected within the observable domain of our level.
- *The Cosmological Constant Anomaly ($\\Lambda \\approx 10^{-120} M_P^4$):* In the black-hole universe / torsion cosmology framework (Popławski 2010; Smolin 1992), $\\Lambda$ is not an unconstrained local vacuum expectation value, but an **effective boundary curvature** inherited from the parent horizon parameters during gravitational bounce into the child manifold $\\Omega_\\mathbb{C}^{L_{i+1}}$.

5. **Epistemological Closure (Interior Observer Axiom):**
From within $\\Omega_\\mathbb{C}^{L_i}$, an interior observer lacks an external reference frame and cannot determine whether $\\Omega_\\mathbb{R}^{L_i}$ is the cosmological ground floor $L_0$ or the carrier space $\Omega_{\\mathfrak{Im}}^{L_{i-1}}$ of an enclosing parent entity. The framework is strictly epistemologically closed and well-founded.
"""

    tier1_content = tier1_body + sec64_addition + '\n\n---\n\n' + refs

    with open('essays/existence/tier1_physics_framework.md', 'w', encoding='utf-8') as f:
        f.write(tier1_content)

    tier2_header = """# Cosmological Scale, Universal Consciousness Identity, and Ontological Correspondences
*Extension of the Continuum-Mechanical and Thermodynamic Ledger Framework to Universal Scales and Philosophical Ontologies*

---

> **Preamble & Foundational Context:** This treatise provides the cosmological, philosophical, and ontological extensions of the mathematical physics framework established in [`tier1_physics_framework.md`](./tier1_physics_framework.md). The preceding work rigorously establishes the non-equilibrium thermodynamics, continuum mechanics, Lie algebra operator structures, and Bekenstein information bounds for physical (Tier I) and biological/cognitive (Tier II) entities. Here, we analyze the recursive application of these theorems to the cosmological horizon $\\mathcal{D}_T$, exploring universal consciousness identity, the thermodynamics of cosmic negentropy, and the formal isomorphism with the classical ontology of Advaita Vedanta (Sanatan Dharm).

---

"""
    tier2_content = tier2_header + sec7_marker + '\n\n' + tier2_body + '\n\n---\n\n' + refs

    with open('essays/existence/tier2_cosmological_ontology.md', 'w', encoding='utf-8') as f:
        f.write(tier2_content)

    print("SUCCESS: Created tier1_physics_framework.md and tier2_cosmological_ontology.md")

if __name__ == '__main__':
    main()
