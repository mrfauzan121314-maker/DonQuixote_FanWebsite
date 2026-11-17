PY ?= python3
SITE_URL ?=

.PHONY: build check preview assets og clean

# Build every page. Set SITE_URL to emit absolute OG/canonical URLs.
build:
	SITE_URL=$(SITE_URL) $(PY) -m builder.build

# Static checks: metadata, local references, markup structure.
check:
	$(PY) tools/check_site.py $(if $(SITE_URL),--base-url $(SITE_URL))

# Regenerate artwork variants, fonts and OG images.
assets:
	$(PY) optimize-assets.py
	$(PY) self-host-fonts.py
	$(PY) make-og-images.py

# Rebuild the Open Graph cards only.
og:
	$(PY) make-og-images.py

preview:
	$(PY) -m http.server 3000 --bind 0.0.0.0
