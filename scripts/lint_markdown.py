#!/usr/bin/env python3
"""
Comprehensive Markdown & LaTeX Math Linter for the Repository.
Runs all validation checks on Markdown (.md) files:
1. Math Delimiters: Verifies balanced `$`, `$$`, `{ }`, `\\left` / `\\right`.
2. GFM Collision Check: Ensures no unpadded `($` or `$)` or `[$` or `$]` punctuation collisions.
3. Code Block Indentation Check: Ensures no prose lines have 3+ or 4+ space leading indentation after blank lines.
4. Display Math Alignment: Ensures all `$$` equations start at column 0 with blank line padding.
5. Relative Link Validation: Ensures all local Markdown links `[text](target.md)` resolve to existing files.

Usage:
    python scripts/lint_markdown.py             # Lint all markdown files
    python scripts/lint_markdown.py --staged    # Lint only staged git markdown files
"""

import os
import sys
import glob
import re
import argparse
import subprocess

sys.stdout.reconfigure(encoding='utf-8')

def get_staged_markdown_files():
    """Retrieve list of staged .md files using git diff."""
    try:
        res = subprocess.run(
            ["git", "diff", "--cached", "--name-only", "--diff-filter=ACM"],
            capture_output=True,
            text=True,
            check=True
        )
        files = [f.strip() for f in res.stdout.splitlines() if f.strip().endswith('.md')]
        return [f for f in files if os.path.exists(f)]
    except Exception as e:
        print(f"Warning: Could not get staged files from git ({e}). Falling back to all files.")
        return []

