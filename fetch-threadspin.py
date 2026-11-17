#!/usr/bin/env python3
"""Fetch the {{Threadspin}} block of every E.G.O page and merge it into data/ego.json.

Usage:  python3 fetch-threadspin.py
"""

import json
import pathlib
import re
import urllib.parse
import urllib.request

ROOT = pathlib.Path(__file__).parent
DATA = ROOT / "data" / "ego.json"
API = "https://limbuscompany.wiki.gg/api.php"
UA = {"User-Agent": "DonQuixoteFanSite/1.0 (local dev)"}


def wikitext(title):
    query = urllib.parse.urlencode(
        {"action": "parse", "page": title, "prop": "wikitext", "format": "json", "formatversion": "2"}
    )
    request = urllib.request.Request(f"{API}?{query}", headers=UA)
    payload = json.load(urllib.request.urlopen(request, timeout=60))
    if "error" in payload:
        raise RuntimeError(payload["error"].get("info", "unknown error"))
    return payload["parse"]["wikitext"]


def find_template(text, name):
    marker = "{{" + name
    start = text.lower().find(marker.lower())
    if start == -1:
        return None
    depth = 0
    i = start
    while i < len(text) - 1:
        pair = text[i : i + 2]
        if pair == "{{":
            depth += 1
            i += 2
            continue
        if pair == "}}":
            depth -= 1
            i += 2
            if depth == 0:
                return text[start + 2 : i - 2]
            continue
        i += 1
    return None


def split_params(body):
    parts, buf, depth = [], [], 0
    i = 0
    while i < len(body):
        pair = body[i : i + 2]
        if pair in ("{{", "[["):
            depth += 1
            buf.append(pair)
            i += 2
            continue
        if pair in ("}}", "]]"):
            depth -= 1
            buf.append(pair)
            i += 2
            continue
        if body[i] == "|" and depth == 0:
            parts.append("".join(buf))
            buf = []
            i += 1
            continue
        buf.append(body[i])
        i += 1
    parts.append("".join(buf))
    return parts


def params_of(body):
    out = {}
    for chunk in split_params(body):
        if "=" not in chunk:
            continue
        key, value = chunk.split("=", 1)
        out[key.strip().lower()] = value.strip()
    return out


def _expand(name, parts):
    if name == "statuseffect":
        return parts[1].strip() if len(parts) > 1 else ""
    if name == "icons":
        icon = (parts[1].strip() if len(parts) > 1 else "")
        match = re.match(r"CoinEffect(\d)", icon, flags=re.I)
        return f"[Coin {match.group(1)}] " if match else ""
    if name in ("uptiecoin", "coin"):
        number = parts[1].strip() if len(parts) > 1 else "1"
        body = "|".join(parts[2:]) if len(parts) > 2 else ""
        return f"[Coin {number}] {body}"
    return ""


def clean(text):
    # Expand innermost templates first so nested ones survive intact.
    for _ in range(20):
        match = re.search(r"\{\{([^{}]*)\}\}", text)
        if not match:
            break
        inner = match.group(1)
        parts = inner.split("|")
        replacement = _expand(parts[0].strip().lower(), parts)
        text = text[: match.start()] + replacement + text[match.end() :]

    text = re.sub(r"\[\[[^\]|]*\|([^\]]*)\]\]", r"\1", text)
    text = re.sub(r"\[\[([^\]]*)\]\]", r"\1", text)
    text = re.sub(r"<br\s*/?>", " ", text, flags=re.I)
    text = text.replace("'''", "").replace("''", "")
    text = re.sub(r"<[^>]+>", "", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip(" ,;|")


def bullets(raw):
    """Turn wiki bullets into plain strings, joining continuation lines."""
    items, current = [], None
    for line in raw.split("\n"):
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith("*"):
            if current:
                items.append(current)
            current = stripped.lstrip("*").strip()
        elif current is not None:
            current += " " + stripped
    if current:
        items.append(current)

    cleaned = []
    for item in items:
        text = clean(item)
        if text:
            cleaned.append(text)
    return cleaned


def threadspin(title):
    body = find_template(wikitext(title), "Threadspin")
    if body is None:
        return {}
    params = params_of(body)
    result = {"awakening": {}, "corrosion": {}}
    for level in ("2", "3", "4"):
        for prefix, key in (("au", "awakening"), ("cu", "corrosion")):
            items = bullets(params.get(prefix + level, ""))
            if items:
                result[key][level] = items
    if not result["awakening"] and not result["corrosion"]:
        return {}
    return result


def main():
    entries = json.loads(DATA.read_text(encoding="utf-8"))
    for entry in entries:
        title = urllib.parse.unquote(entry["wiki"].rsplit("/", 1)[-1])
        try:
            data = threadspin(title)
        except Exception as error:  # noqa: BLE001
            print(f"  ! {entry['id']}: {error}")
            data = {}
        entry["threadspin"] = data
        levels = sorted(set(data.get("awakening", {})) | set(data.get("corrosion", {})))
        print(f"{entry['id']}: level berubah = {levels or 'tidak ada'}")
    DATA.write_text(json.dumps(entries, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"updated {DATA.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
