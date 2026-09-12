#!/usr/bin/env python3
"""
build_paper.py -- Unified md -> tex -> pdf build orchestrator for research papers.

Reads BUILD.yaml manifests placed alongside each paper's source markdown files.
Each manifest declares which .md file is the source, where the .tex output lives,
and where the .pdf output lives.

Usage:
    python scripts/build_paper.py                          # build all papers
    python scripts/build_paper.py --changed                # only papers with staged/changed .md
    python scripts/build_paper.py --paper papers/tier1_cosmology
    python scripts/build_paper.py --md papers/tier1_cosmology/TIER1_MASTER_FRAMEWORK.md
    python scripts/build_paper.py --step tex               # tex only
    python scripts/build_paper.py --step pdf               # pdf only

Exit codes:
    0  all builds succeeded
    1  one or more builds failed
"""

import os, sys, re, html, base64, argparse, subprocess, tempfile, glob

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ---------------------------------------------------------------------------
# LaTeX preamble
# ---------------------------------------------------------------------------
LATEX_PREAMBLE_TEMPLATE = r"""\documentclass[11pt,a4paper]{{article}}
\usepackage[utf8]{{inputenc}}
\usepackage[T1]{{fontenc}}
\usepackage{{amsmath,amssymb,amsfonts,amsthm,mathtools,bm,physics}}
\usepackage{{geometry}}\geometry{{top=25mm,bottom=25mm,left=25mm,right=25mm}}
\usepackage{{microtype,booktabs,array,longtable,enumitem,xcolor}}
\usepackage{{hyperref}}\hypersetup{{colorlinks=true,linkcolor=blue!70!black,citecolor=red!70!black,urlcolor=blue!60!black}}
\newtheorem{{axiom}}{{Axiom}}\newtheorem{{theorem}}{{Theorem}}\newtheorem{{lemma}}{{Lemma}}
\newtheorem{{proposition}}{{Proposition}}
\theoremstyle{{definition}}\newtheorem{{definition}}{{Definition}}
\theoremstyle{{remark}}\newtheorem{{remark}}{{Remark}}
\newcommand{{\Tr}}{{\mathrm{{Tr}}}}\newcommand{{\Area}}{{\mathrm{{Area}}}}
\title{{\textbf{{{title}}}}}\author{{\textbf{{{author}}}}}\date{{\today}}
\begin{{document}}\maketitle\tableofcontents\newpage
"""

