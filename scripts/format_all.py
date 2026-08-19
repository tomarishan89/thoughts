#!/usr/bin/env python3
"""
Run all repository Markdown formatters and sanitizers in sequence:
1. sanitize_math.py - Column-0 alignment, macro spacing, equation splitting.
2. harden_gfm_math.py - Punctuation delimiter padding, inline formula optimization.
3. strip_accidental_code_indentation.py - 3+ space indentation cleanup.
4. clean_relative_links.py - Relative link normalization.
"""

import sys
import subprocess

sys.stdout.reconfigure(encoding='utf-8')

def main():
    scripts = [
        "scripts/sanitize_math.py",
        "scripts/harden_gfm_math.py",
        "scripts/strip_accidental_code_indentation.py",
        "scripts/clean_relative_links.py",
    ]
    
    print("=== Running Complete Repository Formatting Suite ===\n")
    for s in scripts:
        print(f"--> Executing {s}...")
        res = subprocess.run([sys.executable, s], capture_output=True, text=True, encoding='utf-8')
        if res.stdout:
            print(res.stdout.strip())
        if res.stderr:
            print(f"Error in {s}:\n{res.stderr.strip()}", file=sys.stderr)
        print()
        
    print("=== All Formatting Tasks Completed. ===")

if __name__ == '__main__':
    main()
