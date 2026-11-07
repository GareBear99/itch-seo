# Bluesky + Threads — Full API Routes for Posting

Research date: 2026-11-07. Researched for Gary (GareBear99 / TizWildin Entertainment) so the
Bluesky and Threads promotion of the paying assets can use every posting route that exists —
including routes the current posters do not use, and routes that need an account.

**Accounts:** Bluesky `@tizwildin.bsky.social` · Threads `@garebearproductionz`
(account ID `17841424267170652`, 216 followers at setup).

**Current posters (what is already used):**
- Bluesky poster — Mac, `/Users/gary/bluesky-poster/poster.py` (VM copy at
  `~/workspace/bluesky-poster/poster.py`, stale, 2 queue files). Direct AT Protocol calls.
- Threads poster — VM, `~/workspace/threads-poster/poster.py` + `post-thread.py`.
  Goes through the connected Threads connector (`/opt/hatch/bin/threads-cli`).

**Rules that stay in force:** no live posting from this research; no account creation;
no credential use or storage; no secrets in any document. The posters' own safety caps
(Bluesky ≥6h between posts, ≤2/day; Threads ≥6h, ≤3/day, no duplicate text in 7 days)
are Gary's design, not platform limits.

---

## 1. Bluesky — AT Protocol (XRPC)

Bluesky is one app on the AT Protocol. There is **no application form, no review, no API
key**. Any account can post after authenticating with an app password or OAuth.

- **Writes host (PDS):** `https://bsky.social` — most accounts live here; a custom PDS
  goes in its place. All write XRPC calls go to `<PDS>/xrpc/<method>`.
- **Public reads host (AppView):** `https://public.api.bsky.app` — read endpoints
  (`app.bsky.*`) work here **with no account and no auth**.
- **Docs:** https://bsky.network/docs · https://atproto.com · lexicons at
  https://github.com/bluesky-social/atproto
