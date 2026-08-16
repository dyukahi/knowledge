#!/usr/bin/env python3
"""Deterministically convert oversized published illustrations to WebP.

Only assets/illustrations is in scope. Markdown and YAML references are rewritten
after every conversion has passed dimension and decoder verification.
"""

from __future__ import annotations

import argparse
import os
import re
import shutil
import struct
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
IMAGE_ROOT = ROOT / "assets" / "illustrations"
SOURCE_SUFFIXES = {".png", ".jpg", ".jpeg"}
DEFAULT_THRESHOLD = 500 * 1024
DEFAULT_BUDGET = 700 * 1024


def dimensions(path: Path) -> tuple[int, int]:
    data = path.read_bytes()
    if data.startswith(b"\x89PNG\r\n\x1a\n") and len(data) >= 24:
        return struct.unpack(">II", data[16:24])
    if data[:2] == b"\xff\xd8":
        i = 2
        while i + 9 < len(data):
            if data[i] != 0xFF:
                i += 1
                continue
            marker = data[i + 1]
            i += 2
            if marker in (0xD8, 0xD9) or 0xD0 <= marker <= 0xD7:
                continue
            if i + 2 > len(data):
                break
            size = struct.unpack(">H", data[i : i + 2])[0]
            if marker in {0xC0, 0xC1, 0xC2, 0xC3, 0xC5, 0xC6, 0xC7, 0xC9, 0xCA, 0xCB, 0xCD, 0xCE, 0xCF}:
                return struct.unpack(">HH", data[i + 3 : i + 7])[::-1]
            i += size
    if data.startswith(b"RIFF") and data[8:12] == b"WEBP":
        kind = data[12:16]
        if kind == b"VP8X" and len(data) >= 30:
            return (1 + int.from_bytes(data[24:27], "little"), 1 + int.from_bytes(data[27:30], "little"))
        if kind == b"VP8 " and len(data) >= 30 and data[23:26] == b"\x9d\x01\x2a":
            return (int.from_bytes(data[26:28], "little") & 0x3FFF, int.from_bytes(data[28:30], "little") & 0x3FFF)
        if kind == b"VP8L" and len(data) >= 25 and data[20] == 0x2F:
            bits = int.from_bytes(data[21:25], "little")
            return ((bits & 0x3FFF) + 1, ((bits >> 14) & 0x3FFF) + 1)
    raise ValueError(f"unsupported or corrupt image: {path}")


def encode(cwebp: str, dwebp: str, source: Path, output: Path, budget: int) -> None:
    original_dimensions = dimensions(source)
    attempts = (84, 80, 76, 72)
    for quality in attempts:
        subprocess.run(
            [cwebp, "-quiet", "-mt", "-m", "6", "-q", str(quality), "-metadata", "all", str(source), "-o", str(output)],
            check=True,
        )
        if dimensions(output) != original_dimensions:
            raise RuntimeError(f"dimension mismatch: {source}")
        subprocess.run([dwebp, "-quiet", str(output), "-o", os.devnull], check=True)
        if output.stat().st_size <= budget:
            return
    raise RuntimeError(f"cannot meet {budget} byte budget without lowering quality below 72: {source}")


def reference_files() -> list[Path]:
    return sorted(p for p in ROOT.rglob("*.md") if ".git" not in p.parts)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--threshold", type=int, default=DEFAULT_THRESHOLD)
    parser.add_argument("--budget", type=int, default=DEFAULT_BUDGET)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    cwebp = shutil.which("cwebp")
    dwebp = shutil.which("dwebp")
    if (not cwebp or not dwebp) and not args.check:
        parser.error("cwebp and dwebp are required")

    sources = sorted(p for p in IMAGE_ROOT.rglob("*") if p.is_file() and p.suffix.lower() in SOURCE_SUFFIXES and p.stat().st_size > args.threshold)
    if args.check:
        if sources:
            print(f"{len(sources)} oversized source illustrations remain")
            return 1
        print("image source budget check passed")
        return 0

    before = sum(p.stat().st_size for p in sources)
    converted: list[tuple[Path, Path]] = []
    with tempfile.TemporaryDirectory(prefix="redpill-webp-") as temp_dir:
        temp = Path(temp_dir)
        for source in sources:
            relative = source.relative_to(IMAGE_ROOT)
            staged = temp / relative.with_suffix(".webp")
            staged.parent.mkdir(parents=True, exist_ok=True)
            encode(cwebp, dwebp, source, staged, args.budget)
            converted.append((source, staged))

        replacements = {source.relative_to(ROOT).as_posix(): source.relative_to(ROOT).with_suffix(".webp").as_posix() for source, _ in converted}
        changed_text: dict[Path, str] = {}
        for doc in reference_files():
            text = doc.read_text(encoding="utf-8")
            updated = text
            for old, new in replacements.items():
                updated = updated.replace(old, new).replace("../" + old, "../" + new).replace("/" + old, "/" + new)
                updated = updated.replace(Path(old).name, Path(new).name)
            if updated != text:
                changed_text[doc] = updated

        for source, staged in converted:
            destination = source.with_suffix(".webp")
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(staged, destination)
        for doc, text in changed_text.items():
            doc.write_text(text, encoding="utf-8", newline="")

        # Refuse deletion if any published Markdown still mentions an old asset.
        joined = "\n".join(p.read_text(encoding="utf-8") for p in reference_files())
        stale = [old for old in replacements if old in joined or Path(old).name in joined]
        if stale:
            raise RuntimeError(f"stale references prevent source removal: {stale[:5]}")
        for source, _ in converted:
            source.unlink()

    after = sum(source.with_suffix(".webp").stat().st_size for source, _ in converted)
    print(f"converted={len(converted)} before={before} after={after} saved={before-after}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
