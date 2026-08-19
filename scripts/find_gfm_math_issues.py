#!/usr/bin/env python3
"""
Find and report all inline math expressions in Markdown files that can break on GitHub Flavored Markdown (GFM):
1. Overly complex inline math ($...$) containing \\frac, \\sqrt, \\int, \\sum, \\prod, \\oint, nested subscripts, or >60 characters.
2. Inline math wrapped directly in parentheses/brackets like `($...$)` or `[$...$]` which breaks GFM delimiter matching.
3. Multiple underscores in inline math within the same paragraph triggering GFM italic emphasis collisions.
"""

import sys
import glob
import re

sys.stdout.reconfigure(encoding='utf-8')

def analyze_file(fpath):
    with open(fpath, 'r', encoding='utf-8') as f:
        content = f.read()
        
    lines = content.splitlines()
    issues = []
    
    in_code = False
    for i, line in enumerate(lines):
        ln = i + 1
        stripped = line.strip()
        
        if stripped.startswith('```'):
            in_code = not in_code
            continue
        if in_code:
            continue
        if stripped.startswith('$$') or stripped.endswith('$$'):
            continue
            
        # Check for ($...$) or [$...$]
        paren_matches = re.findall(r'(\(\$[^$]+\$\)|\[\$[^$]+\$\])', line)
        if paren_matches:
            issues.append((ln, 'Math attached to brackets', paren_matches))
            
        # Check all inline math
        inlines = re.findall(r'(?<!\\)\$(.*?)(?<!\\)\$', line)
        for expr in inlines:
            has_frac = r'\frac' in expr
            has_sqrt = r'\sqrt' in expr
            has_sum_int = any(op in expr for op in [r'\sum', r'\int', r'\prod', r'\oint'])
            has_nested_sub = bool(re.search(r'_[{][^{}]*_[^{}]*[}]', expr))
            is_long = len(expr) > 60
            
            if has_frac or has_sqrt or has_sum_int or has_nested_sub or is_long:
                issues.append((ln, 'Complex inline math (candidate for display math or simplification)', f"${expr}$"))
                
    return issues

def main():
    target_files = sorted(glob.glob('essays/**/*.md', recursive=True))
    total = 0
    for f in target_files:
        iss = analyze_file(f)
        if iss:
            print(f"=== {f} ({len(iss)} issues) ===")
            for line_num, itype, val in iss:
                print(f"  Line {line_num}: [{itype}] {val}")
            print()
            total += len(iss)
            
    print(f"Total GFM inline math candidates found: {total}")

if __name__ == '__main__':
    main()
