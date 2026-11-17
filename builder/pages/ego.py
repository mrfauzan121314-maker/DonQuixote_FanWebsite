"""E.G.O gallery and detail pages."""

from .. import data, layout
from ..components import (
    badge,
    ego_card,
    pager,
    resist_chips,
    skill_block,
    threadspin_table,
)
from ..config import RISK_ORDER, ROOT, SIN_COLORS
from ..layout import esc
from ..template import render


def risk_stats(entries):
    counts = {}
    for entry in entries:
        counts[entry.get("risk")] = counts.get(entry.get("risk"), 0) + 1
    order = sorted(counts.items(), key=lambda kv: RISK_ORDER.index(kv[0]) if kv[0] in RISK_ORDER else 99)
    return "\n".join(
        f"        <div><strong>{count}</strong><span>{esc(risk)}</span></div>" for risk, count in order
    )


def gallery_note(entries):
    highest = max(entries, key=lambda e: RISK_ORDER.index(e["risk"]) if e["risk"] in RISK_ORDER else -1)
    latest = max(entries, key=lambda e: e.get("releasedate") or "")
    return (
        f"      Tingkat tertinggi: {esc(highest.get('name'))} ({esc(highest.get('risk'))}) &middot;\n"
        f"      rilis terbaru: {esc(latest.get('name'))} ({esc(latest.get('releasedate'))}).\n"
        "      Artwork E.G.O milik Project Moon, bersumber dari Limbus Company Wiki (CC BY-SA 4.0)."
    )


def gallery():
    entries = data.egos()
    head = layout.head(
        title="Galeri E.G.O — Don Quixote · Fan Site",
        description=(
            "Semua E.G.O Don Quixote dari Limbus Company: artwork, kutipan awakening, "
            "efek serangan, passive, biaya sin, dan resistensi."
        ),
        og_image="assets/og/site.jpg",
        og_image_alt="Galeri E.G.O Don Quixote",
        image_size=(1200, 630),
        canonical="ego.html",
    )
    body = render(
        "ego-gallery.html",
        total=len(entries),
        stats=risk_stats(entries),
        cards="\n".join(ego_card(entry) for entry in entries),
        footer_note=gallery_note(entries),
    )
    page = layout.document(head_html=head, body_html=body, active="ego")
    (ROOT / "ego.html").write_text(page, encoding="utf-8")
    return {"ego.html": len(page)}


def facts_html(entry, accent):
    rows = [
        ("Abnormality", entry.get("abnormality") or "—"),
        ("Didapat", entry.get("obtained") or "—"),
        ("Rilis", entry.get("releasedate") or "—"),
        ("Tingkat", entry.get("risk") or "—"),
        ("Biaya", ", ".join(entry.get("costs") or []) or "—"),
        ("Sanity", f"{entry.get('asanity') or '—'} / {entry.get('csanity') or '—'}"),
    ]
    return "\n".join(
        f"            <div><dt>{esc(label)}</dt><dd>{esc(value)}</dd></div>" for label, value in rows
    )


def passive_html(entry):
    passive = entry.get("passive") or {}
    if not passive.get("name"):
        return '          <p class="detail__empty">Tidak ada data passive.</p>'
    return f"""          <article class="passive">
            <h3>{esc(passive.get('name'))}</h3>
            <p>{esc(passive.get('text'))}</p>
          </article>"""


def corrosion_html(entry, accent):
    corrosion = entry.get("corrosion") or {}
    if not corrosion.get("name"):
        return (
            '        <p class="detail__empty">Sebagai E.G.O dasar, varian ini tidak memiliki '
            "bentuk Corrosion — hanya bisa dipakai lewat Awakening.</p>"
        )
    quote = (entry.get("cquote") or "").strip()
    quote_html = f'            <blockquote class="edetail__quote">{esc(quote)}</blockquote>\n' if quote else ""
    return f"""        <div class="ecorrosion">
          <div>
            {quote_html}{skill_block(corrosion, "Corrosion", accent, show_label=False)}
          </div>
        </div>"""


def detail(index, entry, entries):
    name = entry.get("name") or entry["id"]
    accent = SIN_COLORS.get(entry.get("sin", ""), "#ffef23")
    quote = (entry.get("quote") or "").strip()

    head = layout.head(
        title=f"{name} — E.G.O Don Quixote · Fan Site",
        description=(
            f"E.G.O {name} milik Don Quixote: efek coin lengkap, resistensi, passive, "
            "dan varian Corrosion."
        ),
        root="../",
        og_image=f"assets/og/ego-{entry['id']}.jpg",
        og_image_alt=f"E.G.O {name} — Don Quixote",
        og_type="article",
        image_size=(1200, 630),
        canonical=f"ego/{entry['id']}.html",
    )

    body = render(
        "ego-detail.html",
        accent=accent,
        art=entry.get("art") or "",
        name=name,
        badges="\n          ".join(
            [badge(entry.get("sin")), badge(entry.get("risk")), '<span class="ebadge">E.G.O</span>']
        ),
        quote=f'        <blockquote class="edetail__quote">{esc(quote)}</blockquote>\n' if quote else "",
        facts=facts_html(entry, accent),
        resist=resist_chips(entry),
        passive=passive_html(entry),
        awakening=skill_block(entry.get("awakening"), "Awakening", accent, show_label=False),
        corrosion=corrosion_html(entry, accent),
        threadspin=threadspin_table(entry),
        pager=pager(entries, index, lambda e: f"{e['id']}.html",
                    aria="Navigasi antar E.G.O"),
        wiki=esc(entry.get("wiki")),
    )

    page = layout.document(head_html=head, body_html=body, root="../", active="ego")
    target = ROOT / "ego" / f"{entry['id']}.html"
    target.write_text(page, encoding="utf-8")
    return str(target.relative_to(ROOT)), len(page)


def build():
    entries = data.egos()
    written = gallery()
    for index, entry in enumerate(entries):
        path, size = detail(index, entry, entries)
        written[path] = size
    return written
