# itch.io promotion — fully-API paths (research)

**Date:** 2026-11-05 (~18:10–18:35 PST)
**Ordered by:** Gary, 2026-11-05 ~18:08 PST — "fatty research on fully api paths for promotion of itch assets that you can accomplish while im away you have my permision for just keep track so when i get back i can know whats up"
**Scope:** research + mapping + preparation ONLY. No live posting, no accounts created, no money spent, no credentials stored. Every path below was checked against its own docs or a current (2026) guide; where a claim rests on a secondary source it says so.
**Assets to promote:** FreeEQ8, ProEQ8, sample packs (808, Violin, Crown, Phonk, Riser, Drum, Future Bass, Dark Piano, VocalSamples, etc.), Rift Ascent, A Devil's Game, VFX packs, Shadow Run maps. Publisher: **GareBearProductionz**, account currency **CAD**. itch rules that carry over to every path: short description ≤120 chars, dark theme (BG #050308, text #ffffff, link #D7A0FF), **AI disclosure always "No AI"** on itch.

## 0. Bottom line

Only **one** path is live today: **Bluesky** (poster built, account @tizwildin.bsky.social, posting on a queue + crons). Everything else needs something from Gary — usually one key or one account — or is closed. The two pieces of news that change the plan:

1. **Reddit is effectively closed for a new app.** Reddit stopped taking new public API requests on **Oct 31, 2026**, and the public API closes **March 2027**. The Reddit poster is built and ready, but there is almost certainly no app to run it with. (§4)
2. **X/Twitter now charges per post.** No free tier for new developers since Feb 2026 (pay-per-use): **$0.20 per post with a link** — and every promo post carries a link. (§7)

## Status table

| # | Path | Status | What it needs from Gary | Cost |
|---|---|---|---|---|
| 1 | itch.io API (api.itch.io) | **NEEDS CREDENTIAL** | API key (User Settings → API Keys) | Free |
| 2 | butler (itch uploads) | **NEEDS CREDENTIAL** | `butler login` once, or BUTLER_API_KEY | Free |
| 3 | Bluesky (AT Protocol) | **READY** — live today | Nothing | Free |
| 4 | dev.to API (Forem) | **NEEDS CREDENTIAL** | API key (Settings → Extensions) | Free |
| 5 | Reddit (PRAW / Data API) | **BLOCKED** | An already-approved app (none known) — new apps closed Oct 31, 2026 | Free tier, non-commercial only |
| 6 | Mastodon | **NEEDS GARY** | Pick instance + create account + token | Free |
| 7 | Discord webhooks | **NEEDS GARY** | A server he owns + webhook URL | Free |
| 8 | X / Twitter API | **NEEDS GARY + PAID** | Account + developer app + payment method | $0.20/link-post |
| 9 | Threads API (Meta) | **NEEDS GARY** | Confirm account + Meta app + token | Free |
| 10 | Instagram Graph API | **NEEDS GARY** | Pro account + Meta app + App Review | Free |
| 11 | YouTube Data API | **NEEDS GARY + AUDIT** | Channel + Cloud project; uploads stay private until audit | Free |
| 12 | TikTok Content Posting API | **NEEDS GARY + HEAVY GATES** | Account + app + review + audit; private-only until audited | Free |
| 13 | Facebook Pages (Graph API) | **NEEDS GARY** | A Page + Meta app | Free |
| 14 | Newsletter (Buttondown) | **NEEDS GARY** | An account (no mailing list exists yet) | Free tier |
| 15 | RSS/Atom from itch-seo repo | **READY TO BUILD** | Nothing (builds with the SEO repo, Phase 2) | Free |

Status meanings: **READY** = works now, nothing needed from Gary. **NEEDS CREDENTIAL** = the account exists; one key/token Gary must generate. **NEEDS GARY** = an account or setup step only he can do. **BLOCKED** = the path is closed or unusable, with the reason given. **PAID** = it costs money per use.

---

## 1. itch.io's own API — the foundation, not a promo channel

**Docs:** https://itch.io/docs/api/serverside (new API at `api.itch.io`; legacy at `itch.io/api/1/KEY/...`).

