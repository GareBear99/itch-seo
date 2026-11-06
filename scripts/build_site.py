#!/usr/bin/env python3
"""Build the static SEO site for the GareBearProductionz itch index.

Reads all_items.json and writes the GitHub Pages site under docs/:
  - docs/index.html            home: full list grouped by category
  - docs/items/<slug>.html     one page per itch item (JSON-LD Product,
                               canonical = the itch listing, dark theme)
  - docs/categories/<slug>.html one index page per category
  - docs/sitemap.xml, docs/robots.txt, docs/llms.txt
  - docs/all_items.json        copy of the inventory, served at the site's own URL
  - docs/feed.xml              RSS feed of the inventory (newest first)

Validation runs at the end of every build and fails the run (non-zero exit)
when anything is off: every page has a title, a canonical URL, and valid
JSON-LD where required; the sitemap lists exactly the pages that exist; no
broken internal links. A failed build must never be committed.

Stdlib-only. Run from the repo root: python scripts/build_site.py
"""
from __future__ import annotations

import html
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = ROOT / "all_items.json"
DOCS = ROOT / "docs"
SITE_URL = "https://garebear99.github.io/itch-seo"
PROFILE_URL = "https://garebearproductionz.itch.io/"

BG = "#050308"
TEXT = "#ffffff"
ACCENT = "#D7A0FF"

CATEGORY_NAMES = {
    "audio_music": "Audio & Music",
    "wraith_lore": "Wraith Lore",
    "icons_sigils": "Icons & Sigils",
    "live_backdrops": "Live Backdrops",
    "weapons_props": "Weapons & Props",
    "hero_generators": "Hero Generators",
    "sprite_characters": "Sprites & Characters",
    "games_engines": "Games & Engines",
    "game_tools": "Game Tools",
    "free_samples": "Free Samples",
}


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def esc(s) -> str:
    return html.escape(str(s or ""), quote=True)


def slug_of(item: dict) -> str:
    return item.get("id") or item.get("url", "").rstrip("/").split("/")[-1]


def price_text(item: dict) -> str:
    price = item.get("price")
    if item.get("priceType") == "free" or price == 0:
        return "Free"
    if price is None:
        return (item.get("itch") or {}).get("priceLabel") or "See itch.io"
    return f"${price:.2f} CAD"


def category_name(cat: str) -> str:
    return CATEGORY_NAMES.get(cat, cat.replace("_", " ").title())


def meta_description(item: dict) -> str:
    desc = (item.get("description") or "").strip()
    if len(desc) > 155:
        desc = desc[:154].rsplit(" ", 1)[0] + "…"
    return desc or item.get("name", "GareBearProductionz itch item")


def json_ld(item: dict) -> dict:
    price = item.get("price")
    if item.get("priceType") == "free" or price == 0:
        price = 0
    ld = {
        "@context": "https://schema.org",
        "@type": "Product",
        "name": item.get("name", ""),
        "description": meta_description(item),
        "url": item.get("url", ""),
        "category": category_name(item.get("category", "")),
        "brand": {"@type": "Brand", "name": "GareBearProductionz"},
        "seller": {"@type": "Organization", "name": "GareBearProductionz",
                   "url": PROFILE_URL},
        "offers": {
            "@type": "Offer",
            "url": item.get("url", ""),
            "priceCurrency": "CAD",
            "price": price if price is not None else 0,
            "availability": "https://schema.org/InStock",
            "seller": {"@type": "Organization", "name": "GareBearProductionz"},
        },
    }
    cover = (item.get("media") or {}).get("cover") or (item.get("media") or {}).get("animated")
    if cover:
        ld["image"] = cover
    return ld


