import re


def slugify(text: str) -> str:
    value = text.strip().lower()
    value = value.replace(" ", "-")
    value = re.sub(r"[^a-z0-9-]", "", value)
    return value
