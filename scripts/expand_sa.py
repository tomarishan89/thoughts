#!/usr/bin/env python3
"""Expand \\sa{key} markers via glossary tables.

Pipeline (markers only in rough; Devanagari from draft onward):
  --compile-to draft   rough.md -> draft.md   (promote / compile draft)
  --compile-to output  stage.md -> output.md  (green flag)

Optional previews (do not replace working layers):
  --source rough -> rough-preview.md
  --source draft -> draft-preview.md  (rarely needed if draft is already compiled)

By default syncs \\sa{key = देव} on the *source* before expanding.
Resolution: chapter glossary.md -> lexicons/glossary.md.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

SA_RE = re.compile(r"\\sa\{([^}]+)\}")
BARE_SA_RE = re.compile(r"\\sa\{\s*([A-Za-z][A-Za-z0-9_-]*)\s*\}")
DEFINE_SA_RE = re.compile(
    r"\\sa\{\s*([A-Za-z][A-Za-z0-9_-]*)\s*=\s*([^}]+?)\s*\}"
)
SKIP_BLOCK_RE = re.compile(
    r"(```.*?```|<!--.*?-->)",
    re.DOTALL,
)

SOURCE_DEFAULTS = {
    "stage": ("stage.md", "output.md"),
    "draft": ("draft.md", "draft-preview.md"),
    "rough": ("rough.md", "rough-preview.md"),
}


def project_root() -> Path:
    return Path(__file__).resolve().parent.parent


def parse_glossary(path: Path) -> dict[str, str]:
    """Parse a markdown glossary table: key | Devanagari | ..."""
    if not path.is_file():
        return {}

    mapping: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if len(cells) < 2:
            continue
        key, dev = cells[0], cells[1]
        if not key or key.lower() == "key":
            continue
        if set(key) <= {"-", ":"} or set(dev) <= {"-", ":"}:
            continue
        if not dev:
            continue
        mapping[key] = dev
    return mapping


def parse_glossary_rows(path: Path) -> list[dict[str, str]]:
    """Full rows for completions: key, Devanagari, IAST, gloss."""
    if not path.is_file():
        return []
    rows: list[dict[str, str]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if len(cells) < 2:
            continue
        key, dev = cells[0], cells[1]
        if not key or key.lower() == "key":
            continue
        if set(key) <= {"-", ":"} or set(dev) <= {"-", ":"}:
            continue
        if not dev:
            continue
        rows.append(
            {
                "key": key,
                "dev": dev,
                "iast": cells[2] if len(cells) > 2 else key,
                "gloss": cells[3] if len(cells) > 3 else "",
            }
        )
    return rows


def load_lexicon(chapter_dir: Path, root: Path) -> dict[str, str]:
    master_path = root / "essays" / "interospection_01" / "lexicons" / "glossary.md"
    if not master_path.exists():
        master_path = root / "lexicons" / "glossary.md"
    master = parse_glossary(master_path)
    chapter = parse_glossary(chapter_dir / "glossary.md")
    return {**master, **chapter}


def expand_text(text: str, lexicon: dict[str, str]) -> tuple[str, list[str], int]:
    missing: list[str] = []
    expanded_count = 0

    def replace_in_segment(segment: str) -> str:
        nonlocal expanded_count

        def repl(match: re.Match[str]) -> str:
            nonlocal expanded_count
            key = match.group(1)
            if key in lexicon:
                expanded_count += 1
                return lexicon[key]
            missing.append(key)
            return match.group(0)

        return BARE_SA_RE.sub(repl, segment)

    parts: list[str] = []
    last = 0
    for block in SKIP_BLOCK_RE.finditer(text):
        parts.append(replace_in_segment(text[last : block.start()]))
        parts.append(block.group(0))
        last = block.end()
    parts.append(replace_in_segment(text[last:]))
    return "".join(parts), missing, expanded_count


def resolve_chapter(arg: str, root: Path) -> Path:
    path = Path(arg)
    layer_names = {
        "draft.md",
        "stage.md",
        "rough.md",
        "output.md",
        "draft-preview.md",
        "rough-preview.md",
    }
    if path.is_file() and path.name in layer_names:
        return path.parent if path.is_absolute() else (root / path).resolve().parent
    if path.is_dir():
        return path if path.is_absolute() else (root / path).resolve()
    candidate = root / "essays" / arg
    if candidate.is_dir():
        return candidate
    raise SystemExit(f"Chapter not found: {arg}")


def collect_sa_keys(text: str) -> list[str]:
    """Bare \\sa{key} keys only (inline defines excluded)."""
    keys: list[str] = []

    def from_segment(segment: str) -> None:
        cleaned = DEFINE_SA_RE.sub("", segment)
        keys.extend(BARE_SA_RE.findall(cleaned))

    last = 0
    for block in SKIP_BLOCK_RE.finditer(text):
        from_segment(text[last : block.start()])
        last = block.end()
    from_segment(text[last:])
    return keys


COMPILE_TO = {
    "draft": ("rough.md", "draft.md", False),   # markers -> Devanagari working draft
    "output": ("stage.md", "output.md", True),  # green flag; optional header
}


def expand_file(
    source_path: Path,
    dest_path: Path,
    chapter_dir: Path,
    root: Path,
    *,
    sync: bool = True,
    header: str | None = None,
) -> tuple[int, list[str]]:
    """Expand source_path into dest_path. Returns (count, missing_keys)."""
    if sync:
        from sync_sa_defines import sync_file

        sync_file(
            source_path,
            chapter_dir,
            root,
            force=False,
            chapter_glossary=False,
        )

    lexicon = load_lexicon(chapter_dir, root)
    source = source_path.read_text(encoding="utf-8")
    expanded, missing, count = expand_text(source, lexicon)
    body = expanded if header is None else header + expanded.lstrip()
    dest_path.write_text(body, encoding="utf-8")
    return count, sorted(set(missing))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "chapter",
        help="Chapter folder, slug under essays/, or path to a layer file",
    )
    parser.add_argument(
        "--compile-to",
        choices=sorted(COMPILE_TO),
        help="Compile into a working layer: draft (from rough) or output (from stage)",
    )
    parser.add_argument(
        "--source",
        choices=sorted(SOURCE_DEFAULTS),
        help="Preview mode: expand a layer to *-preview.md (default if no --compile-to: stage preview path = output)",
    )
    parser.add_argument(
        "-o",
        "--output",
        help="Override output path",
    )
    parser.add_argument(
        "--inplace",
        action="store_true",
        help="Write expanded text over the source file",
    )
    parser.add_argument(
        "--no-sync",
        action="store_true",
        help="Skip syncing \\sa{key = देव} defines before expand",
    )
    parser.add_argument(
        "--no-header",
        action="store_true",
        help="Do not prepend a generated HTML comment header",
    )
    args = parser.parse_args(argv)

    root = project_root()
    chapter_dir = resolve_chapter(args.chapter, root)

    # Default green-flag style: --compile-to output if neither flag set
    if args.compile_to is None and args.source is None:
        args.compile_to = "output"

    if args.compile_to:
        source_name, dest_name, use_header = COMPILE_TO[args.compile_to]
        source_path = chapter_dir / source_name
        dest_path = chapter_dir / dest_name
        if args.output:
            dest_path = Path(args.output)
            if not dest_path.is_absolute():
                dest_path = (root / dest_path).resolve()
        if not source_path.is_file():
            hint = ""
            if args.compile_to == "draft":
                hint = "\nCreate rough.md first."
            elif args.compile_to == "output":
                hint = "\nSeed stage with: python scripts/pipeline.py new-stage <chapter>"
            raise SystemExit(f"Missing {source_name}: {source_path}{hint}")

        header = None
        if use_header and not args.no_header:
            header = (
                f"<!-- Generated by scripts/expand_sa.py from {source_name}. -->\n\n"
            )
        count, unique_missing = expand_file(
            source_path,
            dest_path,
            chapter_dir,
            root,
            sync=not args.no_sync,
            header=header,
        )
        print(f"Compile: {source_name} -> {dest_path.name}")
        print(f"Wrote {dest_path}")
        print(f"Expanded: {count}  Missing keys: {len(unique_missing)}")
        if unique_missing:
            print("Unresolved (use \\sa{key = देव} in rough, or glossary_add.py):")
            for key in unique_missing:
                print(f"  - {key}")
            return 1
        return 0

    # Preview / legacy --source mode
    source_name, default_out = SOURCE_DEFAULTS[args.source]
    source_path = chapter_dir / source_name
    if not source_path.is_file():
        raise SystemExit(f"Missing {source_name}: {source_path}")

    if args.inplace:
        dest_path = source_path
        header = None
    else:
        dest_path = Path(args.output) if args.output else chapter_dir / default_out
        if not dest_path.is_absolute():
            dest_path = (root / dest_path).resolve()
        header = None
        if not args.no_header:
            header = (
                f"<!-- Generated by scripts/expand_sa.py from {source_name}. -->\n\n"
            )

    count, unique_missing = expand_file(
        source_path,
        dest_path,
        chapter_dir,
        root,
        sync=not args.no_sync,
        header=header,
    )
    print(f"Source: {source_name}")
    print(f"Wrote {dest_path}")
    print(f"Expanded: {count}  Missing keys: {len(unique_missing)}")
    if unique_missing:
        print("Unresolved (use \\sa{key = देव} or glossary_add.py, then re-run):")
        for key in unique_missing:
            print(f"  - {key}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
