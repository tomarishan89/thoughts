#!/usr/bin/env python3
"""Build Cursor/VS Code snippets from glossary keys for \\sa{...} insertion.

Writes .vscode/sa.code-snippets.

- Type ``sa-<key>`` (e.g. ``sa-moksha``) to insert full ``\\sa{moksha}``.
- Inside already-open ``\\sa{...}``, accept the bare key completion (body is just the key) to avoid a double ``}``.

Examples:
  python scripts/build_sa_completions.py
  python scripts/build_sa_completions.py --chapter essays/01-darshan-of-kundalini
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

_SCRIPTS = Path(__file__).resolve().parent
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

from expand_sa import parse_glossary_rows, project_root, resolve_chapter  # noqa: E402


def load_all_rows(root: Path, chapter: str | None) -> dict[str, dict[str, str]]:
    """key -> row; chapter overrides master."""
    by_key: dict[str, dict[str, str]] = {}
    master_path = root / "essays" / "interospection_01" / "lexicons" / "glossary.md"
    if not master_path.exists():
        master_path = root / "lexicons" / "glossary.md"
    for row in parse_glossary_rows(master_path):
        by_key[row["key"]] = row
    if chapter:
        chapter_dir = resolve_chapter(chapter, root)
        for row in parse_glossary_rows(chapter_dir / "glossary.md"):
            by_key[row["key"]] = row
    else:
        essays = root / "essays"
        if essays.is_dir():
            for child in essays.iterdir():
                if child.is_dir():
                    for row in parse_glossary_rows(child / "glossary.md"):
                        by_key[row["key"]] = row
    return by_key


def build_snippets(rows: dict[str, dict[str, str]]) -> dict:
    """Two snippets per key to avoid \\sa{key}} when braces auto-close.

    - sa-{key}: full \\sa{key} (type sa-moksha from scratch)
    - sakey-{key}: bare key only (type inside already-open \\sa{...})
    """
    snippets: dict = {}
    for key, row in sorted(rows.items()):
        dev = row.get("dev", "")
        gloss = row.get("gloss", "")
        desc = f"{dev}" + (f" — {gloss}" if gloss else "")
        snippets[f"sa-{key}"] = {
            "prefix": [f"sa-{key}"],
            "body": [f"\\sa{{{key}}}"],
            "description": desc or key,
            "scope": "markdown",
        }
        snippets[f"sakey-{key}"] = {
            "prefix": [key],
            "body": [key],
            "description": (desc + " (inside \\sa{})") if desc else f"{key} (inside \\sa{{}})",
            "scope": "markdown",
        }
    return snippets


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--chapter",
        help="Include/override with this chapter glossary (default: all chapters)",
    )
    parser.add_argument(
        "-o",
        "--output",
        help="Output path (default: .vscode/sa.code-snippets)",
    )
    args = parser.parse_args(argv)

    root = project_root()
    rows = load_all_rows(root, args.chapter)
    snippets = build_snippets(rows)

    out = Path(args.output) if args.output else root / ".vscode" / "sa.code-snippets"
    if not out.is_absolute():
        out = (root / out).resolve()
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(
        json.dumps(snippets, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"Wrote {out} ({len(snippets)} snippets)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
