"""One definition of <head>, navigation and footer, shared by every page."""

import html

from . import data
from .config import BASE_URL, LANG, LOCALE, NAV_LINKS, SITE_NAME


def esc(value):
    return html.escape(str(value), quote=True)


def _meta(attr, key, value):
    return f'  <meta {attr}="{key}" content="{esc(value)}" />'


def head(
    *,
    title,
    description,
    root="",
    og_image=None,
    og_image_alt="",
    og_type="website",
    canonical="",
    image_size=None,
):
    """Build the document head.

    OG and canonical URLs are absolute as soon as SITE_URL is set at build time;
    without it they stay relative so local previews keep working.
    """
    image = data.absolute(og_image) if og_image else ""
    # A relative canonical is worse than none: only emit it once a site URL exists.
    page_url = data.absolute(canonical) if (canonical and BASE_URL) else ""
    alt = og_image_alt or title

    lines = [
        '<meta charset="UTF-8" />',
        '<meta name="viewport" content="width=device-width, initial-scale=1" />',
        f"<title>{esc(title)}</title>",
        _meta("name", "description", description),
        '  <meta name="theme-color" content="#0a0910" />',
        '  <meta name="color-scheme" content="dark" />',
        _meta("property", "og:type", og_type),
        _meta("property", "og:site_name", SITE_NAME),
        _meta("property", "og:locale", LOCALE),
        _meta("property", "og:title", title),
        _meta("property", "og:description", description),
    ]
    if page_url:
        lines.append(_meta("property", "og:url", page_url))
    if image:
        lines.append(_meta("property", "og:image", image))
        lines.append(_meta("property", "og:image:alt", alt))
        if image_size:
            width, height = image_size
            lines.append(_meta("property", "og:image:width", width))
            lines.append(_meta("property", "og:image:height", height))

    lines += [
        '  <meta name="twitter:card" content="summary_large_image" />',
        _meta("name", "twitter:title", title),
        _meta("name", "twitter:description", description),
    ]
    if image:
        lines.append(_meta("name", "twitter:image", image))
        lines.append(_meta("name", "twitter:image:alt", alt))
    if page_url:
        lines.append(f'  <link rel="canonical" href="{esc(page_url)}" />')

    lines += [
        f'  <link rel="icon" href="{root}assets/favicon.svg" type="image/svg+xml" />',
        f'  <link rel="icon" href="{root}assets/favicon-32.png" sizes="32x32" type="image/png" />',
        f'  <link rel="apple-touch-icon" href="{root}assets/apple-touch-icon.png" />',
        f'  <link rel="preload" href="{root}assets/fonts/cinzel-latin.woff2" as="font" type="font/woff2" crossorigin />',
        f'  <link rel="stylesheet" href="{root}assets/fonts/fonts.css" />',
        "  <noscript><style>.reveal{opacity:1;transform:none}</style></noscript>",
        f'  <link rel="stylesheet" href="{root}styles.css" />',
    ]
    return "\n".join(lines)


MARK_SVG = (
    '<svg viewBox="0 0 24 24" fill="none">'
    '<path d="M11.2 2.4 12.7 9l6.6 1.6-6.6 1.6-1.5 6.6-1.5-6.6L3.1 10.6 9.7 9z" fill="currentColor" />'
    '<path d="M17.9 15.3 22 21.7" stroke="currentColor" stroke-width="1.2" stroke-linecap="round" />'
    "</svg>"
)


def nav(root="", active=None):
    items = []
    for key, label, href in NAV_LINKS:
        current = ' class="is-active"' if key == active else ""
        items.append(f'      <a href="{root}{href}"{current}>{label}</a>')
    links = "\n".join(items)
    return f"""  <header class="nav">
    <a class="nav__brand" href="{root}index.html">
      <span class="nav__mark" aria-hidden="true">{MARK_SVG}</span>
      <span class="nav__name">DON QUIXOTE</span>
    </a>
    <button class="nav__toggle" id="navToggle" aria-expanded="false" aria-controls="navMenu">
      <span></span><span></span><span></span>
      <span class="sr-only">Buka menu</span>
    </button>
    <nav class="nav__menu" id="navMenu">
{links}
    </nav>
  </header>"""


def footer():
    return """  <footer class="footer">
    <div class="footer__star" aria-hidden="true">&#10022;</div>
    <p class="footer__title">&ldquo;Dream the impossible dream.&rdquo;</p>
    <p class="footer__note">
      Fan site tidak resmi, dibuat oleh penggemar. <em>Limbus Company</em> dan seluruh karakternya
      adalah milik Project Moon. Materi referensi dari Limbus Company Wiki (CC BY-SA 4.0).
    </p>
  </footer>"""


def document(*, head_html, body_html, root="", active=None, body_class=""):
    """Assemble a full page: head, chrome (nav + body + footer), script tag."""
    body_attr = f' class="{body_class}"' if body_class else ""
    return f"""<!DOCTYPE html>
<html lang="{LANG}">
<head>
{head_html}
</head>
<body{body_attr}>
  <div class="grain" aria-hidden="true"></div>

{nav(root=root, active=active)}

{body_html}

{footer()}
  <script src="{root}script.js" defer></script>
</body>
</html>
"""
