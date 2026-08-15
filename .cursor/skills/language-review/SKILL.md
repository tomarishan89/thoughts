---
name: language-review
description: >-
  Proofreads essay drafts for grammar and vocabulary with keep / ignore-once /
  ignore-forever / add actions. Use when the user asks for language review,
  proofreading, grammar check, vocabulary check, or style flags on a draft.
---

# Language review

## Instructions

1. Identify the target file: prefer **`stage.md`** (pre-compile), else `draft.md` if stage is not seeded. Read:
   - `lexicons/allowlist.md` (skip forever)
   - chapter `review-log.md` (skip ignore-once items still relevant to this pass if noted)
2. Flag grammar, wording, and awkward vocabulary. Be concise; group related issues.
3. Stay Sanskrit-aware:
   - Do not flag Devanagari, IAST, or `\sa{key}` as English errors.
   - Do not “fix” intentional bilingual texture unless asked.
4. For each finding, present options:
   - **keep** / **ignore forever** → append to `lexicons/allowlist.md` when the user confirms
   - **ignore once** → append to chapter `review-log.md` when the user confirms
   - **add** → glossary entry and/or allowlist note when the user confirms
5. Do not apply keep/ignore/add file edits until the user chooses an action (unless they say “apply all keeps” or similar).
6. After the pass, offer a short priority list (must-fix vs optional taste).

## Allowlist / log format

Allowlist row: `| phrase or pattern | reason | YYYY-MM-DD |`

Review-log row: `| YYYY-MM-DD | location | finding | ignore-once | note |`

## Example prompt

“Language review `essays/01-untitled/draft.md`”
