# Facebook Page Posts & Comments Scraper — free, no login, no cookies

**Free Facebook page posts & comments scraper.** Paste a Page URL or handle — takes
N recent public posts (`maxPosts`) and scrapes each post's comments and replies.
Also groups, profiles, and single post URLs. Optional **date range**, **comment
cap**, and **posts-only** modes. No login. **$0 developer fee; only Apify platform
usage.**

> Looking for a **free Facebook page posts & comments scraper**? Paste a Page URL,
> set `maxPosts` (or a date window), export posts + comments as JSON/CSV. No login.
> **$0 developer fee; only Apify platform usage.**

## What can this free Facebook page posts & comments scraper do?

- **Scrape comments and replies** from public **Pages**, **user profiles**, **Groups**,
  or a single **post URL**
- **Date filter** — calendar `afterDate` / `beforeDate` with optional `dateTimezone`
  (`UTC`, `+3`, `Africa/Khartoum`, …); walks the feed until the window ends
  (`maxPosts` ignored while filtering by date)
- **Cap comments per post** — `maxComments` stops top-level pagination at N (heavy
  threads are truncated, not skipped)
- **Posts only** — discover posts (with `created_time`) without scraping comments
- **No login** — no cookies, no account, no session to maintain
- **Paginate comments to exhaustion** (or until `maxComments`), not just the first page
- **Stream results** to the dataset as each post finishes
- **Export** to CSV, Excel, JSON, or pull via Apify API
- **Schedule** runs, monitor failures, and integrate with Zapier/Make/n8n
- **High comment coverage** on public threads (see [coverage](#comment-coverage-and-rate-limits))

## Supported targets

Paste the link straight from your browser or Facebook's share sheet — no editing needed.
Any Facebook host (`www.`, `m.`, `web.`, `mbasic.`, `fb.com`), a profile tab (`/about`,
`/photos`), and tracking parameters (`?mibextid=…`) are all handled, as is a bare handle.

| Target | Example `pageOrUrl` | Notes |
|--------|---------------------|-------|
| **Page** | `ronaldo`, `https://www.facebook.com/ronaldo` | Public Page timeline |
| **Profile** | `mohamed.ayuop.5`, `https://www.facebook.com/profile.php?id=61561308996622`, `https://www.facebook.com/people/Some-Name/61561308996622/`, or a bare numeric id | Only if the profile is visible logged out |
| **Group** | `https://www.facebook.com/groups/2693577247594660` | Public groups only |
| **Post** | `https://www.facebook.com/.../posts/...`, `/permalink/...`, `/reel/...`, `?story_fbid=...`, or a `pfbid…` share link | Scrapes that thread only (`maxPosts` / date filter ignored). Opaque `pfbid` links are resolved to the post via its permalink page |

## Sample output

One dataset item per post (`schema_version` **2**):

```json
{
  "schema_version": 3,
  "post": {
    "post_id": "1234567890",
    "text": "Check out our new product launch!",
    "permalink": "https://www.facebook.com/...",
    "comment_count": 74,
    "created_time": 1690000000,
    "reaction_count": 120,
    "share_count": 8,
    "reactions": [
      {"type": "like", "count": 90, "name": "Like"},
      {"type": "love", "count": 25, "name": "Love"},
      {"type": "care", "count": 5, "name": "Care"}
    ]
  },
  "tops": 42,
  "replies": 29,
  "total_scraped": 71,
  "coverage": 0.96,
  "nested_replies_on": true,
  "comments": [
    {
      "comment_id": "...",
      "author": "Jane Doe",
      "text": "Love this!",
      "reaction_count": 4,
      "reactions": [
        {"type": "like", "count": 3, "name": null},
        {"type": "love", "count": 1, "name": null}
      ],
      "created_time": 1690000000,
      "media": null,
      "replies": [
        {"comment_id": "...", "author": "Brand Page", "text": "Thank you!"}
      ]
    }
  ]
}
```

## What data can you extract from Facebook?

| Field | Description |
|-------|-------------|
| `post.post_id`, `text`, `permalink` | Post identity and content |
| `post.created_time` | Post publish time (unix seconds UTC) |
| `post.comment_count` | Facebook's reported total |
| `post.reaction_count` | Total reactions on the post |
| `post.reactions` | Per-type breakdown (`like` / `love` / `care` / `haha` / `wow` / `sad` / `angry`) with counts |
| `post.share_count` | Share count on the post |
| `tops`, `replies`, `total_scraped` | Counts actually returned |
| `coverage` | Fraction of `comment_count` actually returned |
| `nested_replies_on` | `true` if nested replies were fetched; `false` for tops-only / skipped replies |
| `author` | Commenter's display name |
| `text` | Comment body |
| `reaction_count` | Total reactions on the comment/reply |
| `reactions` | Per-type breakdown on the comment/reply |
| `created_time` | Comment/reply unix timestamp |
| `media` | Attached photo/sticker, or `null` |
| `replies` | One level of nested replies (when `nested_replies_on` is true) |

## Use cases

- **Brand monitoring** — track what people say on your Facebook page or public group
- **Sentiment analysis** — export comment text for NLP pipelines
- **Competitive research** — scrape public competitor page/group threads
- **Market research** — collect audience reactions on viral posts
- **LLM training data** — public comment threads as structured text
- **Date-bounded exports** — scrape only posts in a calendar window

## How to use this free Facebook page posts & comments scraper on Apify

### Quick start

1. Click **Try for free** / **Run**
2. Set **Page, profile, group, or post URL** — e.g. `ronaldo`, a profile handle, a
   `/groups/...` link, or a full post permalink
3. Leave the defaults (residential proxy on) or set `maxPosts` / `maxComments` for a page feed —
   or pick **Posts on or after** / **Posts before** for a date window
4. Start the run — results stream into the **Dataset** tab as each post finishes

Default input:

```json
{
  "pageOrUrl": "ronaldo",
  "maxPosts": 1,
  "maxComments": 100,
  "profile": "tops_only"
}
```

Date-window example (all posts on 2026-07-31 in UTC+3; `maxPosts` ignored):

```json
{
  "pageOrUrl": "yourbrand",
  "afterDate": "2026-07-31",
  "beforeDate": "2026-08-01",
  "dateTimezone": "+3",
  "profile": "tops_only"
}
```

That's it. No credential step.

**How long a run takes depends entirely on the target.** Comments are paginated to
exhaustion (unless you set `maxComments`) — there is no artificial page cap — so a post
with tens of comments finishes quickly and a post with thousands takes much longer and
uses proportionally more proxy traffic. Run `maxPosts: 1` first, look at the run's
duration and proxy usage on your own target page, then scale up from a number you have
actually measured.

### Task examples

Copy any of these into a new **Task** on this Actor's page (Tasks → Create task):

| Task | Input | Best for |
|------|-------|----------|
| Quick test — 1 page post + comments | `{"pageOrUrl": "ronaldo", "maxPosts": 1, "maxComments": 100, "profile": "tops_only"}` | Verify the scraper works |
| Scrape last 5 page posts + comments | `{"pageOrUrl": "yourbrand", "maxPosts": 5}` | Daily brand monitoring |
| Posts in a date window | `{"pageOrUrl": "yourbrand", "afterDate": "2026-07-31", "beforeDate": "2026-08-01", "dateTimezone": "+3", "profile": "tops_only"}` | Day / range export (local TZ) |
| Cap heavy threads | `{"pageOrUrl": "yourbrand", "maxPosts": 5, "maxComments": 500}` | Bound cost on viral posts |
| Posts only (no comments) | `{"pageOrUrl": "yourbrand", "afterDate": "2026-07-01", "beforeDate": "2026-08-01", "dateTimezone": "+3", "postsOnly": true}` | Feed inventory / timestamps |
| Scrape public group posts + comments | `{"pageOrUrl": "https://www.facebook.com/groups/123...", "maxPosts": 3}` | Group discussion threads |
| Public profile | `{"pageOrUrl": "some.public.profile", "maxPosts": 1}` | Profile posts (if visible logged out) |
| Scrape one Facebook post comments thread | `{"pageOrUrl": "https://www.facebook.com/.../posts/..."}` | Deep-dive one thread |
| Export 10 page posts + comments for sentiment | `{"pageOrUrl": "competitor", "maxPosts": 10, "profile": "default"}` | Research export |

Pre-made configs live in [`.actor/task-examples/`](.actor/task-examples/) (when developing
from `apify/`) and [`.actor/task-examples/`](../.actor/task-examples/) (repo-root actor
definition) — same files, kept in sync.

## Is this Facebook page posts & comments scraper free?

**Yes — free.** **$0 developer fee; only Apify platform usage.** No rental and no
pay-per-result markup from the developer.

You only pay **Apify platform usage** — the infrastructure cost of running on Apify:

| Cost component | What it is | Driven by |
|----------------|------------|-----------|
| **Compute units (CUs)** | CPU + RAM while the Actor runs | How long the run takes, i.e. how many comments it paginates |
| **Residential proxy** | Traffic through Apify residential IPs (on by default) | GB transferred — usually the dominant cost here |
| **Dataset storage** | Storing exported results | Negligible for most jobs |

We deliberately don't quote a per-post price, because it isn't ours to quote: it depends
on Apify's current rates, your plan, and above all how many comments the posts you target
actually have. Run `maxPosts: 1` on **your** page, read the compute and proxy usage Apify
reports for that run, and scale from that figure. Current rates are on
[Apify pricing](https://apify.com/pricing); Apify's free plan includes monthly credits
that cover small runs.

### Want zero Apify fees? Run it locally for free

This scraper is **open source (MIT)**. Clone the repo and run on your own machine —
no Apify account needed, no platform charges:

```bash
git clone https://github.com/bsho5/fbgql.git
cd fbgql
./run.sh doctor              # smoke test — checks the API still answers (no login)
./run.sh ronaldo 1          # scrape 1 post, anonymous, free
```

Or install as a library/CLI:

```bash
pip install -e .
fbgql scrape --page ronaldo --posts 3 --out out/result.json

# Date window (max posts ignored); tops only; cap tops at 500
fbgql scrape --page yourbrand --after 2026-07-30 --before 2026-07-31 \
  --profile tops_only --max-comments 500 --out out/day.json
```

You bring your own IP (or your own proxy). The Apify Actor is a thin hosted wrapper
around the same [`fbgql`](https://github.com/bsho5/fbgql) engine — same output, your
infrastructure.

## Input

| Field | Required | Notes |
|-------|----------|-------|
| `pageOrUrl` | yes | Page/profile handle, group URL, numeric id, or a single post URL |
| `maxPosts` | no | Max recent posts when scraping a feed (default 1). **Ignored** when `afterDate`/`beforeDate` is set, and for post URLs |
| `afterDate` | no | Calendar date (`YYYY-MM-DD`) — keep posts on or after midnight in `dateTimezone`. **Required** if you use a date filter |
| `beforeDate` | no | Calendar date — keep posts strictly before midnight in `dateTimezone` (exclusive). Pair with `afterDate` for a day/range |
| `dateTimezone` | no | Timezone for calendar dates: `UTC` (default), `+3`, `+03:00`, or IANA (`Africa/Khartoum`) |
| `postsOnly` | no | Discover posts only (includes `created_time`); skip comment/reply scraping |
| `maxComments` | no | Stop after this many **top-level** comments per post; truncate heavy threads |
| `proxyConfiguration` | no | Apify residential proxy, sticky per run (on by default) — **set country** if runs return 0 posts |
| `profile` | no | `default` (recommended), `tops_only`, `full_replies` |
| `engine` | no | `async` (default, streaming) or `threads` |
| `workers`, `replyFbCap`, `minIntervalSec`, `megaThreshold` | no | Advanced tuning |

## What it can and cannot reach

Because the Actor is logged out, it sees exactly what any anonymous visitor sees:

- ✅ Public **Page** posts, comments, and one level of replies
- ✅ Public **profile** posts (when Facebook embeds the profile id in logged-out HTML)
- ✅ Public **Group** posts and comments
- ✅ Individual public **post** URLs
- ❌ Private groups and private / login-gated profiles
- ❌ Age-gated or geo-restricted posts

## Troubleshooting

| Symptom | Likely cause | What to try |
|---------|--------------|-------------|
| **0 posts** / run fails with “No posts found” | Proxy IP/country blocked or empty feed from that exit | In **Proxy**, set **Apify Proxy country** to the audience’s country (or yours). Retry another country. Keep **RESIDENTIAL** on. |
| Works locally, fails on Apify | Different IP path (home vs residential exit) | Same as above — match proxy country; do not turn proxy off on the platform long-term |
| `Could not resolve numeric id` | Target is login-gated from this IP (URL shapes themselves are handled — see Supported targets) | Switch **proxy country**, or pass a direct **post URL**; or use the [`fbgql` CLI](https://github.com/bsho5/fbgql) with cookies locally |
| Login wall / `SessionInvalid` | Target private, or IP flagged | Rotate residential proxy / country; confirm the target is public in a private browser window |
| Fewer comments than Facebook shows | Deleted/hidden/nested comments, or `maxComments` cap | Normal — check per-post `coverage`; raise or clear `maxComments` if you capped |
| Date filter needs `afterDate` | Only `beforeDate` was set | Always set **Posts on or after** when using a date window |
| Very slow / expensive run | Huge comment threads or a wide date window | Start with `maxPosts: 1`, use `tops_only`, set `maxComments`, raise `minIntervalSec` |

### Proxy tips (most common fix)

1. Leave **Use Apify Proxy** + **RESIDENTIAL** enabled.
2. Set **Country** to where the Page/group’s audience (or you) sits — wrong exits often return empty feeds even when the target is public.
3. Re-run with `maxPosts: 1` after changing country before scaling up.

## Comment coverage and rate limits

Coverage is bounded by Facebook's rate limits, not by an artificial cap in the Actor
(unless you set `maxComments`). Facebook's `comment_count` also includes deleted, hidden,
or deeply nested comments the API will not return, so `coverage` below 1.0 is normal. Our
own logged-out test runs on public pages measured **87–94%** (`coverage` is reported per
post in every dataset item, so you can check it against your own targets rather than take
ours). If you hit blocks, raise `minIntervalSec`, lower `workers`, or use `tops_only`.

## Avoiding blocks

- Keep the residential proxy on — the IP is the main reliability lever
- Prefer fewer `workers` and a higher `minIntervalSec` over raw speed
- Cap expensive threads with `maxComments` when you do not need full coverage
- A blocked run costs only a retry; there is no account to checkpoint

## FAQ

**Is this a free Facebook comments scraper on Apify?**
Yes — free. $0 developer fee; only Apify platform usage (compute + proxy).

**Is this a free Facebook scraper (posts + comments)?**
Yes for public content — each dataset item includes the post and its comment thread.
Free. $0 developer fee; only Apify platform usage.

**Do I need a Facebook account?**
No. The Actor scrapes public content logged out and never asks for credentials.

**Why don't you accept cookies?**
A public Actor should never ask users to paste a Facebook session. Coverage on public
targets is high without one (87–94% in our page test runs). For login-gated content, use
the [`fbgql` CLI/library](https://github.com/bsho5/fbgql) locally with your own session.

**Can I scrape a single post?**
Yes — pass the post URL as `pageOrUrl`.

**Can I scrape a public group?**
Yes — pass the full `https://www.facebook.com/groups/...` URL (or the numeric group id).

**Can I filter by date?**
Yes — set `afterDate` and optionally `beforeDate` (calendar pickers). Use `dateTimezone`
(`UTC`, `+3`, `Africa/Khartoum`, …) so midnight matches your local day. `maxPosts` is
ignored; the feed is walked until the window ends. `afterDate` is required for a date
filter.

**What does `nested_replies_on` mean?**
`true` when nested replies were fetched for that post; `false` for tops-only /
`postsOnly` / errors where replies were not scraped.

**Why fewer comments than Facebook shows?**
Facebook's count includes deleted/hidden/deeply nested comments the API won't return.
Also check whether you set `maxComments`.

**Why did a run fail with a login wall or “No posts found”?**
The target isn't publicly visible from that IP, or the proxy country is a bad fit. Change
the residential proxy country and retry — see [Troubleshooting](#troubleshooting).

**Can I run this completely free?**
On Apify, platform usage always applies (though the free plan covers small runs). For
**zero platform cost**, clone [github.com/bsho5/fbgql](https://github.com/bsho5/fbgql)
and run locally.

## Legal and data protection

Facebook comments contain personal data (author names). Automated scraping may breach
Facebook's Terms of Service. You are responsible for having a lawful basis for the
data you collect. See [LEGAL.md](https://github.com/bsho5/fbgql/blob/master/LEGAL.md).
