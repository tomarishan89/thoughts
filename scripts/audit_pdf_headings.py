#!/usr/bin/env python3
"""
PDF Heading & Publication Audit Script.
Scans compiled PDF files to verify that zero raw Markdown heading tokens
(e.g., '#', '##', '###', '####', '#####', '######') appear in rendered text.
Also validates absence of forbidden institutional affiliations ('Vidyaman').
"""
import os
import sys
import glob
import re
import argparse
import pymupdf as fitz

sys.stdout.reconfigure(encoding='utf-8')

def audit_pdf(pdf_path):
    issues = []
    doc = fitz.open(pdf_path)
    total_pages = len(doc)
    
    for page_num in range(total_pages):
        page = doc[page_num]
        text = page.get_text()
        lines = text.splitlines()
        
        for line_idx, line in enumerate(lines):
            stripped = line.strip()
            # Check for raw markdown headings: ##, ###, ####, #####, ######
            # or # followed by title-like text (excluding obvious code comments)
            m = re.match(r'^(#{1,6})\s+(.*)$', stripped)
            if m:
                hashes = m.group(1)
                heading_text = m.group(2)
                # Ignore code comment lines inside bash blocks
                if hashes == '#' and any(heading_text.startswith(kw) for kw in ['or directly', 'python ', 'bash ', 'cd ', 'pip ', '!']):
                    continue
                issues.append((page_num + 1, hashes, heading_text[:80]))
            
            # Check for forbidden institutional affiliation
            if 'vidyaman' in stripped.lower():
                issues.append((page_num + 1, "FORBIDDEN_AFFILIATION", stripped[:80]))
                
    doc.close()
    return total_pages, issues

def main():
    parser = argparse.ArgumentParser(description="Audit PDFs for raw markdown headings and forbidden affiliations.")
    parser.add_argument("pdf_files", nargs="*", help="Specific PDF files to audit")
    args = parser.parse_args()
    
    if args.pdf_files:
        files = args.pdf_files
    else:
        files = sorted(glob.glob("**/pdfs/*.pdf", recursive=True))
        
    if not files:
        print("[AUDIT] No PDF files found to audit.")
        sys.exit(0)
        
    print(f"[AUDIT] Scanning {len(files)} PDF file(s) for raw markdown headings...\n")
    total_issues = 0
    
    for f in files:
        try:
            pages, issues = audit_pdf(f)
            if issues:
                print(f"FAILED: {f} ({pages} pages, {len(issues)} issue(s)):")
                for pno, itype, snippet in issues:
                    print(f"  Page {pno:3d} [{itype}]: {snippet}")
                total_issues += len(issues)
            else:
                print(f"PASSED: {f} ({pages} pages, 0 heading issues)")
        except Exception as e:
            print(f"ERROR reading {f}: {e}")
            total_issues += 1
            
    print("-" * 60)
    if total_issues == 0:
        print(f"[AUDIT SUCCESS] All PDF files verified! Zero raw markdown headings found.")
        sys.exit(0)
    else:
        print(f"[AUDIT FAILED] Found {total_issues} raw heading/formatting issue(s) across PDFs.")
        sys.exit(1)

if __name__ == '__main__':
    main()