def page_shell(title: str, description: str, canonical: str, body: str,
               og_image: str = "", extra_head: str = "") -> str:
    og = f'\n  <meta property="og:image" content="{esc(og_image)}">' if og_image else ""
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)}</title>
<meta name="description" content="{esc(description)}">
<link rel="canonical" href="{esc(canonical)}">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(description)}">
<meta property="og:url" content="{esc(canonical)}">{og}
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{esc(title)}">
<meta name="twitter:description" content="{esc(description)}">{extra_head}
<style>
body{{background:{BG};color:{TEXT};font-family:system-ui,-apple-system,Segoe UI,Roboto,sans-serif;margin:0;padding:0 1.2rem 3rem;line-height:1.55}}
a{{color:{ACCENT}}}
header,main,footer{{max-width:900px;margin:0 auto}}
header{{padding:1.5rem 0 .5rem;border-bottom:1px solid #2a2133}}
h1{{font-size:1.7rem;margin:.4rem 0}}
h2{{margin-top:2rem}}
.btn{{display:inline-block;background:{ACCENT};color:#14001f;font-weight:700;padding:.6rem 1.1rem;border-radius:8px;text-decoration:none;margin:.8rem 0}}
.btn:hover{{opacity:.9}}
img.cover{{max-width:100%;height:auto;border-radius:10px;margin:1rem 0}}
.grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(240px,1fr));gap:1rem}}
.card{{border:1px solid #2a2133;border-radius:10px;padding:.9rem}}
.card img{{width:100%;height:auto;border-radius:6px}}
.card h3{{margin:.5rem 0 .2rem;font-size:1.05rem}}
.price{{font-weight:700}}
.muted{{color:#b9a8cc}}
nav{{margin:.6rem 0}}
</style>
</head>
<body>
<header>
<nav><a href="{SITE_URL}/">GareBearProductionz itch index</a> · <a href="{SITE_URL}/feed.xml">RSS feed</a></nav>
</header>
<main>
{body}
</main>
<footer>
<p class="muted">All items are sold on <a href="{PROFILE_URL}">itch.io</a> — this index is a signpost, not a store. Prices in Canadian dollars (CAD).</p>
</footer>
</body>
</html>
"""


def item_card(item: dict) -> str:
    slug = slug_of(item)
    media = item.get("media") or {}
    img = media.get("cover") or media.get("animated") or ""
    img_tag = f'<img src="{esc(img)}" alt="{esc(item.get("name", ""))}" loading="lazy">' if img else ""
    return (f'<div class="card">{img_tag}<h3><a href="{SITE_URL}/items/{quote(slug)}.html">'
            f'{esc(item.get("name", ""))}</a></h3>'
            f'<p class="price">{esc(price_text(item))}</p>'
            f'<p class="muted">{esc(meta_description(item))}</p>'
            f'<p><a href="{esc(item.get("url", ""))}">Buy / Download on itch.io →</a></p></div>')


def build_item_page(item: dict) -> str:
    slug = slug_of(item)
    media = item.get("media") or {}
    cover = media.get("cover") or media.get("animated") or ""
    ld = json.dumps(json_ld(item), ensure_ascii=False, indent=2)
    title = f"{item.get('name', '')} — GareBearProductionz on itch.io"
    desc = meta_description(item)
    img_tag = f'<img class="cover" src="{esc(cover)}" alt="{esc(item.get("name", ""))}">' if cover else ""
    tags = ", ".join(item.get("tags") or [])
    tags_line = f"<p><strong>Tags:</strong> {esc(tags)}</p>" if tags else ""
    published = (item.get("itch") or {}).get("published", "")
    updated = (item.get("itch") or {}).get("updated", "")
    dates = ""
    if published:
        dates += f"<p><strong>Published:</strong> {esc(published)}</p>"
    if updated:
        dates += f"<p><strong>Updated:</strong> {esc(updated)}</p>"
    body = f"""<h1>{esc(item.get("name", ""))}</h1>
<p><a href="{SITE_URL}/categories/{quote(item.get('category', 'game_tools'))}.html">{esc(category_name(item.get('category', '')))}</a> · <span class="price">{esc(price_text(item))}</span></p>
{img_tag}
<p>{esc(item.get("description", ""))}</p>
{tags_line}{dates}
<p><a class="btn" href="{esc(item.get('url', ''))}">Buy / Download on itch.io</a></p>
<p class="muted">Listed on itch.io as <a href="{esc(item.get('url', ''))}">{esc(item.get('url', ''))}</a></p>"""
    extra = f'\n<script type="application/ld+json">{ld}</script>'
    if cover:
        extra += f'\n<meta name="twitter:image" content="{esc(cover)}">'
    return page_shell(title, desc, item.get("url", ""), body,
                      og_image=cover, extra_head=extra)


def build_category_page(cat: str, items: list[dict]) -> str:
    name = category_name(cat)
    title = f"{name} — GareBearProductionz itch index"
    cards = "\n".join(item_card(i) for i in items)
    body = f"""<h1>{esc(name)}</h1>
<p class="muted">{len(items)} item(s)</p>
<div class="grid">
{cards}
</div>"""
    return page_shell(title, f"{name} — {len(items)} items by GareBearProductionz on itch.io.",
                      f"{SITE_URL}/categories/{quote(cat)}.html", body)


def build_home(items: list[dict]) -> str:
    by_cat: dict[str, list[dict]] = {}
    for item in items:
        by_cat.setdefault(item.get("category", "game_tools"), []).append(item)
    sections = []
    for cat in sorted(by_cat, key=lambda c: category_name(c)):
        cat_items = by_cat[cat]
        cards = "\n".join(item_card(i) for i in cat_items)
        sections.append(f'<h2><a href="{SITE_URL}/categories/{quote(cat)}.html">{esc(category_name(cat))}</a> ({len(cat_items)})</h2>\n<div class="grid">\n{cards}\n</div>')
    body = f"""<h1>GareBearProductionz on itch.io</h1>
<p>{len(items)} items — game assets, audio packs, tools, and games. Every page here points at the itch.io listing where the item is sold.</p>
<p><a class="btn" href="{PROFILE_URL}">Browse the itch.io profile</a></p>
""" + "\n".join(sections)
    return page_shell("GareBearProductionz itch index — every item, one page each",
                      f"Every GareBearProductionz itch.io listing in one index — {len(items)} items: game assets, audio packs, tools, and games.",
                      f"{SITE_URL}/", body)


def build_sitemap(pages: list[str]) -> str:
    today = datetime.now(timezone.utc).date().isoformat()
    lines = ['<?xml version="1.0" encoding="UTF-8"?>',
             '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for page in pages:
        loc = f"{SITE_URL}/{page}" if page else f"{SITE_URL}/"
        lines.append(f'  <url><loc>{esc(loc)}</loc><lastmod>{today}</lastmod>'
                     f'<changefreq>weekly</changefreq><priority>{"1.0" if not page else "0.8"}</priority></url>')
    lines.append("</urlset>")
    return "\n".join(lines) + "\n"


def build_robots() -> str:
    return f"User-agent: *\nAllow: /\nSitemap: {SITE_URL}/sitemap.xml\n"


def build_llms(items: list[dict]) -> str:
    lines = ["# GareBearProductionz itch index", "",
             f"Index of every public GareBearProductionz listing on itch.io ({len(items)} items).",
             f"Home: {SITE_URL}/", f"Profile: {PROFILE_URL}", "",
             "## Items", ""]
    for item in sorted(items, key=lambda i: (i.get("name") or "").lower()):
        lines.append(f"- {item.get('name', '')}: {meta_description(item)}")
        lines.append(f"  Page: {SITE_URL}/items/{quote(slug_of(item))}.html")
        lines.append(f"  itch.io: {item.get('url', '')}")
        lines.append(f"  Price: {price_text(item)}")
        lines.append("")
    return "\n".join(lines)


def build_feed(items: list[dict], generated_at: str) -> str:
    def rss_date(iso: str) -> str:
        try:
            dt = datetime.fromisoformat(iso.replace("Z", "+00:00"))
        except ValueError:
            dt = datetime.now(timezone.utc)
        return dt.strftime("%a, %d %b %Y %H:%M:%S +0000")

    feed_items = sorted(items, key=lambda i: i.get("rank", 999))[:50]
    entries = []
    for item in feed_items:
        entries.append(
            "  <item>\n"
            f"    <title>{esc(item.get('name', ''))}</title>\n"
            f"    <link>{esc(item.get('url', ''))}</link>\n"
            f"    <guid isPermaLink=\"true\">{esc(item.get('url', ''))}</guid>\n"
            f"    <description>{esc(meta_description(item))} — {esc(price_text(item))}</description>\n"
            f"    <pubDate>{rss_date(generated_at)}</pubDate>\n"
            "  </item>")
    return ("<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n"
            "<rss version=\"2.0\">\n<channel>\n"
            "  <title>GareBearProductionz itch index</title>\n"
            f"  <link>{SITE_URL}/</link>\n"
            "  <description>New and updated listings from GareBearProductionz on itch.io.</description>\n"
            f"  <lastBuildDate>{rss_date(generated_at)}</lastBuildDate>\n"
            + "\n".join(entries) + "\n</channel>\n</rss>\n")


def build_site() -> dict:
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    items = manifest.get("items", [])
    generated_at = manifest.get("generatedAt") or now_iso()

    (DOCS / "items").mkdir(parents=True, exist_ok=True)
    (DOCS / "categories").mkdir(parents=True, exist_ok=True)

    pages: list[str] = ["", "feed.xml", "all_items.json", "llms.txt"]
    for item in items:
        slug = slug_of(item)
        (DOCS / "items" / f"{slug}.html").write_text(build_item_page(item), encoding="utf-8")
        pages.append(f"items/{slug}.html")
    cats: dict[str, list[dict]] = {}
    for item in items:
        cats.setdefault(item.get("category", "game_tools"), []).append(item)
    for cat, cat_items in cats.items():
        (DOCS / "categories" / f"{cat}.html").write_text(
            build_category_page(cat, cat_items), encoding="utf-8")
        pages.append(f"categories/{cat}.html")

    (DOCS / "index.html").write_text(build_home(items), encoding="utf-8")
    (DOCS / "sitemap.xml").write_text(build_sitemap(pages), encoding="utf-8")
    (DOCS / "robots.txt").write_text(build_robots(), encoding="utf-8")
    (DOCS / "llms.txt").write_text(build_llms(items), encoding="utf-8")
    (DOCS / "feed.xml").write_text(build_feed(items, generated_at), encoding="utf-8")
    (DOCS / "all_items.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return {"items": len(items), "categories": len(cats), "pages": pages}


def validate() -> list[str]:
    """Validate the generated site. Returns a list of problems (empty = pass)."""
    problems: list[str] = []
    html_files = sorted(DOCS.rglob("*.html"))
    if not html_files:
        return ["no HTML pages generated"]
    for path in html_files:
        text = path.read_text(encoding="utf-8")
        rel = str(path.relative_to(DOCS))
        if "<title>" not in text or "</title>" not in text:
            problems.append(f"{rel}: missing <title>")
        if 'rel="canonical"' not in text:
            problems.append(f"{rel}: missing canonical link")
        # JSON-LD must parse on item pages.
        if "/items/" in rel.replace("\\", "/"):
            m = re.search(r'<script type="application/ld\+json">(.*?)</script>', text, re.S)
            if not m:
                problems.append(f"{rel}: missing JSON-LD")
            else:
                try:
                    ld = json.loads(m.group(1))
                    offers = ld.get("offers", {})
                    if ld.get("@type") != "Product":
                        problems.append(f"{rel}: JSON-LD @type is not Product")
                    if offers.get("priceCurrency") != "CAD":
                        problems.append(f"{rel}: JSON-LD priceCurrency is not CAD")
                    if "price" not in offers:
                        problems.append(f"{rel}: JSON-LD offers missing price")
                except json.JSONDecodeError as exc:
                    problems.append(f"{rel}: JSON-LD does not parse: {exc}")
        # Internal links must resolve to a file that exists.
        for href in re.findall(r'href="([^"]+)"', text):
            if href.startswith(SITE_URL + "/"):
                target = href[len(SITE_URL) + 1:].split("#")[0].split("?")[0]
                if not target:
                    continue
                if not (DOCS / target).exists():
                    problems.append(f"{rel}: broken internal link {href}")
    # Sitemap must list exactly the pages that exist (HTML + feed + JSON + llms).
    sitemap_path = DOCS / "sitemap.xml"
    if not sitemap_path.exists():
        problems.append("sitemap.xml missing")
    else:
        sitemap_text = sitemap_path.read_text(encoding="utf-8")
        listed = {u[len(SITE_URL) + 1:] if u.startswith(SITE_URL + "/") else ("" if u.rstrip("/") == SITE_URL else u)
                  for u in re.findall(r"<loc>([^<]+)</loc>", sitemap_text)}
        expected = set()
        for path in DOCS.rglob("*"):
            if path.is_file() and path.suffix in {".html", ".xml", ".json", ".txt"} and path.name != "sitemap.xml" and path.name != "robots.txt":
                rel = str(path.relative_to(DOCS)).replace("\\", "/")
                # Home is listed in the sitemap as the bare site URL, not index.html.
                expected.add("" if rel == "index.html" else rel)
        if listed != expected:
            problems.append(f"sitemap mismatch: listed-only {sorted(listed - expected)[:5]}, "
                            f"missing-from-sitemap {sorted(expected - listed)[:5]}")
    return problems


def main() -> int:
    result = build_site()
    problems = validate()
    print(f"built {result['items']} item pages, {result['categories']} category pages, "
          f"{len(result['pages'])} sitemap URLs")
    if problems:
        print("VALIDATION FAILED:", file=sys.stderr)
        for p in problems:
            print(f"  - {p}", file=sys.stderr)
        return 1
    print("validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
