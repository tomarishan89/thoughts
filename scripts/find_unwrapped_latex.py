#!/usr/bin/env python3
"""
Find any unescaped LaTeX macros / math expressions appearing OUTSIDE of $...$, $$...$$, or ```...``` blocks.
"""

import os
import sys
import glob
import re

sys.stdout.reconfigure(encoding='utf-8')

LATEX_INDICATORS = [
    r'\\hat\{', r'\\mathcal\{', r'\\mathbf\{', r'\\mathbb\{', r'\\mathrm\{', r'\\text\{',
    r'\\rho', r'\\tau', r'\\neq', r'\\equiv', r'\\int', r'\\sum', r'\\partial',
    r'\\sigma', r'\\nabla', r'\\alpha', r'\\beta', r'\\gamma', r'\\lambda', r'\\Lambda',
    r'\\Delta', r'\\Omega', r'\\in\b', r'\\le\b', r'\\ge\b', r'\\times\b', r'\\approx\b',
    r'\\exp\(', r'\\sqrt\{', r'\\subset\b', r'\\cup\b', r'\\cap\b', r'\\oint'
]

def find_unwrapped_latex(fpath):
    with open(fpath, 'r', encoding='utf-8') as f:
        content = f.read()

    lines = content.splitlines()
    in_code_block = False
    in_display_math = False
    unwrapped = []

    for i, line in enumerate(lines):
        ln = i + 1
        stripped = line.strip()

        if stripped.startswith('```'):
            in_code_block = not in_code_block
            continue
        if in_code_block:
            continue

        if stripped.startswith('$$'):
            if stripped == '$$':
                in_display_math = not in_display_math
            continue
        if in_display_math:
            continue

        # Mask display math if on same line
        masked = re.sub(r'\$\$.*?\$\$', '', line)
        # Mask inline math
        masked = re.sub(r'(?<!\\)\$.*?(?<!\\)\$', '', masked)
        # Mask HTML tags
        masked = re.sub(r'<.*?>', '', masked)
        # Mask inline code `...`
        masked = re.sub(r'`.*?`', '', masked)

        # Check for LaTeX macros in the remaining text
        for pattern in LATEX_INDICATORS:
            match = re.search(pattern, masked)
            if match:
                unwrapped.append((ln, match.group(0), line.strip()))
                break

    return unwrapped

def main():
    target_files = sorted(glob.glob('**/*.md', recursive=True))
    target_files = [f for f in target_files if '.git' not in f and 'node_modules' not in f]

    total = 0
    print(f"Scanning {len(target_files)} Markdown files for unwrapped LaTeX math...\n")

    for fpath in target_files:
        hits = find_unwrapped_latex(fpath)
        if hits:
            print(f"=== {fpath} ({len(hits)} unwrapped LaTeX instances) ===")
            for ln, token, text in hits:
                print(f"  Line {ln:4d} [Found {token}]: {text}")
            print()
            total += len(hits)

    print(f"Total unwrapped LaTeX instances found: {total}")

if __name__ == '__main__':
    main()