**Auth:** API key generated at User Settings → API Keys, sent as an `Authorization: Bearer <key>` header. User-generated keys are **unscoped** — they can call every endpoint. OAuth 2.0 also exists (authorization-code + implicit flows; scopes `profile:me`, `profile:games`, `game:view:*`, `collection:edit`). **All endpoints require authentication — there is no public unauthenticated API, and there is no RSS feed for a creator's items** (already established in the SEO repo design, re-confirmed here).

**Endpoints (new API):**

| Endpoint | What it returns |
|---|---|
| `GET https://api.itch.io/profile` | Public profile data for the key owner |
| `GET https://api.itch.io/profile/games` | All games you uploaded or can edit (`my-games`) |
| `GET https://api.itch.io/profile/owned-keys` | Games purchased/claimed |
| `GET https://api.itch.io/games/GAME_ID/purchases` | Purchase records for a game |
| `GET https://api.itch.io/games/GAME_ID/download_keys` | Download-key check |
| `GET https://api.itch.io/games/GAME_ID/uploads` | Upload/file metadata for a game |
| `GET https://api.itch.io/games/GAME_ID/ownership` | Ownership check |
| `GET https://api.itch.io/profile/collections` + `/collections/COLLECTION_ID/collection-games` | Collections and their games |
| `POST` under `/collections` (`collection:edit` scope) | Create, edit, reorder, delete collections and the games in them |

**What it CAN do:** structured inventory of every listing (title, URL, price, cover, description) — replaces the HTML scraping the HUB and SEO repo currently do, and sees drafts/unlisted items the public page doesn't show (filter to public-only). Purchase/download counts per game. Curated public collections (a mild promo lever: a "best of" collection is a public page).

**What it CANNOT do:** there is **no endpoint to create or edit a game page, change a price, set tags/descriptions, upload a file, feature anything, or reach buyers**. There is no discovery or promotion endpoint at all. Uploads go through butler (§2); page creation is browser-only (`itch.io/game/new`).

