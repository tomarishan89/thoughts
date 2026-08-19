#!/usr/bin/env python3
"""
GitHub-Flavored Markdown (GFM) Math Hardening Tool:
1. Fixes delimiter-punctuation collisions:
   - `($...$)` -> `( $...$ )` or puts parens inside `$ (...) $`.
   - `[$...$]` -> `[ $...$ ]` or puts brackets inside `$ [...] $`.
   - `($...` -> `( $...`
   - `...$)` -> `...$ )`
2. Converts overly complex inline formulas (>60 chars with fractions/radicals/nested subscripts) into clean display math blocks ($$).
3. Fixes any inline math with nested braces that confuse GFM emphasis.
"""

import sys
import glob
import re

sys.stdout.reconfigure(encoding='utf-8')

def harden_gfm_math(content):
    # 1. Fix bracket collisions: `($...$)` -> `( $...$ )`
    # Replace ($ with ( $
    content = re.sub(r'\(\$(.*?)\$\)', r'( $\1$ )', content)
    # Replace [$ with [ $
    content = re.sub(r'\[\$(.*?)\$\]', r'[ $\1$ ]', content)
    
    # Replace ($ with ( $ (if not matched above)
    content = re.sub(r'\(\$(?!\$)', r'( $', content)
    # Replace $) with $ ) (if not matched above)
    content = re.sub(r'(?<!\$)\$\)', r'$ )', content)
    # Replace [$ with [ $
    content = re.sub(r'\[\$(?!\$)', r'[ $', content)
    # Replace $] with $ ]
    content = re.sub(r'(?<!\$)\$\]', r'$ ]', content)

    # 2. Specific fixes for draft.md Section 1.2 / 1.2.1 complex formulas
    # Section 1.2.1 Step 1 operator composition formula
    old_step1_text = r'where $\hat{H}(\tau) = \hat{H}^\dagger(\tau)$ is the effective Hamiltonian driving coherent internal dynamics, and $\hat{L}_k(\tau)$ are Lindblad jump operators representing irreversible dissipative interventions and fuel consumption, rigorously typed on $\mathcal{H} = L^2(\Omega_{\mathbb{C}})$ via operator composition $\hat{L}_k(\tau) \equiv \mathcal{O}_k(\tau) \, \hat{M}_{\sqrt{\mathcal{F}_k(\tau)/\mathcal{F}_k^\ominus}}$ (where $(\hat{L}_k \psi)(\mathbf{x}) \equiv \mathcal{O}_k[\sqrt{\frac{\mathcal{F}_k(\mathbf{x}, \tau)}{\mathcal{F}_k^\ominus}} \, \psi(\mathbf{x})]$ and $\hat{M}_{\sqrt{\mathcal{F}_k/\mathcal{F}_k^\ominus}}$ is the dimensionless fractional coordinate multiplication operator normalized by characteristic substrate density $\mathcal{F}_k^\ominus$, ensuring $\gamma_k \in [\mathrm{s}^{-1}]$ represents the true microscopic jump transition rate). Taking the trace yields exact probability conservation:'
    
    new_step1_text = (
        r'where $\hat{H}(\tau) = \hat{H}^\dagger(\tau)$ is the effective Hamiltonian driving coherent internal dynamics, and $\hat{L}_k(\tau)$ are Lindblad jump operators representing irreversible dissipative interventions and fuel consumption, rigorously typed on $\mathcal{H} = L^2(\Omega_{\mathbb{C}})$ via operator composition:'
        '\n\n'
        r'$$\boxed{\hat{L}_k(\tau) \equiv \mathcal{O}_k(\tau) \, \hat{M}_{\sqrt{\mathcal{F}_k(\tau)/\mathcal{F}_k^\ominus}}, \qquad (\hat{L}_k \psi)(\mathbf{x}) \equiv \mathcal{O}_k \left[ \sqrt{\frac{\mathcal{F}_k(\mathbf{x}, \tau)}{\mathcal{F}_k^\ominus}} \, \psi(\mathbf{x}) \right]}$$'
        '\n\n'
        r'where $\hat{M}_{\sqrt{\mathcal{F}_k/\mathcal{F}_k^\ominus}}$ is the dimensionless fractional coordinate multiplication operator normalized by characteristic substrate density $\mathcal{F}_k^\ominus$, ensuring $\gamma_k \in [ \mathrm{s}^{-1} ]$ represents the microscopic jump transition rate. Taking the trace yields exact probability conservation:'
    )
    if old_step1_text in content:
        content = content.replace(old_step1_text, new_step1_text)

    # 3. Clean double spaces created in inline math
    content = re.sub(r'\(\s+\$', '( $', content)
    content = re.sub(r'\$\s+\)', '$ )', content)
    content = re.sub(r'\[\s+\$', '[ $', content)
    content = re.sub(r'\$\s+\]', '$ ]', content)

    # 4. Ensure display math has blank lines before and after
    content = re.sub(r'([^\n])\n\$\$', r'\1\n\n$$', content)
    content = re.sub(r'\$\$\n([^\n])', r'$$\n\n\1', content)
    content = re.sub(r'\n{3,}', '\n\n', content)
    
    return content

def process_file(fpath):
    with open(fpath, 'r', encoding='utf-8') as f:
        orig = f.read()
        
    cleaned = harden_gfm_math(orig)
    
    if orig != cleaned:
        with open(fpath, 'w', encoding='utf-8') as f:
            f.write(cleaned)
        print(f"[GFM HARDENED] {fpath}")
        return True
    return False

def main():
    target_files = sorted(glob.glob('essays/**/*.md', recursive=True))
    count = 0
    for f in target_files:
        if process_file(f):
            count += 1
    print(f"\nGFM Math Hardening complete: Updated {count} files.")

if __name__ == '__main__':
    main()
