"""Small markup pieces shared by more than one page."""

from .config import RESIST_COLORS, SIN_COLORS
from .layout import esc


def badge(text, accent=None):
    style = f' style="--accent: {accent}"' if accent else ""
    return f'<span class="ebadge"{style}>{esc(text)}</span>'


def identity_card(entry):
    """Gallery card for one Identity, driven entirely by data/identities.json."""
    card = entry["card"]
    style = f"--accent: {card['accent']}"
    if card.get("focus"):
        style += f"; --focus: {card['focus']}"
    classes = "idcard idcard--sprite reveal" if card.get("sprite") else "idcard reveal"
    tags = "".join(f"<li>{esc(tag)}</li>" for tag in card.get("tags") or [])

    return f"""        <article class="{classes}" data-group="{card['group']}" style="{style}">
          <div class="idcard__poster">
            <span class="idcard__index">{esc(card['label'])}</span>
            <a class="idcard__poster-link" href="identity/{entry['id']}.html" aria-label="Lihat detail {esc(card['name'])}"><img class="idcard__art" width="560" height="315" src="assets/identities/{entry['id']}.webp" alt="Artwork {esc(card['name'])} Don Quixote" loading="lazy" decoding="async" /></a>
          </div>
          <div class="idcard__body">
            <p class="idcard__world">{esc(card['world'])}</p>
            <h3>{esc(card['name'])}</h3>
            <p class="idcard__desc">
              {esc(card['blurb'])}
            </p>
            <ul class="idcard__tags">{tags}</ul>
          </div>
        </article>"""


def ego_card(entry):
    accent = SIN_COLORS.get(entry.get("sin", ""), "#ffef23")
    quote = (entry.get("quote") or "").strip()
    quote_html = f'          <p class="egocard__quote">{esc(quote)}</p>\n' if quote else ""
    meta_rows = "\n".join(
        f"            <div><dt>{esc(label)}</dt><dd>{esc(value)}</dd></div>"
        for label, value in (
            ("Didapat", entry.get("obtained") or "—"),
            ("Rilis", entry.get("releasedate") or "—"),
            ("Biaya", ", ".join(entry.get("costs") or []) or "—"),
            ("Abnormality", entry.get("abnormality") or "—"),
        )
    )
    return f"""      <article class="egocard reveal" data-risk="{esc(entry.get('risk'))}" data-release="{(entry.get('releasedate') or '').replace('.', '')}" data-cost="{ego_cost(entry)}" style="--accent: {accent}">
        <div class="egocard__art">
          <img src="{esc(entry.get('art') or '')}" alt="Artwork {esc(entry.get('name'))} Don Quixote" width="640" height="640" loading="lazy" decoding="async" />
          <div class="egocard__badges">
            {badge(entry.get('sin'))}
            {badge(entry.get('risk'))}
          </div>
        </div>
        <div class="egocard__body">
          <h2>{esc(entry.get('name'))}</h2>
{quote_html}          <p class="egocard__note">{esc(entry.get('note'))}</p>
          <dl class="egocard__meta">
{meta_rows}
          </dl>
          <a class="egocard__link" href="ego/{esc(entry['id'])}.html">Efek coin &amp; Corrosion &rarr;</a>
        </div>
      </article>"""


def ego_cost(entry):
    total = 0
    for part in entry.get("costs") or []:
        tail = part.rsplit(" ", 1)[-1]
        if tail.isdigit():
            total += int(tail)
    return total


def skill_block(skill, label, accent, show_label=True):
    """Power/coin summary plus the per-coin effect list of one E.G.O skill."""
    if not skill or not skill.get("name"):
        return ""
    stats = [
        prefix + value
        for prefix, value in (
            ("Base ", skill.get("spower")),
            ("Coin ", skill.get("cpower")),
            ("", (skill.get("coin") or "") and skill["coin"] + " coin"),
            ("Atk Weight ", skill.get("atkweight")),
        )
        if value
    ]
    stats_html = "".join(f"<span>{esc(stat)}</span>" for stat in stats)
    coins = "".join(
        f'<li><span class="coin-n">Coin {i}</span><span>{esc(text)}</span></li>'
        for i, text in enumerate(skill.get("effects") or [], start=1)
    )
    coins_html = (
        f'<ul class="coins">{coins}</ul>'
        if coins
        else '<p class="detail__empty">Tidak ada efek coin tercatat.</p>'
    )
    heading = f"<h3>{esc(label)}</h3>" if show_label else ""
    return f"""        <div class="eskill">
          <div class="eskill__head">
            {heading}
            {badge(skill.get('sin'), accent)}
            {badge(skill.get('type'), accent)}
          </div>
          <div class="eskill__stats">{stats_html}</div>
{coins_html}
        </div>"""


def resist_chips(entry):
    chips = "".join(
        f'<span>{esc(item["sin"])} <b style="color: {RESIST_COLORS.get(item["value"], "#ffef23")}">'
        f'{esc(item["value"])}</b></span>'
        for item in entry.get("resist_full") or []
    )
    return f'        <div class="resist">{chips}</div>'


def bullet_list(items, empty_text):
    if not items:
        return f'<span class="tspin__none">{esc(empty_text)}</span>'
    return '<ul class="tspin__list">' + "".join(f"<li>{esc(i)}</li>" for i in items) + "</ul>"


def threadspin_table(entry):
    data = entry.get("threadspin") or {}
    if not data:
        return (
            '<p class="detail__empty">E.G.O dasar ini tidak memiliki peningkatan Threadspin — '
            "efektif sejak awal pada nilai yang tertera di atas.</p>"
        )

    has_corrosion = bool((entry.get("corrosion") or {}).get("name"))
    rows = ""
    for level in ("2", "3", "4"):
        awakening = bullet_list((data.get("awakening") or {}).get(level), "Tidak ada perubahan")
        if has_corrosion:
            corrosion = bullet_list((data.get("corrosion") or {}).get(level), "Tidak ada perubahan")
        else:
            corrosion = '<span class="tspin__none">Tidak ada varian Corrosion</span>'
        rows += (
            f'<tr><th scope="row">TS {level}</th>'
            f'<td data-label="Awakening">{awakening}</td>'
            f'<td data-label="Corrosion">{corrosion}</td></tr>'
        )

    return f"""        <table class="tspin">
          <caption class="tspin__caption">Threadspin 1 adalah nilai dasar yang tertera pada panel Awakening dan Corrosion di atas.</caption>
          <thead>
            <tr><th scope="col">Level</th><th scope="col">Awakening</th><th scope="col">Corrosion</th></tr>
          </thead>
          <tbody>{rows}</tbody>
        </table>"""


def pager(entries, index, href, label_prev="Sebelumnya", label_next="Selanjutnya", aria="Navigasi"):
    """Previous/next links inside an ordered collection."""
    parts = []
    if index > 0:
        prev = entries[index - 1]
        parts.append(
            f'<a class="pager__link pager__link--prev" href="{href(prev)}">'
            f"<span>{label_prev}</span>{esc(prev.get('name'))}</a>"
        )
    if index < len(entries) - 1:
        nxt = entries[index + 1]
        parts.append(
            f'<a class="pager__link pager__link--next" href="{href(nxt)}">'
            f"<span>{label_next}</span>{esc(nxt.get('name'))}</a>"
        )
    return f'    <nav class="pager" aria-label="{aria}">\n      ' + "\n      ".join(parts) + "\n    </nav>"