**Value for promotion:** it is the source of truth for the inventory (the SEO repo's autopull), and it keeps the promo copy honest (prices, titles, URLs straight from itch, never hand-copied). **Status: NEEDS CREDENTIAL** — Gary generates the key; optional, because scraping already works without it. Recommend adding it later if scraping proves brittle.

## 2. butler — automated uploads, the closest thing to an API publish loop on itch

**Docs:** https://itch.io/docs/butler/pushing.html — `butler push <directory-or-zip> <user>/<game>:<channel>`, e.g. `butler push ./dist garebearproductionz/rift-ascent:html5`. Channels are free-form names (`windows`, `osx`, `linux`, `html5`, `windows-beta`, …); the channel name sets the platform tag. First push uploads everything; later pushes diff against the last build (rsync-style block diff + Brotli) and upload only what changed. `butler status <user>/<game>` lists channels/builds; `butler push-preview` shows what a push would change. Limit: 30 GB uncompressed per build.

**Auth:** `butler login` (opens a browser to authorize) for interactive use, or `BUTLER_API_KEY` env var for CI/scripts. **The project page must already exist** — butler cannot create it.

**Value for promotion:** a fresh build on the listing is itself a promo event (itch shows updated dates; the SEO repo picks it up within hours; the Bluesky poster can announce it). Every future re-upload (Rift Ascent fix, pack updates) can be one command instead of a browser upload. **Status: NEEDS CREDENTIAL** — Gary runs `butler login` once, or provides an API key.

## 3. Bluesky (AT Protocol) — READY, live today

**State now:** poster built and running on the Mac — account **@tizwildin.bsky.social**, queue + crons, app password already in place. VM copy at `~/workspace/bluesky-poster/` (`poster.py`, `rules.json`, `queue/`). The live queue is on the Mac; the VM queue holds 2 unapproved drafts (01-gui-pack, 02-gui-pack-variant). Posting the Muse referral is already automated (weekly, standing permission); product posts run on the same machinery.

**How it works:** a post is an `app.bsky.feed.post` record written with `com.atproto.repo.createRecord` to the account's repo on its PDS (`https://bsky.social/xrpc/...`). Auth is an app password → `com.atproto.server.createSession` (returns `accessJwt` + `refreshJwt` + DID). **Refresh the session, don't re-login:** `createSession` is capped at 30 per 5 min and 300 per day per account.

**Limits (Bluesky PDS, verified against current guides):**

| Limit | Value |
|---|---|
| Post text | 300 graphemes / 3,000 UTF-8 bytes |
| Images per post | 4, up to 2 MB each (via `uploadBlob`, then `app.bsky.embed.images`) |
| Video | Up to 10 min / 300 MB per video, 25 videos or 10 GB per day (raised Aug 2026) |
| Write points | 5,000/hour, 35,000/day per account (a create costs 3 → ~1,666 posts/hour) |
| API requests | 3,000 per 5 min per IP |
| Link cards | Facets (byte offsets) + `app.bsky.embed.external`, thumb via `uploadBlob` |
| Threads | Reply records with `parent`/`root` — the API supports them, the current poster doesn't build them yet |
| Scheduling | **None native** — the queue + cron does it (that is what the poster already does) |
| Analytics | **None** — no analytics API |
| Cost / review | **Free. No app review, no developer application, no fee.** |

**Current poster's own caps (self-imposed, far under the platform limits):** ≥6h between posts, max 2/day, no duplicate text in 7 days, 300 chars enforced, link cards from the linked page's OG tags, no auto-likes/reposts/replies/follows. Drafts must be `"approved": true`.

**What else the API could do (extensions, same script, no new auth):** image embeds (up to 4 per post — pack cover art, the strongest promo upgrade available), threads (a launch thread instead of a single post), video posts (trailer clips), language tags (`langs`), up to 8 `tags`. All of it is one script change away; the auth and the queue already exist.

**Status: READY.** The only path live today. Recommended first use: keep the weekly cadence, extend the poster with image embeds next.

---

## 4. dev.to API (Forem v1) — NEEDS CREDENTIAL (one key)

**Docs:** `https://dev.to/api`, reference at developers.forem.com. Gary's account: **tizwildin** (id 3931231), logged in on Brave on the Mac, ~30 articles May–Jun 2026. A dev.to poster does not exist yet — this would be built in the Bluesky-poster pattern (queue + approval + cron).

**Auth:** one header, `api-key`. Key generated at **Settings → Extensions → DEV Community API Keys** — Gary generates it in his logged-in session (1-minute job). The key grants write access to the account; treat it like a password. Reads (`GET /api/articles`) are public and need no key.

**Endpoints:**

| Call | What it does |
|---|---|
| `POST https://dev.to/api/articles` | Create an article. Body is one `article` object: `title`, `body_markdown`, `published` (`false` = draft, `true` = live), `tags` (max 4), `series`, `canonical_url`, `description`, `cover_image`, `ai_disclosure_level` |
| `PUT https://dev.to/api/articles/{id}` | Update the same article (same payload) — this is how a draft becomes published |
| `GET /api/articles/me`, `/me/unpublished`, `/me/all` | Your articles, drafts included (the drafts list is the only way to read a draft back — a draft 404s on the public by-id endpoint) |

**Rules and quirks (verified from current guides and live use):**
- **Drafts first:** create with `published: false`, inspect in the editor, then `PUT` with `published: true`. A published post notifies followers immediately; deleting it afterwards does not unsend that.
- **No dedup:** every `POST` creates a new article, even with the same title/canonical URL. Keep a local id mapping (post → dev.to id) and update instead of re-creating.
- **Rate limit:** 3 article publishes per 30 seconds (HTTP 429 after that, with a `Retry-After` header that is sometimes seconds, sometimes an HTTP-date — parse both). Reads are throttled too (Forem-scale: roughly 10–30 req/min); back off on 429.
- **User-Agent required:** a browser-like `User-Agent` header, or the API returns 403 "Forbidden Bots" (Python's default urllib UA is blocked).
- **Tags:** max 4 per post; stored as lowercase alphanumeric slugs — hyphens are silently stripped (`machine-learning` → `machinelearning`).
- **No file uploads:** the API accepts no image uploads. Host images elsewhere and use absolute `https://` URLs in `body_markdown`.
- **No scheduling field:** scheduling is external — create the draft, then a cron publishes it (same pattern as the Bluesky poster).
- **`ai_disclosure_level` is part of the payload** — Gary decides the value per article (his itch rule is "No AI"; dev.to is a separate disclosure surface).

**Why it fits:** the dev.to audience overlaps with his plugin/tool buyers (FreeEQ8/ProEQ8 are dev tools), articles rank well, and a "new pack / new version" article is a natural promo format with a link back to itch. **Status: NEEDS CREDENTIAL** — one key from Gary, then a poster script (same shape as the Bluesky one) can draft and publish.

## 5. Reddit (PRAW / Data API) — BLOCKED (read this one first)

**State now:** poster built on the VM (`~/workspace/reddit-poster/`: `poster.py` + `rules.json` + 6 drafts, all `"approved": false`). It ran once in dry-run (Nov 4 log: both seeded drafts skipped, not approved). `done/` is empty — **it has never posted**. No Reddit app credentials are known to exist anywhere.

**How it was supposed to work:** PRAW (Python Reddit API Wrapper) over Reddit's Data API, script-type app: client ID + secret + username + password + user agent. Free tier: **100 queries/min per OAuth client, non-commercial only**. Per-subreddit rules in `rules.json`:

| Subreddit | Direct posts? | Notes |
|---|---|---|
| r/gameassets | ✅ | Asset posts are the point of the sub; 7-day cooldown |
| r/roguelikedev | ✅ | Dev-to-dev; show the pack in use, not just a store link; 7-day cooldown |
| r/indiegames | ✅ | Promo-friendly, **Promotion flair mandatory**; 7-day cooldown |
| r/godot | ✅ | Godot guides ship in the pack; showcase style, no bare store link; 7-day cooldown |
| r/IndieGaming | ✅ | Fan-and-dev mix; self-promo within limits; 7-day cooldown |
| r/Unity2D | ✅ | Unity setup guides in the pack; 7-day cooldown |
| r/roguelikes | ✅ | Player-heavy; one post, framed for players; 14-day cooldown |
| r/GameDeals | ✅ | **Only with a real discount**, once a month max, link post |
| r/gamedev | ❌ | Direct promo is not what the sub is for — promo only inside the weekly Screenshot Saturday / Feedback Friday megathreads, which the poster does not thread-reply into |
| r/itchio | ❌ | Direct advertising does nothing here — do not post |

Global caps in the poster: ≥6h between posts, max 2/day, per-sub cooldowns, no duplicate title in 7 days.

**Why it is blocked — the finding that matters:** Reddit announced on **Sept 30, 2026** (reported by TechCrunch / The Next Web) that it **stopped taking new public API requests on Oct 31, 2026**, cuts off unregistered apps on **Jan 12, 2027**, and **closes the public API in March 2027**. Today is Nov 5, 2026 — the window for a new app has closed. Separately, since late 2025 every new app needs explicit approval first (Responsible Builder Policy), and the free tier is **non-commercial only** — promoting products for sale sits in a gray area against that condition. Unauthenticated `.json` endpoints were shut down in May 2026, and datacenter IPs get 403 on first attempt (the VM is a datacenter IP — the poster would have to run on the Mac).

**Status: BLOCKED.** The only way back is if Gary **already holds an approved Reddit app** (no evidence one exists). If he does, it may keep working until March 2027 — check with him; if he doesn't, this path is closed and the poster stays shelved. Do not spend setup time here until that question is answered.

## 6. Mastodon — NEEDS GARY (no account exists)

**How it works:** Mastodon is federated — your account lives on one instance (server), and the API lives at that instance's own domain (`https://{instance}/api/v1/...`). Post with `POST /api/v1/statuses` (text + media ids + visibility + `scheduled_at`). Auth is OAuth 2.0: register an app (`POST /api/v1/apps` → `client_id` + `client_secret` → `/oauth/token`), or for a single-account poster, a **personal access token** from Preferences → Development (scopes `read` / `write` / `follow`).

**Limits (defaults, per-instance — verify with `GET /api/v2/instance`):** 300 requests per 5 min (mastodon.social default), 30 media uploads / status deletions per 30 min. **500 characters per post** by default (instances can raise it — some run into the thousands). 4 images up to 16 MB each, 1 video up to 99 MB. **Native scheduling:** `scheduled_at` is server-side (Sidekiq job); confirm via `GET /api/v1/scheduled_statuses`. **No approval queue, no cost.**

**Instance choice is the whole decision.** Natural homes for Gary's stuff: **mastodon.gamedev.place** (game-dev community — the best fit for Rift Ascent / game assets), **fosstodon.org** (FOSS/dev — fits FreeEQ8/ProEQ8), or **mastodon.social** (general, largest). The instance is also the audience: Mastodon has no algorithmic discovery, so the account grows by federation and by people finding the instance community.

**Status: NEEDS GARY** — pick an instance, create the account, generate a token. Then a poster script in the Bluesky pattern (same queue/caps shape; 500-char posts, link + optional image). No account exists today, so nothing can run until he creates one.

## 7. Discord webhooks — NEEDS GARY (no server/webhook known)

**How it works:** a webhook is a URL for one channel: `POST https://discord.com/api/webhooks/{id}/{token}` with JSON. `content` up to **2,000 chars**, up to **10 embeds** (6,000 chars total across them — title 256, description 4,096, 25 fields), up to **10 files**, plus polls and link buttons. Success is `204 No Content` (or `200` with `?wait=true`). No bot, no gateway, no app review, no cost.

**Limits:** ~**5 requests per 2 seconds per webhook**, ~**30 messages/min per webhook/channel**; Discord answers `429` with `retry_after` — read the headers, don't hard-code a sleep. 15 webhooks per channel, 1,000 per server.

**The catch is reach, not tech:** a webhook posts **into a server Gary owns** (an announcements channel) — it reaches only people already in that server. It is an **owned-audience** channel (release notes to his own community), not a discovery channel. Posting promo into other people's servers needs those servers' permission — that is manual outreach, not an API path. **Status: NEEDS GARY** — a server + a webhook URL (created in the channel settings by someone with Manage Webhooks). Once the URL exists, a poster is a 20-line script.

## 8. X / Twitter API — NEEDS GARY + PAID

**The change:** the write-only free tier (1,500 posts/month, no reads) that existed from Feb 2023 **closed to new signups on Feb 6, 2026**. Since then X has been **pay-per-use only, no free tier, no subscriptions** (multiple secondary sources citing docs.x.com, checked Sept 2026 — confirm on X's pricing page before spending). Basic ($100–200/mo) and Pro ($5,000/mo) stopped taking new signups in Feb 2026; existing Basic moved to pay-per-use after June 1, 2026.

**Current per-operation prices (pay-per-use):** plain post **$0.015**, **post with a URL $0.200** (April 2026 anti-spam surcharge), post read $0.005, profile $0.010. Cap: 3M post reads/month. Every promo post carries a link, so **every promo post costs $0.20**: 1/day ≈ **$6/month**, 2/day ≈ **$12/month**.

**Needs:** an X account + a developer app + a payment method on file. Gary has no X account mentioned anywhere in his setup.

**Status: NEEDS GARY + PAID.** Technically fully automatable (v2 `POST /tweets`), but it is the only path here that charges per post, and the per-link surcharge is aimed squarely at promo use. Not recommended as a first path; revisit only if he already has an X presence worth feeding.

---

## 9. Threads API (Meta) — NEEDS GARY (confirm the account)

**How it works:** official API since June 18, 2024. Two calls per post: create a media container (`POST https://graph.threads.net/v1.0/{threads-user-id}/threads`, `media_type` TEXT / IMAGE / VIDEO / CAROUSEL) → publish it (`POST /{threads-user-id}/threads_publish` with `creation_id`). Wait ~30s between the two for media. Auth is Threads-specific OAuth (authorize at `threads.net/oauth/authorize`, exchange for a 1-hour token, upgrade to a **60-day long-lived token**, refreshable once ≥24h old). Scopes: `threads_basic` + `threads_content_publish`.

**Limits:** **250 API-published posts / 24h** per profile, 1,000 replies, 100 deletions (moving 24h windows; check live usage at `GET /{threads-user-id}/threads_publishing_limit`). Call budget: 4,800 × impressions (floored at 10 → 48,000/day minimum). Text **500 chars** (emoji count as UTF-8 bytes), up to **5 links per post** (more fails). Images JPEG/PNG ≤8 MB; video MOV/MP4 ≤5 min, 1 GB. **No native scheduling** — publish happens at once (queue + cron does the timing). **No fee, no pricing page.**

**App Review — the nuance:** sources disagree at first glance, and the truth is split. Until your app passes App Review, only Threads testers you invite under App roles can grant it — so **posting for your own profile works as a tester/admin on your own Meta app without full App Review**; App Review (~1 week per permission) is required before profiles without a role on your app can grant it. For Gary's own account, that means: Meta app + himself as tester = postable without the review queue.

**Status: NEEDS GARY** — confirm he has a Threads account (a Threads connector exists in the toolset, but no account is confirmed), plus a Meta app and the token plumbing (60-day refresh). If the account exists, this is the closest thing to a second Bluesky: free, generous limits, same short-post shape.

## 10. Instagram Graph API — NEEDS GARY (account type + review)

**The gate:** publishing works **only for Professional accounts (Business or Creator)** — personal accounts cannot publish through the API at all. Two login paths: **Instagram Login** (no Facebook Page needed; permissions `instagram_business_basic` + `instagram_business_content_publish`) or **Facebook Login** (needs a linked Facebook Page; `instagram_basic` + `instagram_content_publish` + `pages_read_engagement`).

**How it works:** two-step container flow — `POST /{ig-user-id}/media` with a **public media URL** (Instagram fetches the file; no upload in the request body) → poll until `FINISHED` → `POST /{ig-user-id}/media_publish`. Images JPEG only, ≤8 MB, 4:5–1.91:1. Reels 3s–15 min, ≤300 MB. Carousels up to 10 items. **100 API-published posts per rolling 24h** per account (carousel counts as one). **Media is always required — there is no text-only post on Instagram.** Tokens are 60-day long-lived (refresh only when ≥24h old).

**Review:** App Review takes **2–4 weeks per permission**, plus Business Verification before the app can publish for accounts it doesn't own. For Gary's own account as a tester the review burden is lower, but the account-type and app setup are still his to do.

**Status: NEEDS GARY** — check whether his Instagram account is Professional (a connector exists, account type unknown), plus Meta app + review. Strong format for pack art / game screenshots, but the heaviest Meta setup of the three Meta paths.

## 11. YouTube Data API v3 — NEEDS GARY + AUDIT GATE

**How it works:** `videos.insert` (resumable upload with title, description, privacy). Auth: Google Cloud project + OAuth 2.0, scope `youtube.upload`. Free — usage is counted in quota, not billed.

**Quota (current model, since June 1, 2026):** uploads in their own bucket — **100 `videos.insert`/day at 1 unit each**; general pool 10,000 units/day; `search.list` 100/day. (Older guides cite 1,600 units per upload / ~6 a day — superseded.) Quotas reset at midnight Pacific.

**The gate that matters:** for projects created after **July 28, 2020**, videos uploaded via the API stay **PRIVATE until YouTube's compliance audit** — which has **no published timeline**. A new API project cannot publish publicly until that audit passes. Separately, Google OAuth verification for sensitive scopes takes ~10 business days (restricted scopes ~6 weeks), and while the consent screen is in Testing, refresh tokens expire after 7 days.

**Fit:** YouTube is for trailers and demo videos (Rift Ascent gameplay, pack walkthroughs), not text promos. Gary has a Google account (Gmail is connected); a YouTube channel is not confirmed. **Status: NEEDS GARY + AUDIT GATE** — channel + Cloud project + an unbounded audit wait before anything goes public.

## 12. TikTok Content Posting API — NEEDS GARY + HEAVY GATES (likely poor fit)

**Two modes:** **Direct Post** (`video.publish` scope) publishes immediately; **Upload** (`video.upload`) sends to the creator's inbox as a draft the creator finishes in TikTok.

**Gates (all verified against TikTok's own docs, Oct 2026):** register an app → add the Content Posting API product → **app review** (days to 2 weeks, needs a demo video of the full flow; changes after approval are re-reviewed) → **compliance audit for Direct Post** (2–4 weeks, checks the posting-screen UX against TikTok's rules). **Until audited, every post is forced PRIVATE (`SELF_ONLY`), the posting account must itself be private, and max 5 users can post per 24h.** Caps after audit: ~15 posts/day per creator (shared across apps), 6 init requests/min per user token, 5 pending inbox shares/24h. Caption 2,200 chars; video up to 4 GB / 10 min; photos up to 35 images. Also: TikTok's guidelines say API clients must serve a wide audience, **not be for private or personal use** — a one-creator promo tool is at real risk of rejection at review.

**Status: NEEDS GARY + HEAVY GATES.** No TikTok account is known. The audit wall + the "not for personal use" rule make this the worst effort-to-reward ratio on the list. Only revisit if he already has a TikTok audience.

## 13. Facebook Pages (Graph API) — NEEDS GARY

A Facebook **Page** can publish via the Graph API with a page token (text, links, photos, video). Gary has a Facebook connector (facebook_cli), so the tooling exists. Needs a Page + a Meta app (+ App Review for some permissions). Same Meta overhead as Instagram/Threads, lower reach per post than the others for itch-style assets. Listed for completeness; not a first path.

## 14. Owned-audience extras (no discovery, but fully API-able)

- **Newsletter — Buttondown.** Simple API (API key, `POST` a new email/draft), free tier. Gary has no mailing list mentioned anywhere — this would start from zero subscribers. Worth doing only once there is an audience to mail (e.g. HUB account holders). Status: NEEDS GARY (account).
- **RSS/Atom from the itch-seo repo.** The planned SEO repo (Phase 2, `GareBear99/itch-seo`) already generates `all_items.json` + a sitemap; emitting an **RSS feed of new/changed items** is a few lines in the same generator. Free, no account, no approval. Feed readers pick it up, and any automation (IFTTT/Zapier-style, or a small script) can consume it to cross-post. Status: **READY TO BUILD** with the SEO repo.
- **Substack:** no official public write API — skip.

## 15. What itch itself offers (non-API levers — for completeness)

itch.io has **no promotion API**, but the storefront has promo levers that are manual today:
- **Game jams** (itch runs them; entry is via the site, manual).
- **Bundles and sales** (price/discount set in the dashboard, manual — this is what made A Devil's Game $2.10; GameDeals on Reddit only allows posts with a real discount).
- **Tags / categories / short description** (dashboard, manual — the ≤120-char short description and the dark theme are already Gary's rules).
- **Collections** (API-editable, §1 — the one promo-ish thing the API can do).
- **Freshness:** a new build pushed via butler updates the listing date and the SEO repo picks it up within hours.

The API loop that exists is: **butler push → SEO repo notices → Bluesky/dev.to announce**. That loop is the whole promotion machine; everything else is a channel plugged into its end.

## 16. How to run it (where the posters live)

| Runner | Verdict |
|---|---|
| **Mac crons (current)** | Bluesky runs here today (queue + cron). Works, but fails when the Mac sleeps, is off, or is busy with Ableton/Lucid. |
| **GitHub Actions** | **Recommended for new posters.** Free for public repos; the HUB already proves the pattern (`itch-inventory-refresh.yml` — daily cron + auto-commit). Runs even when the Mac is off. Keys go in as repo secrets — Gary's call on secret storage. |
| Cloudflare Worker | Possible, but adds a second system for a job GitHub already does free; no advantage for posting. Skip. |

**Secrets rule (standing):** keys live in env files on the machine that runs the poster, or in GitHub repo secrets — never in chat, never in a repo, never in this file.

## 17. Recommended order — top 3 to use first

**Foundation (do once, unlocks everything else):** itch API key + `butler login`. One-time, Gary's hands, ~5 minutes. Gives structured inventory, fresh uploads, and collections.

1. **Bluesky — already live.** Keep the weekly cadence. Next upgrade, same script: **image embeds** (pack cover art on the post itself instead of only in the link card), then threads for launches. Zero new auth, zero cost, zero gates.
2. **dev.to — one key away.** Gary generates the API key in his logged-in session; then a poster in the Bluesky pattern drafts articles (new pack / new version / devlog) and publishes on a cron, drafts-first. The dev audience fits his tools (FreeEQ8/ProEQ8) better than any other channel here.
3. **Threads — if the account exists.** Free, 250 posts/day, 500 chars, same short-post shape as Bluesky. Needs a Meta app + token plumbing (60-day refresh); own-profile posting works as a tester without full App Review.

**After that, in order:** Mastodon (if he wants the fediverse — pick mastodon.gamedev.place), Discord webhook (the moment he has a server), YouTube (trailers, once the audit clears), Instagram (if the account is Professional). **Skip/delay:** Reddit (closed to new apps), X ($0.20 per link-post), TikTok (audit wall + personal-use rule).

## 18. What Gary must provide (checklist for his return)

- [ ] **itch API key** — User Settings → API Keys (optional upgrade; scraping works without it)
- [ ] **`butler login`** — run once on the machine that will push builds (or a BUTLER_API_KEY)
- [ ] **dev.to API key** — Settings → Extensions → DEV Community API Keys (1 minute, in his logged-in Brave)
- [ ] **Confirm: Threads account?** (a connector exists; account not confirmed)
- [ ] **Confirm: Instagram account Professional or personal?**
- [ ] **Confirm: Reddit — do you already hold an approved Reddit app?** (if yes, the poster may work until March 2027; if no, Reddit is closed)
- [ ] **Decide: Mastodon instance?** (mastodon.gamedev.place / fosstodon.org / mastodon.social)
- [ ] **Decide: Discord server + webhook?** (only if he wants an announcements channel)
- [ ] **Decide: X — worth $0.20 per link-post?** (needs account + app + payment)
- [ ] **Confirm: YouTube channel?** (needed before the API audit wait starts)

## 19. Progress log

- **2026-11-05 ~18:10 PST — Research started.** Task from Gary (~18:08 PST). Read local context first: SEO repo design (itch API/RSS already established), Bluesky poster (README + poster.py + rules.json), Reddit poster (README + poster.py + rules.json + queue + logs), dev.to badges plan.
- **2026-11-05 ~18:15 PST — Local state established.** Bluesky poster: live on the Mac, app password in place, caps 6h/2-per-day/no-dup-7-days; VM queue has 2 unapproved drafts. Reddit poster: built, never posted (done/ empty, Nov 4 log shows dry-run skips only), 6 drafts all unapproved. dev.to: account tizwildin (id 3931231), logged in on Brave, no API key known. itch: no API key known; scraping is the current inventory path.
- **2026-11-05 ~18:20 PST — Web research, batch 1.** itch.io server-side API docs (new api.itch.io + legacy), butler pushing docs, Bluesky AT Protocol limits (multiple guides, consistent), dev.to/Forem API (create/update/drafts/tags/rate limit), Reddit Data API pricing + the Sept 30, 2026 shutdown announcement, Mastodon API (statuses, OAuth, per-instance limits, native scheduling), Discord webhooks (limits + rate handling), X API pricing (free tier closed Feb 2026, pay-per-use rates).
- **2026-11-05 ~18:30 PST — Web research, batch 2.** dev.to rate-limit details (3 publishes/30s, Retry-After formats, User-Agent requirement), Threads API (two-call publish, quotas, App Review nuance for own-profile testers), YouTube Data API (2026 quota buckets, private-until-audit gate), TikTok Content Posting API (review + audit gates, private-only until audited), Instagram Graph API (Pro-only, container flow, review timelines).
- **2026-11-05 ~18:35 PST — File written.** Full findings + status table + recommended order + Gary's checklist above. Nothing posted, no accounts created, no money spent, no credentials stored. **Headline findings for Gary's return: (1) Reddit is closed to new apps (window shut Oct 31, 2026; public API ends March 2027) — check whether he already holds an approved app; (2) X now charges $0.20 per link-post; (3) only Bluesky is live today; dev.to is one key away.**
