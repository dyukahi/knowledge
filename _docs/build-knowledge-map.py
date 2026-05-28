from __future__ import annotations

import json
import re
from collections import Counter, defaultdict
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any

ROOT = Path.cwd()
OUT_MD = ROOT / "_docs" / "KNOWLEDGE-MAP.md"
OUT_JSON = ROOT / "_docs" / "knowledge-map.json"

EXCLUDE_DIRS = {".git", ".github", ".obsidian", "assets"}
TOP_LEVEL_DOMAINS = {
    "esoterica": "Esoterica / Huyền học",
    "health": "Health / Sức khỏe",
    "mental-models": "Mental Models / Mô hình tư duy",
    "politics-conspiracy": "Politics & Conspiracy",
    "science-tech": "Science & Tech",
    "crypto-finance": "Crypto & Finance",
    "_docs": "Docs / Meta",
}

WIKILINK_RE = re.compile(r"!??\[\[([^\]]+)\]\]")
MDLINK_RE = re.compile(r"\[[^\]]+\]\(([^)]+\.md(?:#[^)]+)?)\)")
TAG_RE = re.compile(r"(?<![\w/])#([\w\-/À-ỹ]+)", re.UNICODE)
HEADING_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*$", re.MULTILINE)


def read_text(path: Path) -> str:
    for enc in ("utf-8-sig", "utf-8", "cp1258", "cp1252"):
        try:
            return path.read_text(encoding=enc)
        except UnicodeDecodeError:
            continue
    return path.read_text(encoding="utf-8", errors="replace")


def strip_frontmatter(text: str) -> tuple[dict[str, Any], str]:
    if not text.startswith("---"):
        return {}, text
    end = text.find("\n---", 3)
    if end == -1:
        return {}, text
    raw = text[3:end].strip()
    body = text[end + 4 :].lstrip("\r\n")
    fm: dict[str, Any] = {}
    current_key = None
    for line in raw.splitlines():
        if not line.strip() or line.strip().startswith("#"):
            continue
        if re.match(r"^\s*-\s+", line) and current_key:
            fm.setdefault(current_key, [])
            if isinstance(fm[current_key], list):
                fm[current_key].append(line.split("-", 1)[1].strip().strip('"\''))
            continue
        if ":" in line:
            key, val = line.split(":", 1)
            key = key.strip()
            val = val.strip()
            current_key = key
            if val.startswith("[") and val.endswith("]"):
                fm[key] = [x.strip().strip('"\'') for x in val[1:-1].split(",") if x.strip()]
            elif val == "":
                fm[key] = []
            else:
                fm[key] = val.strip('"\'')
    return fm, body


def title_from_path(path: Path, body: str, fm: dict[str, Any]) -> str:
    if isinstance(fm.get("title"), str) and fm["title"].strip():
        return fm["title"].strip()
    m = HEADING_RE.search(body)
    if m:
        return re.sub(r"[*_`#]", "", m.group(2)).strip()
    return path.stem.replace("-", " ").replace("_", " ").strip()


def slugify_name(s: str) -> str:
    return s.lower().replace(" ", "-").strip()


def first_paragraph(body: str, limit: int = 260) -> str:
    clean = re.sub(r"```.*?```", "", body, flags=re.S)
    clean = re.sub(r"<!--.*?-->", "", clean, flags=re.S)
    paras = [p.strip() for p in re.split(r"\n\s*\n", clean) if p.strip()]
    for p in paras:
        if p.startswith("#") or p.startswith("|") or p.startswith(">"):
            continue
        p = re.sub(r"\s+", " ", p)
        p = re.sub(r"!\[\[[^\]]+\]\]", "", p)
        p = re.sub(r"\[\[([^\]|]+)(?:\|([^\]]+))?\]\]", lambda m: m.group(2) or m.group(1), p)
        p = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", p)
        if len(p) > limit:
            p = p[: limit - 1].rstrip() + "…"
        return p
    return ""


@dataclass
class Note:
    path: str
    title: str
    domain: str
    tags: list[str]
    aliases: list[str]
    headings: list[str]
    wikilinks: list[str]
    mdlinks: list[str]
    outlinks: list[str]
    backlinks: list[str]
    words: int
    summary: str


def collect_files() -> list[Path]:
    files = []
    for p in ROOT.rglob("*.md"):
        parts = set(p.relative_to(ROOT).parts)
        if parts & EXCLUDE_DIRS:
            continue
        if p == OUT_MD:
            continue
        files.append(p)
    return sorted(files, key=lambda x: x.as_posix().lower())


