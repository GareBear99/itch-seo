# Promotion — how the itch products get promoted

The tracked record of the promotion work for GareBearProductionz itch products.
Working copies live on the VM at `~/workspace/`; the copies here are the record on
GitHub, so nothing is lost. No secrets, no tokens, no post IDs in any file here.

## Files

- `bluesky-threads-api-routes.md` — the full Bluesky (AT Protocol XRPC) + Threads
  (Meta Threads API) route reference for posting. Research, not code. Working copy:
  `~/workspace/bluesky-threads-api-routes.md`.
- `bluesky-threads-api-daily.md` — the daily log. One dated entry per evening:
  what was posted (Bluesky + Threads), what was promoted, what was acquired
  (new listings, price changes, sales, assets that landed), and what API-routes
  work was done. Appended every evening ~20:42 PST by the `api-routes-daily-log`
  cron, which also updates the two mirrors below. Working copy:
  `~/workspace/bluesky-threads-api-daily.md`.
- `itch-api-promotion-research.md` — the fully-API promotion research (2026-11-05):
  itch.io API, butler, Bluesky, dev.to, Reddit (blocked), Mastodon, Discord, X,
  Threads, Instagram, YouTube, TikTok, Facebook, newsletter, RSS. Status table +
  what each path needs from Gary. Working copy:
  `~/workspace/itch-api-promotion-research.md`.

## Mirrors of the daily log (same content, kept in sync)

1. `~/workspace/bluesky-threads-api-daily.md` — the VM working copy.
2. `~/workspace/TizWildinEntertainmentHUB/docs/api-routes-daily.md` — the HUB mirror.
3. `promotion/bluesky-threads-api-daily.md` (this file) — the itch-seo tracked copy.

The daily cron appends the same entry to all three, then commits + pushes the
HUB and itch-seo copies (only the daily-log file in each repo — never a whole
worktree). The route reference and the research doc change only when the
research changes, not daily.

## What is live today

Only Bluesky is posting (poster on the Mac, account `@tizwildin.bsky.social`).
Threads posts through `threads-cli`. Everything else in the research needs
something from Gary (usually one key or one account) or is closed — see the
status table in `itch-api-promotion-research.md`.
