#!/usr/bin/env python3
"""Validate the Theravāda curriculum, provenance, Pāli, and source-license contract."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOMAIN = ROOT / "theravada"
CURRICULUM_PATH = ROOT / "_docs" / "theravada-curriculum.json"
LICENSE_PATH = ROOT / "_docs" / "theravada-source-licenses.json"

EXPECTED_MODULE_COUNTS = [4, 6, 6, 6, 6, 4, 4]
ALLOWED_PROVENANCE = {
    "early-sutta",
    "vinaya",
    "abhidhamma",
    "commentary",
    "historical-scholarship",
    "modern-theravada",
    "comparative",
    "science-comparison",
}
REFERENCE_DOCUMENTS = {
    "theravada/Từ Điển Pāli Cốt Lõi.md",
    "theravada/Chuẩn Nguồn Và Xuất Xứ Theravāda.md",
    "theravada/Mục Lục Kinh Dẫn Pāli.md",
    "theravada/Tiến Độ Chương Trình Theravāda.md",
}
REQUIRED_PALI_TERMS = {
    "Theravāda",
    "Tipiṭaka",
    "dukkha",
    "anicca",
    "anattā",
    "paṭiccasamuppāda",
    "kamma",
    "saṃsāra",
    "nibbāna",
    "satipaṭṭhāna",
    "ānāpānasati",
    "vipassanā",
    "jhāna",
    "upekkhā",
}


def fail(message: str) -> None:
    raise AssertionError(message)


def load_json(path: Path) -> dict:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        fail(f"cannot load {path.relative_to(ROOT)}: {exc}")
    if not isinstance(value, dict):
        fail(f"{path.relative_to(ROOT)} must contain a JSON object")
    return value


def frontmatter_value(text: str, name: str) -> str:
    match = re.match(r"^---\s*\n(.*?)\n---", text, re.DOTALL)
    if not match:
        fail("missing YAML frontmatter")
    field = re.search(rf"^{re.escape(name)}:\s*(.+?)\s*$", match.group(1), re.MULTILINE)
    if not field:
        fail(f"missing frontmatter field: {name}")
    value = field.group(1).strip()
    if len(value) > 1 and value[0] == value[-1] and value[0] in {'"', "'"}:
        value = value[1:-1]
    return value


def validate_foundation_docs() -> None:
    expected_files = {ROOT / "theravada" / "index.md", *(ROOT / path for path in REFERENCE_DOCUMENTS)}
    actual_files = set(DOMAIN.glob("*.md"))
    missing = sorted(str(path.relative_to(ROOT)) for path in expected_files - actual_files)
    if missing:
        fail(f"Theravāda foundation files missing: {missing}")

    titles: set[str] = set()
    for path in sorted(actual_files):
        text = path.read_text(encoding="utf-8")
        title = frontmatter_value(text, "title")
        description = frontmatter_value(text, "description")
        rendered_title = f"{title} | redpill.wiki" if len(f"{title} | redpill.wiki") <= 65 else title
        if len(rendered_title) > 65:
            fail(f"SEO title too long in {path.relative_to(ROOT)}: {len(rendered_title)}")
        if not 70 <= len(description) <= 170:
            fail(f"description length invalid in {path.relative_to(ROOT)}: {len(description)}")
        if title in titles:
            fail(f"duplicate Theravāda title: {title}")
        titles.add(title)


def validate_curriculum() -> dict:
    data = load_json(CURRICULUM_PATH)
    if data.get("schema") != "redpill.theravada.curriculum.v1":
        fail("invalid Theravāda curriculum schema")
    if data.get("gateway") != "theravada/index.md":
        fail("invalid Theravāda gateway path")
    if set(data.get("reference_documents") or []) != REFERENCE_DOCUMENTS:
        fail("reference document manifest mismatch")

    modules = data.get("modules") or []
    if [row.get("id") for row in modules] != list(range(1, 8)):
        fail("module ids must be exactly 1..7")
    counts = [row.get("count") for row in modules]
    if counts != EXPECTED_MODULE_COUNTS:
        fail(f"module counts must be {EXPECTED_MODULE_COUNTS}, got {counts}")

    lessons = data.get("lessons") or []
    if [row.get("lesson") for row in lessons] != list(range(1, 37)):
        fail("lesson ids must be exactly 1..36")

    roles: set[str] = set()
    titles: set[str] = set()
    module_counts = {module_id: 0 for module_id in range(1, 8)}
    for row in lessons:
        lesson = row["lesson"]
        module = row.get("module")
        if module not in module_counts:
            fail(f"lesson {lesson} has invalid module {module}")
        module_counts[module] += 1
        if row.get("module_slug") != modules[module - 1].get("slug"):
            fail(f"lesson {lesson} module slug mismatch")

        role = row.get("canonical_role")
        title = row.get("title")
        if not isinstance(role, str) or not role or role in roles:
            fail(f"lesson {lesson} has missing/duplicate canonical role: {role}")
        if not isinstance(title, str) or not title or title in titles:
            fail(f"lesson {lesson} has missing/duplicate title: {title}")
        roles.add(role)
        titles.add(title)

        prerequisites = row.get("prerequisites")
        if not isinstance(prerequisites, list) or any(type(item) is not int for item in prerequisites):
            fail(f"lesson {lesson} prerequisites must be integer lesson ids")
        if len(prerequisites) != len(set(prerequisites)):
            fail(f"lesson {lesson} has duplicate prerequisites")
        if any(item < 1 or item >= lesson for item in prerequisites):
            fail(f"lesson {lesson} prerequisites must point backward only: {prerequisites}")

        provenance = row.get("provenance")
        if not isinstance(provenance, list) or not provenance:
            fail(f"lesson {lesson} needs provenance")
        unknown = set(provenance) - ALLOWED_PROVENANCE
        if unknown:
            fail(f"lesson {lesson} has unknown provenance: {sorted(unknown)}")

        refs = row.get("canonical_refs")
        if not isinstance(refs, list):
            fail(f"lesson {lesson} canonical_refs must be a list")
        if not refs and "science-comparison" not in provenance:
            fail(f"lesson {lesson} needs at least one canonical/source anchor")

    if [module_counts[module_id] for module_id in range(1, 8)] != EXPECTED_MODULE_COUNTS:
        fail("actual lesson module counts do not match module declaration")

    gateway = (DOMAIN / "index.md").read_text(encoding="utf-8")
    for title in titles:
        if f"[[{title}" in gateway:
            fail(f"gateway creates a premature lesson wikilink: {title}")
    return data


def validate_published_lessons(curriculum: dict) -> None:
    published = [row for row in curriculum["lessons"] if row.get("status") == "published"]
    expected_paths = {ROOT / row["path"] for row in published}
    foundation = {ROOT / "theravada" / "index.md", *(ROOT / path for path in REFERENCE_DOCUMENTS)}
    actual_paths = set(DOMAIN.glob("*.md"))
    if actual_paths != foundation | expected_paths:
        fail("Theravāda public file set does not match foundation plus published curriculum")
    source_manifests = [
        load_json(ROOT / "_docs" / "theravada-batch1-sources.json"),
        load_json(ROOT / "_docs" / "theravada-batch2-sources.json"),
        load_json(ROOT / "_docs" / "theravada-batch3-sources.json"),
    ]
    for batch_sources in source_manifests:
        if not isinstance(batch_sources.get("translation_policy"), str) or not batch_sources["translation_policy"]:
            fail("Theravāda batch translation policy missing")
    editions = {}
    for manifest in source_manifests:
        editions.update({row["id"]: row for row in manifest.get("source_editions", [])})
    if not editions:
        fail("Theravāda source editions missing")
    for source_id, source in editions.items():
        for key in ("edition", "license_status", "allowed_use", "url"):
            if not isinstance(source.get(key), str) or not source[key]:
                fail(f"Batch 1 source edition {source_id} missing {key}")
    source_rows = {}
    for manifest in source_manifests:
        source_rows.update({row["lesson"]: row for row in manifest.get("lessons", [])})
    for row in published:
        path = ROOT / row["path"]
        text = path.read_text(encoding="utf-8")
        if frontmatter_value(text, "lesson") != str(row["lesson"]):
            fail(f"lesson number mismatch: {path.relative_to(ROOT)}")
        if frontmatter_value(text, "module") != str(row["module"]):
            fail(f"lesson module mismatch: {path.relative_to(ROOT)}")
        if frontmatter_value(text, "canonical_role") != row["canonical_role"]:
            fail(f"canonical role mismatch: {path.relative_to(ROOT)}")
        if frontmatter_value(text, "source_license_checked") != "true":
            fail(f"source license not checked: {path.relative_to(ROOT)}")
        source = source_rows.get(row["lesson"])
        if not source or source.get("license_checked") is not True:
            fail(f"source manifest missing licensed lesson {row['lesson']}")
        if not source.get("canonical") or not source.get("verification") or not source.get("allowed_use"):
            fail(f"source verification incomplete for lesson {row['lesson']}")
        if row["lesson"] not in {1, 2, 3, 4, 5, 8} and not source.get("claim_segment_map"):
            fail(f"claim-to-segment map missing for lesson {row['lesson']}")
        translation_sources = source.get("translation_sources") or []
        if not translation_sources or any(source_id not in editions for source_id in translation_sources):
            fail(f"translation source edition missing for lesson {row['lesson']}")
        if "<!-- ILLUSTRATION:" in text:
            fail(f"unresolved image placeholder: {path.relative_to(ROOT)}")
        if row["lesson"] in {1, 2, 3, 4, 5, 8}:
            image_batch = "theravada-batch1"
        elif row["lesson"] <= 16:
            image_batch = "theravada-batch2"
        else:
            image_batch = "theravada-batch3"
        refs = re.findall(rf"\.\./assets/illustrations/{image_batch}/([^)]+\.webp)", text)
        if len(refs) != 7 or len(set(refs)) != 7:
            fail(f"lesson must embed seven unique images: {path.relative_to(ROOT)}")
        for ref in refs:
            if not (ROOT / "assets" / "illustrations" / image_batch / ref).is_file():
                fail(f"missing lesson image: {ref}")


def validate_pali() -> None:
    glossary = (DOMAIN / "Từ Điển Pāli Cốt Lõi.md").read_text(encoding="utf-8")
    missing = sorted(term for term in REQUIRED_PALI_TERMS if term not in glossary)
    if missing:
        fail(f"Pāli glossary missing required terms: {missing}")
    if "chuẩn phát âm duy nhất" not in glossary:
        fail("Pāli glossary must disclaim a single authoritative pronunciation")


def validate_licenses() -> None:
    data = load_json(LICENSE_PATH)
    if data.get("schema") != "redpill.theravada.source-licenses.v1":
        fail("invalid source-license schema")
    policy = data.get("policy") or {}
    if policy.get("lesson_publication_requires_license_checked") is not True:
        fail("lesson publication must require license checks")
    if policy.get("platform_license_never_implies_all_hosted_translations") is not True:
        fail("platform-level license inference must be forbidden")

    sources = data.get("sources") or []
    if not sources:
        fail("source-license manifest must not be empty")
    ids: set[str] = set()
    for row in sources:
        source_id = row.get("id")
        if not isinstance(source_id, str) or not source_id or source_id in ids:
            fail(f"missing/duplicate source id: {source_id}")
        ids.add(source_id)
        for key in ("name", "url", "content_type", "edition", "license_status", "allowed_use", "notes"):
            if not isinstance(row.get(key), str) or not row[key].strip():
                fail(f"source {source_id} missing {key}")
        if "pending" not in row["license_status"] and "unclear" not in row["license_status"] and "varies" not in row["license_status"]:
            fail(f"Batch 0 source {source_id} claims an unreviewed final license state")
        if row["allowed_use"] in {"unrestricted", "commercial_reuse"}:
            fail(f"source {source_id} has overbroad allowed_use")


def main() -> int:
    validate_foundation_docs()
    curriculum = validate_curriculum()
    validate_published_lessons(curriculum)
    validate_pali()
    validate_licenses()
    print(json.dumps({
        "status": "pass",
        "foundation_pages": 5,
        "reference_documents": 4,
        "modules": len(curriculum["modules"]),
        "lessons": len(curriculum["lessons"]),
        "module_counts": [row["count"] for row in curriculum["modules"]],
        "published_lessons": sum(row.get("status") == "published" for row in curriculum["lessons"]),
        "global_source_entries": len(load_json(LICENSE_PATH)["sources"]),
        "batch_source_lessons": sum(len(load_json(ROOT / "_docs" / name)["lessons"]) for name in ("theravada-batch1-sources.json", "theravada-batch2-sources.json", "theravada-batch3-sources.json")),
    }, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except AssertionError as exc:
        print(f"Theravāda validation failed: {exc}", file=sys.stderr)
        raise SystemExit(1)