# ---------------------------------------------------------------------------
# md -> tex
# ---------------------------------------------------------------------------
def md_to_latex(md: str, title: str, author: str) -> str:
    mblocks, minlines = [], []

    def sb(m):
        i = len(mblocks); mblocks.append(m.group(1).strip()); return f"%%MB{i}%%"
    def si(m):
        i = len(minlines); minlines.append(m.group(1).strip()); return f"%%MI{i}%%"

    c = re.sub(r'\$\$(.*?)\$\$', sb, md, flags=re.DOTALL)
    c = re.sub(r'(?<!\\)\$(.*?)(?<!\\)\$', si, c)
    c = re.sub(r'```mermaid.*?```', '%% [Diagram omitted] %%', c, flags=re.DOTALL)
    c = re.sub(r'```[a-zA-Z0-9_-]*\n(.*?)```', r'\\begin{verbatim}\1\\end{verbatim}', c, flags=re.DOTALL)
    c = re.sub(r'^\s*######\s+(.*?)$', r'\\subparagraph{\1}', c, flags=re.MULTILINE)
    c = re.sub(r'^\s*#####\s+(.*?)$',  r'\\paragraph{\1}',    c, flags=re.MULTILINE)
    c = re.sub(r'^\s*####\s+(.*?)$',   r'\\subsubsection{\1}',c, flags=re.MULTILINE)
    c = re.sub(r'^\s*###\s+(.*?)$',    r'\\subsection{\1}',   c, flags=re.MULTILINE)
    c = re.sub(r'^\s*##\s+(.*?)$',     r'\\section{\1}',      c, flags=re.MULTILINE)
    c = re.sub(r'^\s*#\s+(.*?)$',      r'\\section*{\1}',     c, flags=re.MULTILINE)
    c = re.sub(r'!\[([^\]]*)\]\(([^)]+)\)', lambda m: f'%% Figure: {m.group(1)} %%', c)
    c = re.sub(r'(?<!!)\[([^\]]+)\]\(([^)]+)\)',
               lambda m: f'\\href{{{m.group(2)}}}{{{re.sub(chr(96)+r"([^`]+)"+chr(96), r"\\texttt{\1}", m.group(1))}}}', c)
    c = re.sub(r'\*\*\*(.*?)\*\*\*', r'\\textbf{\\textit{\1}}', c)
    c = re.sub(r'\*\*(.*?)\*\*',     r'\\textbf{\1}', c)
    c = re.sub(r'\*(.*?)\*',         r'\\textit{\1}', c)
    c = re.sub(r'`([^`\n]+)`',       r'\\texttt{\1}', c)
    c = re.sub(r'^> (.*?)$',         r'\\begin{quote}\1\\end{quote}', c, flags=re.MULTILINE)
    c = re.sub(r'^---$',             r'\\noindent\\rule{\\linewidth}{0.4pt}', c, flags=re.MULTILINE)

    def conv_table(m):
        rows = [r.strip() for r in m.group(0).strip().split('\n') if r.strip()]
        data = [r for r in rows if not re.match(r'^\|?\s*:?-+', r)]
        if not data: return m.group(0)
        ncols = max(1, len([x for x in data[0].split('|') if x.strip()]))
        out = [f'\\begin{{longtable}}{{{"l"*ncols}}}', '\\hline']
        for i, row in enumerate(data):
            cells = [re.sub(r'\*\*(.*?)\*\*', r'\\textbf{\1}', x.strip()) for x in row.strip('|').split('|')]
            out.append(' & '.join(cells) + r' \\')
            if i == 0: out.append('\\hline')
        out += ['\\hline', '\\end{longtable}']
        return '\n'.join(out)
    c = re.sub(r'(?:^\|.*\|[ \t]*\n)+', conv_table, c, flags=re.MULTILINE)

    c = re.sub(r'(?<!\\)%', r'\\%', c)
    c = re.sub(r'(?<!\\)&', r'\\&', c)

    for i, b in enumerate(mblocks):
        c = c.replace(f'%%MB{i}%%', f'\n\\begin{{equation}}\n{b}\n\\end{{equation}}\n')
    for i, b in enumerate(minlines):
        c = c.replace(f'%%MI{i}%%', f'${b}$')

    return LATEX_PREAMBLE_TEMPLATE.format(title=title, author=author) + '\n\n' + c + '\n\n\\end{document}\n'


# ---------------------------------------------------------------------------
# md -> pdf via headless browser
# ---------------------------------------------------------------------------
def get_browser():
    for p in [r'C:\Program Files\Google\Chrome\Application\chrome.exe',
              r'C:\Program Files (x86)\Google\Chrome\Application\chrome.exe',
              r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe',
              r'C:\Program Files\Microsoft\Edge\Application\msedge.exe',
              '/usr/bin/google-chrome', '/usr/bin/chromium-browser']:
        if os.path.exists(p): return p
    return None


