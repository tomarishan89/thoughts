#!/usr/bin/env python3
"""Chapter pipeline helpers: rough -> draft -> stage -> output.

\\sa{} markers live in rough.md only. promote-draft compiles them to Devanagari
in draft.md. stage/output stay Devanagari.

Subcommands:
  refresh-rough  Copy content-of-record -> rough.md (prefer stage, else draft)
  promote-draft  Compile rough.md -> draft.md (Devanagari; warns on missing keys)
  new-stage      Copy draft.md -> stage.md
  status         Layer existence, mtimes, unresolved keys, stale output
  check-keys     List unresolved \\sa{} keys in a layer (usually rough)
"""

from __future__ import annotations

import argparse
import sys
from datetime import datetime, timezone
from pathlib import Path

_SCRIPTS = Path(__file__).resolve().parent
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

from expand_sa import (  # noqa: E402
    SOURCE_DEFAULTS,
    collect_sa_keys,
    expand_file,
    load_lexicon,
    project_root,
    resolve_chapter,
)
from sync_sa_defines import sync_file  # noqa: E402

LAYER_FILES = ("rough.md", "draft.md", "stage.md", "output.md")


def _mtime(path: Path) -> float | None:
    if not path.is_file():
        return None
    return path.stat().st_mtime


def _fmt_mtime(ts: float | None) -> str:
    if ts is None:
        return "-"
    return datetime.fromtimestamp(ts, tz=timezone.utc).strftime("%Y-%m-%d %H:%M UTC")


def _copy_file(src: Path, dest: Path) -> None:
    text = src.read_text(encoding="utf-8")
    dest.write_text(text, encoding="utf-8")


def missing_keys_in(
    chapter_dir: Path,
    root: Path,
    source: str,
    *,
    sync_first: bool = True,
) -> list[str]:
    name, _ = SOURCE_DEFAULTS[source]
    path = chapter_dir / name
    if not path.is_file():
        return []
    if sync_first:
        sync_file(
            path,
            chapter_dir,
            root,
            force=False,
            chapter_glossary=False,
        )
    lexicon = load_lexicon(chapter_dir, root)
    keys = collect_sa_keys(path.read_text(encoding="utf-8"))
    return sorted({k for k in keys if k not in lexicon})


def cmd_refresh_rough(chapter_dir: Path) -> int:
    stage = chapter_dir / "stage.md"
    draft = chapter_dir / "draft.md"
    rough = chapter_dir / "rough.md"
    if stage.is_file():
        src = stage
        label = "stage.md"
    elif draft.is_file():
        src = draft
        label = "draft.md (no stage.md yet)"
    else:
        print(f"Neither stage.md nor draft.md found in {chapter_dir}", file=sys.stderr)
        return 1
    _copy_file(src, rough)
    print(f"Refreshed rough.md from {label}")
    print(f"Wrote {rough}")
    print(
        "NOTE: draft/stage/output are Devanagari. This copy has no \\sa{} markers. "
        "Re-introduce \\sa{key} (or \\sa{key = देव}) for new Sanskrit terms."
    )
    return 0


def cmd_promote_draft(chapter_dir: Path, root: Path) -> int:
    rough = chapter_dir / "rough.md"
    draft = chapter_dir / "draft.md"
    if not rough.is_file():
        print(f"Missing rough.md: {rough}", file=sys.stderr)
        return 1

    # Sync defines on rough, warn about missing keys, then compile to draft.
    missing = missing_keys_in(chapter_dir, root, "rough", sync_first=True)
    if missing:
        print("WARNING: unresolved \\sa{} keys in rough.md (promote continues):")
        for key in missing:
            print(f"  - {key}")
        print('  Tip: write \\sa{key = देव} or tell the agent the Devanagari form.')

    before = draft.read_text(encoding="utf-8") if draft.is_file() else None
    count, still_missing = expand_file(
        rough,
        draft,
        chapter_dir,
        root,
        sync=False,  # already synced above
        header=None,
    )
    print("Promoted + compiled rough.md -> draft.md (Devanagari)")
    print(f"Wrote {draft}")
    print(f"Expanded: {count}  Still missing: {len(still_missing)}")
    after = draft.read_text(encoding="utf-8")
    if before is None:
        print("Summary: created draft.md")
    elif before == after:
        print("Summary: draft unchanged")
    else:
        b_lines, a_lines = before.splitlines(), after.splitlines()
        print(
            f"Summary: draft updated "
            f"({len(b_lines)} -> {len(a_lines)} lines)"
        )
    return 1 if still_missing else 0


