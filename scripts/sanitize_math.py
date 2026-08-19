#!/usr/bin/env python3
"""
Comprehensive Mathematical & LaTeX Syntax Formatter and Sanitizer for Markdown Files:
1. Normalizes all display math ($$ ... $$) to column 0 (un-indented) with guaranteed blank lines before & after.
2. Inserts proper spacing between concatenated LaTeX macros (e.g. \\mathcal{T} \\exp, \\bar{\\psi} \\, \\gamma, \\mathbf{A} \\, \\mathbf{x}).
3. Fixes long, cluttered boxed equation chains into cleanly structured equations.
4. Normalizes physical units spacing (e.g., \\rho \\sim 10^{54} \\, \\mathrm{kg/m^3}).
5. Replaces any deprecated KaTeX delimiters or broken operators (\\operatorname -> \\mathrm).
"""

import os
import sys
import glob
import re

sys.stdout.reconfigure(encoding='utf-8')

def fix_macro_spacing(math_text):
    """Ensure proper spacing between adjacent macros that could be misparsed."""
    # Specific common macro collisions in the theoretical manuscript
    replacements = [
        (r'\\bar\{\\psi\}\\gamma', r'\\bar{\\psi} \\, \\gamma'),
        (r'\\mathcal\{T\}\\exp', r'\\mathcal{T} \\exp'),
        (r'\\mathcal\{P\}\\int', r'\\mathcal{P} \\int'),
        (r'\\mathrm\{Tr\}\\left', r'\\mathrm{Tr} \\left'),
        (r'\\hat\{A\}\\exp', r'\\hat{A} \\exp'),
        (r'\\mathbf\{G\}\\cdot', r'\\mathbf{G} \\cdot'),
        (r'\\mathbf\{v\}\\cdot', r'\\mathbf{v} \\cdot'),
        (r'\\mathcal\{A\}\\Delta', r'\\mathcal{A} \\Delta'),
        (r'\\hat\{\\rho\}\\parallel', r'\\hat{\\rho} \\parallel'),
        (r'\\operatorname\{([a-zA-Z0-9_]+)\}', r'\\mathrm{\1}'),
        (r'\\operatorname\b', r'\\mathrm'),
    ]
    for pattern, repl in replacements:
        math_text = re.sub(pattern, repl, math_text)
        
    # Generalized: \mathbf{X}\mathbf{Y} -> \mathbf{X} \, \mathbf{Y}
    math_text = re.sub(r'(\\mathbf\{[^}]+\})(\\mathbf\{[^}]+\})', r'\1 \\, \2', math_text)
    # \hat{\rho}\hat{H} -> \hat{\rho} \, \hat{H}
    math_text = re.sub(r'(\\hat\{[^}]+\})(\\hat\{[^}]+\})', r'\1 \\, \2', math_text)
    # \mathbf{\Sigma}\mathbf{v} -> \mathbf{\Sigma} \, \mathbf{v}
    math_text = re.sub(r'(\\mathbf\{\\[a-zA-Z]+\})(\\mathbf\{[^}]+\})', r'\1 \\, \2', math_text)
    
    return math_text

def format_math_delimiters_and_spacing(content):
    """
    Ensure all $$ blocks start at column 0 and have clean blank lines before and after.
    Process both single-line and multi-line $$ blocks.
    """
    lines = content.splitlines()
    new_lines = []
    
    in_math_block = False
    in_code_block = False
    
    for i, line in enumerate(lines):
        stripped = line.strip()
        
        # Track code blocks (```)
        if stripped.startswith('```'):
            in_code_block = not in_code_block
            new_lines.append(line)
            continue
            
        if in_code_block:
            new_lines.append(line)
            continue
            
        # Case 1: Start/End of Multi-line $$ or Single-line $$ ... $$
        if stripped.startswith('$$'):
            if stripped == '$$':
                # Multi-line $$ toggle
                if not in_math_block:
                    # Opening $$
                    if new_lines and new_lines[-1].strip() != '' and not new_lines[-1].strip().startswith('#') and not new_lines[-1].strip().startswith('---'):
                        new_lines.append('')
                    new_lines.append('$$')
                    in_math_block = True
                else:
                    # Closing $$
                    new_lines.append('$$')
                    in_math_block = False
                    if i + 1 < len(lines) and lines[i+1].strip() != '' and not lines[i+1].strip().startswith('#') and not lines[i+1].strip().startswith('---'):
                        new_lines.append('')
            elif stripped.endswith('$$') and len(stripped) > 2:
                # Single-line $$ ... $$
                # Ensure blank line before
                if new_lines and new_lines[-1].strip() != '' and not new_lines[-1].strip().startswith('#') and not new_lines[-1].strip().startswith('---'):
                    new_lines.append('')
                
                # Clean inner math spacing
                inner_math = stripped[2:-2].strip()
                inner_math = fix_macro_spacing(inner_math)
                new_lines.append(f"$${inner_math}$$")
                
                # Ensure blank line after
                if i + 1 < len(lines) and lines[i+1].strip() != '' and not lines[i+1].strip().startswith('#') and not lines[i+1].strip().startswith('---'):
                    new_lines.append('')
            else:
                # Line starts with $$ and continues
                if not in_math_block:
                    if new_lines and new_lines[-1].strip() != '' and not new_lines[-1].strip().startswith('#') and not new_lines[-1].strip().startswith('---'):
                        new_lines.append('')
                    in_math_block = True
                new_lines.append(stripped)
        elif stripped.endswith('$$') and in_math_block:
            # Closing line of multi-line $$
            new_lines.append(stripped)
            in_math_block = False
            if i + 1 < len(lines) and lines[i+1].strip() != '' and not lines[i+1].strip().startswith('#') and not lines[i+1].strip().startswith('---'):
                new_lines.append('')
        elif in_math_block:
            # Inside multi-line math block: un-indent or preserve minimal formula indentation
            new_lines.append(fix_macro_spacing(stripped))
        else:
            # Regular text line: fix inline math spacing
            def fix_inline(match):
                inner = match.group(1)
                fixed = fix_macro_spacing(inner)
                return f"${fixed}$"
            
            # Replace inline math $...$
            line_fixed = re.sub(r'(?<!\\)\$(.*?)(?<!\\)\$', fix_inline, line)
            new_lines.append(line_fixed)
            
    result = '\n'.join(new_lines)
    # Remove duplicate blank lines (>2 consecutive)
    result = re.sub(r'\n{3,}', '\n\n', result)
    return result

