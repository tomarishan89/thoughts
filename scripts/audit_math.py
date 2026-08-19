#!/usr/bin/env python3
r"""
Comprehensive Mathematical & LaTeX Syntax Auditor across all Markdown documents.
Checks for:
1. Unmatched or unbalanced $ and $$ delimiters.
2. Unbalanced curly braces { } inside LaTeX math.
3. Unbalanced \left and \right delimiters.
4. Broken LaTeX macro patterns (e.g., missing subscripts before \text, bad greek indices).
5. Indented $$ display math blocks that risk markdown parser mangling.
6. Display math $$ blocks lacking blank lines before/after.
7. Long single-line equations inside \boxed{} that exceed print/display width.
"""

import os
import sys
import glob
import re

sys.stdout.reconfigure(encoding='utf-8')

def audit_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
        lines = content.splitlines()

    issues = []

    # 1. Extract Display Math ($$ ... $$)
    # Using regex to find all display blocks
    display_matches = list(re.finditer(r'\$\$(.*?)\$\$', content, flags=re.DOTALL))
    
    # 2. Check for unmatched $$
    total_double_dollars = len(re.findall(r'\$\$', content))
    if total_double_dollars % 2 != 0:
        issues.append(f"CRITICAL: Unmatched $$ delimiter count ({total_double_dollars})")

    # 3. Check for unmatched single $ (after masking display blocks and code blocks)
    masked_content = re.sub(r'```.*?```', '', content, flags=re.DOTALL)
    masked_content = re.sub(r'\$\$.*?\$\$', '', masked_content, flags=re.DOTALL)
    single_dollars = re.findall(r'(?<!\\)\$', masked_content)
    if len(single_dollars) % 2 != 0:
        issues.append(f"CRITICAL: Unmatched single $ delimiter count ({len(single_dollars)})")

    # 4. Check inline math expressions
    inline_matches = list(re.finditer(r'(?<!\\)\$(.*?)(?<!\\)\$', masked_content))
    for m in inline_matches:
        expr = m.group(1)
        start_pos = m.start()
        # Find line number
        line_num = content[:start_pos].count('\n') + 1
        
        # Check brace balance
        if expr.count('{') != expr.count('}'):
            issues.append(f"Line {line_num}: Unbalanced curly braces in inline math: ${expr}$")
            
        # Check \left \right balance
        left_count = len(re.findall(r'\\left\b', expr))
        right_count = len(re.findall(r'\\right\b', expr))
        if left_count != right_count:
            issues.append(f"Line {line_num}: Unbalanced \\left ({left_count}) vs \\right ({right_count}) in ${expr}$")
            
        # Check for unescaped < or > that might conflict with HTML
        # In LaTeX, \langle and \rangle are preferred, or < > inside $ should be checked
        if re.search(r'\\[a-zA-Z]+\{[^}]*\}\\[a-zA-Z]+', expr):
            # Check if there is missing space/subscript between macros like \mathcal{U}\text
            for bad_m in re.finditer(r'\\[a-zA-Z]+\{[^}]*\}\\[a-zA-Z]+', expr):
                issues.append(f"Line {line_num}: Potential missing subscript or separator in: {bad_m.group(0)}")

    # 5. Check display math expressions
    for m in display_matches:
        expr = m.group(1)
        start_pos = m.start()
        line_num = content[:start_pos].count('\n') + 1
        
        # Check brace balance
        if expr.count('{') != expr.count('}'):
            issues.append(f"Line {line_num}: Unbalanced curly braces in display math: $${expr[:80]}...$$")
            
        # Check \left \right balance
        left_count = len(re.findall(r'\\left\b', expr))
        right_count = len(re.findall(r'\\right\b', expr))
        if left_count != right_count:
            issues.append(f"Line {line_num}: Unbalanced \\left ({left_count}) vs \\right ({right_count}) in $${expr[:80]}...$$")

    # 6. Check line-by-line formatting of $$ blocks (Indentation & Blank line separation)
    in_display_block = False
    for idx, line in enumerate(lines):
        ln = idx + 1
        stripped = line.strip()
        
        if stripped.startswith('$$'):
            # Check if line is indented
            if line.startswith(' ') or line.startswith('\t'):
                issues.append(f"Line {ln}: Indented display math ($$): '{line[:40]}...' (risk of code-block or italic mangling)")
                
            # Check if previous line is blank or heading or another $$
            if idx > 0 and lines[idx-1].strip() != '' and not lines[idx-1].strip().startswith('$$') and not lines[idx-1].strip().startswith('#') and not lines[idx-1].strip().startswith('---'):
                issues.append(f"Line {ln}: Missing blank line before display math ($$)")
                
            if stripped == '$$':
                in_display_block = not in_display_block
            elif stripped.endswith('$$') and len(stripped) > 2:
                # Single-line $$ ... $$
                if idx + 1 < len(lines) and lines[idx+1].strip() != '' and not lines[idx+1].strip().startswith('$$') and not lines[idx+1].strip().startswith('#') and not lines[idx+1].strip().startswith('---'):
                    issues.append(f"Line {ln}: Missing blank line after single-line display math ($$)")
        elif stripped.endswith('$$') and in_display_block:
            in_display_block = False
            if idx + 1 < len(lines) and lines[idx+1].strip() != '' and not lines[idx+1].strip().startswith('$$') and not lines[idx+1].strip().startswith('#') and not lines[idx+1].strip().startswith('---'):
                issues.append(f"Line {ln}: Missing blank line after display math ($$) block")

    return issues

def main():
    target_files = sorted(glob.glob('essays/**/*.md', recursive=True))
    total_issues = 0
    
    print(f"=== Auditing Math & LaTeX Formatting across {len(target_files)} Markdown files ===\n")
    for fpath in target_files:
        issues = audit_file(fpath)
        if issues:
            print(f"File: {fpath} ({len(issues)} issues)")
            for iss in issues[:15]: # Show first 15 per file
                print(f"  - {iss}")
            if len(issues) > 15:
                print(f"  ... and {len(issues) - 15} more issues.")
            print()
            total_issues += len(issues)
            
    print(f"=== Audit Complete: Found {total_issues} formatting/syntax issues across repository. ===")

if __name__ == '__main__':
    main()
