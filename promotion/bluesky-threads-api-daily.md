# Bluesky + Threads — Daily API-Routes Log

Daily record of what I do with the Bluesky + Threads API routes, for Gary.
One entry per day, newest last. Each entry: date, which API routes were used, which posts
went out on Bluesky and Threads, which paying assets were promoted, the result, and any
new routes found or used.

Rules: no secrets in this file — no tokens, no passwords, no app passwords, no account
credentials. Post IDs are machine handles and are NOT recorded here; the draft file name,
the asset, the platform, and the result are enough. The full route reference is
`~/workspace/bluesky-threads-api-routes.md`. A mirror of this file lives in the HUB repo
at `docs/api-routes-daily.md` for promotional continuity (same content, no secrets).

---

## 2026-11-07 (Sat)

- **API routes work:** Researched and documented the FULL Bluesky + Threads API routes
  (`~/workspace/bluesky-threads-api-routes.md`). Bluesky: AT Protocol XRPC — session
  (`createSession`/`refreshSession`/`deleteSession`), repo writes (`createRecord`,
  `uploadBlob`, `putRecord`, `deleteRecord`, `applyWrites`), post record
  (`app.bsky.feed.post`, facets, embeds, replies), video (`app.bsky.video.*`), public
  AppView reads (no account needed). Threads: Meta Threads API on
  `graph.threads.net/v1.0` — OAuth, two-step container flow (`POST /{user-id}/threads`
  then `POST /{user-id}/threads_publish`), `reply_to_id` replies, carousels, reply
  management, insights, `threads_publishing_limit` quota. Also documented the
  `threads-cli` connector commands the posters use. No new routes used and no poster
  changes after that.
- **Bluesky posts:** `11-arcanum-i-part2.json` — Arcanum I Part 2 ($2.88 CAD) —
  POSTED 07:47 PST, verified live via the public API; plain link only, no link card
  (itch.io returned 429 on the card fetch). `08-arcanum-ii-part1.json` — Arcanum II
  Part 1 ($2.88 CAD) — POSTED 13:49 PST, verified live; it posted in place of the
  scheduled draft 12 because the poster takes the lowest-numbered approved due draft.
  `12-kings-gambit.json` — King's Gambit — NOT posted (queue order, then the 2/day cap
  was reached); next slot Sun Nov 8 07:42 PST. Cron runs: bluesky-post-daily-am 07:42
  PST and bluesky-post-daily-pm 13:42 PST fired; bluesky-post-kings-gambit 13:42 PST
  reported failed (draft 12 did not post).
- **Threads posts:** `04-arcanum-i-part1.json` — Arcanum I Part 1 ($1.78 CAD) —
  POSTED 06:49 PST, verified live (publish call timed out after 300s but the post had
  gone live; reconciled, no duplicate). `threads/llmbuilder-thread.json` parts 1–4 —
  LLMBuilder repo promo thread — POSTED 06:49–06:57 PST, verified live. Midday run
  12:42 PST: HELD, nothing posted (6h interval not yet clear). `05-arcanum-i-part2.json`
  — Arcanum I Part 2 ($2.88 CAD) — POSTED 18:43 PST, verified live (text, image, itch
  link match draft). Note: a concurrent run of the morning job ran poster.py live while
  the main run was posting the thread — no duplicates resulted, but a possible duplicate
  cron trigger to investigate. Also recorded here (no Nov 6 entry exists in this log):
  `03-arcanum-ii-part2.json` — Arcanum II Part 2 — POSTED 21:47 PST Nov 6.
- **Paying assets promoted:** Arcanum I Part 1 ($1.78), Arcanum I Part 2 ($2.88),
  Arcanum II Part 1 ($2.88). (The LLMBuilder thread promoted the repo, not a paid asset.)
