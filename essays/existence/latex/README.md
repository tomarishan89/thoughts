# Synchronized LaTeX Essay Sources

**Directory Status:** Active & Synchronized  
**Last Updated Date:** **September 8, 2026**  
**Generator Script:** `scripts/md_to_latex.py`  
**Canonical Sources of Truth:** Markdown files in `essays/existence/` and `essays/cognitive_social_extensions/`  
**Archival PDF Snapshots:** `essays/existence/pdfs/` (Last updated: **August 19, 2026**)

---

## 1. Synchronization & Discrepancy Notice

All LaTeX (`.tex`) files in this directory are fully up to date as of **September 8, 2026**. 

### Checking Discrepancies Against `essays/existence/pdfs/`

| Metric / Attribute | LaTeX Directory (`latex/`) | PDF Directory (`pdfs/`) |
| :--- | :--- | :--- |
| **Last Updated Date** | **September 8, 2026** | **August 19, 2026** |
| **Status** | Active, up-to-date mathematical source | Archival milestone build snapshot |
| **Tier-1 Physics Framework** | **Present** (`tier1_physics_framework.tex`) | **Absent** (Not compiled in PDFs) |
| **Thermodynamic Boundary Closure** | **Present** (§6.2 resolutions, flux limits) | **Absent** (Pre-closure formulation) |
| **Cosmology & Dark Matter Cutoffs** | **Present** ( $M_{\text{min}} \sim 10^7 M_\odot$, $c(M, z)$ ) | **Absent** (Pre-CAMB / baseline state) |
| **Git Tracking Impact** | Text files; lightweight diffs | Large binary files (~3.8 MB snapshot) |

Readers or reviewers comparing the compiled PDF (`pdfs/draft.pdf`) against `draft.tex` will notice substantial analytical additions in Section 6.2 (Weakness Log), improved notation, and the complete addition of the Tier-1 Physics Framework.

---

## 2. Instructions: Compiling PDFs from LaTeX Sources

### Option A: Local TeX Distribution (`pdflatex` or `latexmk`)

Ensure you have a TeX distribution installed (e.g., TeX Live, MiKTeX, or MacTeX).

1. Open your terminal and navigate to this directory:
   ```bash
   cd essays/existence/latex
   ```

2. Compile individual documents using `pdflatex`:
   ```bash
   # Run twice to resolve hyperref links, table of contents, and cross-references:
   pdflatex draft.tex
   pdflatex draft.tex
   ```

3. Alternatively, use `latexmk` for automatic multi-pass compilation:
   ```bash
   latexmk -pdf draft.tex
   latexmk -pdf tier1_physics_framework.tex
   ```

4. Batch compile all LaTeX files (PowerShell):
   ```powershell
   Get-ChildItem *.tex | ForEach-Object {
       pdflatex -interaction=nonstopmode $_.Name
       pdflatex -interaction=nonstopmode $_.Name
   }
   ```

5. Clean up auxiliary files (`.aux`, `.log`, `.out`):
   ```bash
   # Linux / macOS / Git Bash:
   rm -f *.aux *.log *.out *.toc *.fls *.fdb_latexmk
   
   # Windows PowerShell:
   Remove-Item *.aux, *.log, *.out, *.toc, *.fls, *.fdb_latexmk -ErrorAction SilentlyContinue
   ```

### Option B: Cloud Compilation (Overleaf)

1. Open [Overleaf](https://www.overleaf.com) and create a **New Project > Blank Project**.
2. Upload the desired `.tex` file (e.g., `draft.tex` or `tier1_physics_framework.tex`).
3. Ensure the project compiler is set to **pdfLaTeX** or **XeLaTeX** (Menu > Settings > Compiler).
4. Click **Recompile** to generate and download the PDF.

### Option C: Headless Browser Compiler (No TeX Installation Required)

If you do not have TeX Live or MiKTeX installed, the repository provides a vector-quality PDF generator that compiles directly from the canonical Markdown files using MathJax 3 and Headless Chrome/Edge:

```bash
# Compile specific essay:
python scripts/generate_pdf.py essays/existence/draft.md

# Compile all essays:
python scripts/generate_pdf.py --all
```

---

## 3. How to Regenerate LaTeX Files from Markdown

The canonical source of truth for all essays is the Markdown (`.md`) format. Whenever an essay is revised, regenerate the corresponding `.tex` file using `scripts/md_to_latex.py`:

```bash
# Regenerate a single essay:
python scripts/md_to_latex.py essays/existence/draft.md

# Regenerate all essays:
python scripts/md_to_latex.py --all
```

---

## 4. LaTeX File Directory Inventory

| LaTeX File | Canonical Markdown Source | Primary Focus |
| :--- | :--- | :--- |
| `draft.tex` | `essays/existence/draft.md` | Primary manuscript & foundation theory |
| `tier1_physics_framework.tex` | `essays/existence/tier1_physics_framework.md` | Rigorous mathematical physics & field equations |
| `interpretation.tex` | `essays/existence/interpretation.md` | Philosophical & epistemological synthesis |
| `dialogues_and_explorations.tex` | `essays/existence/dialogues_and_explorations.md` | Pedagogical dialogues & dialectical inquiries |
| `core_ontology_and_dharma.tex` | `essays/existence/interpretations/core_ontology_and_dharma.md` | Foundational ontology & resistance formulation |
| `cosmology_and_brahmanda.tex` | `essays/existence/interpretations/cosmology_and_brahmanda.md` | Astrophysical & cosmological interpretations |
| `biophysics_and_syncytia.tex` | `essays/existence/interpretations/biophysics_and_syncytia.md` | Living systems & cellular syncytia dynamics |
| `cognitive_and_psychology.tex` | `essays/cognitive_social_extensions/cognitive_and_psychology.md` | Neural networks & perception mechanics |
| `societal_and_institutional.tex` | `essays/cognitive_social_extensions/societal_and_institutional.md` | Macro-social & institutional governance |
