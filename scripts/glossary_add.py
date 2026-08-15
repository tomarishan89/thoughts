#!/usr/bin/env python3
"""Add or update a \\sa{key} row in the master or chapter glossary.

Examples:
  python scripts/glossary_add.py --key atman --dev आत्मन --iast atman --gloss self
  python scripts/glossary_add.py --key foo --dev फू --chapter essays/01-darshan-of-kundalini
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

_SCRIPTS = Path(__file__).resolve().parent
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

from expand_sa import project_root, resolve_chapter  # noqa: E402

HEADER = (
    "| key | Devanagari | IAST | gloss | dhatu | analysis | sense_source | notes |"
)
SEPARATOR = (
    "|-----|------------|------|-------|-------|----------|--------------|-------|"
)


def _escape_cell(value: str) -> str:
    return value.replace("|", "\\|").strip()


def _row(
    key: str,
    dev: str,
    iast: str,
    gloss: str,
    dhatu: str,
    analysis: str,
    sense_source: str,
    notes: str,
) -> str:
    cells = [key, dev, iast, gloss, dhatu, analysis, sense_source, notes]
    return "| " + " | ".join(_escape_cell(c) for c in cells) + " |"


def _ensure_table(path: Path, title: str) -> None:
    if path.is_file():
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        f"# {title}\n\n{HEADER}\n{SEPARATOR}\n",
        encoding="utf-8",
    )


def upsert_row(path: Path, new_row: str, key: str, force: bool) -> str:
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    key_lower = key.lower()
    out: list[str] = []
    found = False
    has_header = False

    for line in lines:
        stripped = line.strip()
        if stripped.startswith("|") and "key" in stripped.lower() and "Devanagari" in stripped:
            has_header = True
            out.append(line)
            continue
        if stripped.startswith("|"):
            cells = [c.strip() for c in stripped.strip("|").split("|")]
            row_key = cells[0] if cells else ""
            is_sep = bool(row_key) and set(row_key) <= {"-", ":"}
            if row_key and not is_sep and row_key.lower() == key_lower:
                if not force:
                    raise SystemExit(
                        f"Key already exists in {path}: {key}\n"
                        "Re-run with --force to overwrite."
                    )
                out.append(new_row)
                found = True
                continue
        out.append(line)

    action = "added"
    if not has_header:
        if out and out[-1].strip():
            out.append("")
        out.extend([HEADER, SEPARATOR, new_row])
    elif found:
        action = "updated"
    else:
        insert_at = len(out)
        for i in range(len(out) - 1, -1, -1):
            if out[i].strip().startswith("|"):
                insert_at = i + 1
                break
        out.insert(insert_at, new_row)

    path.write_text("\n".join(out) + "\n", encoding="utf-8")
    return action


def add_entry(
    *,
    key: str,
    dev: str,
    iast: str = "",
    gloss: str = "",
    dhatu: str = "",
    analysis: str = "",
    sense_source: str = "",
    notes: str = "",
    chapter: str | Path | None = None,
    force: bool = False,
    root: Path | None = None,
) -> tuple[str, Path]:
    """Add or update a glossary row. Returns (action, path)."""
    root = root or project_root()
    if chapter:
        chapter_dir = resolve_chapter(str(chapter), root)
        path = chapter_dir / "glossary.md"
        _ensure_table(path, f"Chapter glossary - {chapter_dir.name}")
    else:
        path = root / "lexicons" / "glossary.md"
        _ensure_table(path, "Master glossary")

    iast_val = iast or key
    new_row = _row(
        key,
        dev,
        iast_val,
        gloss,
        dhatu,
        analysis,
        sense_source,
        notes,
    )
    action = upsert_row(path, new_row, key, force)
    return action, path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--key", required=True, help="Stable \\sa{key} (IAST-like)")
    parser.add_argument("--dev", required=True, help="Devanagari form")
    parser.add_argument("--iast", default="", help="IAST transliteration")
    parser.add_argument("--gloss", default="", help="Short English gloss")
    parser.add_argument("--dhatu", default="", help="Root / dhatu note")
    parser.add_argument("--analysis", default="", help="Morphological / working analysis")
    parser.add_argument("--sense-source", default="", help="Where the sense comes from")
    parser.add_argument("--notes", default="", help="Free notes")
    parser.add_argument(
        "--chapter",
        help="If set, write chapter glossary.md instead of master",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite an existing key row",
    )
    args = parser.parse_args(argv)

    action, path = add_entry(
        key=args.key,
        dev=args.dev,
        iast=args.iast,
        gloss=args.gloss,
        dhatu=args.dhatu,
        analysis=args.analysis,
        sense_source=args.sense_source,
        notes=args.notes,
        chapter=args.chapter,
        force=args.force,
    )
    print(f"{action.capitalize()} key '{args.key}' in {path}")
    try:
        from build_sa_completions import main as build_completions

        build_completions([])
    except Exception as exc:  # noqa: BLE001
        print(f"(completions rebuild skipped: {exc})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
