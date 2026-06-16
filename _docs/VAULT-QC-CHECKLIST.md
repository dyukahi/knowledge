# Vault QC Checklist

Use this before committing/pushing public redpill.wiki content changes.

## 1. Rebuild map

```bash
python3 _docs/build-knowledge-map.py
```

Required targets:

- `brokenLinks` should be `0` unless intentionally deferred and documented.
- Duplicate frontmatter titles must be `0`.
- New articles must appear in `_docs/KNOWLEDGE-MAP.md` and `_docs/knowledge-map.json`.

## 2. Run QC audit

```bash
python3 scripts/vault_qc_audit.py
```

Read:

- `_docs/VAULT-QC-AUDIT.md`
- `_docs/vault-qc-audit.json`

Hard blockers before push:

- duplicate titles > 0
- broken links > 0
- mobile-hostile code blocks > 0 for public prose articles
- missing aliases/descriptions on newly touched public articles

Soft warnings:

- text-block candidates: review top offenders, especially new/edited articles
- horizontal chains: allowed in mermaid/tables/short quotes, but avoid long one-line chains on mobile
- thin pages: utility pages may stay short; substantive pages need a clear editorial angle before expansion

## 3. New article publication checklist

When adding a new article, do **all** of these before commit:

- frontmatter:
  - `title`
  - `description`
  - `aliases`
  - `tags`
  - `status`
  - `related`
- root `index.md`:
  - total count if shown
  - domain count if shown
  - Browse by Domain section if relevant
  - Best of/flagship section if relevant
  - Recent Updates section
- domain gateway, e.g. `mental-models/index.md`, `esoterica/index.md`
- related MOC pages if it belongs to a cross-domain path
- run map builder
- run QC audit
- grep exact title across likely index/MOC files

## 4. Mobile formatting rules

Avoid:

```text
A → B → C → D → E → F
```

Prefer prose, bullets, tables, or mermaid diagrams. Do not use fenced code blocks for conceptual chains unless it is actual code.

Bad:

```text
sex → reproduction → gestation → motherhood → parenthood → lineage
```

Good:

- sex is separated from reproduction
- reproduction is separated from gestation
- gestation is separated from motherhood
- parenthood is separated from lineage

Or use prose.

## 5. Claim discipline for high-risk topics

For health, politics/conspiracy, science revisionism, gender/family, finance and esoteric-history articles, include one of:

- `Evidence Discipline / Cách Đọc Bài Này`
- `Source Discipline`
- `Vault Position`
- `Claim Discipline`

Minimum layers:

- Fact / documentable
- Pattern / systems reading
- Symbol / myth reading
- Speculative synthesis

Do not present symbolic/speculative synthesis as proof.
