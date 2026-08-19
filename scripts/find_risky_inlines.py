#!/usr/bin/env python3
"""
Scanner for risky inline math expressions across all Markdown files.
Identifies inline math expressions `$ ... $` that:
1. Contain 2 or more underscores (`_`) which trigger GFM emphasis mangling.
2. Contain complex multi-operator formulas (>40 chars with \\int, \\sum, \\frac, etc.) that belong in display math ($$).
"""

import os
import sys
import glob
import re

sys.stdout.reconfigure(encoding='utf-8')

def find_risky_inlines(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.read().splitlines()

    in_code_block = False
    in_display_math = False
    risky = []

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

        if stripped.startswith('$$') and stripped.endswith('$$'):
            continue

        # Find all inline math $...$
        inlines = re.findall(r'(?<!\\)\$(.*?)(?<!\\)\$', line)
        for expr in inlines:
            underscore_count = expr.count('_')
            has_complex_ops = bool(re.search(r'\\(int|sum|prod|oint|frac|sqrt|exp|lim)\b', expr))
            
            # Risk condition: multiple underscores or long complex formula
            if underscore_count >= 2 or (has_complex_ops and len(expr) > 35):
                risky.append((ln, underscore_count, expr, line.strip()))

    return risky

def main():
    target_files = sorted(glob.glob('**/*.md', recursive=True))
    target_files = [f for f in target_files if '.git' not in f and 'node_modules' not in f]

    total = 0
    print(f"Scanning {len(target_files)} Markdown files for risky inline math...\n")

    for fpath in target_files:
        hits = find_risky_inlines(fpath)
        if hits:
            print(f"=== {fpath} ({len(hits)} risky inlines) ===")
            for ln, ucount, expr, raw in hits:
                print(f"  Line {ln:4d} [{ucount} underscores, len {len(expr)}]: ${expr}$")
            print()
            total += len(hits)

    print(f"Total risky inline math occurrences found: {total}")

if __name__ == '__main__':
    main()