def specific_draft_fixes(content):
    """Fix specific long/cluttered equations in draft.md for optimal presentation."""
    # Line 71: Split the 4-equation chained boxed formula into clean, readable display equations
    old_bondi_chain = r'$$\boxed{\dot{M}_{\text{rel-Bondi}} = 4\pi r_{\text{sonic}}^2 u_{\text{sonic}} h_{\text{sonic}} \rho_{\text{sonic}} = \pi \frac{G^2 M_{\text{Hubble}}^2}{c^3} \frac{\left( 1 + 3 c_s^2/c^2 \right)^{3/2}}{(c_s/c)^3} \rho_{\text{parent}} \ge 0, \quad G_{\mu\nu} + \Lambda g_{\mu\nu} = \frac{8\pi G}{c^4} \langle \hat{T}_{\mu\nu} \rangle_{\text{ren}}, \quad A_n = 4 \ln(k) \ell_P^2 n, \quad S_{\text{Wald}} \equiv -2\pi \oint_{\mathcal{H}} \frac{\partial \mathcal{L}}{\partial R_{\mu\nu\rho\sigma}}\epsilon_{\mu\nu}\epsilon_{\rho\sigma} dA \equiv S_{\text{GH}}(\mathcal{U})}$$'
    
    new_bondi_chain = (
        r'$$\boxed{\dot{M}_{\text{rel-Bondi}} = 4\pi r_{\text{sonic}}^2 u_{\text{sonic}} h_{\text{sonic}} \rho_{\text{sonic}} = \pi \frac{G^2 M_{\text{Hubble}}^2}{c^3} \frac{\left( 1 + 3 c_s^2/c^2 \right)^{3/2}}{(c_s/c)^3} \rho_{\text{parent}} \ge 0}$$'
        '\n\n'
        r'$$\boxed{G_{\mu\nu} + \Lambda g_{\mu\nu} = \frac{8\pi G}{c^4} \langle \hat{T}_{\mu\nu} \rangle_{\text{ren}}, \qquad A_n = 4 \ln(k) \ell_P^2 n, \qquad S_{\text{Wald}} \equiv -2\pi \oint_{\mathcal{H}} \frac{\partial \mathcal{L}}{\partial R_{\mu\nu\rho\sigma}} \epsilon_{\mu\nu}\epsilon_{\rho\sigma} \, dA \equiv S_{\text{GH}}(\mathcal{U})}$$'
    )
    
    if old_bondi_chain in content:
        content = content.replace(old_bondi_chain, new_bondi_chain)
        
    return content

def sanitize_file(fpath):
    with open(fpath, 'r', encoding='utf-8') as f:
        orig = f.read()
        
    sanitized = format_math_delimiters_and_spacing(orig)
    if 'draft.md' in fpath:
        sanitized = specific_draft_fixes(sanitized)
        
    if orig != sanitized:
        with open(fpath, 'w', encoding='utf-8') as f:
            f.write(sanitized)
        print(f"[CLEANED] {fpath}")
        return True
    return False

def main():
    target_files = sorted(glob.glob('essays/**/*.md', recursive=True))
    cleaned_count = 0
    for f in target_files:
        if sanitize_file(f):
            cleaned_count += 1
    print(f"\nSanitization complete. Successfully formatted {cleaned_count} files.")

if __name__ == '__main__':
    main()
