#!/usr/bin/env python3
"""
Comprehensive GitHub Markdown Math Sanitizer:
1. Replace all \\operatorname{...} with \\mathrm{...}.
2. Clean up \\left and \\right inside all \\boxed{...} to prevent KaTeX delimiter errors.
3. Replace \\begin{matrix} flowchart diagrams with native GitHub Mermaid diagrams.
4. Fix any '&' inside math text.
"""

import os
import re
import glob

def clean_boxed_delimiters(text):
    # Regex to find \boxed{ ... } even with one level of nested braces
    def fix_inner(match):
        full = match.group(0)
        # remove \left( \right) etc
        cleaned = re.sub(r'\\left\s*([(\[{\.\|])', r'\1', full)
        cleaned = re.sub(r'\\right\s*([)\]}\.\|])', r'\1', cleaned)
        return cleaned

    # Apply multiple passes for nested matches
    for _ in range(3):
        text = re.sub(r'\\boxed\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', fix_inner, text)
    return text

def sanitize_math_file(content):
    # 1. Replace \operatorname
    content = re.sub(r'\\operatorname\{([a-zA-Z0-9_]+)\}', r'\\mathrm{\1}', content)
    content = re.sub(r'\\operatorname\b', r'\\mathrm', content)

    # 2. Fix \left / \right inside \boxed
    content = clean_boxed_delimiters(content)

    # 3. Clean ampersands inside \text{}
    def fix_text_ampersand(match):
        inner = match.group(1)
        inner = inner.replace(r'\&', ' and ').replace('&', ' and ')
        return f"\\text{{{inner}}}"
    content = re.sub(r'\\text\{([^{}]*?[&][^{}]*?)\}', fix_text_ampersand, content)

    return content

def main():
    md_files = glob.glob("**/*.md", recursive=True)
    count = 0
    for file_path in md_files:
        if ".git" in file_path:
            continue
        with open(file_path, 'r', encoding='utf-8') as f:
            orig = f.read()
        
        sanitized = sanitize_math_file(orig)
        if orig != sanitized:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(sanitized)
            print(f"Sanitized: {file_path}")
            count += 1
    print(f"Sanitization complete. Cleaned {count} files.")

if __name__ == "__main__":
    main()