- **Acquired today:** itch sales-audit apply pass COMPLETE — Brief C batches C1–C3
  applied today (C1: 11 short descriptions + 12 funnel lines; C2: 12 + 11; C3: 12 + 12),
  completing Brief C and the whole apply pass (85 short descriptions + 36 funnel lines
  total); every free listing now funnels to the arena collection (source: itch listing
  updates). itch-seo autopull (2 refreshes today): inventory still 112 items, no new
  listings; new price points first seen today — Orc Bungalo Mystic Meadow Arena Kit
  $2.75, Animated VFX UI Pack (80 assets) $3.75 (−50%). No sales verified today.
- **New routes used/found:** none today.

## 2026-11-08 (Sun) — final (closes the in-progress section above)

- **API routes work:** none today — no new routes researched or used, no poster changes.
- **Bluesky posts:** no post verified from run history. bluesky-post-daily-am 07:42 PST and bluesky-post-daily-pm 13:42 PST fired, but neither run's summary confirms a post. Runonce bluesky-post-cloudworks 07:42 PST FAILED (held — queue order would have posted draft 09 Arcanum II Part 2 instead of the required draft 13 Cloudworks, so nothing ran). Runonce bluesky-post-shadow-run-vfx 13:42 PST FAILED (Mac offline — draft 14 Shadow Run VFX not posted). Evening retry bluesky-post-evening-retry-2026-11-08 20:00 PST FAILED (Mac offline, last seen 18:43 PST; no post attempted, 13:42 slot status unverifiable). Latest Bluesky post remains Nov 7 13:49 PST (Arcanum II Part 1).
- **Threads posts:** `06-kings-gambit.json` — The King's Gambit ($2.25 CAD) — POSTED 06:42 PST, verified live. `07-cloudworks.json` — Cloudworks ($6.99 CAD) — POSTED 14:06 PST, verified live (posted immediately on Gary's "posts too now", not waiting for slots). Midday 12:42 PST run: held, nothing posted (6h interval). Evening 18:42 PST run: no post — `08-shadow-run-vfx.json` and `09-adevils-game.json` held by the 6h interval (only 4.6h since Cloudworks). Next due: `10-gui-pack.json` 06:42 PST Nov 9.
- **Nostr posts:** #8 King's Gambit posted ~11:58 PST, verified live. #9 Cloudworks posted 17:00 PST, verified live (4/7 relays accepted).
- **Paying assets promoted:** The King's Gambit ($2.25 CAD — Threads + Nostr), Cloudworks ($6.99 CAD — Threads + Nostr). A Devil's Game ($2.10 CAD) did not go out (held by spacing). Bluesky promoted nothing today.
- **Acquired today:** New FREE itch listing "Avatar Generator — 2.4 Billion Succubus Combinations" (https://garebearproductionz.itch.io/avatar-generator), first seen in itch-seo autopull 85d0fd7 (11:45 PST); inventory 112 → 113 items. No new paid price points today (autopull only refreshed lastSeen); no sales verified; no sales-audit work today. Code landed (not itch): Lucid Google Drive OAuth + segment voice mp3s pushed to GitHub master (b525729); Lucid text-spacing pass committed locally as bundle bb88d35, not yet pushed (Mac offline).
- **New routes used/found:** none today.

## 2026-11-09 (Mon)

- **Bluesky posts:** `09-arcanum-ii-part2.json` — Arcanum II Part 2 ($2.16 CAD) — POSTED 06:50 PST, verified live via public API: https://bsky.app/profile/tizwildin.bsky.social/post/3mzv6ewgauw2k. First Bluesky post since Nov 7 13:49 PST. Poster posts first approved+due in sorted order, so 09 went out (not 15-adevils-game); the 07:42 AM adevils-game runonce will post the next due draft in order. Run from the Mac poster (VS Code Terminal 60).
- **Threads posts:** `08-shadow-run-vfx.json` — Live Smog VFX & Shadow Run Map Layers ($1.37 CAD) — POSTED 06:43 PST (already posted when this run started; found in state.json, verified live via threads-cli profile-threads): https://www.threads.com/@garebearproductionz/post/DfhksKqjhtp (0 likes). Followers 217. Next due: `09-adevils-game.json`, not before ~12:43 PST (6h interval).
- **Nostr posts:** #10 A Devil's Game ($2.10 CAD sale, was $4.20) — POSTED ~06:51 PST, verified live on relay.primal.net (event b3288112…, note https://nostr.band/note1kv5gzyjtee5ty22zw0yzr0egfn9pxc5mgchappnm9nsk7t7qwyas2t4ttt, 3/7 relays: primal, nostr.net, wellorder; damus 503, nos.lol + nostr.mom timeouts, nostr.band connection lost). Fresh angle "Build your own hell", cover via nostr.build. Note: nostr_poster.py has no --image-url flag (docstring stale); image URL goes in the note text (actual flag is --upload-image). #11 Muse referral (boss video) — POSTED ~11:44 PST, verified live on relay.primal.net + relay.nostr.net + wellorder (event 9d115d9c…, note https://nostr.band/note1n5g4m8yew7pn7vre2hl92htymk4alqvvrmlklfejrru274v6qujqun4439, 3/7 relays; damus 503, nos.lol + nostr.mom timeouts, nostr.band connection lost). Full video via nostr.build: https://video.nostr.build/971516b42bd801a9c8c6465dca4202320251ae04d824aa8de569602b4bcea02c.mp4. This is today's one referral note (max 1/day).
- **Paying assets promoted:** Arcanum II Part 2 (Bluesky, $2.16 CAD), Live Smog VFX & Shadow Run Map Layers (Threads, $1.37 CAD), A Devil's Game (Nostr, $2.10 CAD sale), Orc Bungalo Mystic Meadow Arena Kit (Hive, $2.75 CAD).
- **Revenue:** $0 new today (no sales verified).
- **New routes used/found:** none today.
- **Muse referral — boss video (Gary's order ~08:59 PST, NOT an itch product):** video = our siren boss animated (10s, 960x960, 8.1 MB). Copy: "Our Muse made this" + code 7LU3P6 + https://muse.ai/join (redeem in Settings within 48h, both get 1B tokens).
  - **Bluesky:** QUEUED — draft `08-muse-referral-boss.json` in Mac queue, not_before 12:50:29 PST, posts at the 13:42 PST run. FORM: text + link card only (poster has no video/image attach).
  - **Threads:** QUEUED — draft `08d-muse-referral-boss.json` in VM queue, not_before 12:43:44 PST, posts at the 18:42 PST run. FORM: still frame + text (poster supports static PNG only).
  - **Nostr:** POSTED ~11:44 PST — full video uploaded to nostr.build + note, verified live on 3 relays (primal, nostr.net, wellorder). Event 9d115d9c…, https://nostr.band/note1n5g4m8yew7pn7vre2hl92htymk4alqvvrmlklfejrru274v6qujqun4439. FORM: full video.
  - Reddit NOT used (referral spam = ban).
- **Hive — NEW, LIVE today (tizwildin):** account created 2026-11-09 10:52 PST via Ecency (free signup; profile https://ecency.com/@tizwildin, hive.blog/@tizwildin also loads). First post LIVE 10:23 AM PST — Orc Bungalo Mystic Meadow Arena Kit ($2.75 CAD), verified live: https://hive.blog/@tizwildin/orc-bungalo-mystic-meadow-arena-kit. Daily schedule 10:42 AM + 4:42 PM PST (crons `hive-post-daily-am` / `hive-post-daily-pm`, both verified enabled + daily ~14:10 PST; ≥4h gap, ≤3/day, approved drafts only). Queue (verified from queue files): 02 King's Gambit due today 14:30 PST (posts at today's 16:42 run), 03 Cloudworks due Nov 10 08:00 PST, 04 A Devil's Game due Nov 10 14:00 PST. **QUEUE WARNING: queue is EMPTY after Nov 10 16:42 — more drafts owed.** Hive referral draft owed ~Nov 10 20:00 PST (image route TBD — try ecdsasig.sign_message for images.hive.blog, else text-only). Keys in ~/workspace/hive-keys.txt; master password still only in the Ecency "Your account created" email — Gary to save.
- **Muse referral — NEW PACE TARGET (Gary, ~14:10 PST):** "get one muse a week to a month depending on conet flow for tokens" — ONE new Muse signup per WEEK to per MONTH, depending on content flow; each signup = 1B tokens for both sides (code 7LU3P6, https://muse.ai/join). This supersedes the daily referral pace. Today's referral state: Nostr referral POSTED ~11:44 PST (above). Bluesky referral draft `08-muse-referral-boss.json` was STILL in the Mac queue at ~14:08 PST (approved, not_before 12:50 PST) — the 13:42 run's outcome is UNCONFIRMED, do not claim it posted. Threads referral draft `08d-muse-referral-boss.json` due at today's 18:42 run — subject to the new pace rule (open question whether it still goes out; not claimed either way).
- **Only money makers get promoted (standing rule, Gary ~12:50 PST):** promotion slots go to PAID products only — Orc Bungalo $2.75 CAD, King's Gambit $2.25, Cloudworks $6.99, A Devil's Game $2.10. Free packs are funnel entries only (they carry a funnel line to the paid Arena Kits collection). Applied today: the Nostr post queued for 16:42 PST was SWAPPED from the free Boss Backgrounds pack to the paid Cloudworks ($6.99).
- **Packs published/updated today:**
  - Boss Backgrounds — Free Pack — LIVE: https://garebearproductionz.itch.io/boss-backgrounds-free-pack (project 5330214). All 10 files uploaded + verified; funnel line to the paid Arena Kits collection added ~12:49 PST.
  - Minds Eye — Free Pack — LIVE: https://garebearproductionz.itch.io/minds-eye-free-pack (project 5330542, published 09 Nov 2026 @ 21:23 UTC). 5 tracks, 66 MB zip.
  - Subwoofer Crown Bass Pack — UPDATED (existing listing, NOT a duplicate): https://garebearproductionz.itch.io/subwoofer-crown-bass-pack. New 25 MB zip with the 00_Showcase_Song preview, title fixed to "Subwoofer Crown Bass Pack".
  - Inventory note: the re-audit counted 112 listings (76 paid, 36 free) BEFORE these two new free packs. No new autopull inventory count was run today — not claimed here.
- **Sites setup — new places + setup run:**
  - 7 places found + verified live 2026-11-08: Hive, Minds, Misskey, Game Jolt, IndieDB, GAMES.GG, Odysee. Setup run 2026-11-09 ~09:43–10:09 PST: 1 of 7 done (Hive). Minds / Game Jolt / IndieDB / Odysee blocked on Gary's password; Misskey invite-only; GAMES.GG draft only (no Rift Ascent store link, pitch unapproved, $199 fast-track NEVER paid).
  - NEW places offered 2026-11-09 ~14:09 PST — Gary has NOT picked any yet: OpenGameArt.org, IGDB, IndieRadar, Newgrounds, TikTok, Instagram.
  - Instagram DONE 2026-11-09 — already linked as garebearproductionz (professional, via Meta Accounts Center); no sign-in needed; credentials file /Users/gary/projects/instagram-credentials.txt.
  - Game Jolt — Gary authorized Google login ~14:35 PST ("just log in it with google if you can and you have my permission to go to my gmail and verify") — "Continue with Google" in his Brave; the signup is being moved to his Brave on the Mac. Standing rule: signups/logins happen in GARY'S browser, not Muse's.
  - IndieDB BLOCKED on Gary's date of birth (required field on the register form — do not invent).
- **Still due today:** Hive King's Gambit 16:42 PST; Nostr Cloudworks 16:42 PST (loop GIF + static PNG, $6.99 CAD); Threads referral 18:42 PST (subject to the new pace rule). **Tomorrow:** Bluesky A Devil's Game 07:42 PST; Hive Cloudworks (due Nov 10 08:00, posts at 10:42 run); Hive A Devil's Game (due Nov 10 14:00, posts at 16:42 run).
