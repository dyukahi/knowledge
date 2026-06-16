# Visual Publication Audit — redpill.wiki 9.5 Pass

Date: 2026-06-16 GMT+7  
Scope: final visual/public polish after the 9.5 publication-pack work.

## Local build

Workflow mirrored locally:

1. Clone Quartz `v4` into `/tmp/redpill-quartz-preview/quartz`.
2. Copy vault content into `quartz/content`.
3. Copy `quartz.config.ts`.
4. Apply `scripts/patch-quartz-seo.mjs`.
5. Run `npm ci`.
6. Run `npx quartz build`.

Result:

```text
Quartz v4.5.2
Found 205 input files
Parsed 205 Markdown files
Filtered out 1 files
Emitted 978 files to public
Done processing 205 files
```

## Pages visually checked

Local preview served at:

```text
http://127.0.0.1:8099/
```

Checked:

- Home / `index.md`
- Publication Packs section on mobile viewport
- `mental-models/Orphan Train 2.0 - Khi Ma Trận Chở Trẻ Em Ra Khỏi Dòng Máu.md`
- `esoterica/Ma Trận.md`

Screenshots captured in OpenClaw browser media:

- Home first screen: `/Users/justinld/.openclaw/media/browser/369e5a1d-67ca-44f2-9935-33284aa30e4d.jpg`
- Publication Packs section: `/Users/justinld/.openclaw/media/browser/60cce436-27a6-438c-8fa4-2fdb9d5dd98b.jpg`
- Orphan Train page first screen: `/Users/justinld/.openclaw/media/browser/4d0b3bee-1198-4f18-90f9-592f0a990224.jpg`

## Observations

### Home / first screen

Status: **pass**

- Header, title, intro and Start Here section render cleanly on mobile.
- Domain table begins below the fold but is readable.
- No obvious first-screen overflow or broken typography.

### Publication Packs

Status: **pass**

- Section is visible and understandable.
- Five packs are scannable on mobile.
- Long article links wrap instead of forcing horizontal scroll.
- Pack hierarchy is clear enough: Core, Health, Family/Dopamine, Finance, Disclosure.

### Orphan Train 2.0

Status: **pass**

- First screen reads like a public essay, not a Telegram text-block draft.
- No horizontal code block / long chain issue seen.
- Evidence Discipline table is readable on mobile.
- JS overflow check on rendered page: body width equals viewport width, no body-level overflow.

### Ma Trận

Status: **pass**

- Core hub page loads and titles correctly.
- JS overflow check: no body-level horizontal overflow.

## QC state after visual pass

```text
broken_links: 0
duplicate_titles: 0
missing_description: 0
missing_aliases: 0
mobile_hostile_code: 0
```

## Remaining non-blockers

- Some intentional manifesto-style pages still trigger `textblock_candidates`. This is a soft editorial queue, not a deploy blocker.
- GitHub Pages deploy/cache can lag after push. If public site still shows old formatting, wait for workflow/deploy or hard refresh.

## Verdict

Current repo state is **public-visual-safe** and publication-pack architecture is visible on the home page. Rating target is now realistically around **9.4–9.5** from repo/content side. Remaining gap is live deployment verification on `redpill.wiki` after GitHub Pages finishes.
