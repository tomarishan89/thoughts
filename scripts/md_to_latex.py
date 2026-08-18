#!/usr/bin/env python3
"""
Convert Markdown manuscripts to standard, publication-grade LaTeX (.tex) documents.
Usage:
    python scripts/md_to_latex.py essays/existence/draft.md -o essays/existence/latex/draft.tex
    python scripts/md_to_latex.py --all
"""

import os
import re
import argparse

LATEX_PREAMBLE = r"""\documentclass[11pt,a4paper]{article}

% --- Essential Mathematical & Physical Packages ---
\usepackage[utf8]{inputenc}
\usepackage[T1]{fontenc}
\usepackage{amsmath,amssymb,amsfonts,amsthm,mathtools}
\usepackage{bm}
\usepackage{physics}
\usepackage{geometry}
\geometry{top=25mm,bottom=25mm,left=25mm,right=25mm}

% --- Typography & Layout ---
\usepackage{microtype}
\usepackage{booktabs}
\usepackage{array}
\usepackage{enumitem}
\usepackage{xcolor}
\usepackage{hyperref}
\hypersetup{
    colorlinks=true,
    linkcolor=blue!70!black,
    citecolor=red!70!black,
    urlcolor=blue!60!black
}

% --- Theorem & Axiom Environments ---
\newtheorem{axiom}{Axiom}
\newtheorem{theorem}{Theorem}
\newtheorem{lemma}{Lemma}
\newtheorem{proposition}{Proposition}
\theoremstyle{definition}
\newtheorem{definition}{Definition}
\theoremstyle{remark}
\newtheorem{remark}{Remark}

% --- Standard Mathematical Operators ---
\newcommand{\Tr}{\mathrm{Tr}}
\newcommand{\Area}{\mathrm{Area}}
\newcommand{\supp}{\mathrm{supp}}
\newcommand{\RealPart}{\mathrm{Re}}
\newcommand{\ImagPart}{\mathrm{Im}}

\title{\textbf{A Continuum-Mechanical and Non-Equilibrium Thermodynamic Framework of Physical and Biological Existence}}
\author{\textbf{Ishan Tomar} \\ \textit{Vidyaman Research Institute}}
\date{\today}

\begin{document}

\maketitle

\begin{abstract}
We formulate a scale-invariant, continuum-mechanical, and non-equilibrium thermodynamic field theory of physical and biological existence. Every existing entity is modeled as an active open boundary interface $\partial E$ maintaining positive structural yield margin $\phi(x,t) \ge 0$ under continuous exergy harvest $\dot{E}_{\text{fuel}} \ge T_{\text{ambient}}\dot{S}_{\text{gen}}$. We derive the exact Schwarzschild-Hubble horizon identity ($R_s \equiv R_H \approx 1.37 \times 10^{26}\,\mathrm{m}$), proving the horizon duality theorem $\mathrm{Topology}(E_{\text{living}}) \cong \mathrm{Topology}(\mathcal{U}_{\text{BH}}) \not\cong \mathrm{Topology}(\mathcal{U}_{\text{closed}})$. Cosmological expansion is proven as a necessary consequence of the Generalized Second Law ($\dot{S}_{\text{GH}} \ge 0$), yielding a net multiverse matter accretion rate $\dot{M}_{\text{accrete}} \approx 47,991\,M_\odot/\mathrm{s}$. Dark Energy is analytically derived as the infrared holographic boundary surface tension ($\Lambda = 1.091 \times 10^{-52}\,\mathrm{m^{-2}}$, matching observations to $1.35\%$), and Dark Matter is derived from Einstein-Cartan spin-torsion boundary stresses ($a_0 = 1.042 \times 10^{-10}\,\mathrm{m/s^2}$), exactly predicting flat galactic rotation ($v_{\text{MW}} = 219.7\,\mathrm{km/s}$ to $0.14\%$). We establish the causal operator-theoretic temporal triad $\mathcal{F}_{\text{ledger}} \to \hat{\mathbf{P}} \to \boldsymbol{\mathcal{X}}$ across 4 scale-invariant tiers.
\end{abstract}

\vspace{1em}
\tableofcontents
\newpage
"""

