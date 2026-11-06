#!/usr/bin/env python3
"""Refresh the GareBearProductionz itch inventory into all_items.json.

Stdlib-only so it runs inside GitHub Actions or any Python 3 install with no
dependency setup.

Adapted from the TizWildinEntertainmentHUB autopull
(scripts/update_itch_all_inventory.py). The two scripts diverge by design:
this one scrapes the public itch profile page (no key, no login), enriches
detail data (og:image, published/updated dates) ONLY for new or changed
slugs, and tracks price history in price-history.json.

One run does:
  1. Fetch https://garebearproductionz.itch.io/ (1 request) and parse every
     public listing: title, URL, price label, cover, description, category.
  2. Fetch each NEW or CHANGED item's detail page for its full cover image
     and published/updated dates. A no-change run is ~1 request total.
  3. Diff against the repo's all_items.json and record price changes in
     price-history.json (a price change is recorded, not just overwritten).
  4. Write all_items.json + price-history.json. The site generator
     (scripts/build_site.py) turns the inventory into the static site.
"""
from __future__ import annotations

import argparse
import os
import shutil
import html
import http.client
import json
import re
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Iterable
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin, urlparse
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
PROFILE_URL = "https://garebearproductionz.itch.io/"
ACCOUNT_HOST = "garebearproductionz.itch.io"
MANIFEST_PATH = ROOT / "all_items.json"
PRICE_HISTORY_PATH = ROOT / "price-history.json"
USER_AGENT = "Mozilla/5.0 (compatible; GareBearProductionz-ItchSEO-Bot/1.0; +https://garebear99.github.io/itch-seo/)"

BUNDLE_SLUGS = {"bundle"}

# Ordered most-specific-first. Generic catch-alls like bare "engine" were
# removed from game_tools because they swallowed dice packs, backdrops, and
# playable engines into the wrong bucket.
CATEGORY_RULES = [
    ("audio_music", ["audio", "sfx", "violin", "eq", "theme", "npc", "synth formula", "sound"]),
    ("wraith_lore", ["wraith", "comic", "cathedral", "darkhold", "necropolis", "jukebox", "nekranomicon"]),
    ("icons_sigils", ["icon", "sigil", "covenant", "holy", "spectral", "hell", "evil eye"]),
    ("live_backdrops", ["backdrop", "sphinx", "alien", "mountain", "sky", "crawl space", "sunset", "gate", "live map", "scene"]),
    ("weapons_props", ["hammer", "mjolnir", "scythe", "device", "cart", "paladin", "teleportation", "prop", "dice", "d20", "coin"]),
    ("hero_generators", ["laser", "fireball", "sprite fusion", "sprite mutation", "combat timeline", "moon", "generator engine"]),
    ("sprite_characters", ["sprite", "sprites", "haunter", "demon", "chibi", "pyro", "skully", "elemental", "character", "portrait"]),
    ("games_engines", ["neolution", "grid", "controller", "game", "canvas", "mode-7", "floorcast", "ray trace", "raycast", "ray cast", "playable"]),
    ("game_tools", ["formula", "timeline", "metadata", "action command", "reward pocket", "projectile", "pentagram", "converter", "exporter", "physics", "fx engine", "overlay engine", "toolkit", "engine"]),
]


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")

RELATIVE_UNITS = {"minute": 60, "minutes": 60, "hour": 3600, "hours": 3600,
                  "day": 86400, "days": 86400, "week": 604800, "weeks": 604800,
                  "month": 2592000, "months": 2592000, "year": 31536000, "years": 31536000}


