"""Home page: the long-form profile, assembled from templates/home.html."""

from .. import data, layout
from ..components import identity_card
from ..config import IDENTITY_GROUPS, ROOT, SITE_NAME, SITE_TAGLINE
from ..template import render


def filters_html(entries):
    counts = {"all": len(entries)}
    for entry in entries:
        group = entry["card"]["group"]
        counts[group] = counts.get(group, 0) + 1

    buttons = []
    for key, label in IDENTITY_GROUPS:
        active = ' is-active' if key == "all" else ""
        pressed = "true" if key == "all" else "false"
        count = f' <span>{counts.get(key, 0)}</span>' if key == "all" else ""
        buttons.append(
            f'          <button type="button" class="filter{active}" data-filter="{key}" '
            f'aria-pressed="{pressed}">{label}{count}</button>'
        )
    return "\n".join(buttons)


def build():
    entries = data.identity_cards()
    cards = "\n\n".join(identity_card(entry) for entry in entries)

    head = layout.head(
        title="Don Quixote — Sinner #3 · Fan Site",
        description=(
            "Fan site untuk Don Quixote, Sinner #3 dari Limbus Company: profil, dua wajahnya "
            "sebagai Sancho, Rocinante, SUEÑO IMPOSIBLE, kutipan, dan 17 Identity."
        ),
        og_image="assets/og/site.jpg",
        og_image_alt="Don Quixote — Sinner #3, Limbus Company fan site",
        image_size=(1200, 630),
        canonical="/",
    )

    body = render(
        "home.html",
        identity_cards=cards,
        identity_filters=filters_html(entries),
        identity_total=len(entries),
    )

    page = layout.document(head_html=head, body_html=body)
    (ROOT / "index.html").write_text(page, encoding="utf-8")
    return {"index.html": len(page)}
