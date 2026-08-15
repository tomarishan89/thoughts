#!/usr/bin/env python3
"""Sync inline \\sa{key = Devanagari} definitions into the glossary.

Finds markers like \\sa{halahal = हलाहल}, adds glossary rows, rewrites to \\sa{halahal}.
Run before expand/preview/compile.

Examples:
  python scripts/sync_sa_defines.py essays/01-darshan-of-kundalini --source rough
  python scripts/sync_sa_defines.py essays/01-darshan-of-kundalini --all
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

_SCRIPTS = Path(__file__).resolve().parent
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

from expand_sa import (  # noqa: E402
    SKIP_BLOCK_RE,
    SOURCE_DEFAULTS,
    load_lexicon,
    project_root,
    resolve_chapter,
)
from glossary_add import add_entry  # noqa: E402

# \sa{key = देव} with optional spaces around =
DEFINE_RE = re.compile(
    r"\\sa\{\s*([A-Za-z][A-Za-z0-9_-]*)\s*=\s*([^}]+?)\s*\}"
)

# Rough check: RHS should contain Devanagari
DEVANAGARI_RE = re.compile(r"[\u0900-\u097F]")


def sync_text(
    text: str,
    lexicon: dict[str, str],
    *,
    chapter: str | None,
    force: bool,
    root: Path,
) -> tuple[str, list[str], list[str], list[str]]:
    """Return (new_text, added_keys, warned_keys, skipped_keys)."""
    added: list[str] = []
    warned: list[str] = []
    skipped: list[str] = []

    def process_segment(segment: str) -> str:
        def repl(match: re.Match[str]) -> str:
            key = match.group(1)
            dev = match.group(2).strip()
            if not DEVANAGARI_RE.search(dev):
                skipped.append(f"{key} (RHS not Devanagari: {dev})")
                return match.group(0)
            if key in lexicon and lexicon[key] != dev:
                if not force:
                    warned.append(f"{key}: glossary has {lexicon[key]!r}, define has {dev!r}")
                    return f"\\sa{{{key}}}"
            if key not in lexicon or (force and lexicon.get(key) != dev):
                action, _path = add_entry(
                    key=key,
                    dev=dev,
                    iast=key,
                    gloss="",
                    sense_source="inline-define",
                    chapter=chapter,
                    force=force or key in lexicon,
                    root=root,
                )
                lexicon[key] = dev
                added.append(f"{key} ({action})")
            return f"\\sa{{{key}}}"

        return DEFINE_RE.sub(repl, segment)

    parts: list[str] = []
    last = 0
    for block in SKIP_BLOCK_RE.finditer(text):
        parts.append(process_segment(text[last : block.start()]))
        parts.append(block.group(0))
        last = block.end()
    parts.append(process_segment(text[last:]))
    return "".join(parts), added, warned, skipped


def sync_file(
    path: Path,
    chapter_dir: Path,
    root: Path,
    *,
    force: bool,
    chapter_glossary: bool,
) -> int:
    if not path.is_file():
        print(f"Skip (missing): {path}")
        return 0

    lexicon = load_lexicon(chapter_dir, root)
    text = path.read_text(encoding="utf-8")
    chapter_arg = str(chapter_dir) if chapter_glossary else None
    new_text, added, warned, skipped = sync_text(
        text,
        lexicon,
        chapter=chapter_arg,
        force=force,
        root=root,
    )
    if new_text != text:
        path.write_text(new_text, encoding="utf-8")
        print(f"Updated {path}")
    else:
        print(f"No define changes in {path.name}")

    if added:
        print("Glossary:")
        for item in added:
            print(f"  + {item}")
        try:
            from build_sa_completions import main as build_completions

            build_completions([])
        except Exception as exc:  # noqa: BLE001
            print(f"(completions rebuild skipped: {exc})")
    if warned:
        print("Warnings (normalized marker; glossary unchanged; use --force to overwrite):")
        for item in warned:
            print(f"  ! {item}")
    if skipped:
        print("Skipped:")
        for item in skipped:
            print(f"  ? {item}")
    return 1 if warned or skipped else 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("chapter", help="Chapter folder or slug")
    parser.add_argument(
        "--source",
        choices=sorted(SOURCE_DEFAULTS),
        help="Single layer to sync (rough/draft/stage)",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Sync rough, draft, and stage if present",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite glossary Devanagari when define disagrees",
    )
    parser.add_argument(
        "--chapter-glossary",
        action="store_true",
        help="Write new keys to chapter glossary.md instead of master",
    )
    args = parser.parse_args(argv)

    if not args.source and not args.all:
        args.all = True

    root = project_root()
    chapter_dir = resolve_chapter(args.chapter, root)
    sources = list(SOURCE_DEFAULTS) if args.all else [args.source]
    code = 0
    for src in sources:
        name, _ = SOURCE_DEFAULTS[src]
        code |= sync_file(
            chapter_dir / name,
            chapter_dir,
            root,
            force=args.force,
            chapter_glossary=args.chapter_glossary,
        )
    return code


if __name__ == "__main__":
    sys.exit(main())
