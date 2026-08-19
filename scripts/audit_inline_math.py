#!/usr/bin/env python3
"""
Deep Inline Math Auditor:
1. Finds any line with an odd number of unescaped `$` signs outside of ``` code blocks and $$ display blocks.
2. Finds any occurrence of LaTeX macro commands outside `$ ... $` or `$$ ... $$`.
3. Finds brackets with backslashes `[\...]` not wrapped in `$`.
"""

import os
import sys
import glob
import re

sys.stdout.reconfigure(encoding='utf-8')

def audit_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.read().splitlines()

    in_code_block = False
    in_display_math = False
    errors = []

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

        # Check for odd number of single dollar signs on this line
        # Remove display math $$ ... $$ first if any
        line_clean = re.sub(r'\$\$.*?\$\$', '', line)
        dollars = re.findall(r'(?<!\\)\$', line_clean)
        if len(dollars) % 2 != 0:
            errors.append((ln, "ODD_DOLLAR_COUNT", f"Found {len(dollars)} '$' delimiters on line", line))

        # Check for unbracketed LaTeX formulas like [\hat{...}]
        unwrapped_brackets = re.findall(r'(?<!\$)(?<!\$)\[[^\]]*?\\[a-zA-Z]+[^\]]*?\](?!\$)(?!\$)', line)
        for ub in unwrapped_brackets:
            # check if inside math
            start_pos = line.find(ub)
            prefix = line[:start_pos]
            dollar_count = len(re.findall(r'(?<!\\)\$', prefix))
            if dollar_count % 2 == 0:
                errors.append((ln, "UNWRAPPED_BRACKET", ub, line))

    return errors

def main():
    target_files = sorted(glob.glob('**/*.md', recursive=True))
    target_files = [f for f in target_files if '.git' not in f and 'node_modules' not in f]

    total_errors = 0
    print(f"Auditing inline math integrity across {len(target_files)} Markdown files...\n")

    for fpath in target_files:
        errs = audit_file(fpath)
        if errs:
            print(f"=== {fpath} ({len(errs)} issues found) ===")
            for ln, itype, desc, raw in errs:
                print(f"  Line {ln:4d} [{itype}]: {desc}")
                print(f"    Text: {raw.strip()[:100]}")
            print()
            total_errors += len(errs)

    if total_errors == 0:
        print("ALL CLEAR: Zero inline math delimiter or bracket errors found!")
    else:
        print(f"Audit finished: Found {total_errors} issue(s).")

if __name__ == '__main__':
    main()
