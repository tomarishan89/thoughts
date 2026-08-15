# Essay writing workspace

Long-form bilingual writing (English + Sanskrit) with a staged pipeline, glossary-backed markup, language review, and Pāṇini-aware critique.

## Obsidian

This folder is an Obsidian vault. **Open folder as vault** and choose this project root.

- Shared vault settings live in `.obsidian/` (committed).
- Personal UI state (`workspace.json`, etc.) is gitignored.
- `.git/`, `.cursor/`, and scratch folders are hidden from the file list.

**Note:** Live `\sa{…}` suggestions work in **Cursor**. In Obsidian, use `\sa{key}` or `\sa{key = देव}` in **rough**.

## Writing pipeline

```
rough.md (\sa{}) → draft.md (Devanagari) → stage.md (Devanagari) → output.md
```

| File | Role |
|------|------|
| `rough.md` | Ideas + `\sa{key}` markers |
| `draft.md` | Settled prose **with Sanskrit compiled** |
| `stage.md` | Critical edit; content-of-record once it exists |
| `output.md` | Final pass after green flag |
| `notes.md` / `glossary.md` / `review-log.md` | Support files |

### Commands

```bash
python scripts/pipeline.py refresh-rough essays/01-darshan-of-kundalini
python scripts/pipeline.py promote-draft essays/01-darshan-of-kundalini   # compiles to draft
python scripts/pipeline.py new-stage essays/01-darshan-of-kundalini
python scripts/pipeline.py status essays/01-darshan-of-kundalini
python scripts/pipeline.py check-keys essays/01-darshan-of-kundalini --source rough

# Same compile as promote (rough -> draft)
python scripts/expand_sa.py essays/01-darshan-of-kundalini --compile-to draft

# Green flag (stage -> output)
python scripts/expand_sa.py essays/01-darshan-of-kundalini --compile-to output

# Glossary + Cursor snippets
python scripts/glossary_add.py --key atman --dev आत्मन् --iast ātman --gloss self
python scripts/build_sa_completions.py
```

In **rough** (Cursor):

- Type `sa-dharma` → `\sa{dharma}`
- Inside `\sa{…}`, pick the bare key (avoids extra `}`)

## Start writing

Edit [`essays/01-darshan-of-kundalini/rough.md`](essays/01-darshan-of-kundalini/rough.md):

```markdown
Known term: \sa{dharma}
New term:    \sa{halahal = हलाहल}
```

Then **promote to draft** to compile Devanagari into `draft.md`. Continue critical edit on `stage.md` after `new-stage`.

## Ask the assistants

- **Promote to draft** — compiles `\sa{}` into `draft.md`
- **New stage** / **need rough space** / **check keys** / **pipeline status**
- **Green flag** — `stage` → `output`
- **Missing key** — Devanagari or `\sa{key = देव}` in rough; agent fills the rest
- **Language review** / **Debate**

## Lexicons

- [`lexicons/glossary.md`](lexicons/glossary.md)
- [`lexicons/allowlist.md`](lexicons/allowlist.md)
- [`references/panini-notes.md`](references/panini-notes.md)
