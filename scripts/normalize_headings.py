#!/usr/bin/env python3
"""
Markdown Heading Normalizer.
Ensures all Markdown headings (# to ######):
1. Start at column 0 without leading indentation.
2. Are preceded by a blank line (unless at start of file or following another heading/---).
3. Are followed by a blank line (unless followed by another heading or EOF).
4. Strictly isolates headings so they never fuse with following paragraph text.
"""
import os
import sys
import glob
import re
import argparse

def normalize_headings_in_text(text):
    lines = text.splitlines()
    new_lines = []
    in_code = False
    in_math = False
    
    for i, line in enumerate(lines):
        stripped = line.strip()
        
        # Track code blocks
        if in_code:
            new_lines.append(line)
            if stripped.startswith('```'):
                in_code = False
            continue

        if stripped.startswith('```'):
            in_code = True
            new_lines.append(line)
            continue
            
        # Track display math
        if in_math:
            new_lines.append(line)
            if stripped.endswith('$$'):
                in_math = False
            continue

        if stripped.startswith('$$'):
            new_lines.append(line)
            if not (stripped.endswith('$$') and len(stripped) > 2):
                in_math = True
            continue
            
        # Match ATX headings
        m = re.match(r'^\s*(#{1,6})\s+(.*)$', line)
        if m:
            hashes = m.group(1)
            heading_content = m.group(2).strip()
            clean_heading = f"{hashes} {heading_content}"
            
            # Ensure blank line before
            if new_lines and new_lines[-1].strip() != '' and not new_lines[-1].strip().startswith('#') and not new_lines[-1].strip().startswith('---'):
                new_lines.append('')
                
            new_lines.append(clean_heading)
            
            # Ensure blank line after
            if i + 1 < len(lines):
                next_l = lines[i + 1].strip()
                if next_l != '' and not next_l.startswith('#'):
                    new_lines.append('')
        else:
            new_lines.append(line)
            
    # Collapse any accidental 3+ consecutive blank lines down to 1
    result = []
    blank_count = 0
    for l in new_lines:
        if l.strip() == '':
            blank_count += 1
            if blank_count <= 1:
                result.append('')
        else:
            blank_count = 0
            result.append(l)
            
    return '\n'.join(result) + ('\n' if text.endswith('\n') else '')

def process_file(filepath, dry_run=False):
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        original = f.read()
        
    normalized = normalize_headings_in_text(original)
    
    if normalized != original:
        if not dry_run:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(normalized)
        return True
    return False

def main():
    parser = argparse.ArgumentParser(description="Normalize Markdown headings.")
    parser.add_argument("files", nargs="*", help="Specific files to normalize")
    parser.add_argument("--dry-run", action="store_true", help="Report without modifying")
    args = parser.parse_args()
    
    if args.files:
        files = args.files
    else:
        files = sorted(glob.glob("**/*.md", recursive=True))
        
    changed = []
    for f in files:
        if '.gemini' in f or 'node_modules' in f or '.git' in f:
            continue
        if process_file(f, dry_run=args.dry_run):
            changed.append(f)
            
    action = "Would modify" if args.dry_run else "Normalized"
    print(f"{action} {len(changed)} file(s):")
    for c in changed:
        print(f"  {c}")

if __name__ == '__main__':
    main()
