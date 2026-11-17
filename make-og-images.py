#!/usr/bin/env python3
"""Render 1200x630 Open Graph cards for every E.G.O (identity cards already exist).

Usage:  python3 make-og-images.py
"""

import json
import pathlib

from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = pathlib.Path(__file__).parent
DATA = ROOT / "data" / "ego.json"
OUT = ROOT / "assets" / "og"
FONT_DIR = pathlib.Path(
    "/opt/freestyle/python/lib/python3.12/site-packages/matplotlib/mpl-data/fonts/ttf"
)

W, H = 1200, 630
SIN_COLORS = {
    "Wrath": (224, 66, 79),
    "Lust": (255, 123, 208),
    "Sloth": (224, 166, 60),
    "Gluttony": (255, 180, 162),
    "Gloom": (69, 224, 255),
    "Pride": (127, 166, 255),
    "Envy": (184, 107, 255),
}
GOLD = (255, 239, 35)
PARCHMENT = (242, 234, 216)
MUTED = (164, 159, 178)


def font(name, size):
    return ImageFont.truetype(str(FONT_DIR / name), size)


def wrap(draw, text, face, max_width):
    words, lines, current = text.split(), [], ""
    for word in words:
        candidate = f"{current} {word}".strip()
        if draw.textlength(candidate, font=face) <= max_width:
            current = candidate
        else:
            lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def background(accent):
    base = Image.new("RGB", (W, H), (10, 9, 16))
    glow = Image.new("RGB", (W, H), (10, 9, 16))
    draw = ImageDraw.Draw(glow)
    draw.ellipse((640, -160, 1280, 480), fill=tuple(int(c * 0.42) for c in accent))
    glow = glow.filter(ImageFilter.GaussianBlur(150))
    base = Image.blend(base, glow, 0.75)

    vignette = Image.new("L", (W, H), 0)
    ImageDraw.Draw(vignette).rectangle((0, 0, W, H), fill=255)
    return base


def card(entry):
    accent = SIN_COLORS.get(entry.get("sin", ""), GOLD)
    image = background(accent)
    draw = ImageDraw.Draw(image)

    # artwork on the right, circular like the in-game E.G.O portrait
    art = Image.open(ROOT / entry["art"]).convert("RGBA")
    art = art.resize((520, 520), Image.LANCZOS)
    image.paste(art, (650, 55), art)

    # text block
    eyebrow_face = font("DejaVuSans.ttf", 20)
    title_face = font("DejaVuSerif-Bold.ttf", 54)
    body_face = font("DejaVuSans.ttf", 24)
    small_face = font("DejaVuSans.ttf", 19)

    draw.rectangle((70, 74, 86, 90), fill=GOLD)
    draw.text((104, 72), "E.G.O", font=eyebrow_face, fill=GOLD)
    draw.text(
        (170, 72),
        f"· {entry.get('sin', '')} · {entry.get('risk', '')}",
        font=eyebrow_face,
        fill=MUTED,
    )

    y = 130
    for line in wrap(draw, entry.get("name", ""), title_face, 540)[:3]:
        draw.text((70, y), line, font=title_face, fill=PARCHMENT)
        y += 66

    y += 14
    abnormality = entry.get("abnormality") or "—"
    draw.text((70, y), f"Abnormality · {abnormality}", font=body_face, fill=accent)
    y += 52

    quote = (entry.get("quote") or "").replace("\n", " ")
    for line in wrap(draw, quote, small_face, 520)[:3]:
        draw.text((70, y), line, font=small_face, fill=MUTED)
        y += 30

    draw.text((70, H - 78), "DON QUIXOTE · FAN SITE", font=small_face, fill=(120, 114, 138))

    target = OUT / f"ego-{entry['id']}.jpg"
    image.save(target, "JPEG", quality=86, optimize=True, progressive=True)
    return target


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    entries = json.loads(DATA.read_text(encoding="utf-8"))
    for entry in entries:
        target = card(entry)
        print(f"{target.relative_to(ROOT)} ({target.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    main()