def main() -> None:
    files = collect_files()
    raw_notes: dict[str, dict[str, Any]] = {}
    title_index: dict[str, str] = {}
    stem_index: dict[str, str] = {}
    path_index: dict[str, str] = {}
    alias_index: dict[str, str] = {}

    for path in files:
        rel = path.relative_to(ROOT).as_posix()
        text = read_text(path)
        fm, body = strip_frontmatter(text)
        title = title_from_path(path, body, fm)
        aliases = []
        for k in ("aliases", "alias"):
            v = fm.get(k)
            if isinstance(v, list):
                aliases.extend(str(x) for x in v)
            elif isinstance(v, str):
                aliases.append(v)
        domain = rel.split("/", 1)[0] if "/" in rel else "root"
        headings = [h.strip() for _, h in HEADING_RE.findall(body)]
        tags = set(TAG_RE.findall(body))
        fm_tags = fm.get("tags") or fm.get("tag")
        if isinstance(fm_tags, list):
            tags.update(str(x).lstrip("#") for x in fm_tags)
        elif isinstance(fm_tags, str):
            tags.update(x.strip().lstrip("#") for x in re.split(r"[,\s]+", fm_tags) if x.strip())
        wikilinks = []
        for match in WIKILINK_RE.findall(body):
            target = match.split("|", 1)[0].split("#", 1)[0].strip()
            if target and not re.search(r"\.(png|jpg|jpeg|gif|webp|svg|pdf|mp4|mp3)$", target, re.I):
                wikilinks.append(target)
        mdlinks = [m.split("#", 1)[0] for m in MDLINK_RE.findall(body)]
        words = len(re.findall(r"\w+", body, re.UNICODE))
        raw_notes[rel] = dict(
            path=rel,
            title=title,
            domain=domain,
            tags=sorted(tags, key=str.lower),
            aliases=sorted(set(aliases), key=str.lower),
            headings=headings,
            wikilinks=sorted(set(wikilinks), key=str.lower),
            mdlinks=sorted(set(mdlinks), key=str.lower),
            body=body,
            words=words,
            summary=first_paragraph(body),
        )
        title_index[title.lower()] = rel
        stem_index[path.stem.lower()] = rel
        path_index[rel.lower()] = rel
        path_index[path.with_suffix("").relative_to(ROOT).as_posix().lower()] = rel
        for alias in aliases:
            alias_index[alias.lower()] = rel

    def resolve(target: str, source_rel: str) -> str | None:
        t = target.strip().replace("\\", "/")
        t_no_ext = t[:-3] if t.lower().endswith(".md") else t
        keys = [t.lower(), t_no_ext.lower(), slugify_name(t), Path(t).stem.lower()]
        # direct indexes
        for key in keys:
            if key in path_index:
                return path_index[key]
            if key in title_index:
                return title_index[key]
            if key in alias_index:
                return alias_index[key]
            if key in stem_index:
                return stem_index[key]
        # relative markdown link
        if target.lower().endswith(".md"):
            src_dir = Path(source_rel).parent
            rel_candidate = (src_dir / target).as_posix().lower()
            if rel_candidate in path_index:
                return path_index[rel_candidate]
        return None

    backlinks: dict[str, set[str]] = defaultdict(set)
    broken: list[dict[str, str]] = []
    outlinks_by_rel: dict[str, list[str]] = {}

    for rel, data in raw_notes.items():
        outlinks = []
        for target in data["wikilinks"] + data["mdlinks"]:
            resolved = resolve(target, rel)
            if resolved and resolved != rel:
                outlinks.append(resolved)
                backlinks[resolved].add(rel)
            elif not resolved:
                broken.append({"source": rel, "target": target})
        outlinks_by_rel[rel] = sorted(set(outlinks), key=str.lower)

    notes: dict[str, Note] = {}
    for rel, data in raw_notes.items():
        notes[rel] = Note(
            path=rel,
            title=data["title"],
            domain=data["domain"],
            tags=data["tags"],
            aliases=data["aliases"],
            headings=data["headings"],
            wikilinks=data["wikilinks"],
            mdlinks=data["mdlinks"],
            outlinks=outlinks_by_rel[rel],
            backlinks=sorted(backlinks.get(rel, set()), key=str.lower),
            words=data["words"],
            summary=data["summary"],
        )

    domain_counts = Counter(n.domain for n in notes.values())
    tag_counts = Counter(tag for n in notes.values() for tag in n.tags)
    hubs = sorted(notes.values(), key=lambda n: (len(n.backlinks) + len(n.outlinks), len(n.backlinks)), reverse=True)[:25]
    orphans = sorted([n for n in notes.values() if not n.backlinks and not n.outlinks], key=lambda n: n.path.lower())
    sources = sorted([n for n in notes.values() if not n.backlinks and n.outlinks], key=lambda n: len(n.outlinks), reverse=True)
    sinks = sorted([n for n in notes.values() if n.backlinks and not n.outlinks], key=lambda n: len(n.backlinks), reverse=True)

    by_domain: dict[str, list[Note]] = defaultdict(list)
    for n in notes.values():
        by_domain[n.domain].append(n)
    for domain in by_domain:
        by_domain[domain].sort(key=lambda n: (-(len(n.backlinks) + len(n.outlinks)), n.title.lower()))

    data_json = {
        "stats": {
            "notes": len(notes),
            "domains": dict(domain_counts),
            "tags": len(tag_counts),
            "wikilinkEdges": sum(len(n.outlinks) for n in notes.values()),
            "brokenLinks": len(broken),
            "orphans": len(orphans),
        },
        "domains": {d: [asdict(n) for n in arr] for d, arr in sorted(by_domain.items())},
        "hubs": [asdict(n) for n in hubs],
        "orphans": [asdict(n) for n in orphans],
        "sources": [asdict(n) for n in sources[:50]],
        "sinks": [asdict(n) for n in sinks[:50]],
        "topTags": tag_counts.most_common(100),
        "brokenLinks": broken,
        "notes": {rel: asdict(n) for rel, n in sorted(notes.items())},
    }
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(data_json, ensure_ascii=False, indent=2), encoding="utf-8")

    def note_link(n: Note) -> str:
        return f"[[{n.path[:-3]}|{n.title}]]"

    lines: list[str] = []
    lines.append("# Knowledge Map — redpill.wiki")
    lines.append("")
    lines.append("> Auto-generated by Bé Tôm from the markdown vault. This is a Zettelkasten map of content domains, hubs, tags, links, orphan notes, and suggested MOCs. Regenerate after major content changes.")
    lines.append("")
    lines.append("## Snapshot")
    lines.append("")
    lines.append(f"- **Notes scanned:** {len(notes)}")
    lines.append(f"- **Top-level domains:** {len(domain_counts)}")
    lines.append(f"- **Tags detected:** {len(tag_counts)}")
    lines.append(f"- **Resolved internal edges:** {sum(len(n.outlinks) for n in notes.values())}")
    lines.append(f"- **Broken/unresolved links:** {len(broken)}")
    lines.append(f"- **Orphan notes:** {len(orphans)}")
    lines.append("")

    lines.append("## Zettelkasten Reading")
    lines.append("")
    lines.append("This vault already behaves like a bilingual Zettelkasten: domain folders act as broad **areas**, individual essays act as **literature/permanent notes**, and cross-links/tags create the second-brain graph. The next structural upgrade is to add stronger **MOC / hub notes** that connect clusters across folders, especially where health, esoterica, conspiracy, and mental models overlap.")
    lines.append("")
    lines.append("Recommended note types:")
    lines.append("- **MOC notes:** map-of-content pages per cluster, e.g. `MOC - Consciousness`, `MOC - Metabolic Health`, `MOC - Financial Sovereignty`.")
    lines.append("- **Evergreen notes:** short atomic claims that can be linked from multiple essays.")
    lines.append("- **Bridge notes:** explicit cross-domain synthesis, e.g. metabolism ↔ consciousness, propaganda ↔ epistemology, crypto ↔ sovereignty.")
    lines.append("- **Index notes:** folder-level landing pages that summarize the best reading path.")
    lines.append("")

    lines.append("## Domain Map")
    lines.append("")
    for domain, count in sorted(domain_counts.items(), key=lambda x: (-x[1], x[0])):
        label = TOP_LEVEL_DOMAINS.get(domain, domain)
        lines.append(f"### {label} `{domain}` — {count} notes")
        lines.append("")
        top = by_domain[domain][:12]
        for n in top:
            degree = len(n.backlinks) + len(n.outlinks)
            tags = ", ".join(f"#{t}" for t in n.tags[:5])
            lines.append(f"- {note_link(n)} — degree `{degree}`, backlinks `{len(n.backlinks)}`, outlinks `{len(n.outlinks)}`" + (f" — {tags}" if tags else ""))
        if len(by_domain[domain]) > len(top):
            lines.append(f"- … {len(by_domain[domain]) - len(top)} more notes in this domain. See JSON for full list.")
        lines.append("")

    lines.append("## Current Hub Notes")
    lines.append("")
    lines.append("High-degree notes are good candidates for hub/MOC treatment.")
    lines.append("")
    for i, n in enumerate(hubs[:20], 1):
        lines.append(f"{i}. {note_link(n)} — degree `{len(n.backlinks) + len(n.outlinks)}` · backlinks `{len(n.backlinks)}` · outlinks `{len(n.outlinks)}`")
        if n.summary:
            lines.append(f"   - {n.summary}")
    lines.append("")

    lines.append("## Tag Constellations")
    lines.append("")
    if tag_counts:
        for tag, count in tag_counts.most_common(40):
            sample = [n for n in notes.values() if tag in n.tags][:5]
            sample_links = "; ".join(note_link(n) for n in sample)
            lines.append(f"- `#{tag}` — {count} notes" + (f": {sample_links}" if sample_links else ""))
    else:
        lines.append("No tags detected. Consider adding tags sparingly for cross-domain clusters, not as folder duplicates.")
    lines.append("")

    lines.append("## Suggested MOCs / Maps of Content")
    lines.append("")
    moc_specs = [
        ("MOC - Esoterica & Consciousness", ["esoterica", "mental-models"], ["consciousness", "symbolism", "gnosis", "tarot", "astro", "kundalini"]),
        ("MOC - Health Sovereignty", ["health", "science-tech"], ["metabolism", "detox", "nutrition", "medicine", "biohacking"]),
        ("MOC - Epistemology & Propaganda", ["mental-models", "politics-conspiracy"], ["propaganda", "media", "belief", "truth", "cognitive"]),
        ("MOC - Financial Sovereignty", ["crypto-finance", "politics-conspiracy"], ["bitcoin", "crypto", "money", "finance", "sovereignty"]),
        ("MOC - Ancient Civilizations & Hidden History", ["esoterica", "science-tech", "politics-conspiracy"], ["ancient", "civilization", "egypt", "history", "archaeology"]),
        ("MOC - Science Revisionism", ["science-tech", "health"], ["science", "physics", "medicine", "research", "revision"]),
    ]
    for title, domains, keywords in moc_specs:
        candidates = []
        for n in notes.values():
            hay = " ".join([n.title, n.summary, " ".join(n.tags), n.path]).lower()
            if n.domain in domains or any(k in hay for k in keywords):
                score = (2 if n.domain in domains else 0) + sum(1 for k in keywords if k in hay) + len(n.backlinks)
                candidates.append((score, n))
        candidates = [n for _, n in sorted(candidates, key=lambda x: (-x[0], x[1].title.lower()))[:12]]
        lines.append(f"### {title}")
        lines.append("")
        for n in candidates:
            lines.append(f"- {note_link(n)}")
        lines.append("")

    lines.append("## Orphan / Low-Connectivity Notes")
    lines.append("")
    lines.append("Orphans are not necessarily bad. In Zettelkasten terms, they are unfinished integration points. Either link them into MOCs or mark as standalone reference notes.")
    lines.append("")
    if orphans:
        for n in orphans[:80]:
            lines.append(f"- {note_link(n)} — `{n.domain}`")
        if len(orphans) > 80:
            lines.append(f"- … {len(orphans) - 80} more orphans in JSON.")
    else:
        lines.append("No fully orphan notes detected.")
    lines.append("")

    lines.append("## Broken / Unresolved Internal Links")
    lines.append("")
    if broken:
        for b in broken[:120]:
            lines.append(f"- `{b['source']}` → `[[{b['target']}]]`")
        if len(broken) > 120:
            lines.append(f"- … {len(broken) - 120} more unresolved links in JSON.")
    else:
        lines.append("No unresolved wikilinks/markdown links detected.")
    lines.append("")

    lines.append("## Maintenance Protocol")
    lines.append("")
    lines.append("1. When adding a new essay, link it to at least one domain index/MOC and 2–5 related evergreen notes.")
    lines.append("2. Prefer bidirectional context links over duplicate tags.")
    lines.append("3. Promote repeated themes into short evergreen notes, then link essays to those notes.")
    lines.append("4. Review orphan notes monthly and either connect, archive, or convert them into references.")
    lines.append("5. Keep folder categories broad; let MOCs express the real cross-domain structure.")
    lines.append("")
    lines.append("## Machine-readable Map")
    lines.append("")
    lines.append("Full graph and note metadata are saved at: [`_docs/knowledge-map.json`](knowledge-map.json).")
    lines.append("")

    OUT_MD.write_text("\n".join(lines), encoding="utf-8")
    print(json.dumps(data_json["stats"], ensure_ascii=False, indent=2))
    print(f"Wrote {OUT_MD}")
    print(f"Wrote {OUT_JSON}")


if __name__ == "__main__":
    main()
