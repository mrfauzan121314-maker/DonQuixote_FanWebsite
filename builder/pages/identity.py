"""Identity detail pages: templates/identity-detail.html + one module of data mapping."""

from .. import data, layout
from ..components import pager
from ..config import ROOT
from ..layout import esc
from ..template import render


def stat_rows(entry):
    rows = [
        ("Rarity", entry.get("rarity") or "&mdash;"),
        ("Dunia", entry.get("world") or "&mdash;"),
        ("Season", entry.get("season") or "&mdash;"),
        ("Rilis", entry.get("releasedate") or "&mdash;"),
        ("HP", entry.get("hp") or "&mdash;"),
        ("Speed", entry.get("speed") or "&mdash;"),
        ("DEF Mod", entry.get("defmod") or "&mdash;"),
    ]
    resist = entry.get("resist") or {}
    rows += [
        ("Slash", resist.get("slash") or "&mdash;"),
        ("Pierce", resist.get("pierce") or "&mdash;"),
        ("Blunt", resist.get("blunt") or "&mdash;"),
    ]
    return "\n".join(
        f'        <div><dt>{esc(label)}</dt>'
        f'<dd>{value if value == "&mdash;" else esc(value)}</dd></div>'
        for label, value in rows
    )


def skills_html(entry):
    skills = entry.get("skills") or []
    if not skills:
        return '      <p class="detail__empty">Data skill belum tersedia untuk Identity ini.</p>'

    items = []
    for skill in skills:
        meta = " &middot; ".join(x for x in (skill.get("sin"), skill.get("type")) if x)
        coin = skill.get("coin") or ""
        coin_label = f'<span class="skill__coin">{esc(coin)} coin</span>' if coin else ""
        items.append(
            f"""        <li class="skill">
          <span class="skill__slot">{esc(skill.get("slot"))}</span>
          <div class="skill__body">
            <p class="skill__name">{esc(skill.get("name"))}</p>
            <p class="skill__meta">{meta}</p>
          </div>
          {coin_label}
        </li>"""
        )
    return '      <ul class="skills">\n' + "\n".join(items) + "\n      </ul>"


def passives_html(entry):
    passives = entry.get("passives") or []
    if not passives:
        return '      <p class="detail__empty">Tidak ada data passive.</p>'
    items = [
        f"""        <article class="passive">
          <h3>{esc(p.get("name"))}</h3>
          <p>{esc(p.get("text"))}</p>
        </article>"""
        for p in passives
    ]
    return '      <div class="passives">\n' + "\n".join(items) + "\n      </div>"


def voicelines_html(entry):
    lines = entry.get("voicelines") or []
    if not lines:
        return (
            '      <p class="detail__empty">Identity ini tidak memiliki voiceline resmi '
            "&mdash; ia hanya muncul sebagai varian event.</p>"
        )
    items = [
        f"""        <li class="vline">
          <p class="vline__occ">{esc(line.get("occasion"))}</p>
          <p class="vline__text">{esc(line.get("english"))}</p>
        </li>"""
        for line in lines
    ]
    return '      <ul class="vlines">\n' + "\n".join(items) + "\n      </ul>"


def build(entries=None):
    entries = entries or data.identities()
    written = {}

    for index, entry in enumerate(entries):
        name = entry.get("name") or entry["id"]
        quote = (entry.get("quote") or "").strip()
        traits = entry.get("traits") or []
        lines = entry.get("voicelines") or []

        head = layout.head(
            title=f"{name} — Don Quixote · Fan Site",
            description=(
                f"Identity {name} milik Don Quixote (Limbus Company): statistik, skill, "
                "passive, dan voiceline."
            ),
            root="../",
            og_image=f"assets/og/{entry['id']}.jpg",
            og_image_alt=f"Identity {name} — Don Quixote",
            og_type="article",
            image_size=(1200, 630),
            canonical=f"identity/{entry['id']}.html",
        )

        traits_html = (
            '        <ul class="chips">\n'
            + "".join(f"          <li>{esc(t)}</li>\n" for t in traits)
            + "        </ul>\n"
            if traits
            else ""
        )

        body = render(
            "identity-detail.html",
            accent=entry.get("card", {}).get("accent") or "#ffef23",
            art=entry.get("art") or "",
            thumb=data.thumb(entry.get("art") or ""),
            name=name,
            rarity=esc(entry.get("rarity")),
            world=esc(entry.get("world") or "Mirror World"),
            quote=f'        <blockquote class="detail__quote">{esc(quote)}</blockquote>\n' if quote else "",
            stats=stat_rows(entry),
            traits=traits_html,
            skills=skills_html(entry),
            passives=passives_html(entry),
            voiceline_count=len(lines),
            voicelines=voicelines_html(entry),
            pager=pager(entries, index, lambda e: f"{e['id']}.html",
                        aria="Navigasi antar Identity"),
            wiki=esc(entry.get("wiki")),
        )

        page = layout.document(head_html=head, body_html=body, root="../")
        target = ROOT / "identity" / f"{entry['id']}.html"
        target.write_text(page, encoding="utf-8")
        written[str(target.relative_to(ROOT))] = len(page)

    return written
