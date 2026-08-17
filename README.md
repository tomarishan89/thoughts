# Vidyaman Research & Essay Workspace

A multi-disciplinary research and writing workspace integrating **continuum mechanics, non-equilibrium thermodynamics, information theory, and classical Sanskrit ontology** with a structured multi-stage compilation pipeline.

---

## 🧠 Interactive Research with Google NotebookLM

This repository supports deep, interactive conversational analysis via Google NotebookLM grounded directly in the formal manuscripts and research corpora:

| Scope | Target | NotebookLM Access Link | Description |
| :--- | :--- | :--- | :--- |
| **Existence Manuscript** | [`essays/existence/draft.md`](essays/existence/draft.md) | [**Open NotebookLM (draft.md)**](https://notebook.google.com/notebook/05af9f0d-d66d-4333-bb98-75a7afb13f1f) | Dedicated interactive model grounded strictly in the full mathematical physics paper (*A Continuum-Mechanical and Non-Equilibrium Thermodynamic Framework of Physical and Biological Existence*). |
| **Existence Corpus Suite** | [`essays/existence/`](essays/existence/) | *`[Link Pending / Update with Folder URL]`* | Comprehensive interactive model spanning all 10 corpus files (foundational theory, entropy dynamics, multi-scale cases, issues log, and exploratory dialogues). |

---

## 📂 Repository Structure

```
Project_writeup_1/
├── essays/
│   ├── existence/               # Continuum-Mechanical & Thermodynamic Existence Framework
│   │   ├── README.md            # Detailed corpus guide and file map
│   │   ├── draft.md             # Flagship mathematical physics manuscript
│   │   ├── issues_log.md        # Mathematical milestones & active research frontier log
│   │   ├── base.md              # Deconstructing Sanatan Dharm (set-theoretic baseline)
│   │   ├── cases_appendix.md    # Multi-scale boundary applications (quantum to institutional)
│   │   ├── entropy.md           # Non-equilibrium thermodynamics & dissipation metrics
│   │   ├── interpretation.md    # Sanskrit ontological mapping (dhṛ, māyā, karma, prāṇa)
│   │   ├── dialogues_and_explorations.md # Adversarial debates & thought experiments
│   │   ├── post_convergence_agenda.md    # Long-term research directions
│   │   ├── review.md            # Peer-review critiques & defense notes
│   │   └── rough.md             # Scratchpad & early ideation
│   └── interospection_01/       # Staged essay on Kuṇḍalinī darśana, Māyā, & Pāṇinian analysis
├── lexicons/                    # Glossaries & terminology controls
│   ├── glossary.md              # Master glossary of Sanskrit roots & roman keys
│   └── allowlist.md             # Allowed terms and canonical spellings
├── references/                  # Pāṇinian grammar notes and citation aids
│   └── panini-notes.md
├── scripts/                     # Toolchain for glossary expansion and pipeline automation
│   ├── pipeline.py              # Lifecycle management (rough → draft → stage → output)
│   ├── expand_sa.py             # Sanskrit markup compiler (\sa{key} → Devanagari)
│   ├── glossary_add.py          # Interactive glossary entry generator
│   └── build_sa_completions.py  # Cursor IDE autocomplete generator
└── .agents/                     # Strict agent reviewer personas & audit protocols
```

---

## 🔬 Key Research Areas

### 1. Unified Field Theory of Existence (`essays/existence/`)
Formalizes physical, biological, and institutional persistence through rigorous mathematical physics:
* **Lorentzian Spacetime & State Space:** $4$D pseudo-Riemannian manifold $(\mathcal{M}, g_{\mu\nu})$ and complexified state manifold $\Omega_{\mathbb{C}} \cong \mathbb{R}^3 \oplus i\mathbb{R}^3$ with canonical Kähler volume measure $d\mu_h$.
* **Boundary Dynamics:** Relativistic Lorentz-bounded level-set propagation ($\|\mathbf{v}_n\| < c$) and equipotential structural margin $\phi(x, t) = 0$.
* **Thermodynamics & Information Erasure:** Non-equilibrium entropy production ($\sigma_S \ge 0$), Onsager reciprocity, and Landauer erasure dissipation bounds.
* **Sanskrit Ontological Deconstruction:** Resolving the Category Error Paradox and defining *Dharm* from the Sanskrit root $\sqrt{\text{dhṛ}}$ as the functional boundary condition upholding systemic extent against external challenge.

### 2. Pāṇinian Morphological Analysis (`essays/interospection_01/`, `lexicons/`)
Deep etymological and grammatical unpacking of core philosophical terms (*māyā*, *mokṣa*, *manas*, *dharm*) via direct Pāṇinian dhātu rules.

---

## 🛠️ Staged Writing Pipeline

The repository uses a staged lifecycle for text containing Sanskrit markup:

```
rough.md (\sa{}) ───► draft.md (Compiled) ───► stage.md (Critical Edit) ───► output.md (Final)
```

| File | Stage Role |
| :--- | :--- |
| `rough.md` | Freeform writing with Sanskrit shorthand markers: `\sa{key}` or `\sa{key = देव}` |
| `draft.md` | Compiled prose with Devanagari and transliteration expanded |
| `stage.md` | Critical editorial review; serves as the canonical content-of-record once created |
| `output.md` | Publication-ready release |

### Toolchain CLI Commands

```bash
# Check pipeline status for an essay
python scripts/pipeline.py status essays/interospection_01

# Compile rough markup to draft
python scripts/pipeline.py promote-draft essays/interospection_01

# Advance to critical editing stage
python scripts/pipeline.py new-stage essays/interospection_01

# Check key validity against the master glossary
python scripts/pipeline.py check-keys essays/interospection_01 --source rough

# Add a new term to the master lexicon
python scripts/glossary_add.py --key atman --dev आत्मन् --iast ātman --gloss "self" --dhatu "√an"

# Rebuild Cursor IDE autocompletions for \sa{}
python scripts/build_sa_completions.py
```

---

## 🖋️ Editor Integration

* **Obsidian:** This root directory is an Obsidian vault. Open this folder in Obsidian (`.obsidian/` configuration included).
* **Cursor / VS Code:** Native syntax support, Python compilation scripts, and snippet triggers (`sa-dharma` → `\sa{dharma}`).
