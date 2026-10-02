import json
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse


ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"


class PageParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []
        self.images = []
        self.in_json_ld = False
        self.json_ld = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "a" and attrs.get("href"):
            self.links.append(attrs["href"])
        if tag in {"img", "script", "link"}:
            value = attrs.get("src") or attrs.get("href")
            if value:
                self.images.append(value)
        if tag == "script" and attrs.get("type") == "application/ld+json":
            self.in_json_ld = True

    def handle_endtag(self, tag):
        if tag == "script" and self.in_json_ld:
            self.in_json_ld = False

    def handle_data(self, data):
        if self.in_json_ld:
            self.json_ld.append(data)


def internal_target(url):
    parsed = urlparse(url)
    if parsed.scheme or parsed.netloc or url.startswith(("mailto:", "tel:", "#")):
        return None
    path = parsed.path
    if not path.startswith("/"):
        return None
    if path.endswith("/"):
        return DIST / path.strip("/") / "index.html"
    return DIST / path.lstrip("/")


def main():
    errors = []
    html_files = list(DIST.rglob("*.html"))
    for page in html_files:
        parser = PageParser()
        parser.feed(page.read_text(encoding="utf-8"))
        for url in parser.links + parser.images:
            target = internal_target(url)
            if target and not target.exists():
                errors.append(f"{page.relative_to(DIST)} -> missing {url}")
        for block in parser.json_ld:
            try:
                json.loads(block)
            except json.JSONDecodeError as exc:
                errors.append(f"{page.relative_to(DIST)} -> invalid JSON-LD: {exc}")
    required = ["robots.txt", "sitemap.xml", "llms.txt", "assets/site.css", "assets/site.js"]
    for name in required:
        if not (DIST / name).exists():
            errors.append(f"Missing required file: {name}")
    if errors:
        print("\n".join(errors))
        raise SystemExit(1)
    print(f"Validated {len(html_files)} HTML files: internal links, assets, and JSON-LD are complete.")


if __name__ == "__main__":
    main()

