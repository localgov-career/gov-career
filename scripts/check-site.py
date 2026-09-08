"""Check built HTML, internal links, metadata and sitemap without extra dependencies.

Usage: python3 scripts/check-site.py [build-directory]
"""
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path
import re
import sys
from urllib.parse import unquote, urljoin, urlparse
import xml.etree.ElementTree as ET


class Page(HTMLParser):
    def __init__(self, source):
        super().__init__()
        self.links, self.ids, self.canonical = [], [], []
        self.meta, self.h1, self.title, self.in_title = {}, 0, "", False
        self.feed(source)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if "id" in attrs:
            self.ids.append(attrs["id"])
        if tag == "h1":
            self.h1 += 1
        if tag == "a" and "href" in attrs:
            self.links.append(attrs["href"])
        if tag == "title":
            self.in_title = True
        if tag == "meta":
            self.meta[attrs.get("name", attrs.get("property"))] = attrs.get("content", "")
        if tag == "link" and attrs.get("rel") == "canonical":
            self.canonical.append(attrs.get("href"))

    def handle_endtag(self, tag):
        if tag == "title":
            self.in_title = False

    def handle_data(self, data):
        if self.in_title:
            self.title += data


root = Path(__file__).resolve().parent.parent
build = Path(sys.argv[1]) if len(sys.argv) > 1 else root / "dist"
base = re.search(r'siteUrl = "([^"]+)"', (root / "src/data/site.js").read_text()).group(1)
pages, errors = {}, []
for path in build.rglob("*.html"):
    route = "/" + path.relative_to(build).as_posix().removesuffix("index.html")
    pages[route] = Page(path.read_text())
if not pages:
    raise SystemExit("No built pages found; run npm run build first.")

for route, page in pages.items():
    if page.h1 != 1 or not page.title or "undefined" in page.title:
        errors.append(f"{route}: invalid title or h1")
    if not page.meta.get("description"):
        errors.append(f"{route}: missing description")
    if page.canonical != [base + route] or page.meta.get("og:url") != base + route:
        errors.append(f"{route}: incorrect canonical or og:url")
    if page.meta.get("og:image") != base + "/og-default.png":
        errors.append(f"{route}: missing social image")
    if any(count > 1 for count in Counter(page.ids).values()):
        errors.append(f"{route}: duplicate IDs")
    for href in page.links:
        url = urlparse(urljoin(base + route, href))
        if url.netloc != urlparse(base).netloc:
            continue
        destination = unquote(url.path)
        target = destination.rstrip("/") + "/"
        if target not in pages and not (build / destination.lstrip("/")).is_file():
            errors.append(f"{route}: broken link {href}")
        elif url.fragment and target in pages and unquote(url.fragment) not in pages[target].ids:
            errors.append(f"{route}: broken fragment {href}")

descriptions = [page.meta.get("description") for page in pages.values()]
if len(set(descriptions)) != len(descriptions):
    errors.append("Page descriptions are not unique")
sitemap = [node.text for node in ET.parse(build / "sitemap.xml").getroot().iter("{http://www.sitemaps.org/schemas/sitemap/0.9}loc")]
if set(sitemap) != {base + route for route in pages} or len(sitemap) != len(set(sitemap)):
    errors.append("Sitemap does not match built pages")
if f"Sitemap: {base}/sitemap.xml" not in (build / "robots.txt").read_text():
    errors.append("robots.txt does not point to the sitemap")
if not (build / "og-default.png").read_bytes().startswith(b"\x89PNG\r\n\x1a\n"):
    errors.append("Invalid social image PNG")

print(f"Checked {len(pages)} pages and {sum(len(page.links) for page in pages.values())} links; {len(errors)} issues.")
for error in errors:
    print(error)
raise SystemExit(bool(errors))
