# Compiled Essay PDFs (Archival Build Snapshots)

**Directory Status:** Archival / Milestone Snapshots  
**Last Updated Date:** **August 19, 2026** (Commit `abd9294`)  
**Canonical Sources of Truth:** Markdown files in `essays/existence/` and `essays/cognitive_social_extensions/`  
**Synchronized LaTeX Sources:** `essays/existence/latex/` (Last updated: **September 8, 2026**)

---

## 1. Discrepancy & Synchronization Notice

> [!WARNING]
> **The PDF files stored in this directory are static build snapshots generated on August 19, 2026.**
> They do **NOT** reflect the significant mathematical, physical, and structural updates committed between August 20, 2026, and September 8, 2026.

### Major Discrepancies Against Current Framework

1. **Tier-1 Physics Framework Missing:** The comprehensive mathematical physics formulation ([tier1_physics_framework.md](../tier1_physics_framework.md)) and its LaTeX counterpart ([tier1_physics_framework.tex](../latex/tier1_physics_framework.tex)) were authored in September 2026 and **have no compiled PDF in this folder**.
2. **Cosmological & Dark Matter Breakthroughs:** Calculations verifying $M_{\text{min}} \approx 10^7\,M_\odot$ halo suppression, cluster concentration modifications ( $c(M, z)$ ), and the Einstein-Cartan bounce primordial perturbation spectra are reflected in the current Markdown and LaTeX files, but are absent from these August 19 PDFs.
3. **Manuscript Refinements (§6.2 Weakness Log & Co-Author Revisions):** The primary manuscript ([draft.md](../draft.md)) has undergone extensive referee review, rigorous boundary closure derivations, and structural reorganization. The bundled `draft.pdf` reflects an earlier, unclosed state.

---

## 2. Repository Policy: Why PDFs Are Not Updated Frequently

PDF files are compiled binary objects ranging between 180 KB and 1.1 MB each. 

* **Git Storage Cost:** Git tracks binary files by storing full compressed snapshots upon every modification rather than text diffs. Committing updated PDFs across iterative commits inflates the `.git` repository size by tens or hundreds of megabytes.
* **Separation of Concerns:** In this repository, **Markdown (`.md`) is the canonical source of truth**, and **LaTeX (`.tex`) is the publication typesetting intermediate**. PDFs are transient or milestone artifacts.
* **Pre-Commit Guard:** To prevent accidental bloat, the repository includes a pre-commit hook that intercepts and blocks staged `.pdf` files unless an explicit milestone bypass flag (`ALLOW_PDF_COMMIT=1`) is supplied.

---

## 3. How to Generate Fresh, Up-to-Date PDFs

Readers and researchers requiring up-to-date PDFs corresponding to the latest Markdown/LaTeX sources can compile them immediately using either of the following two workflows:

### Method A: Zero-Dependency Vector Rendering (Recommended)

The repository provides an automated compiler that utilizes MathJax 3 with full AMS physics extensions paired with any installed Chromium browser (Google Chrome or Microsoft Edge):

```bash
# Compile a specific essay to PDF:
python scripts/generate_pdf.py essays/existence/draft.md

# Compile the newly formulated Tier-1 Physics Framework:
python scripts/generate_pdf.py essays/existence/tier1_physics_framework.md

# Rebuild all repository essays to PDF simultaneously:
python scripts/generate_pdf.py --all
```

*The generated PDFs will be written locally to `essays/existence/pdfs/` with high-resolution vector fonts and selectable mathematics.*

### Method B: Native LaTeX Compilation (`pdflatex` / `latexmk`)

Up-to-date `.tex` source files are maintained in [essays/existence/latex/](../latex/). To compile using your local TeX distribution:

```bash
# Navigate to the LaTeX directory
cd essays/existence/latex

# Compile with pdflatex (run twice to resolve cross-references)
pdflatex draft.tex
pdflatex draft.tex

# Or compile using latexmk with automated bibliography/cross-ref handling
latexmk -pdf draft.tex
```

For full details and Overleaf upload instructions, see [essays/existence/latex/README.md](../latex/README.md).

---

## 4. Current Inventory & Discrepancy Table

| PDF File | Build Snapshot Date | LaTeX Source | Canonical Markdown Source | Sync Discrepancy Level |
| :--- | :--- | :--- | :--- | :--- |
| `draft.pdf` | 2026-08-19 | [draft.tex](../latex/draft.tex) | [draft.md](../draft.md) | **High** (Major physics updates, §6.2 revisions) |
| *(None)* | *Not built* | [tier1_physics_framework.tex](../latex/tier1_physics_framework.tex) | [tier1_physics_framework.md](../tier1_physics_framework.md) | **Critical** (Entire essay missing from PDFs) |
| `interpretation.pdf` | 2026-08-19 | [interpretation.tex](../latex/interpretation.tex) | [interpretation.md](../interpretation.md) | **Moderate** (Updated cross-references) |
| `dialogues_and_explorations.pdf` | 2026-08-19 | [dialogues_and_explorations.tex](../latex/dialogues_and_explorations.tex) | [dialogues_and_explorations.md](../dialogues_and_explorations.md) | **Moderate** (Formatting & citation updates) |
| `core_ontology_and_dharma.pdf` | 2026-08-19 | [core_ontology_and_dharma.tex](../latex/core_ontology_and_dharma.tex) | [interpretations/core_ontology_and_dharma.md](../interpretations/core_ontology_and_dharma.md) | **Low** |
| `cosmology_and_brahmanda.pdf` | 2026-08-19 | [cosmology_and_brahmanda.tex](../latex/cosmology_and_brahmanda.tex) | [interpretations/cosmology_and_brahmanda.md](../interpretations/cosmology_and_brahmanda.md) | **Low** |
| `biophysics_and_syncytia.pdf` | 2026-08-19 | [biophysics_and_syncytia.tex](../latex/biophysics_and_syncytia.tex) | [interpretations/biophysics_and_syncytia.md](../interpretations/biophysics_and_syncytia.md) | **Low** |
| `cognitive_and_psychology.pdf` | 2026-08-19 | [cognitive_and_psychology.tex](../latex/cognitive_and_psychology.tex) | `../../cognitive_social_extensions/cognitive_and_psychology.md` | **Low** (Moved to extensions directory) |
| `societal_and_institutional.pdf` | 2026-08-19 | [societal_and_institutional.tex](../latex/societal_and_institutional.tex) | `../../cognitive_social_extensions/societal_and_institutional.md` | **Low** (Moved to extensions directory) |
