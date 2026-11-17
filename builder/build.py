"""Build every page of the site.

Usage:
    python3 -m builder.build                    # relative OG URLs (local preview)
    SITE_URL=https://domain.com python3 -m builder.build   # absolute OG + canonical URLs
"""

import sys

from . import data
from .config import BASE_URL
from .pages import ego, home, identity


def main():
    written = {}
    written.update(identity.build(data.identities()))
    written.update(ego.build())
    written.update(home.build())

    pages = {path: size for path, size in written.items() if path.endswith(".html")}
    print(f"built {len(pages)} halaman")
    print(f"OG/canonical: {'absolut → ' + BASE_URL if BASE_URL else 'relatif (set SITE_URL untuk URL absolut)'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
