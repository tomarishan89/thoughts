#!/usr/bin/env python3
"""
Convert absolute file:/// URLs in markdown files to clean relative repository paths.
"""

import os
import re
import glob

def clean_links_in_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    orig = content

    # Replace file:///c:/Users/tomar/Documents/Vidyaman/Project_writeup_1/essays/existence/...
    # with relative paths based on the current file's directory
    file_dir = os.path.dirname(file_path).replace('\\', '/')

    def replace_link(match):
        text = match.group(1)
        target = match.group(2)
        # target might be file:///c:/Users/tomar/Documents/Vidyaman/Project_writeup_1/essays/existence/draft.md#L58-L70
        # or file:///c:/Users/...
        clean_target = re.sub(r'file:///c:/Users/[^/]+/Documents/Vidyaman/Project_writeup_1/', '', target, flags=re.IGNORECASE)
        # clean_target is now relative to repo root, e.g. essays/existence/draft.md#L58-L70
        # compute relative path from file_dir to clean_target
        if '#' in clean_target:
            path_part, anchor = clean_target.split('#', 1)
            anchor = '#' + anchor
        else:
            path_part = clean_target
            anchor = ''

        rel_path = os.path.relpath(path_part, file_dir).replace('\\', '/')
        final_rel = rel_path + anchor
        return f"[{text}]({final_rel})"

    # Match [text](file:///...)
    content = re.sub(r'\[([^\]]+)\]\((file:///[^\)]+)\)', replace_link, content)

    if content != orig:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Cleaned links in: {file_path}")

def main():
    for f in glob.glob("**/*.md", recursive=True):
        if ".git" in f:
            continue
        clean_links_in_file(f)

if __name__ == "__main__":
    main()