def md_to_latex(md_content, title="Academic Paper"):
    # 1. Protect Math Blocks
    math_blocks = []
    def save_block_math(match):
        idx = len(math_blocks)
        math_blocks.append(match.group(1))
        return f"%%MATH_BLOCK_{idx}%%"
    
    math_inlines = []
    def save_inline_math(match):
        idx = len(math_inlines)
        math_inlines.append(match.group(1))
        return f"%%MATH_INLINE_{idx}%%"
    
    content = re.sub(r'\$\$(.*?)\$\$', save_block_math, md_content, flags=re.DOTALL)
    content = re.sub(r'(?<!\\)\$(.*?)(?<!\\)\$', save_inline_math, content)
    
    # 2. Convert Headings
    content = re.sub(r'^# (.*?)$', r'\\section*{\1}', content, flags=re.MULTILINE)
    content = re.sub(r'^## (.*?)$', r'\\section{\1}', content, flags=re.MULTILINE)
    content = re.sub(r'^### (.*?)$', r'\\subsection{\1}', content, flags=re.MULTILINE)
    content = re.sub(r'^#### (.*?)$', r'\\subsubsection{\1}', content, flags=re.MULTILINE)
    
    # 3. Handle Markdown Links [Text](url) -> \href{url}{Text} or \textbf{Text}
    def convert_link(match):
        text = match.group(1)
        url = match.group(2)
        # format text inside link
        text = re.sub(r'`([^`]+)`', r'\\texttt{\1}', text)
        text = text.replace('&', r'\&').replace('§', r'\S ')
        return f"\\href{{{url}}}{{{text}}}"
    content = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', convert_link, content)

    # 4. Bold & Italic & In-line Code
    content = re.sub(r'\*\*\*(.*?)\*\*\*', r'\\textbf{\\textit{\1}}', content)
    content = re.sub(r'\*\*(.*?)\*\*', r'\\textbf{\1}', content)
    content = re.sub(r'\*(.*?)\*', r'\\textit{\1}', content)
    content = re.sub(r'`([^`\n]+)`', r'\\texttt{\1}', content)

    # 5. Strip mermaid diagrams or convert to comments
    content = re.sub(r'```mermaid.*?```', r'%% [Flowchart Diagram Omitted in Raw TeX] %%', content, flags=re.DOTALL)
    
    # 6. Code blocks to verbatim
    content = re.sub(r'```(.*?)```', r'\\begin{verbatim}\1\\end{verbatim}', content, flags=re.DOTALL)
    
    # 7. Blockquotes to quote
    content = re.sub(r'^> (.*?)$', r'\\begin{quote}\1\\end{quote}', content, flags=re.MULTILINE)

    # 8. Unescape or format special LaTeX characters outside math
    content = content.replace(r'§', r'\S ')
    content = content.replace(r'&', r'\&')
    content = content.replace(r'%', r'\%')
    content = content.replace(r'#', r'\#')
    content = content.replace(r'_', r'\_')

    # 9. Restore Math Blocks
    for idx, block in enumerate(math_blocks):
        block_clean = block.strip()
        latex_block = f"\n\\begin{{equation}}\n{block_clean}\n\\end{{equation}}\n"
        content = content.replace(f"\\%\\%MATH\\_BLOCK\\_{idx}\\%\\%", latex_block)
        content = content.replace(f"%%MATH_BLOCK_{idx}%%", latex_block)
        
    for idx, inline in enumerate(math_inlines):
        inline_clean = inline.strip()
        latex_inline = f"${inline_clean}$"
        content = content.replace(f"\\%\\%MATH\\_INLINE\\_{idx}\\%\\%", latex_inline)
        content = content.replace(f"%%MATH_INLINE_{idx}%%", latex_inline)

    # Clean double escaped symbols in math
    content = content.replace(r'\_', '_')  # restore underscores inside math
    
    full_latex = LATEX_PREAMBLE + "\n\n" + content + "\n\n\\end{document}\n"
    return full_latex

def convert_file(input_md, output_tex=None):
    if not os.path.exists(input_md):
        print(f"Error: {input_md} not found.")
        return
    if output_tex is None:
        base = os.path.splitext(os.path.basename(input_md))[0]
        os.makedirs("essays/existence/latex", exist_ok=True)
        output_tex = os.path.join("essays/existence/latex", f"{base}.tex")
    else:
        os.makedirs(os.path.dirname(output_tex), exist_ok=True)
        
    with open(input_md, 'r', encoding='utf-8') as f:
        md_text = f.read()
    
    title = os.path.splitext(os.path.basename(input_md))[0].replace('_', ' ').title()
    latex_text = md_to_latex(md_text, title=title)
    
    with open(output_tex, 'w', encoding='utf-8') as f:
        f.write(latex_text)
    print(f"[OK] Generated LaTeX file: {output_tex}")

def main():
    parser = argparse.ArgumentParser(description="Convert Markdown to LaTeX documents.")
    parser.add_argument("file", nargs="?", help="Markdown file to convert")
    parser.add_argument("--all", action="store_true", help="Convert all main essays to LaTeX")
    parser.add_argument("-o", "--output", help="Output .tex path")
    args = parser.parse_args()

    if args.all:
        target_files = [
            "essays/existence/draft.md",
            "essays/existence/interpretation.md",
            "essays/existence/dialogues_and_explorations.md",
            "essays/existence/interpretations/core_ontology_and_dharma.md",
            "essays/existence/interpretations/cosmology_and_brahmanda.md",
            "essays/existence/interpretations/biophysics_and_syncytia.md",
            "essays/existence/interpretations/cognitive_and_psychology.md",
            "essays/existence/interpretations/societal_and_institutional.md",
        ]
        for f in target_files:
            convert_file(f)
    elif args.file:
        convert_file(args.file, args.output)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
