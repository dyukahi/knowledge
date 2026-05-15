# Schema (LLM Instructions)
This directory is the root of the Knowledge IDE / Zettelkasten.
All knowledge base operations must happen within this knowledge folder.

## Core Philosophy
"The human thinks and curates. The LLM handles the bookkeeping."

## Operations Model (The 4 Pillars)
1. **Ingest**: New knowledge arrives from web clips, raw files, or research conversations into _inbox/. The LLM reads, digests, and converts them into proper refined notes.
2. **Compile**: The LLM checks for overlaps, flags contradictions, merges duplicates, and updates cross-references ONLY in the ## Related section.
3. **Query**: Ask questions against the compiled wiki. The LLM uses semantic search to answer. Good answers get filed back as new notes.
4. **Lint**: Periodic health checks for orphans and missing frontmatter. NO STUB NOTES. Do not create empty placeholders.

## Folder conventions
- _inbox/: Raw capture landing zone.
- _templates/: Obsidian note templates.
- _docs/: Project documentation / Changelogs. Contains /scripts/ for LLM automation.
- Content folders (e.g., i/, wealth/): Topic-based, lowercase, hyphenated.

## Strict Linking Rules
- **NO INLINE LINKS:** The body text must be clean, natural, and readable. Do not use Wikilinks inside the content body.
- **Related Section ONLY:** All connections between notes must be placed exclusively in the ## Related section at the bottom of the file (2-4 links per note).
- **Real Notes ONLY:** Only link to concepts that already have existing, fully-written notes with real data. Do NOT create or link to "stub" or placeholder concepts.
- **Synthesis:** Create synthesis pages for dense clusters (4+ notes).
