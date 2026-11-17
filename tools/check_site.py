#!/usr/bin/env python3
"""Static checks for the generated site.

Verifies that every page has the metadata it needs, that every local reference
resolves, and that the markup is structurally sound. Exit code 1 on failure.

Usage:  python3 tools/check_site.py [--base-url https://domain]
"""

import glob
import os
import re
import sys
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "param", "source", "track", "wbr"}


def pages():
    return ["index.html", "ego.html"] + sorted(glob.glob("identity/*.html")) + sorted(glob.glob("ego/*.html"))


class Balance(HTMLParser):
    def __init__(self):
        super().__init__()
        self.stack = []
        self.problems = []

    def handle_starttag(self, tag, attrs):
        if tag not in VOID:
            self.stack.append(tag)

    def handle_endtag(self, tag):
        if tag in VOID:
            return
        if not self.stack:
            self.problems.append(f"</{tag}> tanpa pembuka")
        elif self.stack[-1] != tag:
            self.problems.append(f"</{tag}> menutup <{self.stack[-1]}>")
            self.stack.pop()
        else:
            self.stack.pop()


def local_refs(html):
    refs = re.findall(r'(?:href|src)="([^"]+)"', html)
    for srcset in re.findall(r'srcset="([^"]+)"', html):
        refs += [part.strip().rsplit(" ", 1)[0] for part in srcset.split(",")]
    return refs


def main():
    base_url = ""
    if "--base-url" in sys.argv:
        base_url = sys.argv[sys.argv.index("--base-url") + 1].rstrip("/")

    errors, warnings = [], []
    page_list = pages()

    for page in page_list:
        html = (ROOT / page).read_text(encoding="utf-8")
        rel = os.path.dirname(page)

        for ref in local_refs(html):
            if ref.startswith(("http", "#", "mailto:", "data:")):
                continue
            target = ref.split("#")[0]
            if target and not (ROOT / os.path.normpath(os.path.join(rel, target))).exists():
                errors.append(f"{page}: referensi hilang → {ref}")

        for tag in re.findall(r"<img[^>]*>", html):
            if "width=" not in tag or "height=" not in tag:
                warnings.append(f"{page}: <img> tanpa width/height")
                break

        checks = {
            "<title>": 1,
            'name="description"': 1,
            'property="og:title"': 1,
            'property="og:description"': 1,
            'property="og:image"': 1,
            'name="twitter:card"': 1,
            "<h1": 1,
            "<script": 1,
            "<noscript>": 1,
        }
        for needle, minimum in checks.items():
            if html.count(needle) < minimum:
                errors.append(f"{page}: tidak ada {needle}")

        if 'rel="canonical"' not in html and base_url:
            warnings.append(f"{page}: tanpa canonical (base URL diisi, seharusnya ada)")
        if "{{" in html or "}}" in html:
            errors.append(f"{page}: sisa placeholder template")

        parser = Balance()
        parser.feed(html)
        if parser.problems or parser.stack:
            errors.append(f"{page}: struktur HTML → {(parser.problems or ['tag tak tertutup'])[:2]}")

    for message in warnings[:10]:
        print(f"  warn  {message}")

    if errors:
        print(f"\n{len(errors)} masalah:")
        for message in errors[:25]:
            print(f"  gagal {message}")
        return 1

    print(f"OK — {len(page_list)} halaman, referensi lengkap, metadata lengkap, struktur valid")
    return 0


if __name__ == "__main__":
    sys.exit(main())
