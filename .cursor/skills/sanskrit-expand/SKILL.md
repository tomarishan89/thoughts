---
name: sanskrit-expand
description: >-
  Compiles \sa{key} from rough into Devanagari draft/output via
  scripts/expand_sa.py. Use for promote/compile-to-draft, green-flag output,
  rough preview, inline \sa{key = देव}, or missing glossary keys. Autofill
  IAST/gloss as llm-provisional after Devanagari is known.
---

# Sanskrit expand / compilation

## Where markers live

| Layer | Content |
|-------|---------|
| `rough.md` | Keep `\sa{key}` (and `\sa{key = देव}`) |
| `draft.md` / `stage.md` / `output.md` | Devanagari only (compiled) |

## Modes

| User ask | Command | Effect |
|----------|---------|--------|
| Promote / compile draft | `python scripts/pipeline.py promote-draft <chapter>` or `python scripts/expand_sa.py <chapter> --compile-to draft` | `rough.md` → `draft.md` (Devanagari) |
| Green flag / compile output | `python scripts/expand_sa.py <chapter> --compile-to output` | `stage.md` → `output.md` |
| Preview rough only | `python scripts/expand_sa.py <chapter> --source rough` | `rough-preview.md` (does not change draft) |

Default with no flags is `--compile-to output`.

**Do not** hand-replace `\sa{key}` in chat. Run the script.

## Inline first-time definition (in rough)

```markdown
\sa{halahal = हलाहल}
```

```bash
python scripts/sync_sa_defines.py <chapter> --source rough
```

Sync runs automatically before expand. Prefer defines in **rough** only.

## Missing keys / LLM autofill

1. List unresolved keys (usually from rough / promote).
2. Ask for Devanagari **or** `\sa{key = देव}` in rough. Never invent Devanagari.
3. Autofill IAST + short gloss (`--sense-source llm-provisional`).
4. Re-run promote / `--compile-to draft`.

```bash
python scripts/glossary_add.py --key <key> --dev <देव> --iast <iast> --gloss "<gloss>" --sense-source llm-provisional
```

## Cursor suggestions

- `sa-moksa` → full `\sa{moksa}` (in rough)
- Inside `\sa{…}`: bare key completion only (avoids `}}`)

```bash
python scripts/build_sa_completions.py
```
