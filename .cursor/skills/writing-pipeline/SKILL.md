---
name: writing-pipeline
description: >-
  Manages rough → draft → stage → output via scripts/pipeline.py. Promote
  compiles \sa{} from rough into Devanagari draft. Use for promote to draft,
  new stage, need rough space, pipeline status, or check-keys.
---

# Writing pipeline

## Layer flow

`rough.md` (`\sa{}`) → `draft.md` (Devanagari) → `stage.md` (Devanagari) → `output.md` (Devanagari)

After `stage.md` exists, it is the **content-of-record** for prose. Markers stay in **rough**.

## Commands

| User ask | Command |
|----------|---------|
| Need rough space / refresh rough | `python scripts/pipeline.py refresh-rough <chapter>` |
| Promote to draft / compile draft | `python scripts/pipeline.py promote-draft <chapter>` |
| New stage | `python scripts/pipeline.py new-stage <chapter>` |
| Pipeline status | `python scripts/pipeline.py status <chapter>` |
| Check missing keys | `python scripts/pipeline.py check-keys <chapter> --source rough` |

## Behavior notes

- **promote-draft** syncs defines on rough, warns on missing keys, then **compiles** rough → draft (Devanagari in `draft.md`). Rough keeps `\sa{}`.
- **refresh-rough** copies stage/draft prose into rough; warn that `\sa{}` must be re-introduced for new terms.
- After **new-stage**: critically edit **stage.md** (Devanagari).
- Green flag → `python scripts/expand_sa.py <chapter> --compile-to output`.

## Rules

- Whole-file copy / compile for v1.
- Summarize script stdout.
- If chapter is unclear, ask once.