def lint_file(filepath):
    """Run all linter checks on a single Markdown file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
        lines = content.splitlines()

    issues = []
    file_dir = os.path.dirname(filepath)

    # 1. Check Display Math Delimiter Balance ($$)
    total_double_dollars = len(re.findall(r'\$\$', content))
    if total_double_dollars % 2 != 0:
        issues.append((1, "MATH_ERROR", f"Unmatched '$$' display math delimiters count: {total_double_dollars}"))

    # 2. Check Single Dollar Delimiter Balance ($)
    masked_content = re.sub(r'```.*?```', '', content, flags=re.DOTALL)
    masked_content = re.sub(r'\$\$.*?\$\$', '', masked_content, flags=re.DOTALL)
    single_dollars = re.findall(r'(?<!\\)\$', masked_content)
    if len(single_dollars) % 2 != 0:
        issues.append((1, "MATH_ERROR", f"Unmatched '$' inline math delimiters count: {len(single_dollars)}"))

    # 3. Line-by-line linting
    in_code_block = False
    in_display_math = False

    for i, line in enumerate(lines):
        ln = i + 1
        stripped = line.strip()

        # Track fenced code blocks (```)
        if stripped.startswith('```'):
            in_code_block = not in_code_block
            continue

        if in_code_block:
            continue

        # Track display math blocks
        if stripped.startswith('$$'):
            # Check column 0
            if line.startswith(' ') or line.startswith('\t'):
                issues.append((ln, "MATH_INDENT", f"Display math '$$' must start at column 0 (found leading whitespace)"))
            # Check blank line before
            if i > 0 and lines[i-1].strip() != '' and not lines[i-1].strip().startswith('#') and not lines[i-1].strip().startswith('---'):
                issues.append((ln, "MATH_PADDING", f"Missing blank line before display math '$$'"))

            if stripped == '$$':
                in_display_math = not in_display_math
            elif stripped.endswith('$$') and len(stripped) > 2:
                # Single line display math
                if i + 1 < len(lines) and lines[i+1].strip() != '' and not lines[i+1].strip().startswith('#') and not lines[i+1].strip().startswith('---'):
                    issues.append((ln, "MATH_PADDING", f"Missing blank line after display math '$$'"))
            continue

        if in_display_math:
            if stripped.endswith('$$'):
                in_display_math = False
                if i + 1 < len(lines) and lines[i+1].strip() != '' and not lines[i+1].strip().startswith('#') and not lines[i+1].strip().startswith('---'):
                    issues.append((ln, "MATH_PADDING", f"Missing blank line after display math '$$'"))
            continue

        # Check for accidental 3+ space indentation on non-list prose lines
        leading_spaces = len(line) - len(line.lstrip())
        is_list_item = bool(re.match(r'^\s*(\*|-|\d+\.)\s+', line))
        if leading_spaces >= 3 and not is_list_item and stripped:
            issues.append((ln, "PROSE_INDENT", f"Prose line has {leading_spaces} leading spaces (triggers accidental code-block): '{stripped[:40]}...'"))

        # Check for GFM delimiter-punctuation collisions: ($ or $) or [$ or $]
        bad_parens = re.findall(r'(\(\$|\$\)|\[\$|\$\])', line)
        if bad_parens:
            # Check if it's ($ without space or $) without space
            if re.search(r'\(\$[^\s]', line) or re.search(r'[^\s]\$\)', line) or re.search(r'\[\$[^\s]', line) or re.search(r'[^\s]\$\]', line):
                issues.append((ln, "GFM_COLLISION", f"Punctuation-math collision detected (use '( $...$ )' with spaces): '{line.strip()[:60]}'"))

        # Check inline math brace and \left \right balance
        inlines = re.findall(r'(?<!\\)\$(.*?)(?<!\\)\$', line)
        for expr in inlines:
            if expr.count('{') != expr.count('}'):
                issues.append((ln, "BRACE_ERROR", f"Unbalanced curly braces in inline math: '${expr[:50]}...'"))
            left_count = len(re.findall(r'\\left\b', expr))
            right_count = len(re.findall(r'\\right\b', expr))
            if left_count != right_count:
                issues.append((ln, "DELIMITER_ERROR", f"Unbalanced \\left ({left_count}) vs \\right ({right_count}) in inline math: '${expr[:50]}...'"))

        # Check local Markdown links in non-math text: [text](target)
        non_math_line = re.sub(r'(?<!\\)\$(.*?)(?<!\\)\$', '', line)
        links = re.findall(r'\[([^\]]+)\]\(([^)]+)\)', non_math_line)
        for text, target in links:
            if target.startswith(('http://', 'https://', '#', 'mailto:')):
                continue
            # Strip anchors
            target_path = target.split('#')[0]
            if target_path:
                resolved_path = os.path.normpath(os.path.join(file_dir, target_path))
                if not os.path.exists(resolved_path):
                    issues.append((ln, "BROKEN_LINK", f"Broken relative link '[{text}]({target})' -> '{resolved_path}' does not exist"))

    return issues

def main():
    parser = argparse.ArgumentParser(description="Lint Markdown files for LaTeX, formatting, and link integrity.")
    parser.add_argument("--staged", action="store_true", help="Lint only git staged Markdown files")
    parser.add_argument("files", nargs="*", help="Specific files to lint")
    args = parser.parse_args()

    if args.staged:
        target_files = get_staged_markdown_files()
        if not target_files:
            print("[LINT] No staged Markdown files to lint.")
            sys.exit(0)
    elif args.files:
        target_files = args.files
    else:
        target_files = sorted(glob.glob('**/*.md', recursive=True))
        target_files = [f for f in target_files if '.git' not in f and 'node_modules' not in f]

    total_issues = 0
    print(f"[LINT] Checking {len(target_files)} Markdown file(s)...\n")

    for fpath in target_files:
        issues = lint_file(fpath)
        if issues:
            print(f"FAILED: {fpath} ({len(issues)} issue(s)):")
            for ln, itype, msg in issues:
                print(f"  Line {ln:4d} [{itype}]: {msg}")
            print()
            total_issues += len(issues)

    if total_issues == 0:
        print(f"[LINT PASSED] All {len(target_files)} Markdown files passed formatting, LaTeX, and link checks!")
        sys.exit(0)
    else:
        print(f"[LINT FAILED] Found {total_issues} issue(s) across Markdown files. Please resolve before committing.")
        sys.exit(1)

if __name__ == '__main__':
    main()