def md_to_html(md: str, base_dir: str, title: str) -> str:
    mblocks, minlines, cblocks = [], [], []

    def sb(m):
        i=len(mblocks); mblocks.append(m.group(1).strip()); return f'\n\n@@MB{i}@@\n\n'
    def si(m):
        i=len(minlines); minlines.append(m.group(1).strip()); return f'@@MI{i}@@'
    def sc(m):
        i=len(cblocks); cblocks.append((m.group(1) or '', m.group(2))); return f'\n\n@@CB{i}@@\n\n'

    c = re.sub(r'\$\$(.*?)\$\$', sb, md, flags=re.DOTALL)
    c = re.sub(r'(?<!\\)\$(.*?)(?<!\\)\$', si, c)
    c = re.sub(r'```([a-zA-Z0-9_-]*)\n(.*?)```', sc, c, flags=re.DOTALL)
    c = re.sub(r'^\s*(#{1,6})\s+(.*?)$',
               lambda m: f'\n\n<h{len(m.group(1))}>{m.group(2).strip()}</h{len(m.group(1))}>\n\n',
               c, flags=re.MULTILINE)

    def rimg(m):
        cap, src = m.group(1).strip(), m.group(2).strip()
        for cand in [src, os.path.join(base_dir, src),
                     os.path.join(base_dir,'figures',os.path.basename(src))]:
            if cand and os.path.isfile(cand):
                try:
                    with open(cand,'rb') as f: b64=base64.b64encode(f.read()).decode()
                    ext=os.path.splitext(cand)[1].lstrip('.').lower()
                    if ext=='jpg': ext='jpeg'
                    uri=f'data:image/{ext};base64,{b64}'
                except: uri=f'file:///{cand.replace(os.sep,"/")}'
                break
        else: uri=src
        cap_h=f'<figcaption>{html.escape(cap)}</figcaption>' if cap else ''
        return f'\n\n<figure><img src="{uri}" alt="{html.escape(cap)}"/>{cap_h}</figure>\n\n'

    c = re.sub(r'!\[([^\]]*)\]\(([^)]+)\)', rimg, c)
    c = re.sub(r'(?<!!)\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2">\1</a>', c)
    c = re.sub(r'`([^`\n]+)`',    r'<code>\1</code>', c)
    c = re.sub(r'\*\*\*(.*?)\*\*\*', r'<strong><em>\1</em></strong>', c)
    c = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', c)
    c = re.sub(r'\*(.*?)\*',     r'<em>\1</em>', c)
    c = re.sub(r'^> (.*?)$',     r'<blockquote>\1</blockquote>', c, flags=re.MULTILINE)
    c = re.sub(r'^---$',         '<hr/>', c, flags=re.MULTILINE)

    parts = []
    for p in c.split('\n\n'):
        p = p.strip()
        if not p: continue
        if p.startswith('@@MB') and p.endswith('@@'):
            parts.append(f"<div class='md'>{p}</div>")
        elif p.startswith(('@@CB','<h','<hr','<blockquote','<figure')):
            parts.append(p)
        elif p.startswith('|'):
            rows=[r.strip() for r in p.split('\n') if r.strip()]
            th='<table><tr>'+''.join(f'<th>{x.strip()}</th>' for x in rows[0].strip('|').split('|') if x.strip())+'</tr>'
            tb=''.join('<tr>'+''.join(f'<td>{x.strip()}</td>' for x in r.strip('|').split('|'))+'</tr>' for r in rows[2:])
            parts.append(th+tb+'</table>')
        elif re.match(r'^(\*|-|\d+\.)\s',p.split('\n')[0]):
            items=''.join(f'<li>{re.sub(r"^(?:\*|-|\d+\.)\s+","",l.strip())}</li>' for l in p.split('\n') if l.strip())
            parts.append(f'<ul>{items}</ul>')
        else:
            parts.append(f'<p>{p.replace(chr(10)," ")}</p>')

    body='\n'.join(parts)
    for i,(lang,code) in enumerate(cblocks):
        body=body.replace(f'@@CB{i}@@',f'<pre><code class="language-{lang}">{html.escape(code)}</code></pre>')
    for i,b in enumerate(mblocks): body=body.replace(f'@@MB{i}@@',f'$${b}$$')
    for i,b in enumerate(minlines): body=body.replace(f'@@MI{i}@@',f'${b}$')

    CSS="""
@page{size:letter;margin:18mm 18mm 22mm 18mm}
body{font-family:'Cambria','Georgia',serif;font-size:10pt;line-height:1.55;color:#1a1a1a;max-width:950px;margin:0 auto;padding:25px}
h1{font-size:17pt;font-weight:bold;color:#0b1d3a;border-bottom:2px solid #0b1d3a;padding-bottom:8px;text-align:center;margin-top:15px}
h2{font-size:13pt;color:#1b263b;border-bottom:1px solid #ced4da;margin-top:22px;page-break-after:avoid}
h3{font-size:11pt;color:#2b2d42;margin-top:16px;page-break-after:avoid}
h4{font-size:10pt;font-style:italic;color:#415a77;page-break-after:avoid}
p{margin-bottom:8px;text-align:justify}
.md{margin:14px 0;text-align:center}
figure{margin:22px auto;text-align:center;page-break-inside:avoid}
figure img{max-width:100%;border:1px solid #ced4da;border-radius:4px}
figcaption{font-size:9.5pt;color:#495057;font-style:italic}
table{width:100%;border-collapse:collapse;font-size:8.5pt;margin:8px 0}
th,td{border:1px solid #ced4da;padding:5px 8px;text-align:left}
th{background:#e9ecef;font-weight:bold}tr:nth-child(even){background:#f8f9fa}
pre{background:#f8f9fa;padding:8px 12px;border-radius:4px;font-size:8pt;white-space:pre-wrap;border:1px solid #dee2e6;page-break-inside:avoid}
blockquote{border-left:3.5px solid #2b5c8f;background:#f4f6f9;margin:12px 0;padding:8px 14px;font-size:9.5pt}
hr{border:none;border-top:1px solid #ced4da;margin:16px 0}
ul{margin:8px 0 12px 20px}li{margin-bottom:4px}
"""
    MJS="""window.MathJax={tex:{inlineMath:[['$','$']],displayMath:[['$$','$$']],processEscapes:true,packages:{'[+]':['ams','physics','mathtools','color','bbox']}},options:{skipHtmlTags:['script','noscript','style','textarea','pre','code']},chtml:{fontURL:'https://cdn.jsdelivr.net/npm/mathjax@3/es5/output/chtml/fonts/woff-v2'}};"""
    return f"""<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8"><title>{html.escape(title)}</title>
<script>{MJS}</script><script src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js" id="MathJax-script" async></script>
<style>{CSS}</style></head><body>{body}</body></html>"""


