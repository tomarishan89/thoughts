#!/usr/bin/env python3
"""
Pre-commit guard to prevent accidental commits of PDF binary files.

Why this guard exists:
- PDF binaries cause repository bloat because Git cannot store diffs of binary files.
- The canonical sources of truth are Markdown (*.md) and LaTeX (*.tex) files.
- Compiled PDFs are milestone-only build artifacts.

To allow an intentional milestone PDF commit:
  - Linux/macOS/Git Bash: ALLOW_PDF_COMMIT=1 git commit -m "..."
  - Windows PowerShell:   $env:ALLOW_PDF_COMMIT='1'; git commit -m "..."; Remove-Item env:ALLOW_PDF_COMMIT
  - Or bypass hook:       git commit --no-verify
"""

import os
import sys
import subprocess

sys.stdout.reconfigure(encoding='utf-8')

def check_staged_pdfs():
    # Allow override via environment variable
    if os.environ.get("ALLOW_PDF_COMMIT", "").strip().lower() in ("1", "true", "yes"):
        print("[PRE-COMMIT] ALLOW_PDF_COMMIT is set. Allowing staged PDF binaries.")
        return 0

    try:
        res = subprocess.run(
            ["git", "diff", "--cached", "--name-only", "--diff-filter=ACM"],
            capture_output=True,
            text=True,
            check=True
        )
        staged_files = [f.strip() for f in res.stdout.splitlines() if f.strip().lower().endswith('.pdf')]
        
        if staged_files:
            print("\n" + "=" * 72)
            print("❌ [PRE-COMMIT BLOCKED] Accidental PDF binary commit prevented!")
            print("=" * 72)
            print("The following staged PDF files were detected:")
            for f in staged_files:
                print(f"   • {f}")
            print("\n[REPOSITORY POLICY]")
            print("  PDF files are compiled binary objects that bloat the .git history.")
            print("  The canonical sources of truth are Markdown (*.md) and LaTeX (*.tex).")
            print("  Please do not commit PDFs on routine edits.")
            print("\n[HOW TO RESOLVE]")
            print("  1. Unstage the PDF files:")
            print("     git restore --staged essays/existence/pdfs/*.pdf")
            print("  2. If this is an INTENTIONAL milestone/release build, bypass this check:")
            print("     ALLOW_PDF_COMMIT=1 git commit")
            print("     (PowerShell: $env:ALLOW_PDF_COMMIT='1'; git commit)")
            print("=" * 72 + "\n")
            return 1
            
    except Exception as e:
        print(f"[PRE-COMMIT] Warning: Could not check for staged PDF files: {e}")
        
    return 0

if __name__ == '__main__':
    sys.exit(check_staged_pdfs())
