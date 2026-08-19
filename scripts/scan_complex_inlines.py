#!/usr/bin/env python3
"""
Find all inline $...$ expressions across Markdown files that contain complex structures:
- Integrals / Summations / Products: \int, \sum, \prod, \oint, \bigcup, \bigcap
- Fractions / Radicals: \frac, \sqrt
- Commutators / Operators: [\hat{...}], \neq \mathbf{...}
"""

import os
import sys
import glob
import re

sys.stdout.reconfigure(encoding='utf-8')

def scan_complex_inlines(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.read().splitlines()

    in_code_block = False
    in_display_math = False
    findings = []

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

        # Skip display math on single lines
        if stripped.startswith('$$') and stripped.endswith('$$'):
            continue

        # Find all inline math $...$
        inlines = re.findall(r'(?<!\\)\$(.*?)(?<!\\)\$', line)
        for expr in inlines:
            # Check if contains complex tokens
            has_int_sum = bool(re.search(r'\\(int|sum|prod|oint|bigcup|bigcap|exp|sqrt|frac)', expr))
            if has_int_sum and len(expr) > 25:
                findings.append((ln, expr, line.strip()))

    return findings

def main():
    target_files = sorted(glob.glob('**/*.md', recursive=True))
    target_files = [f for f in target_files if '.git' not in f and 'node_modules' not in f]

    total = 0
    print(f"Scanning {len(target_files)} Markdown files for complex inline math...\n")

    for fpath in target_files:
        hits = scan_complex_inlines(fpath)
        if hits:
            print(f"=== {fpath} ({len(hits)} complex inlines) ===")
            for ln, expr, raw in hits:
                print(f"  Line {ln:4d}: ${expr}$")
            print()
            total += len(hits)

    print(f"Total complex inline math found: {total}")

if __name__ == '__main__':
    main()
