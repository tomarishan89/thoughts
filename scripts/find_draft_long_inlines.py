#!/usr/bin/env python3
"""
Find all long or multi-operator inline math expressions in draft.md.
"""

import sys
import re

sys.stdout.reconfigure(encoding='utf-8')

with open('essays/existence/draft.md', 'r', encoding='utf-8') as f:
    lines = f.read().splitlines()

in_code = False
in_display = False

for i, line in enumerate(lines):
    stripped = line.strip()
    if stripped.startswith('```'):
        in_code = not in_code
        continue
    if in_code:
        continue
    if stripped.startswith('$$'):
        if stripped == '$$':
            in_display = not in_display
        continue
    if in_display or (stripped.startswith('$$') and stripped.endswith('$$')):
        continue
    
    inlines = re.findall(r'(?<!\\)\$(.*?)(?<!\\)\$', line)
    for expr in inlines:
        has_ops = bool(re.search(r'\\(int|sum|prod|oint|frac|sqrt|lim|equiv|exp)\b', expr))
        if len(expr) > 60 or (has_ops and len(expr) > 35) or expr.count('_') >= 3:
            print(f"Line {i+1:4d} (len {len(expr):3d}, {expr.count('_')} underscores): ${expr}$")
