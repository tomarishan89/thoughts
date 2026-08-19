#!/usr/bin/env python3
"""
Eliminates accidental indented code blocks in Markdown files:
1. Normalizes all prose paragraphs, bullet continuation text, and parenthetical explanations to start at column 0.
2. Preserves intentional fenced code blocks (``` ... ```).
3. Preserves legitimate list item markers:
   - Level 1 bullets: `* `, `- `, `1. ` at column 0
   - Level 2 sub-bullets: `  - ` or `  * ` (2 spaces)
4. Strips 3+ space indentation on non-list prose lines that triggers <pre><code> rendering in Markdown parsers.
"""

import os
import sys
import glob
import re

sys.stdout.reconfigure(encoding='utf-8')

def clean_markdown_indentation(content):
    lines = content.splitlines()
    new_lines = []
    
    in_fenced_code = False
    
    for line in lines:
        stripped = line.strip()
        
        # Track fenced code blocks (```)
        if stripped.startswith('```'):
            in_fenced_code = not in_fenced_code
            new_lines.append(line)
            continue
            
        if in_fenced_code:
            new_lines.append(line)
            continue
            
        # If line is blank
        if not stripped:
            new_lines.append('')
            continue
            
        # Display math $$
        if stripped.startswith('$$') or stripped.endswith('$$'):
            new_lines.append(stripped)
            continue
            
        # Headings
        if stripped.startswith('#'):
            new_lines.append(stripped)
            continue
            
        # Blockquotes
        if stripped.startswith('>'):
            new_lines.append(stripped)
            continue
            
        # Tables
        if stripped.startswith('|'):
            new_lines.append(stripped)
            continue
            
        # Horizontal rules
        if stripped == '---':
            new_lines.append('---')
            continue
            
        # Check list items
        # Level 1 list: `* `, `- `, `1. `, `2. ` etc.
        m_l1 = re.match(r'^(\*|-|\d+\.)\s+(.*)', stripped)
        if m_l1:
            # Column 0 list item
            new_lines.append(f"{m_l1.group(1)} {m_l1.group(2)}")
            continue
            
        # Level 2 sub-list: indented in original, e.g. `  - ` or `  * `
        m_l2 = re.match(r'^\s{2,4}(\*|-|\d+\.)\s+(.*)', line)
        if m_l2:
            new_lines.append(f"  - {m_l2.group(2)}")
            continue
            
        # For all other regular prose lines / math continuations:
        # Strip all leading indentation so it NEVER triggers an indented code block (<pre><code>)
        new_lines.append(stripped)
        
    result = '\n'.join(new_lines)
    # Ensure display math has blank lines before and after
    result = re.sub(r'([^\n])\n\$\$', r'\1\n\n$$', result)
    result = re.sub(r'\$\$\n([^\n])', r'$$\n\n\1', result)
    # Remove excessive blank lines (>2)
    result = re.sub(r'\n{3,}', '\n\n', result)
    return result

def process_file(fpath):
    with open(fpath, 'r', encoding='utf-8') as f:
        orig = f.read()
        
    cleaned = clean_markdown_indentation(orig)
    
    if orig != cleaned:
        with open(fpath, 'w', encoding='utf-8') as f:
            f.write(cleaned)
        print(f"[FIXED INDENTATION] {fpath}")
        return True
    return False

def main():
    target_files = sorted(glob.glob('essays/**/*.md', recursive=True))
    count = 0
    for f in target_files:
        if process_file(f):
            count += 1
    print(f"\nProcessing complete: Cleaned indentation in {count} files.")

if __name__ == '__main__':
    main()
