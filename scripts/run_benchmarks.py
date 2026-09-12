#!/usr/bin/env python3
"""
Root runner for the Layer 0 Numerical Benchmark Suite.
Executes src/explorations/existence/scripts/benchmark_suite.py with proper path resolution.
"""
import sys
import os
import subprocess

def main():
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    suite_path = os.path.join(root_dir, 'src', 'explorations', 'existence', 'scripts', 'benchmark_suite.py')
    if not os.path.exists(suite_path):
        print(f"Error: Benchmark suite not found at {suite_path}")
        sys.exit(1)
    
    cmd = [sys.executable, suite_path] + sys.argv[1:]
    res = subprocess.run(cmd, cwd=root_dir)
    sys.exit(res.returncode)

if __name__ == '__main__':
    main()
