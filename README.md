# itch-seo

SEO index for every public [GareBearProductionz](https://garebearproductionz.itch.io/) listing on itch.io — one crawlable page per item, refreshed four times a day.

The live site is at **https://garebear99.github.io/itch-seo/**. Every item page is a signpost: its canonical URL points at the itch.io listing, where the purchase happens. This repo is not a store — no checkout, no keys, no accounts.

## What is in here

- `all_items.json` — the machine-readable inventory, scraped from the public itch profile page. Source of truth for the site build.
- `price-history.json` — price history per item (a price change is recorded, not just overwritten).
- `scripts/update_itch_inventory.py` — the autopull. Scrapes the public profile page (no key, no login), then fetches detail pages only for new or changed items, so a no-change run is about one request. Adapted from the TizWildinEntertainmentHUB autopull.
- `scripts/build_site.py` — the static site generator: one page per item (JSON-LD `Product`, `priceCurrency: "CAD"`), category index pages, home page, `sitemap.xml`, `robots.txt`, `llms.txt`, `all_items.json` copy, and an RSS feed (`feed.xml`). It validates the build — title, canonical, valid JSON-LD, sitemap coverage, no broken internal links — and fails the run instead of committing a broken site.
- `docs/` — the GitHub Pages site.

## How the daily job works

`.github/workflows/refresh.yml` runs every 6 hours (`17 3,9,15,21 * * *`) and on manual trigger (`workflow_dispatch`):

1. `update_itch_inventory.py` pulls the profile and updates `all_items.json` + `price-history.json`.
2. `build_site.py` regenerates `docs/` and validates it.
3. The auto-commit step commits **only if files changed** — a no-change run commits nothing.

To force a refresh right after publishing a pack: Actions → Refresh Itch SEO Site → Run workflow.

## Running it locally

```bash
python3 scripts/update_itch_inventory.py   # pull live inventory
python3 scripts/build_site.py              # rebuild docs/ + validate
```

Both scripts are stdlib-only — no dependencies to install.
