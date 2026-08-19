#!/usr/bin/env python3
"""
Scanner for unescaped math expressions and unbracketed LaTeX formulas in Markdown files.
Specifically detects:
1. Brackets with LaTeX: `[\hat{\mathcal{L}}_1, \hat{\mathcal{L}}_2]` without `$...$`
2. Relational operators with LaTeX outside math: `... \neq \mathbf{0}`
3. LaTeX commands in prose lines not enclosed in `$...$` or `$$...$$`
"""

import os
import sys
import glob
import re

sys.stdout.reconfigure(encoding='utf-8')

def find_unwrapped_formulas(fpath):
    with open(fpath, 'r', encoding='utf-8') as f:
        content = f.read()

    lines = content.splitlines()
    in_code_block = False
    in_display_math = False
    results = []

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

        # Check for brackets containing LaTeX backslashes without surrounding $
        # e.g., [\hat{\mathcal{L}}_1, \hat{\mathcal{L}}_2]
        bracket_matches = re.finditer(r'(?<!\$)(?<!\$)\[([^\]]*?\\[a-zA-Z]+[^\]]*?)\](?!\$)(?!\$)', line)
        for bm in bracket_matches:
            # Check if this match is inside an existing $...$
            start_pos = bm.start()
            # Count dollar signs before start_pos
            prefix = line[:start_pos]
            dollar_count = len(re.findall(r'(?<!\\)\$', prefix))
            if dollar_count % 2 == 0:  # Even means outside of math!
                results.append((ln, "UNWRAPPED_BRACKET_MATH", bm.group(0), line))

        # Check for LaTeX commands outside of $...$
        # Mask valid inline math: $...$
        masked = re.sub(r'(?<!\\)\$.*?(?<!\\)\$', '', line)
        # Mask inline code: `...`
        masked = re.sub(r'`.*?`', '', masked)
        # Mask html tags: <...>
        masked = re.sub(r'<.*?>', '', masked)
        # Mask markdown links: [text](url)
        masked = re.sub(r'\[.*?\]\(.*?\)', '', masked)

        latex_cmds = re.findall(r'\\[a-zA-Z]+(?:\{[^\}]*\})*(?:_[a-zA-Z0-9]+|\^[a-zA-Z0-9]+)*', masked)
        # Filter out common markdown escaped characters or non-math backslashes
        filtered_cmds = []
        for cmd in latex_cmds:
            # ignore things like \n, \t, etc if plain
            if cmd in [r'\n', r'\t', r'\r', r'\\']:
                continue
            filtered_cmds.append(cmd)

        if filtered_cmds:
            results.append((ln, "UNWRAPPED_LATEX_CMD", ", ".join(filtered_cmds), line))

    return results

def main():
    target_files = sorted(glob.glob('**/*.md', recursive=True))
    target_files = [f for f in target_files if '.git' not in f and 'node_modules' not in f]

    total = 0
    print(f"Scanning {len(target_files)} Markdown files for unwrapped math/LaTeX formulas...\n")

    for fpath in target_files:
        hits = find_unwrapped_formulas(fpath)
        if hits:
            print(f"=== {fpath} ({len(hits)} unwrapped math occurrences) ===")
            for ln, itype, details, raw in hits:
                print(f"  Line {ln:4d} [{itype}]: {details}")
                print(f"    Raw line: {raw.strip()[:100]}")
            print()
            total += len(hits)

    print(f"Total unwrapped math occurrences found: {total}")

if __name__ == '__main__':
    main()
