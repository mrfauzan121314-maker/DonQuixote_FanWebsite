"""Site-wide constants. The only place that knows about names, URLs and colours."""

import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TEMPLATES = ROOT / "templates"
DATA = ROOT / "data"

SITE_NAME = "Don Quixote — Fan Site"
SITE_TAGLINE = "Fan site untuk Don Quixote, Sinner #3 dari Limbus Company"
LANG = "id"
LOCALE = "id_ID"

# Absolute URLs for OG/canonical tags. Set SITE_URL=https://domain when publishing:
#   SITE_URL=https://contoh.com python3 -m builder.build
BASE_URL = os.environ.get("SITE_URL", "").strip().rstrip("/")

NAV_LINKS = (
    ("profil", "Profil", "index.html#profil"),
    ("dua-wajah", "Dua Wajah", "index.html#dua-wajah"),
    ("rocinante", "Rocinante", "index.html#rocinante"),
    ("kutipan", "Kutipan", "index.html#kutipan"),
    ("perjalanan", "Perjalanan", "index.html#perjalanan"),
    ("galeri", "Galeri", "index.html#galeri"),
    ("ego", "E.G.O", "ego.html"),
    ("trivia", "Trivia", "index.html#trivia"),
)

IDENTITY_GROUPS = (
    ("all", "Semua"),
    ("association", "Association"),
    ("corp", "Corp"),
    ("ego", "E.G.O"),
    ("other", "Lainnya"),
)

SIN_COLORS = {
    "Wrath": "#e0424f",
    "Lust": "#ff7bd0",
    "Sloth": "#e0a63c",
    "Gluttony": "#ffb4a2",
    "Gloom": "#45e0ff",
    "Pride": "#7fa6ff",
    "Envy": "#b86bff",
}

RESIST_COLORS = {
    "Ineff": "#7fd6a8",
    "Ineffective": "#7fd6a8",
    "Endure": "#ffd166",
    "Normal": "#a49fb2",
    "Weak": "#ff9f6b",
    "Fatal": "#ff5f6d",
}

RISK_ORDER = ["ZAYIN", "TETH", "HE", "WAW", "ALEPH"]