def generate_pdf(md_path: str, pdf_path: str) -> bool:
    browser = get_browser()
    if not browser:
        print('[WARN] No Chrome/Edge found -- skipping PDF generation.')
        return False
    with open(md_path, encoding='utf-8') as f: md_text = f.read()
    title = os.path.splitext(os.path.basename(md_path))[0].replace('_',' ')
    html_content = md_to_html(md_text, os.path.dirname(os.path.abspath(md_path)), title)
    os.makedirs(os.path.dirname(os.path.abspath(pdf_path)), exist_ok=True)
    with tempfile.NamedTemporaryFile('w', delete=False, suffix='.html', encoding='utf-8') as t:
        t.write(html_content); tmp = t.name
    try:
        res = subprocess.run(
            [browser,'--headless=new','--disable-gpu','--no-sandbox',
             '--virtual-time-budget=25000',
             f'--print-to-pdf={os.path.abspath(pdf_path)}',
             f'file:///{os.path.abspath(tmp).replace(os.sep,"/")}'],
            capture_output=True, text=True, timeout=180)
        if os.path.exists(pdf_path) and os.path.getsize(pdf_path) > 0:
            print(f'[OK] PDF -> {os.path.relpath(pdf_path, REPO_ROOT)} ({os.path.getsize(pdf_path)//1024} KB)')
            return True
        print(f'[FAIL] PDF generation failed:\n{res.stderr[:300]}')
        return False
    finally:
        if os.path.exists(tmp): os.remove(tmp)


# ---------------------------------------------------------------------------
# Manifest loader (simple YAML-free parser for BUILD.yaml)
# ---------------------------------------------------------------------------
def parse_build_yaml(build_file: str) -> list:
    """
    Parse BUILD.yaml without requiring pyyaml.
    Format supported:
      papers:
        - name: "..."
          md: relative/path.md
          tex: relative/path.tex
          pdf: relative/path.pdf
          author: "..."
          title: "..."
    """
    with open(build_file, encoding='utf-8') as f:
        lines = f.readlines()

    entries, current = [], {}
    for line in lines:
        stripped = line.rstrip()
        # New list item
        if re.match(r'^\s*-\s+name:', stripped):
            if current: entries.append(current)
            current = {'name': re.sub(r'^\s*-\s+name:\s*"?([^"]+)"?\s*$', r'\1', stripped).strip()}
        elif current:
            m = re.match(r'^\s+(md|tex|pdf|author|title):\s*"?([^"]+)"?\s*$', stripped)
            if m:
                current[m.group(1)] = m.group(2).strip().strip('"')
    if current:
        entries.append(current)
    return entries