def cmd_new_stage(chapter_dir: Path) -> int:
    draft = chapter_dir / "draft.md"
    stage = chapter_dir / "stage.md"
    if not draft.is_file():
        print(f"Missing draft.md: {draft}", file=sys.stderr)
        return 1
    _copy_file(draft, stage)
    print("Seeded stage.md from draft.md")
    print(f"Wrote {stage}")
    return 0


def cmd_check_keys(chapter_dir: Path, root: Path, source: str) -> int:
    name, _ = SOURCE_DEFAULTS[source]
    path = chapter_dir / name
    if not path.is_file():
        print(f"Missing {name}: {path}", file=sys.stderr)
        return 1
    missing = missing_keys_in(chapter_dir, root, source, sync_first=True)
    print(f"Checked {name}")
    if not missing:
        print("Unresolved keys: 0")
        return 0
    print(f"Unresolved keys: {len(missing)}")
    for key in missing:
        print(f"  - {key}")
    return 1


def cmd_status(chapter_dir: Path, root: Path) -> int:
    print(f"Chapter: {chapter_dir}")
    print("")
    print(f"{'file':<12} {'exists':<8} {'mtime'}")
    print("-" * 44)
    mtimes: dict[str, float | None] = {}
    for name in LAYER_FILES:
        path = chapter_dir / name
        ts = _mtime(path)
        mtimes[name] = ts
        print(f"{name:<12} {'yes' if path.is_file() else 'no':<8} {_fmt_mtime(ts)}")

    print("")
    rough = chapter_dir / "rough.md"
    if rough.is_file():
        missing = missing_keys_in(chapter_dir, root, "rough", sync_first=True)
        keys = collect_sa_keys(rough.read_text(encoding="utf-8"))
        print(f"rough \\sa{{}} keys: {len(keys)}  unresolved: {len(missing)}")
        for key in missing:
            print(f"  - {key}")
    else:
        print("rough.md missing - cannot check \\sa{} keys")

    for label in ("draft", "stage"):
        path = chapter_dir / f"{label}.md"
        if path.is_file():
            leftover = collect_sa_keys(path.read_text(encoding="utf-8"))
            print(f"{label} leftover \\sa{{}} markers: {len(leftover)} (expect 0)")

    print("")
    stage_ts = mtimes.get("stage.md")
    output_ts = mtimes.get("output.md")
    if stage_ts is None:
        print("output vs stage: n/a (no stage)")
    elif output_ts is None:
        print("output vs stage: output missing (stale / never compiled)")
    elif output_ts < stage_ts:
        print("output vs stage: STALE (stage newer than output)")
    else:
        print("output vs stage: up to date (output mtime >= stage)")

    record = "stage.md" if (chapter_dir / "stage.md").is_file() else (
        "draft.md" if (chapter_dir / "draft.md").is_file() else "none"
    )
    print(f"content-of-record for refresh-rough: {record}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    for name, help_text in (
        ("refresh-rough", "Copy stage (else draft) -> rough.md"),
        ("promote-draft", "Compile rough.md -> draft.md (Devanagari)"),
        ("new-stage", "Copy draft.md -> stage.md"),
        ("status", "Show layer status and unresolved keys"),
    ):
        p = sub.add_parser(name, help=help_text)
        p.add_argument(
            "chapter",
            help="Chapter folder, slug under essays/, or path to a layer file",
        )

    p_check = sub.add_parser("check-keys", help="List unresolved \\sa{} keys")
    p_check.add_argument("chapter", help="Chapter folder or slug")
    p_check.add_argument(
        "--source",
        choices=sorted(SOURCE_DEFAULTS),
        default="rough",
        help="Layer to check (default: rough)",
    )

    args = parser.parse_args(argv)
    root = project_root()
    chapter_dir = resolve_chapter(args.chapter, root)

    if args.command == "refresh-rough":
        return cmd_refresh_rough(chapter_dir)
    if args.command == "promote-draft":
        return cmd_promote_draft(chapter_dir, root)
    if args.command == "new-stage":
        return cmd_new_stage(chapter_dir)
    if args.command == "status":
        return cmd_status(chapter_dir, root)
    if args.command == "check-keys":
        return cmd_check_keys(chapter_dir, root, args.source)
    return 1


if __name__ == "__main__":
    sys.exit(main())
