#!/usr/bin/env python3
"""
Generate publication-quality PDFs from Markdown files using MathJax vector math and Headless Chrome/Edge.
Usage:
    python scripts/generate_pdf.py essays/existence/draft.md
    python scripts/generate_pdf.py --all
"""

import sys
import os
import re
import argparse
import subprocess
import tempfile
import html

def get_browser_path():
    """Locate Chrome or Edge executable on Windows/Linux/macOS."""
    candidates = [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
        "/usr/bin/google-chrome",
        "/usr/bin/chromium-browser",
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    ]
    for c in candidates:
        if os.path.exists(c):
            return c
    return None

def markdown_to_html_academic(md_content, title="Academic Paper"):
    """
    Convert Markdown content into a self-contained HTML page
    with MathJax 3 support and publication-ready academic styling.
    """
    math_blocks = []
    def save_block_math(match):
        idx = len(math_blocks)
        math_blocks.append(match.group(0))
        return f"<!--MATH_BLOCK_{idx}-->"
    
    math_inlines = []
    def save_inline_math(match):
        idx = len(math_inlines)
        math_inlines.append(match.group(0))
        return f"<!--MATH_INLINE_{idx}-->"
    
    # Save $$ ... $$
    content = re.sub(r'\$\$(.*?)\$\$', save_block_math, md_content, flags=re.DOTALL)
    # Save $ ... $ (excluding escaped \$)
    content = re.sub(r'(?<!\\)\$(.*?)(?<!\\)\$', save_inline_math, content)
    
    # Escape raw HTML characters outside math
    content = html.escape(content)
    
    # Restore math blocks
    for idx, block in enumerate(math_blocks):
        content = content.replace(f"&lt;!--MATH_BLOCK_{idx}--&gt;", block)
    for idx, inline in enumerate(math_inlines):
        content = content.replace(f"&lt;!--MATH_INLINE_{idx}--&gt;", inline)

    # Process headings
    content = re.sub(r'^# (.*?)$', r'<h1>\1</h1>', content, flags=re.MULTILINE)
    content = re.sub(r'^## (.*?)$', r'<h2>\1</h2>', content, flags=re.MULTILINE)
    content = re.sub(r'^### (.*?)$', r'<h3>\1</h3>', content, flags=re.MULTILINE)
    content = re.sub(r'^#### (.*?)$', r'<h4>\1</h4>', content, flags=re.MULTILINE)

    # Bold & Italic
    content = re.sub(r'\*\*\*(.*?)\*\*\*', r'<strong><em>\1</em></strong>', content)
    content = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', content)
    content = re.sub(r'\*(.*?)\*', r'<em>\1</em>', content)

    # Blockquotes
    content = re.sub(r'^> (.*?)$', r'<blockquote>\1</blockquote>', content, flags=re.MULTILINE)
    
    # Code blocks
    content = re.sub(r'```(.*?)```', r'<pre><code>\1</code></pre>', content, flags=re.DOTALL)

    # Horizontal rules
    content = re.sub(r'^---$', r'<hr/>', content, flags=re.MULTILINE)

    # Paragraphs and Tables
    paragraphs = content.split('\n\n')
    formatted_paras = []
    for p in paragraphs:
        p = p.strip()
        if not p:
            continue
        if p.startswith('<h') or p.startswith('<pre') or p.startswith('<hr') or p.startswith('<blockquote') or p.startswith('$$'):
            formatted_paras.append(p)
        elif p.startswith('|'):
            # Table formatting
            rows = [r.strip() for r in p.split('\n') if r.strip()]
            table_html = "<div class='table-container'><table>"
            for i, r in enumerate(rows):
                if '---' in r:
                    continue
                cells = [c.strip() for c in r.strip('|').split('|')]
                tag = 'th' if i == 0 else 'td'
                table_html += "<tr>" + "".join(f"<{tag}>{c}</{tag}>" for c in cells) + "</tr>"
            table_html += "</table></div>"
            formatted_paras.append(table_html)
        else:
            formatted_paras.append(f"<p>{p.replace(chr(10), '<br/>')}</p>")
    
    body = "\n\n".join(formatted_paras)

    template = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>{html.escape(title)}</title>
    <script>
    MathJax = {{
        tex: {{
            inlineMath: [['$', '$']],
            displayMath: [['$$', '$$']],
            processEscapes: true
        }},
        chtml: {{
            fontURL: 'https://cdn.jsdelivr.net/npm/mathjax@3/es5/output/chtml/fonts/woff-v2'
        }}
    }};
    </script>
    <script src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js" id="MathJax-script" async></script>
    <style>
        @page {{
            size: letter;
            margin: 18mm 18mm 22mm 18mm;
        }}
        body {{
            font-family: 'Cambria', 'Georgia', 'Times New Roman', serif;
            font-size: 10.5pt;
            line-height: 1.55;
            color: #1a1a1a;
            max-width: 950px;
            margin: 0 auto;
            padding: 25px;
            background: #fff;
        }}
        h1 {{
            font-size: 18pt;
            font-weight: bold;
            color: #0b1d3a;
            border-bottom: 2px solid #0b1d3a;
            padding-bottom: 8px;
            margin-top: 20px;
            margin-bottom: 16px;
            text-align: center;
        }}
        h2 {{
            font-size: 13.5pt;
            font-weight: bold;
            color: #1b263b;
            border-bottom: 1px solid #ced4da;
            padding-bottom: 4px;
            margin-top: 20px;
            margin-bottom: 12px;
            page-break-after: avoid;
        }}
        h3 {{
            font-size: 11.5pt;
            font-weight: bold;
            color: #2b2d42;
            margin-top: 16px;
            margin-bottom: 8px;
            page-break-after: avoid;
        }}
        h4 {{
            font-size: 10.5pt;
            font-weight: bold;
            font-style: italic;
            color: #415a77;
            margin-top: 12px;
            margin-bottom: 6px;
            page-break-after: avoid;
        }}
        p {{
            margin-bottom: 10px;
            text-align: justify;
            text-justify: inter-word;
        }}
        blockquote {{
            border-left: 3.5px solid #2b5c8f;
            background: #f4f6f9;
            margin: 12px 0;
            padding: 10px 16px;
            color: #2b2d42;
            font-size: 10pt;
            border-radius: 0 4px 4px 0;
        }}
        pre {{
            background: #f8f9fa;
            padding: 10px 14px;
            border-radius: 4px;
            font-family: 'Cascadia Code', 'Consolas', 'Courier New', monospace;
            font-size: 8.5pt;
            overflow-x: auto;
            border: 1px solid #dee2e6;
            margin: 12px 0;
        }}
        .table-container {{
            margin: 16px 0;
            overflow-x: auto;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 9pt;
            margin: 10px 0;
        }}
        th, td {{
            border: 1px solid #ced4da;
            padding: 6px 9px;
            text-align: left;
        }}
        th {{
            background-color: #e9ecef;
            font-weight: bold;
            color: #212529;
        }}
        tr:nth-child(even) {{
            background-color: #f8f9fa;
        }}
        hr {{
            border: none;
            border-top: 1px solid #ced4da;
            margin: 18px 0;
        }}
        .MathJax {{
            font-size: 102% !important;
        }}
        @media print {{
            body {{
                padding: 0;
                background: none;
            }}
            .table-container, pre, blockquote {{
                page-break-inside: avoid;
            }}
        }}
    </style>
