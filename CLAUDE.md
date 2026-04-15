# Schema (LLM Instructions)
This directory is the root of the Knowledge IDE / Zettelkasten.
All knowledge base operations must happen within this `knowledge` folder.

## Core Philosophy
"The human thinks and curates. The LLM handles the bookkeeping."

## Operations Model (The 4 Pillars)
1. **Ingest**: New knowledge arrives from web clips, raw files, or research conversations into `_inbox/`. The LLM reads, digests, and converts them into proper refined notes.
2. **Compile**: The LLM checks for overlaps, flags contradictions, merges duplicates, updates cross-references (Auto-inline links & `## Related`), and creates synthesis pages.
3. **Query**: Ask questions against the compiled wiki. The LLM uses semantic search to answer. Good answers get filed back as new notes.
4. **Lint**: Periodic health checks for orphans, broken links, missing frontmatter, and stale claims. The LLM auto-heals by filling gaps (Stub notes).

## Folder conventions
- `_inbox/`: Raw capture landing zone.
- `_templates/`: Obsidian note templates.
- `_docs/`: Project documentation / Changelogs. Contains `/scripts/` for LLM automation.
- Content folders (e.g., `ai/`, `wealth/`): Topic-based, lowercase, hyphenated.

## Rules
- Link density: 2-4 outgoing links per note in the `## Related` section.
- Auto-Linking: Key concepts must be inline-linked `[[Concept]]` within the body text.
- Synthesis: Create synthesis pages for dense clusters (4+ notes).