def load_manifests(paper_dir=None) -> list:
    if paper_dir:
        patterns = [os.path.join(REPO_ROOT, paper_dir, 'BUILD.yaml')]
    else:
        patterns = glob.glob(os.path.join(REPO_ROOT, 'papers', '**', 'BUILD.yaml'), recursive=True)

    manifests = []
    for build_file in patterns:
        if not os.path.exists(build_file): continue
        paper_root = os.path.dirname(build_file)
        for p in parse_build_yaml(build_file):
            md  = os.path.normpath(os.path.join(paper_root, p.get('md', '')))
            tex = os.path.normpath(os.path.join(paper_root, p.get('tex', '')))
            pdf = os.path.normpath(os.path.join(paper_root, p.get('pdf', '')))
            manifests.append({'name': p.get('name','unnamed'), 'md': md, 'tex': tex,
                               'pdf': pdf, 'author': p.get('author','Ishan Tomar'),
                               'title': p.get('title','')})
    return manifests


def get_changed_md_files() -> set:
    paths = set()
    for cmd in [['git','diff','--name-only','HEAD'], ['git','diff','--cached','--name-only']]:
        r = subprocess.run(cmd, cwd=REPO_ROOT, capture_output=True, text=True)
        for line in r.stdout.splitlines():
            if line.strip().endswith('.md'):
                paths.add(os.path.normpath(os.path.join(REPO_ROOT, line.strip())))
    return paths


# ---------------------------------------------------------------------------
# Build runner
# ---------------------------------------------------------------------------
def build_paper(m: dict, step: str='all') -> bool:
    name = m['name']
    title = m['title'] or os.path.splitext(os.path.basename(m['md']))[0].replace('_',' ')
    ok = True

    if step in ('all','tex'):
        if not os.path.exists(m['md']):
            print(f'[SKIP] {name}: .md not found'); return False
        print(f'[BUILD] {name}: md -> tex')
        with open(m['md'], encoding='utf-8') as f: md_text = f.read()
        tex = md_to_latex(md_text, title=title, author=m['author'])
        os.makedirs(os.path.dirname(m['tex']), exist_ok=True)
        with open(m['tex'],'w',encoding='utf-8') as f: f.write(tex)
        print(f'[OK] tex -> {os.path.relpath(m["tex"], REPO_ROOT)}')

    if step in ('all','pdf'):
        if not os.path.exists(m['md']):
            print(f'[SKIP] {name}: .md not found'); return False
        print(f'[BUILD] {name}: md -> pdf')
        ok = generate_pdf(m['md'], m['pdf']) and ok

    return ok


def main():
    p = argparse.ArgumentParser(description='Build research papers: md -> tex -> pdf')
    p.add_argument('--changed', action='store_true', help='Only build papers whose .md changed vs HEAD')
    p.add_argument('--paper', metavar='DIR', help='Directory relative to repo root containing BUILD.yaml')
    p.add_argument('--md', metavar='FILE', help='Build only paper with this source .md')
    p.add_argument('--step', choices=['all','tex','pdf'], default='all')
    args = p.parse_args()

    manifests = load_manifests(args.paper)
    if not manifests:
        print('[WARN] No BUILD.yaml manifests found.'); return

    if args.md:
        target = os.path.normpath(os.path.join(REPO_ROOT, args.md))
        manifests = [m for m in manifests if m['md'] == target]
        if not manifests: print(f'[WARN] No manifest for {args.md}'); return

    if args.changed:
        changed = get_changed_md_files()
        manifests = [m for m in manifests if m['md'] in changed]
        if not manifests: print('[INFO] No manifest .md files changed.'); return

    failures = sum(0 if build_paper(m, args.step) else 1 for m in manifests)
    if failures:
        print(f'\n[FAIL] {failures}/{len(manifests)} paper(s) failed.')
        sys.exit(1)
    else:
        print(f'\n[DONE] {len(manifests)} paper(s) built successfully.')

if __name__ == '__main__':
    main()