- **Post limits:** text max **300 graphemes / 3,000 bytes**. Up to **4 images** per post.
  Blob (image) size limit **1,000,000 bytes** (the poster's `MAX_BLOB_BYTES`). Video:
  up to **10 minutes / 300 MB** per video (raised August 2026).
- **Rate limits (points system, per account):** writes cost points — a post costs
  **3 points**. Ceiling **5,000 points/hour, 35,000 points/day** → at most ~1,666 posts/hour,
  ~11,666/day. Published limits: https://bsky.network/docs/rate-limits
- **No scheduling endpoint.** Bluesky has no native scheduled-post API; scheduled posting
  is a cron/queue (which is what the posters already do).
- **No analytics API.**

### 1.1 Auth — sessions and app passwords

| Route | Method | Auth | Purpose |
|---|---|---|---|
| `/xrpc/com.atproto.server.createSession` | POST | none (identifier + password in body) | Log in. Body: `{"identifier": "<handle>", "password": "<app-password>"}`. Returns `did`, `accessJwt`, `refreshJwt`, `handle`, `didDoc`. |
| `/xrpc/com.atproto.server.getSession` | GET | Bearer accessJwt | Check the current session. |
| `/xrpc/com.atproto.server.refreshSession` | POST | Bearer refreshJwt | Refresh an expired access token. Returns new `accessJwt` + `refreshJwt`. |
| `/xrpc/com.atproto.server.deleteSession` | POST | Bearer refreshJwt | Log out / revoke the refresh token. |
| `/xrpc/com.atproto.server.createAppPassword` | POST | Bearer accessJwt | Create a named app password. Body: `{"name": "<name>"}`. |
| `/xrpc/com.atproto.server.listAppPasswords` | GET | Bearer accessJwt | List app passwords (names only, no values). |
| `/xrpc/com.atproto.server.revokeAppPassword` | POST | Bearer accessJwt | Revoke one app password. Body: `{"name": "<name>"}`. |
| `/xrpc/com.atproto.server.describeServer` | GET | none | Server info (available contact, links). |

App passwords are created at https://bsky.app/settings/app-passwords — never the login
password. **OAuth (recommended for apps with their own login flow):** DPoP-bound tokens
with server-issued nonces are mandatory, PKCE `S256` mandatory, `client_id` is the URL of
a public JSON client-metadata document you host. Single-purpose bots/CLI tools may use
app passwords instead (AT Protocol spec wording). The current poster uses app passwords.

### 1.2 Repo writes — the posting surface (all POST, Bearer accessJwt)

| Route | Purpose |
|---|---|
| `/xrpc/com.atproto.repo.createRecord` | **Create a post** (and any record). Body: `{"repo": "<did>", "collection": "app.bsky.feed.post", "record": {...}}`. Returns `{"uri": "at://<did>/app.bsky.feed.post/<rkey>", "cid": "<cid>"}`. Keep both — replies/quotes reference a post by URI + CID. |
| `/xrpc/com.atproto.repo.putRecord` | Create or update a record at a chosen rkey. |
| `/xrpc/com.atproto.repo.deleteRecord` | **Delete a post.** Body: `{"repo": "<did>", "collection": "app.bsky.feed.post", "rkey": "<rkey>"}` — the rkey is the last segment of the `at://` URI. |
| `/xrpc/com.atproto.repo.applyWrites` | Batch multiple creates/updates/deletes in one call. |
| `/xrpc/com.atproto.repo.uploadBlob` | **Upload media.** Raw bytes in the body with the correct `Content-Type` (e.g. `image/jpeg`); returns a blob ref to put in the post's `embed`. One call per file. |
| `/xrpc/com.atproto.repo.getRecord` | GET a single record by repo/collection/rkey. |
| `/xrpc/com.atproto.repo.listRecords` | GET — list records in a collection (paged, `limit` + `cursor`, `reverse` supported). |
| `/xrpc/com.atproto.repo.describeRepo` | GET — repo metadata + which collections exist. |

### 1.3 The post record — `app.bsky.feed.post`

```json
{
  "$type": "app.bsky.feed.post",
  "text": "Hello world",
  "createdAt": "2026-11-07T03:00:00Z",
  "langs": ["en"],
  "tags": ["gamedev"],
  "facets": [{
    "index": {"byteStart": 0, "byteEnd": 11},
    "features": [{"$type": "app.bsky.richtext.facet#link", "uri": "https://example.com"}]
  }],
  "embed": {"$type": "app.bsky.embed.images", "images": [{"image": "<blob-ref>", "alt": "alt text"}]},
  "reply": {
    "root": {"uri": "at://<did>/app.bsky.feed.post/<rkey>", "cid": "<cid>"},
    "parent": {"uri": "at://<did>/app.bsky.feed.post/<rkey>", "cid": "<cid>"}
  }
}
```

- `text` + `createdAt` are required. `text` may be empty when an embed is present.
- **Facets:** Bluesky does NOT auto-link. Links and mentions must be declared as facets
  with **UTF-8 byte offsets** into the text. Facet types: `app.bsky.richtext.facet#link`
  (`uri`), `app.bsky.richtext.facet#mention` (`did`), `app.bsky.richtext.facet#tag` (`tag`).
- **`tags`:** up to 8 extra hashtags that are not in the text.
- **Embeds:** `app.bsky.embed.images` (≤4 images, each with `alt`), `app.bsky.embed.external`
  (link card: `{"uri", "title", "description", "thumb": <blob-ref>}` — the poster builds
  this from the linked page's Open Graph tags), `app.bsky.embed.record` (quote post:
  `{"record": {"uri", "cid"}}`), `app.bsky.embed.video` (video), `app.bsky.embed.recordWithMedia`.
- **Reply:** `reply.root` + `reply.parent` are both `strongRef` (`{uri, cid}`). For a
  top-level reply, root = parent = the post being replied to. A multi-post thread is a
  chain: each part's `reply.parent` is the previous part, `reply.root` is the first part.
  To reply you need the target's CID — recover it with `app.bsky.feed.getPosts` or
  `com.atproto.repo.getRecord` if you only kept the permalink.
- **Like / repost:** also records, same `createRecord` call — collection
  `app.bsky.feed.like` (`{"subject": {uri, cid}}`) and `app.bsky.feed.repost`
  (`{"subject": {uri, cid}}`). The current posters never like/repost (no fake engagement).

### 1.4 Video — `app.bsky.video.*`

Video upload is a separate flow from `uploadBlob` (it sits in the `app.bsky.video`
namespace, not core `com.atproto`):

| Route | Purpose |
|---|---|
| `/xrpc/app.bsky.video.uploadVideo` | Upload a video file (up to 10 min / 300 MB). Returns a job status. |
| `/xrpc/app.bsky.video.getJobStatus` | Poll the processing job (`jobId`) until the video is ready, then embed it. |
| `/xrpc/app.bsky.video.getUploadLimits` | GET — current upload limits for the account. |

### 1.5 Reads — AppView, no account needed (GET, `https://public.api.bsky.app/xrpc/...`)

| Route | Purpose |
|---|---|
| `app.bsky.feed.getTimeline` | The home timeline (auth needed for a personalised one; public use is limited). |
| `app.bsky.feed.getAuthorFeed` | Posts by one author (`actor` + `filter`, paged). |
| `app.bsky.feed.getPostThread` | A post + its replies (`uri`, `depth`). |
| `app.bsky.feed.getPosts` | Several posts by URI (recovers CIDs for replies/quotes). |
| `app.bsky.feed.searchPosts` | Search posts by keyword. |
| `app.bsky.feed.getFeed` | A feed generator's feed (`feed` URI). |
| `app.bsky.feed.getLikes` / `getRepostedBy` | Who liked / reposted a post. |
| `app.bsky.actor.getProfile` / `getProfiles` | Profile(s) by handle/DID. |
| `app.bsky.actor.searchActors` | Search accounts. |
| `app.bsky.graph.getFollowers` / `getFollows` | Follower / following lists. |
| `app.bsky.notification.listNotifications` | Notifications (auth needed). |
| `app.bsky.actor.getPreferences` / `putPreferences` | User preferences (auth needed). |

Reads are public and need no account — that is how the post can be verified after publishing
without logging in.

### 1.6 What the current Bluesky poster uses (and does not use)

- **Uses:** `createSession` (app password), `uploadBlob` (link-card thumbs),
  `createRecord` with collection `app.bsky.feed.post`, link facets (UTF-8 byte offsets),
  `app.bsky.embed.external` link cards from Open Graph tags. Text-only + link-card posts.
- **Does NOT use (available):** image embeds (`app.bsky.embed.images` — the poster has no
  image-post path; media files in the queue are for Threads), video upload
  (`app.bsky.video.*`), replies/threads (`reply.root`/`reply.parent`), quotes
  (`app.bsky.embed.record`), `tags`, `langs`, `putRecord`/`deleteRecord` (edit/delete),
  `applyWrites` (batching), `refreshSession` (it logs in fresh each run),
  any read endpoint (no post verification read-back).

### 1.7 Sources (Bluesky)

- https://bsky.network/docs (official docs; the rate-limits page is
  https://bsky.network/docs/rate-limits)
- https://atproto.com (AT Protocol spec)
- https://github.com/bluesky-social/atproto (lexicons + reference PDS)
- https://github.com/bluesky-social/bps-website/blob/HEAD/docs/bluesky-api/index.mdx
  (official "make your first post" guide)
- https://www.postzen.dev/blog/bluesky-api (2026 guide, checked against the specs 2026-09-08)
- https://posteverywhere.ai/blog/post-to-bluesky-api (2026 guide)
- https://www.upload-post.com/bluesky-api/ (2026 guide)
- https://bundle.social/blog/bluesky-at-protocol-api (OAuth + facets + video)
- https://github.com/barretb/barretapi/blob/HEAD/specs/001-social-post-api/research/bluesky-api.md

---

## 2. Threads — Meta Threads API (Graph)

Threads is Meta's official write API, launched June 2024. It is **separate from the
Instagram Graph API**: different host (`graph.threads.net`), different OAuth, different
permissions. There is also a second host `graph.threads.com` — both answer on `v1.0`.

- **Base URL:** `https://graph.threads.net/v1.0` (also `https://graph.threads.com/v1.0`).
- **Docs:** https://developers.facebook.com/docs/threads
- **Post limits:** text max **500 characters**. A post with **more than 5 links fails**
  with `THREADS_API__LINK_LIMIT_EXCEEDED` (since 2025-12-22). Carousel up to **20 items**.
- **Rate limits (rolling 24-hour window, per profile):** **250 published posts**,
  **1,000 replies**, **100 deletes**. Check the live budget with
  `GET /{threads-user-id}/threads_publishing_limit` instead of counting locally.
- **No scheduling endpoint.** No `scheduled_at` — containers expire 24h after creation,
  so posts cannot be pre-created days ahead. Scheduling is a queue + cron (as now).
- **No edit endpoint.** Delete and repost is the only correction path.
- **No DM/message endpoints** in the official API.
- **No file upload.** Media must sit at a **publicly reachable URL** Meta can fetch;
  the API takes `image_url` / `video_url`, never file bytes.
- **App Review required:** `threads_content_publish` needs advanced access — until App
  Review grants it, an app can post only to its own account and its testers. Tech Provider
  Verification is also required for the publishing flow.

### 2.1 Auth — Threads OAuth

| Step | Route | Purpose |
|---|---|---|
| 1. Authorize | `https://threads.net/oauth/authorize` (or `https://threads.com/oauth/authorize`) | Redirect the user with `client_id`, `redirect_uri`, `scope`, `response_type=code`. Scopes below. |
| 2. Short-lived token | `POST https://graph.threads.net/oauth/access_token` | Exchange the code. Returns a **1-hour** token. Body: `client_id`, `client_secret`, `grant_type=authorization_code`, `redirect_uri`, `code`. |
| 3. Long-lived token | `GET https://graph.threads.net/access_token?grant_type=th_exchange_token&client_secret=...&access_token=<short-lived>` | Upgrade to a **60-day** long-lived token. |
| 4. Refresh | `GET https://graph.threads.net/refresh_access_token?grant_type=th_refresh_token&access_token=<long-lived>` | Refresh a long-lived token. Only works once the token is **at least 24 hours old**; a token not refreshed **within 60 days is gone** — the user reconnects. |

Scopes:

| Scope | Covers |
|---|---|
| `threads_basic` | **Required for every Threads endpoint.** Profile fields + reading your own posts. |
| `threads_content_publish` | Create and publish posts (containers + publish). |
| `threads_manage_insights` | GET calls on insights endpoints. |
| `threads_manage_replies` | POST calls on reply endpoints (hide/unhide, approve/ignore). |
| `threads_read_replies` | GET calls on reply endpoints. |
| `threads_delete` | Delete a post. |
| `threads_share_to_instagram` | Share to Instagram. |

### 2.2 Publishing — the two-step container flow

Every post is two calls. (The Threads connector's `publish-post` does the same thing
behind its approval prompt.)

**Step 1 — create the media container:**

```
POST https://graph.threads.net/v1.0/{threads-user-id}/threads
```

| Field | Notes |
|---|---|
| `media_type` | Required. `TEXT`, `IMAGE`, `VIDEO`, or `CAROUSEL`. |
| `text` | Post text, ≤500 chars. |
| `image_url` | Required for `IMAGE`. Public URL Meta can fetch. |
| `video_url` | Required for `VIDEO`. Public URL Meta can fetch. |
| `children` | Required for `CAROUSEL`: comma-separated list of child container IDs, each created first with `is_carousel_item=true`. |
| `is_carousel_item` | `true` when creating a child container for a carousel. |
| `reply_to_id` | The post ID being replied to — this is how a reply is made. |
| `link_attachment` | Link attachment URL. |
| `topic_tag` | Topic tag (hashtag). |
| `alt_text` | Alt text for the media. |
| `location` | Location tag. |
| `reply_control` | Who can reply: `everyone`, `accounts_you_follow`, `mentioned_only`, `parent_post_author_only`, `followers_only`. |

Returns a container ID. **Step 1b — poll the container** (media only; text-only posts
need no polling):

```
GET https://graph.threads.net/v1.0/{container-id}?fields=status,error_message
```

`status` is `IN_PROGRESS`, `FINISHED`, `ERROR`, `EXPIRED`, or `PUBLISHED`. Only publish
on `FINISHED`. Meta recommends waiting **on average 30 seconds** before publishing.
Poll at most once a minute for no more than five minutes. A container that is never
published flips to `EXPIRED` after **24 hours** and cannot be recovered.

**Step 2 — publish the container:**

```
POST https://graph.threads.net/v1.0/{threads-user-id}/threads_publish
Body: {"creation_id": "<container-id>"}
```

Returns the published post ID. `/me/threads` and `/me/threads_publish` work the same
way with the token's own user instead of an explicit user ID.

**Threads (multi-part):** a thread is a chain of replies — post part 1 standalone, then
each later part is a container with `reply_to_id` = the previous part's post ID, then
publish it. That is exactly what `post-thread.py` does through the connector
(`--reply-to-post-fbid`). Note one guide's caveat: the publishing endpoint does not have
a dedicated "create a thread" call — threading is built from `reply_to_id` replies.

### 2.3 Reading — posts, profiles, conversations

| Route | Method | Scope | Purpose |
|---|---|---|---|
| `/{threads-user-id}` | GET | `threads_basic` | User profile fields. |
| `/me` | GET | `threads_basic` | The token owner's profile. |
| `/{threads-user-id}/threads` | GET | `threads_basic` | List the user's threads (fields: `id`, `media_product_type`, `media_type`, `media_url`, `text`, `timestamp`, `permalink`, `username`, …; `limit` up to 25+). |
| `/{threads-media-id}` | GET | `threads_basic` | One published post's fields. |
| `/{threads-media-id}` | DELETE | `threads_delete` | Delete a post (≤100/24h). |
| `/{threads-media-id}/replies` | GET | `threads_read_replies` | Top-level replies to a post. |
| `/{threads-media-id}/conversation` | GET | `threads_read_replies` | The full conversation, including nested replies. |
| `/{threads-media-id}/insights` | GET | `threads_manage_insights` | Post metrics: `metric=views,likes,replies,reposts,quotes`. |
| `/{threads-user-id}/threads_insights` | GET | `threads_manage_insights` | Account insights + follower demographics. (`/me/threads_insights` also works.) |
| `/{threads-user-id}/threads_publishing_limit` | GET | `threads_basic` | Remaining publishing quota (`quota_usage`, `reply_quota_usage`, `config`). |

### 2.4 Reply management

| Route | Method | Scope | Purpose |
|---|---|---|---|
| `/{threads-media-id}/replies` | GET | `threads_read_replies` | List replies to a post. |
| `/{threads-media-id}/pending_replies` | GET | `threads_read_replies` | Replies waiting for approval (post has reply approvals on). |
| `/{threads-reply-id}/manage_pending_reply` | POST | `threads_manage_replies` | Approve or ignore a pending reply (`action=approve` / `ignore`). |
| `/{threads-reply-id}/manage_reply` | POST | `threads_manage_replies` | Hide or unhide a reply (`hide` / `unhide`). |

### 2.5 What the current Threads poster uses (and does not use)

The poster goes through the **Threads connector** (`/opt/hatch/bin/threads-cli`), not
the Meta API directly. The connector is linked through Meta Accounts Center and every
publish raises its own approval prompt.

**Connector commands (from `threads-cli --help` + the connector doc):**

| Command | Purpose |
|---|---|
| `accounts` | List linked Threads accounts (numeric FBIDs). |
| `connect-url` / `disconnect-url` | Link / unlink an account via Meta Accounts Center. |
| `profile` | The user's own Threads profile. |
| `activity-feed` | Activity notifications (`--first`, `--category-filter`). |
| `liked-media` / `saved-posts` | Posts the user liked / saved. |
| `insights-overview` | Account insights (`--start-date`, `--end-date`, `--sections`). |
| `post-insights` | Insights for one post (`--post-id`). |
| `top-posts` | Most-viewed / most-liked posts in a date range. |
| `user-profile` | A profile by numeric user FBID (`--user-id`). |
| `profile-threads` / `profile-replies` / `profile-media` | A user's posts / replies / media. |
| `followers` / `following` | A user's follower / following lists. |
| `post` | One post by `--url` or `--post-id`. |
| `fetch-post-comments` | Comments for up to 10 posts (`--post-ids`). |
| `fetch-post-likers` | Likers for posts (`--post-ids`, `--reactor-id`). |
| `feedback-hub-overview` / `feedback-hub-tab` | Like / repost / quote / highlight counts and accounts for a post. |
| `trends` | Trending topics. |
| `search` | Search Threads by keyword (`--query`, `--recent`, `--trend-fbid`). |
| `feed` | For You / Following feed (`--variant for_you|following`). |
| `publish-post` | **Publish one post.** Hidden from the command list but works. `--account-id`, `--text` (≤500 chars), 1–20 `--media-item` JSON objects (`file`, optional `cover`, optional `alt_text`), `--reply-to-post-fbid`, `--reply-control`, `--enable-reply-approvals`. Success prints `{"post_id":"<id>"}`. One fresh approval per publish; zero retries. |
| `hide-reply` | Hide / unhide a reply (`--post-id`, `--action hide|unhide`). |
| `pending-replies` | Replies waiting for approval on one of the user's posts. |
| `review-pending-reply` | Approve / ignore a pending reply (`--action approve|ignore`). |
| `dear-algo-whisper` | Feed-ranking feedback (`--message`). |

**What the poster uses:** `publish-post` only (text + optional media item, `--reply-to-post-fbid`
for thread parts). **Does NOT use (available):** carousels (2–20 media items in one post),
`--reply-control`, `--enable-reply-approvals`, any read/insight command (no post
verification read-back, no insights check after posting), `hide-reply`,
`review-pending-reply`, `trends`/`search` (no trend-aware posting).

**Connector rate limits (from the connector doc):** Threads enforces strict rate limits
and scraping protection. A **429 is final and is never retried.** `Threads Request Rate
Limit Reached` = scraping protection — stop calling Threads. `Threads Write Rate Limit
Reached` = the daily limit for that kind of write (publishing, hiding, approving each have
their own limit) — stop only that kind of write until the next day.

### 2.6 Sources (Threads)

- https://developers.facebook.com/docs/threads (official docs)
- https://social-api.ai/blog/threads-api-publishing-posts-developer-guide
- https://www.upload-post.com/threads-api/
- https://postproxy.dev/blog/how-to-post-to-threads-via-api/
- https://posteverywhere.ai/blog/post-to-threads-api
- https://bundle.social/blog/threads-posting-api
- https://www.outstand.so/blog/threads-api
- https://lionfans.cc/en/blog/threads-api-guide
- https://skopx.com/resources/threads-api-posting-guide
- https://github.com/heianxing/cloudless.gr/blob/HEAD/.claude/skills/threads-api/SKILL.md
  (complete endpoint reference, base `https://graph.threads.net/v1.0`)
- `/opt/hatch/connectors/threads/CONNECTOR.md` + `references/read-commands.md` (connector)

---

## 3. Account vs no-account — which routes need what

| Service | Route group | Needs an account? |
|---|---|---|
| Bluesky | `com.atproto.server.createSession` + all `com.atproto.repo.*` writes | **Yes** — app password or OAuth. No review, no app registration. |
| Bluesky | `app.bsky.*` reads via `https://public.api.bsky.app` | **No** — public, no auth. (Personalised timeline / notifications need auth.) |
| Bluesky | `app.bsky.video.*` upload | **Yes** — auth. |
| Threads | Every `graph.threads.net` endpoint | **Yes** — OAuth token + scopes. Publishing also needs App Review (`threads_content_publish`, advanced access) and Tech Provider Verification. |
| Threads | `threads-cli` connector commands | **Yes** — account linked through Meta Accounts Center; every publish needs a fresh approval. |

## 4. Gaps the posters could use next (no decision made — Gary's call)

- **Bluesky:** image embeds (`app.bsky.embed.images`, up to 4 images — the queue already
  has media files, currently Threads-only), video (`app.bsky.video.*`), reply threads
  (`reply.root`/`reply.parent`), quotes, `tags`/`langs`, `deleteRecord` (fix a bad post),
  read-back verification (`getPostThread` / `getPosts` after publishing),
  `refreshSession` instead of logging in fresh each run.
- **Threads:** carousels (up to 20 media items), `--reply-control`, insights read-back
  after posting (`post-insights` / `threads_insights`), `threads_publishing_limit`
  quota checks, `trends`/`search` for trend-aware posting.
- **Both:** neither API schedules posts — the queue + cron pattern stays. Neither API
  has an edit endpoint — Threads is delete-and-repost, Bluesky is `putRecord`/
  `deleteRecord` + repost.

## 5. How to verify a route exists (before using it)

- Bluesky: call the read endpoint on `https://public.api.bsky.app/xrpc/<method>` with no
  auth (reads), or check the lexicon in https://github.com/bluesky-social/atproto.
- Threads: the endpoint list in https://developers.facebook.com/docs/threads is the
  authority; a 4xx with an OAuth error means the scope/app-review is missing, not that
  the route does not exist.