def parse_item_date(raw: str, now: datetime | None = None) -> str | None:
    """Turn an itch date string into an absolute UTC ISO timestamp.

    itch shows relative dates ("24 minutes ago", "5 days ago") that tick
    forward on every fetch — storing them raw makes every run look like a
    change. Converting to an absolute timestamp at fetch time keeps the
    inventory stable between runs. Returns None when unparseable.
    """
    now = now or datetime.now(timezone.utc)
    s = (raw or "").strip()
    if not s:
        return None
    if s.lower() in {"just now", "a moment ago"}:
        return now.replace(microsecond=0).isoformat().replace("+00:00", "Z")
    m = re.match(r"(\d+)\s+(minute|minutes|hour|hours|day|days|week|weeks|month|months|year|years)\s+ago", s, re.I)
    if m:
        seconds = int(m.group(1)) * RELATIVE_UNITS[m.group(2).lower()]
        return (now - timedelta(seconds=seconds)).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    for fmt in ("%d %b %Y @ %H:%M %Z", "%d %b %Y", "%b %d, %Y", "%B %d, %Y", "%Y-%m-%d"):
        try:
            dt = datetime.strptime(s, fmt)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return dt.astimezone(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
        except ValueError:
            continue
    # Already an ISO timestamp.
    try:
        dt = datetime.fromisoformat(s.replace("Z", "+00:00"))
        return dt.astimezone(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    except ValueError:
        return None


def _sameish_date(old: str | None, new: str | None, tolerance_s: int = 3 * 3600) -> bool:
    """True when two stored dates are close enough to be the same event.

    Relative strings are rounded by itch ("24 minutes ago"), so a fresh
    conversion lands a minute or two from the stored one. Within tolerance,
    keep the stored value so the inventory stays byte-stable.
    """
    if not old or not new:
        return False
    try:
        a = datetime.fromisoformat(old.replace("Z", "+00:00"))
        b = datetime.fromisoformat(new.replace("Z", "+00:00"))
        return abs((a - b).total_seconds()) <= tolerance_s
    except ValueError:
        return old == new


def fetch(url: str, timeout: int = 25, tries: int = 3, sleep_s: float = 0.8) -> str:
    # itch resets connections mid-body for urllib from some networks
    # (IncompleteRead after ~64 KB), while curl completes the same request
    # reliably. Prefer curl when it is present (GitHub Actions runners and
    # macOS both ship it); fall back to urllib otherwise.
    if shutil.which("curl"):
        return _fetch_curl(url, timeout=timeout, tries=tries, sleep_s=sleep_s)
    return _fetch_urllib(url, timeout=timeout, tries=tries, sleep_s=sleep_s)


def _fetch_curl(url: str, timeout: int = 25, tries: int = 3, sleep_s: float = 0.8) -> str:
    import subprocess
    import tempfile

    last: Exception | None = None
    for attempt in range(tries):
        body_path = headers_path = None
        try:
            with tempfile.NamedTemporaryFile(delete=False) as tf:
                body_path = tf.name
            with tempfile.NamedTemporaryFile(delete=False) as tf:
                headers_path = tf.name
            proc = subprocess.run(
                ["curl", "-sS", "-L", "--max-time", str(timeout),
                 "-A", USER_AGENT, "-H", "Accept: text/html,application/xhtml+xml",
                 "-o", body_path, "-D", headers_path, "-w", "%{http_code}", url],
                capture_output=True, text=True, timeout=timeout + 10)
            code = (proc.stdout or "").strip()
            body = Path(body_path).read_text(encoding="utf-8", errors="replace") if body_path else ""
            if code == "200" and body:
                return body
            last = RuntimeError(f"HTTP {code or '?'}: {proc.stderr.strip()[:200]}")
            wait = sleep_s
            if code == "429":
                try:
                    headers = Path(headers_path).read_text(encoding="utf-8", errors="replace") if headers_path else ""
                    m = re.search(r"retry-after:\s*(\d+)", headers, re.I)
                    if m:
                        wait = float(m.group(1))
                    else:
                        wait = 30.0
                except OSError:
                    wait = 30.0
            if attempt + 1 < tries:
                time.sleep(wait)
        except (OSError, subprocess.SubprocessError) as exc:
            last = exc
            if attempt + 1 < tries:
                time.sleep(sleep_s)
        finally:
            for f in (body_path, headers_path):
                if f:
                    try:
                        os.unlink(f)
                    except OSError:
                        pass
    raise RuntimeError(f"failed to fetch {url}: {last}")


def _fetch_urllib(url: str, timeout: int = 25, tries: int = 3, sleep_s: float = 0.8) -> str:
    last: Exception | None = None
    for attempt in range(tries):
        try:
            req = Request(url, headers={"User-Agent": USER_AGENT, "Accept": "text/html,application/xhtml+xml"})
            with urlopen(req, timeout=timeout) as resp:
                raw = resp.read()
            return raw.decode("utf-8", errors="replace")
        except HTTPError as exc:
            last = exc
            # itch rate-limits aggressively (429) and sometimes resets the
            # connection mid-body (IncompleteRead). Back off longer on 429
            # (honour Retry-After when the server sends one) and retry.
            if exc.code == 429:
                retry_after = exc.headers.get("Retry-After") if exc.headers else None
                try:
                    wait = float(retry_after) if retry_after else 30.0
                except (TypeError, ValueError):
                    wait = 30.0
            else:
                wait = sleep_s
            if attempt + 1 < tries:
                time.sleep(wait)
        except (URLError, TimeoutError, http.client.HTTPException) as exc:
            last = exc
            if attempt + 1 < tries:
                time.sleep(sleep_s)
    raise RuntimeError(f"failed to fetch {url}: {last}")


def clean_text(s: str) -> str:
    s = re.sub(r"<script[\s\S]*?</script>", " ", s, flags=re.I)
    s = re.sub(r"<style[\s\S]*?</style>", " ", s, flags=re.I)
    s = re.sub(r"<[^>]+>", " ", s)
    s = html.unescape(s)
    return " ".join(s.split())


def slug_from_url(url: str) -> str:
    return urlparse(url).path.strip("/").split("/")[-1]


def abs_media_url(url: str, base: str = PROFILE_URL) -> str:
    url = html.unescape(url or "").strip()
    if not url or url.startswith("data:"):
        return ""
    if url.startswith("//"):
        return "https:" + url
    return urljoin(base, url)


def media_urls_from_html(block: str, base: str) -> list[str]:
    urls: list[str] = []
    attr_re = re.compile(r'''(?:src|href|data-lazy_src|data-lazy-src|data-background_image|poster)\s*=\s*["']([^"']+)["']''', re.I)
    for m in attr_re.finditer(block):
        u = abs_media_url(m.group(1), base)
        if is_media_like(u):
            urls.append(u)
    for m in re.finditer(r'''srcset\s*=\s*["']([^"']+)["']''', block, flags=re.I):
        for part in m.group(1).split(','):
            u = abs_media_url(part.strip().split(' ')[0], base)
            if is_media_like(u):
                urls.append(u)
    for m in re.finditer(r'''url\(([^)]+)\)''', block, flags=re.I):
        u = abs_media_url(m.group(1).strip('"\''), base)
        if is_media_like(u):
            urls.append(u)
    out = []
    seen = set()
    for u in urls:
        if u not in seen:
            out.append(u)
            seen.add(u)
    return out


def is_media_like(url: str) -> bool:
    if not url:
        return False
    lower = url.lower()
    if any(ext in lower for ext in [".png", ".jpg", ".jpeg", ".gif", ".webp", ".avif"]):
        return True
    if "img.itch.zone" in lower or "uploads2.itch.io" in lower:
        return True
    return False


def itch_original(url: str) -> str:
    """Normalize img.itch.zone URLs to the full-resolution 'original' variant."""
    if not url or "img.itch.zone" not in url:
        return url
    return re.sub(r"(img\.itch\.zone/[^/]+/)[^/]+(/)", r"\1original\2", url, count=1)


def pick_media(urls: Iterable[str]) -> dict:
    urls = [itch_original(u) for u in urls if u]
    animated = next((u for u in urls if ".gif" in u.lower()), "")
    cover = next((u for u in urls if u != animated), "") or animated
    media_type = "gif" if animated else ("image" if cover else "fallback")
    return {"cover": cover, "animated": animated, "type": media_type}


def parse_meta_media(page_html: str, base: str) -> list[str]:
    urls = []
    meta_res = [
        re.compile(r'''<meta[^>]+(?:property|name)=["'](?:og:image|twitter:image|twitter:image:src)["'][^>]+content=["']([^"']+)["'][^>]*>''', re.I),
        re.compile(r'''<meta[^>]+content=["']([^"']+)["'][^>]+(?:property|name)=["'](?:og:image|twitter:image|twitter:image:src)["'][^>]*>''', re.I),
    ]
    for meta_re in meta_res:
        for m in meta_re.finditer(page_html):
            u = abs_media_url(m.group(1), base)
            if is_media_like(u):
                urls.append(u)
    urls.extend(media_urls_from_html(page_html, base))
    seen = set()
    out = []
    for u in urls:
        u = itch_original(u)
        if u not in seen:
            out.append(u)
            seen.add(u)
    return out


def split_profile_item_blocks(profile_html: str) -> list[str]:
    # Keep only creator-owned product grid above Supported/Collections so we do not ingest supported products.
    cut_points = [
        profile_html.lower().find("supported by garebearproductionz"),
        profile_html.lower().find("garebearproductionz's collection"),
    ]
    cuts = [x for x in cut_points if x > 0]
    if cuts:
        profile_html = profile_html[:min(cuts)]
    parts = re.split(r'(?=<div[^>]+class=["\'][^"\']*(?:game_cell|game_cell_data|game_grid_cell)[^"\']*["\'])', profile_html, flags=re.I)
    blocks = [p for p in parts if ACCOUNT_HOST in p and "href=" in p]
    if blocks:
        return blocks
    # Fallback: anchor-centered windows.
    out = []
    for m in re.finditer(r'href=["\'](https://garebearproductionz\.itch\.io/[^"\'#?]+)[^"\']*["\']', profile_html, re.I):
        lo = max(0, m.start() - 1200)
        hi = min(len(profile_html), m.end() + 2400)
        out.append(profile_html[lo:hi])
    return out


def parse_price_label(text: str) -> str:
    m = re.search(r"(?:FREE|Free|\$\d+(?:\.\d+)?(?:\s*-\d+%)?)", text)
    return m.group(0) if m else ""


def parse_price(label: str) -> float | None:
    """Numeric price in CAD from a label like '$5.50' or 'Free' (0)."""
    if not label:
        return None
    if re.search(r"\bfree\b", label, flags=re.I):
        return 0.0
    m = re.search(r"\$(\d+(?:\.\d+)?)", label)
    return float(m.group(1)) if m else None


def parse_item_block(block: str, rank: int) -> dict | None:
    links = re.findall(r'''<a[^>]+href=["'](https://garebearproductionz\.itch\.io/[^"'#?]+)[^"']*["'][^>]*>([\s\S]*?)</a>''', block, flags=re.I)
    candidates = []
    for url, inner in links:
        slug = slug_from_url(url)
        if not slug or slug in {"", "community"}:
            continue
        title = clean_text(inner)
        if not title or title.lower() in {"garebearproductionz", "follow", "collection", "add to collection", "image", "gif"}:
            continue
        if title.startswith("$") or len(title) < 3:
            continue
        candidates.append((url, title))
    if not candidates:
        return None
    url, title = candidates[0]
    slug = slug_from_url(url)
    text = clean_text(block)
    desc = text.replace(title, " ").replace("GareBearProductionz", " ")
    desc = re.sub(r"\$\d+(?:\.\d+)?(?:\s*-\d+%)?", " ", desc)
    desc = " ".join(desc.split())
    if len(desc) > 220:
        desc = desc[:219].rsplit(" ", 1)[0] + "…"
    price_label = parse_price_label(text)
    price_type = "free" if re.search(r"\bfree\b|name your own price", text, flags=re.I) or "(FREE" in title.upper() else "paid"
    media = pick_media(media_urls_from_html(block, PROFILE_URL))
    return {
        "id": slug,
        "rank": rank,
        "name": title,
        "url": url,
        "description": desc,
        "priceType": price_type,
        "price": parse_price(price_label),
        "media": {
            **media,
            "alt": title,
            "source": "itch-profile",
            "updatedAt": now_iso(),
        },
        "itch": {"slug": slug, "priceLabel": price_label, "creator": "GareBearProductionz", "lastSeenOnProfile": now_iso()},
    }


def infer_category(name: str, default: str = "game_tools") -> str:
    low = name.lower()
    for cat, terms in CATEGORY_RULES:
        if any(t in low for t in terms):
            return cat
    if "free" in low:
        return "free_samples"
    return default


def merge_item(existing: dict | None, scraped: dict) -> dict:
    merged = dict(existing or {})
    merged.update({
        "id": existing.get("id") if existing else scraped["id"],
        "rank": scraped.get("rank") or (existing or {}).get("rank", 999),
        "name": scraped.get("name") or (existing or {}).get("name", ""),
        "url": scraped.get("url") or (existing or {}).get("url", ""),
        # Only take the scraped price type when the profile actually showed a
        # price: some "Name your own price" items show no label at all on the
        # profile, and the detail page already proved them free.
        "priceType": scraped.get("priceType") if scraped.get("price") is not None else (existing or {}).get("priceType") or scraped.get("priceType", "paid"),
        "price": scraped.get("price") if scraped.get("price") is not None else (existing or {}).get("price"),
        "status": (existing or {}).get("status", "released"),
        "accountOwner": "GareBearProductionz",
        "source": PROFILE_URL,
    })
    if not merged.get("category"):
        merged["category"] = infer_category(merged.get("name", ""))
    slug_now = slug_from_url(merged.get("url", ""))
    if slug_now in BUNDLE_SLUGS:
        merged["kind"] = "bundle"
    elif not merged.get("kind"):
        merged["kind"] = "tool" if merged["category"] in {"game_tools", "hero_generators"} else "asset_pack"
    # Preserve hand-written descriptions unless the scraped one is more useful.
    if not merged.get("description") or len(merged.get("description", "")) < 30:
        merged["description"] = scraped.get("description", "")
    merged.setdefault("tags", [])
    merged.setdefault("featured", False)
    old_media = merged.get("media") or {}
    new_media = scraped.get("media") or {}
    # Keep the existing cover once one is known: the profile thumbnail and
    # the detail og:image are different variants of the same art, and
    # swapping between them every run makes every run look like a change.
    cover = old_media.get("cover") or new_media.get("cover", "")
    animated = old_media.get("animated") or new_media.get("animated", "")
    media_changed = (cover != old_media.get("cover") or animated != old_media.get("animated"))
    merged["media"] = {
        "cover": cover,
        "animated": animated,
        "type": "gif" if animated else ("image" if cover else "fallback"),
        "alt": merged.get("name", "GareBearProductionz itch item cover"),
        "source": old_media.get("source") or new_media.get("source") or "pending-autopull",
        "updatedAt": now_iso() if media_changed or not old_media.get("updatedAt") else old_media["updatedAt"],
    }
    old_itch = dict(merged.get("itch") or {})
    new_itch = dict(scraped.get("itch") or {})
    # The profile price label is display-only and unstable between fetches
    # (sale suffixes like "-50%" come and go, "Free" vs "Name your own
    # price" varies) while the numeric price stays put. Only take a new
    # label when the numeric price moved or the item is new.
    price_moved = (existing or {}).get("price") != scraped.get("price") and scraped.get("price") is not None
    if not price_moved and old_itch.get("priceLabel"):
        new_itch["priceLabel"] = old_itch["priceLabel"]
    itch = dict(old_itch)
    itch.update(new_itch)
    itch.setdefault("slug", slug_from_url(merged.get("url", "")))
    itch.setdefault("creator", "GareBearProductionz")
    merged["itch"] = itch
    return merged


def profile_changed(existing: dict | None, scraped: dict) -> bool:
    """True when a slug is new, its name moved, or its numeric price moved.

    The profile price label and cover variant churn between fetches while
    the price and art stay the same, so they are deliberately NOT triggers
    — a detail fetch per run per item would make every run look changed.
    """
    if not existing:
        return True
    if existing.get("name") != scraped.get("name"):
        return True
    scraped_price = scraped.get("price")
    if scraped_price is not None and existing.get("price") != scraped_price:
        return True
    if not (existing.get("itch") or {}).get("detailEnrichedAt"):
        return True
    return False


def enrich_from_detail_page(item: dict) -> tuple[dict, str]:
    url = item.get("url", "")
    if not url:
        return item, "no-url"
    try:
        body = fetch(url, tries=1)
    except Exception as exc:
        return item, f"detail-fetch-failed:{exc}"
    media_urls = parse_meta_media(body, url)
    picked = pick_media(media_urls)
    media = item.setdefault("media", {})
    if picked.get("animated"):
        media["animated"] = picked["animated"]
    if picked.get("cover"):
        media["cover"] = picked["cover"]
    media["type"] = "gif" if media.get("animated") else ("image" if media.get("cover") else "fallback")
    media["source"] = "itch-detail"
    media["alt"] = item.get("name", "GareBearProductionz itch item cover")
    media["updatedAt"] = now_iso()
    text = clean_text(body)
    itch = item.setdefault("itch", {})
    now = datetime.now(timezone.utc)
    for label in ["Published", "Updated"]:
        m = re.search(label + r"\s+(.{0,60}?)(?:\s+(?:Updated|Published|Status|Category|Author|Tags|Purchase|Game assets)|$)", text, re.I)
        if m:
            raw = " ".join(m.group(1).split())[:60]
            ts = parse_item_date(raw, now)
            if ts:
                key = label.lower()
                if not _sameish_date(itch.get(key), ts):
                    itch[key] = ts
            elif raw:
                itch[label.lower()] = raw
    # Price: the profile grid shows no label at all for some "Name your own
    # price" items, so resolve the price from the detail page itself. The
    # page embeds "min_price"/"actual_price" in cents.
    nyop = "name your own price" in text.lower()
    actual = re.search(r'"actual_price"\s*:\s*(\d+)', body)
    minimum = re.search(r'"min_price"\s*:\s*(\d+)', body)
    if actual is not None:
        cents = int(actual.group(1))
        price = cents / 100.0
        item["price"] = price
        if price > 0:
            item["priceType"] = "paid"
            itch["priceLabel"] = f"${price:.2f}"
        elif nyop:
            item["priceType"] = "free"
            itch["priceLabel"] = "Name your own price"
        else:
            item["priceType"] = "free"
            itch["priceLabel"] = "Free"
    elif nyop:
        item["priceType"] = "free"
        if item.get("price") is None:
            item["price"] = 0.0
        itch["priceLabel"] = itch.get("priceLabel") or "Name your own price"
    elif minimum is not None and int(minimum.group(1)) == 0 and item.get("price") is None:
        item["price"] = 0.0
        item["priceType"] = "free"
    itch["detailEnrichedAt"] = now_iso()
    return item, "ok"


def load_json(path: Path, default):
    if path.exists():
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return default
    return default


def update_price_history(history: dict, items: list[dict]) -> dict:
    """Record a price change instead of just overwriting the last price."""
    now = now_iso()
    for item in items:
        slug = slug_from_url(item.get("url", ""))
        price = item.get("price")
        label = (item.get("itch") or {}).get("priceLabel", "")
        entry = history.setdefault(slug, {"name": item.get("name", slug), "history": []})
        entry["name"] = item.get("name", slug)
        hist = entry["history"]
        if not hist:
            hist.append({"price": price, "priceLabel": label, "firstSeen": now, "lastSeen": now})
        elif hist[-1].get("price") != price:
            hist.append({"price": price, "priceLabel": label, "firstSeen": now, "lastSeen": now})
        else:
            hist[-1]["lastSeen"] = now
            if label and hist[-1].get("priceLabel") != label:
                hist[-1]["priceLabel"] = label
    # Drop slugs that no longer exist on the profile.
    live = {slug_from_url(i.get("url", "")) for i in items}
    for slug in list(history):
        if slug not in live:
            del history[slug]
    return history


def diff_items(old_items: list[dict], new_items: list[dict]) -> dict:
    old = {slug_from_url(i.get("url", "")): i for i in old_items}
    new = {slug_from_url(i.get("url", "")): i for i in new_items}
    added = [new[s] for s in new if s not in old]
    removed = [old[s] for s in old if s not in new]
    price_changed = []
    changed = []
    for slug in new:
        if slug not in old:
            continue
        o, n = old[slug], new[slug]
        if o.get("price") != n.get("price"):
            price_changed.append({"slug": slug, "name": n.get("name", slug),
                                  "from": o.get("price"), "to": n.get("price")})
        elif o.get("name") != n.get("name") or o.get("description") != n.get("description"):
            changed.append({"slug": slug, "name": n.get("name", slug)})
    return {"added": added, "removed": removed, "priceChanged": price_changed, "changed": changed}


VOLATILE_KEYS = {"generatedAt"}


def _stripped(item: dict) -> dict:
    """A copy of an item with run-volatile fields removed for comparison."""
    import copy
    c = copy.deepcopy(item)
    (c.get("media") or {}).pop("updatedAt", None)
    itch = c.get("itch") or {}
    for k in ("lastSeenOnProfile", "detailEnrichedAt"):
        itch.pop(k, None)
    return c


def meaningful_change(old_manifest: dict, new_items: list[dict]) -> bool:
    """True when the inventory really moved (items added/removed, or a
    name/description/price/category/media change). Timestamps, last-seen
    stamps, and the unstable profile price label do not count."""
    old_items = old_manifest.get("items", [])
    if len(old_items) != len(new_items):
        return True
    old_by_slug = {slug_from_url(i.get("url", "")): _stripped(i) for i in old_items}
    new_by_slug = {slug_from_url(i.get("url", "")): _stripped(i) for i in new_items}
    if set(old_by_slug) != set(new_by_slug):
        return True
    for slug, new_item in new_by_slug.items():
        old_item = old_by_slug[slug]
        # Price label is display-only churn; the numeric price is the truth.
        old_item.get("itch", {}).pop("priceLabel", None)
        new_item.get("itch", {}).pop("priceLabel", None)
        if old_item != new_item:
            return True
    return False


def update_manifest(enrich_details: bool = True, limit: int | None = None) -> tuple[dict, dict, dict]:
    old_manifest = load_json(MANIFEST_PATH, {"items": []})
    old_items = old_manifest.get("items", [])
    existing_by_slug = {slug_from_url(i.get("url", "")): i for i in old_items}

    profile_html = fetch(PROFILE_URL)
    blocks = split_profile_item_blocks(profile_html)
    scraped = []
    seen = set()
    rank = 1
    for block in blocks:
        item = parse_item_block(block, rank)
        if not item:
            continue
        slug = item["id"]
        if slug in seen:
            continue
        seen.add(slug)
        scraped.append(item)
        rank += 1
        if limit and len(scraped) >= limit:
            break

    merged = []
    detail_status = []
    for scraped_item in scraped:
        slug = slug_from_url(scraped_item.get("url", ""))
        existing = existing_by_slug.get(slug)
        item = merge_item(existing, scraped_item)
        # Incremental detail enrichment: only new/changed slugs hit their
        # detail page. A no-change run is ~1 request total.
        if enrich_details and profile_changed(existing, scraped_item):
            item, status = enrich_from_detail_page(item)
            detail_status.append({"slug": slug, "status": status})
            time.sleep(0.15)
        merged.append(item)

    merged.sort(key=lambda x: x.get("rank", 999))
    diff = diff_items(old_items, merged)
    old_history = load_json(PRICE_HISTORY_PATH, {})
    if not meaningful_change(old_manifest, merged):
        # Nothing real moved (timestamps and label churn excluded): keep the
        # committed files byte-identical so the scheduled job commits nothing.
        report = {
            "generatedAt": now_iso(),
            "profileUrl": PROFILE_URL,
            "itemsParsed": len(scraped),
            "itemsWritten": len(merged),
            "mediaReadyItems": sum(1 for i in merged if (i.get("media") or {}).get("cover") or (i.get("media") or {}).get("animated")),
            "detailEnriched": len(detail_status),
            "detailStatus": detail_status[:200],
            "diff": {
                "added": [], "removed": [], "priceChanged": [], "changed": [],
            },
            "changed": False,
        }
        return old_manifest, old_history, report
    history = update_price_history(old_history, merged)

    manifest = {
        "generatedAt": now_iso(),
        "source": PROFILE_URL,
        "accountOwner": "GareBearProductionz",
        "items": merged,
        "summary": {
            "totalItems": len(merged),
            "paidItems": sum(1 for i in merged if i.get("priceType") == "paid"),
            "freeItems": sum(1 for i in merged if i.get("priceType") == "free"),
            "mediaReadyItems": sum(1 for i in merged if (i.get("media") or {}).get("cover") or (i.get("media") or {}).get("animated")),
        },
        "metadata": {
            "generatedAt": now_iso(),
            "autopullLastRun": now_iso(),
            "autopullSource": PROFILE_URL,
            "autopullItemCount": len(merged),
            "autopullDetailEnriched": len(detail_status),
        },
    }
    report = {
        "generatedAt": now_iso(),
        "profileUrl": PROFILE_URL,
        "itemsParsed": len(scraped),
        "itemsWritten": len(merged),
        "mediaReadyItems": manifest["summary"]["mediaReadyItems"],
        "detailEnriched": len(detail_status),
        "detailStatus": detail_status[:200],
        "diff": {
            "added": [i.get("name", i.get("id")) for i in diff["added"]],
            "removed": [i.get("name", i.get("id")) for i in diff["removed"]],
            "priceChanged": diff["priceChanged"],
            "changed": [i.get("name") for i in diff["changed"]],
        },
        "changed": True,
    }
    return manifest, history, report


def main() -> int:
    ap = argparse.ArgumentParser(description="Refresh all_items.json from the public GareBearProductionz itch inventory.")
    ap.add_argument("--no-detail", action="store_true", help="Do not fetch detail pages for new/changed items.")
    ap.add_argument("--limit", type=int, default=None, help="Debug limit for number of profile items to process.")
    args = ap.parse_args()
    manifest, history, report = update_manifest(enrich_details=not args.no_detail, limit=args.limit)
    d = report["diff"]
    if not report.get("changed", True):
        print(f"no meaningful changes: {MANIFEST_PATH} left untouched "
              f"({report['itemsWritten']} items, {report['detailEnriched']} detail pages fetched)")
        return 0
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    PRICE_HISTORY_PATH.write_text(json.dumps(history, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"wrote {MANIFEST_PATH} with {report['itemsWritten']} items "
          f"({report['detailEnriched']} detail pages fetched); media ready {report['mediaReadyItems']}; "
          f"added {len(d['added'])}, removed {len(d['removed'])}, "
          f"price changes {len(d['priceChanged'])}, changed {len(d['changed'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