</head>
<body>
    {body}
</body>
</html>"""
    return template

def convert_md_to_pdf(input_md_path, output_pdf_path=None):
    if not os.path.exists(input_md_path):
        print(f"Error: Input file '{input_md_path}' does not exist.")
        return False
    
    browser_path = get_browser_path()
    if not browser_path:
        print("Error: Chrome or Microsoft Edge browser not found.")
        return False
    
    if output_pdf_path is None:
        base = os.path.splitext(os.path.basename(input_md_path))[0]
        os.makedirs("pdfs", exist_ok=True)
        output_pdf_path = os.path.abspath(os.path.join("pdfs", f"{base}.pdf"))
    else:
        output_pdf_path = os.path.abspath(output_pdf_path)
        os.makedirs(os.path.dirname(output_pdf_path), exist_ok=True)
    
    with open(input_md_path, 'r', encoding='utf-8') as f:
        md_text = f.read()
    
    title = os.path.splitext(os.path.basename(input_md_path))[0].replace('_', ' ').title()
    html_content = markdown_to_html_academic(md_text, title=title)
    
    with tempfile.NamedTemporaryFile('w', delete=False, suffix='.html', encoding='utf-8') as temp_html:
        temp_html.write(html_content)
        temp_html_path = temp_html.name
    
    try:
        cmd = [
            browser_path,
            "--headless=new",
            "--disable-gpu",
            "--no-sandbox",
            "--virtual-time-budget=3000",
            f"--print-to-pdf={output_pdf_path}",
            f"file:///{os.path.abspath(temp_html_path).replace(os.sep, '/')}"
        ]
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=25)
        if os.path.exists(output_pdf_path) and os.path.getsize(output_pdf_path) > 0:
            print(f"[OK] PDF Generated: {os.path.relpath(output_pdf_path)} ({os.path.getsize(output_pdf_path) // 1024} KB)")
            return True
        else:
            print(f"[FAIL] Failed to generate PDF for {input_md_path}. Stderr: {res.stderr}")
            return False
    finally:
        if os.path.exists(temp_html_path):
            os.remove(temp_html_path)

def main():
    parser = argparse.ArgumentParser(description="Convert Markdown files to publication-grade PDFs.")
    parser.add_argument("file", nargs="?", help="Specific markdown file to convert")
    parser.add_argument("--all", action="store_true", help="Convert all main essays in the repository")
    parser.add_argument("--output", "-o", help="Custom output PDF file path")
    args = parser.parse_args()

    if args.all:
        target_files = [
            "essays/existence/draft.md",
            "essays/existence/interpretation.md",
            "essays/existence/dialogues_and_explorations.md",
            "essays/existence/interpretations/core_ontology_and_dharma.md",
            "essays/existence/interpretations/cosmology_and_brahmanda.md",
            "essays/existence/interpretations/biophysics_and_syncytia.md",
            "essays/existence/interpretations/cognitive_and_psychology.md",
            "essays/existence/interpretations/societal_and_institutional.md",
        ]
        print(f"Compiling {len(target_files)} papers to PDF in pdfs/ folder...\n")
        for f in target_files:
            if os.path.exists(f):
                convert_md_to_pdf(f)
    elif args.file:
        convert_md_to_pdf(args.file, args.output)
    else:
        print("Please provide a markdown file or use --all.")
        parser.print_help()

if __name__ == "__main__":
    main()
