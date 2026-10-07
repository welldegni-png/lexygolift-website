from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
LOCALES = [
    "en", "es", "pt-br", "de", "fr", "it", "ar", "id", "tr",
    "pl", "vi", "th", "ru", "ja", "ko", "hi", "ms",
]
LOCALE_DIRS = set(LOCALES) - {"en"}
LANG_ATTRS = {locale: locale for locale in LOCALES}
LANG_ATTRS["pt-br"] = "pt-BR"


def english_pages():
    return [
        page for page in DIST.rglob("*.html")
        if page.relative_to(DIST).parts[0] not in LOCALE_DIRS
    ]


def fail(message):
    raise SystemExit(message)


base_pages = english_pages()
if len(base_pages) != 83:
    fail(f"Expected 83 English pages, found {len(base_pages)}")

for locale in LOCALES:
    pages = base_pages if locale == "en" else list((DIST / locale).rglob("*.html"))
    if len(pages) != 83:
        fail(f"Expected 83 {locale} pages, found {len(pages)}")

    for page in pages:
        html = page.read_text(encoding="utf-8")
        expected_html = rf'<html lang="{re.escape(LANG_ATTRS[locale])}"(?: dir="(?:ltr|rtl)")?'
        if not re.search(expected_html, html):
            fail(f"Incorrect html language on {page}")
        if locale == "ar" and '<html lang="ar" dir="rtl"' not in html:
            fail(f"Arabic page is missing RTL direction: {page}")
        if locale != "ar" and ' dir="rtl"' in html.split(">", 1)[0]:
            fail(f"Unexpected RTL direction: {page}")
        if html.count('rel="alternate" hreflang=') != 18:
            fail(f"Incorrect hreflang count: {page}")
        if 'class="language-switcher"' not in html:
            fail(f"Missing language switcher: {page}")
        if not re.search(r'<link rel="canonical" href="https://www\.lexygolift\.com/', html):
            fail(f"Missing canonical URL: {page}")
        if re.search(r"ZXPROTECT|zxprotected_|ZXSEG", html, re.I):
            fail(f"Translation placeholder found: {page}")
        title = re.search(r"<title>(.*?)</title>", html, re.S)
        if not title or not title.group(1).strip():
            fail(f"Missing page title: {page}")

print(f"Validated {len(base_pages) * len(LOCALES)} pages across {len(LOCALES)} languages.")
