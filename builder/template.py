"""A deliberately tiny template renderer: `{{name}}` placeholders, no logic."""

import re

from .config import TEMPLATES

PLACEHOLDER = re.compile(r"\{\{\s*([a-z_]+)\s*\}\}")


def render(template_name, /, **context):
    source = (TEMPLATES / template_name).read_text(encoding="utf-8")

    def replace(match):
        key = match.group(1)
        if key not in context:
            raise KeyError(f"{template_name}: placeholder {{{{{key}}}}} tidak punya nilai")
        return str(context[key])

    return PLACEHOLDER.sub(replace, source)
