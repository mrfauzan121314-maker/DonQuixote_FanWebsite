#!/usr/bin/env python3
"""Artwork pipeline.

1. Converts any leftover PNG artwork to WebP at its display size.
2. Makes a 640px-wide variant of every detail hero for `srcset` on mobile.

Usage:  python3 optimize-assets.py [--drop-png]
"""

import pathlib
import sys

from PIL import Image

ROOT = pathlib.Path(__file__).parent
CARD_DIR = ROOT / "assets" / "identities"
DETAIL_DIR = ROOT / "assets" / "identities" / "large"
EGO_DIR = ROOT / "assets" / "ego"
QUALITY = 82
THUMB_WIDTH = 640


def to_webp(path):
    image = Image.open(path).convert("RGBA")
    out = path.with_suffix(".webp")
    image.save(out, "WEBP", quality=QUALITY, method=6)
    return path.stat().st_size, out.stat().st_size


def make_thumb(path):
    out = path.with_name(f"{path.stem}-{THUMB_WIDTH}.webp")
    if out.exists() and out.stat().st_mtime >= path.stat().st_mtime:
        return 0, 0
    with Image.open(path) as image:
        image = image.convert("RGBA")
        image.thumbnail((THUMB_WIDTH, THUMB_WIDTH), Image.LANCZOS)
        image.save(out, "WEBP", quality=QUALITY, method=6)
    return 0, out.stat().st_size


def main():
    drop = "--drop-png" in sys.argv
    before = after = 0
    converted = 0

    for folder in (CARD_DIR, DETAIL_DIR, EGO_DIR):
        if not folder.exists():
            continue
        for path in sorted(folder.glob("*.png")):
            old, new = to_webp(path)
            before += old
            after += new
            converted += 1
            if drop:
                path.unlink()

    if converted:
        print(f"png → webp: {converted} file, {before / 1024 / 1024:.2f} MB → {after / 1024 / 1024:.2f} MB")

    thumbs = [make_thumb(p) for p in sorted(DETAIL_DIR.glob("*.webp")) if not p.stem.endswith(f"-{THUMB_WIDTH}")]
    if thumbs:
        count = sum(1 for _, size in thumbs if size)
        total = sum(size for _, size in thumbs) / 1024
        print(f"varian {THUMB_WIDTH}w: {count} file baru ({total:.0f} KB)")


if __name__ == "__main__":
    main()
