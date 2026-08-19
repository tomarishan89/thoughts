#!/usr/bin/env python3
"""
Install Git pre-commit hook into .git/hooks/pre-commit.
Works seamlessly across Windows (Git Bash/PowerShell), Linux, and macOS.
"""

import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

HOOK_CONTENT = """#!/bin/sh
# Git pre-commit hook for Vidyaman Research Repository
# Lints all staged Markdown files for LaTeX syntax, GFM collisions, and broken links.

echo "[PRE-COMMIT] Running Markdown and LaTeX linter on staged files..."
python scripts/lint_markdown.py --staged

RESULT=$?
if [ $RESULT -ne 0 ]; then
    echo ""
    echo "❌ [PRE-COMMIT BLOCKED] Commit rejected due to Markdown/LaTeX linter errors."
    echo "💡 Hint: Run 'mise run format' or check the line numbers reported above."
    exit 1
fi

echo "[PRE-COMMIT] All staged checks passed! Proceeding with commit."
exit 0
"""

def install_hook():
    git_dir = ".git"
    if not os.path.isdir(git_dir):
        print("Error: .git directory not found. Please run from repository root.")
        sys.exit(1)
        
    hooks_dir = os.path.join(git_dir, "hooks")
    os.makedirs(hooks_dir, exist_ok=True)
    
    hook_path = os.path.join(hooks_dir, "pre-commit")
    
    # Write LF line endings for POSIX / Git Bash compatibility
    with open(hook_path, "wb") as f:
        f.write(HOOK_CONTENT.replace("\r\n", "\n").encode("utf-8"))
        
    try:
        # Make executable on Unix-like filesystems
        os.chmod(hook_path, 0o755)
    except Exception:
        pass
        
    print(f"✅ Git pre-commit hook installed successfully at: {hook_path}")

if __name__ == '__main__':
    install_hook()
