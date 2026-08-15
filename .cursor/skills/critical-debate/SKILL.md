---
name: critical-debate
description: >-
  Critiques or debates essay content from a named perspective with Sanskrit-
  and Pāṇini-aware analysis (form vs lexicon vs prayoga). Use when the user
  asks to debate, critique, challenge arguments, or examine Sanskrit terms
  morphologically or philosophically.
---

# Critical debate (Pāṇini-aware v1)

## Instructions

1. Confirm or adopt a perspective (user-named, or default: charitable but strict philosophical critic).
2. Read the relevant section from the right layer: unsettled ideas → **`rough.md`**; settled argument → **`draft.md`**; polish/pre-compile → **`stage.md`**. Also read glossary rows for any `\sa{key}` or Devanagari terms involved.
3. Consult `references/panini-notes.md` for standing method preferences.
4. Structure feedback in layers:
   - **Argument** — claims, warrants, gaps, counters
   - **Evidence** — what supports or undercuts the claim
   - **Sanskrit** — for each contested term, separate:
     - **form** — morphological/Pāṇinian reading (dhātu, pratyaya, vibhakti, samāsa type) when relevant
     - **lexicon** — dictionary / traditional senses
     - **prayoga** — how the essay uses it
5. Honesty rules (v1):
   - Prefer traditional categories; cite sūtra numbers/names only when confident.
   - Never invent sūtra IDs. Mark uncertainty.
   - Do not claim full Aṣṭādhyāyī execution; LLM analysis is provisional until a v2 tool is wired.
6. Prefer formulations like: “This reading is licensed if we take X as from √Y with Z.”
7. Write the debate in chat. Append a dated section to chapter `notes.md` only if the user asks to save it.
8. When an analysis settles, offer to update glossary fields: `dhatu`, `analysis`, `sense_source`, `notes`.

## Example prompts

- “Debate this section from a Nyāya perspective.”
- “Challenge my use of \sa{dharma} here.”
- “Is this reading compatible with a √dhṛ derivation?”
