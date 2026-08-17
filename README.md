# fbgql

Clean-room Facebook **GraphQL** post & comment scraper — usable as a **library**, a
**CLI**, and a **public Apify actor**. One engine, many callers.

> Working name `fbgql` — rename before publishing. [MIT license](LICENSE); compliance
> notes in [`LEGAL.md`](LEGAL.md).

## What it does

Given a Facebook **Page**, **public profile**, **public Group**, or a single **post URL**,
it fetches recent posts and paginates their comments + one level of replies via the
private GraphQL API, using the proven coverage policy:

- permalink `feedLocation` (`POST_PERMALINK_DIALOG`)
- `1675012` empty-page retry with backoff
- no artificial page cap
- bin-packed multi-worker runner with a configurable reply cap

## Two access modes — anonymous is the default

| Mode | How | Reach |
|---|---|---|
| **anonymous** (default) | pass no account — actor `0`, no cookies, no `fb_dtsg` | public content only |
| **authenticated** | supply cookies (`--cookies` / `Account(cookies=…)`) | everything the account can see |

Facebook's GraphQL endpoint answers public timeline, comment, and reply queries to a
logged-out actor, so page discovery, full comment pagination, and replies all work with
no account at all — no browser, no login, no token bootstrap:

```bash
fbgql scrape --page ronaldo --posts 3           # anonymous; nothing to set up
fbgql scrape --page ronaldo --cookies c.json    # authenticated, for gated content
```

Reference runs on the same page and post count: **93.5% weighted coverage anonymous**
(20 posts, 2 817 comments, 0 errors) against a documented **77.1% authenticated**
baseline. The two were measured on different days against different posts, so read that
as "anonymous is in the same class or better on public pages", not a controlled result.

Anonymous is the default because it removes the operational bottleneck: there is no
`c_user` to checkpoint, so a block costs a retry instead of a session, and scale depends
on IP diversity rather than on a supply of healthy accounts.

**Supplying an account whose cookies lack `c_user` is still a hard failure** — that is a
dead session, not an anonymous one, and it must not silently degrade. Anonymous applies
when you pass *no* account (or set `anonymous=True` explicitly).

Login-gated, age-gated, and geo-restricted content and private groups/profiles stay
unreachable anonymously — use authenticated mode for those. Public groups use a separate
GraphQL feed query (`GroupsCometFeedRegularStoriesPaginationQuery`). If anonymous handle
resolution fails for a profile, try a residential proxy in a matching country or pass a
post URL.

## Target links

`--page` / `ScrapeJob(page=…)` accepts a bare handle, a numeric id, or any link users
actually paste — every Facebook host (`www.`, `m.`, `web.`, `mbasic.`, `fb.com`),
`profile.php?id=…`, `/people/<slug>/<id>/`, a profile tab (`/ronaldo/about`), and
tracking parameters. Extracting the id yourself is never required.

Single posts go to `--post-url` / `post_url=…` and accept `/posts/<id>`, `/permalink/<id>`,
`/reel/<id>`, `?story_fbid=<id>`, and opaque `pfbid…` share links — the last are resolved
to the numeric post id from the permalink page, since the `feedback:<id>` query needs a
numeric id. Callers with one input field (the Apify actor, a web form) can route with
`fbgql.is_post_url(value)` instead of duplicating that logic.

Measured, mechanism, and limits: [`reports/ANONYMOUS_ACCESS_SOLVED_2026-07-28.md`](reports/ANONYMOUS_ACCESS_SOLVED_2026-07-28.md).

## Two engines (pick per job)

| `engine` | Backend | When |
|----------|---------|------|
| `"threads"` (default) | `ThreadPoolExecutor` + `requests` | Proven, reproduces measured coverage |
| `"async"` | `asyncio` + `httpx` | Streaming, native fit for the Apify actor |

Both share all decision logic (payloads, parsing, retry policy, bin-packing); only
the I/O loop differs.

## Quickstart (one command)

`run.sh` does everything — picks Python 3.11+, creates the venv, installs, then scrapes.
The default path is anonymous, so it needs **no browser and no login**:

```bash
./run.sh doctor           # smoke test — resolves the page + all 3 doc_ids, no scraping
./run.sh ronaldo 1       # smallest real scrape, logged out

./run.sh                  # scrape the default page (PAGE/POSTS defaults), logged out
./run.sh <page> 30        # page + post count

AUTH=1 ./run.sh           # authenticated instead (mints cookies if needed)
./run.sh login            # just mint/refresh cookies
```

Override via env: `PAGE=… POSTS=… PROFILE=… ENGINE=… OUT=… PROXY=… ./run.sh`.
Only `AUTH=1`, `login`, and `capture` need a display for the browser step; the default
anonymous path runs fine in containers.

**Budget the run time.** There is no artificial page cap — comments are paginated to
exhaustion (unless you set `--max-comments`) — so wall-clock scales with how many comments
the target has, not with post count alone. Don't extrapolate from someone else's page;
measure your own. One data point for calibration: a single `facebook` (Meta's own page)
post, logged out, returned **861 comments in 295 s** on 2026-07-28 — that page averages
~1 000 comments per post, so it is close to a worst case (avoid for demos/quick tests; prefer a quieter page like `ronaldo`). Use `./run.sh doctor` when you
only want to confirm the plumbing.

With `--after` / `--before` (UTC `YYYY-MM-DD` or unix seconds), `--posts` is **ignored**
and the feed is walked until the date window ends (`--after` is required). Use
`--posts-only` to discover posts without scraping comments, and `--max-comments N` to stop
top-level pagination at N per post.

Note that `tops_only` is **not** a speed knob: it sets `workers=1`, so it serialises posts
and can be *slower* than `default` on a multi-post run despite skipping replies. To trade
coverage for time, keep the `default` profile and use `--reply-cap` (or lower `--posts` /
`--max-comments`).

## Install

```bash
pip install -e .            # core (library + CLI)
pip install -e ".[dev]"     # + ruff, pytest
pip install -e ".[mint]"    # + selenium, for the interactive login helper
pip install -e ".[apify]"   # + apify SDK
```

## Library

```python
from fbgql import Scraper, ScrapeJob, Account, Profile

# Anonymous (default) — no accounts needed
job = ScrapeJob(
    page="ronaldo",
    max_posts=3,
    profile=Profile.DEFAULT,     # DEFAULT | TOPS_ONLY | FULL_REPLIES
    engine="threads",            # or "async"
    # Optional: after_time / before_time (unix UTC), max_comments, posts_only
)

# Authenticated — supply a session for login-gated content
job = ScrapeJob(
    page="ronaldo",
    max_posts=3,
    accounts=[Account(cookies=cookies_dict, proxy="http://user:pass@host:port")],
)

result = Scraper().run(job)
result.to_json("out/result.json")

# streaming (threads):
for post in Scraper().stream(job):
    ...
```

The engine **never logs in** — anonymous runs as actor `0`, and authenticated runs
consume cookies you supply. With cookies, `fb_dtsg` is derived at runtime; a dead
session raises `SessionInvalid` so a wrapper can alert a human to re-mint. See "Auth"
below.

## CLI

```bash
# Anonymous (default)
fbgql scrape --page ronaldo --posts 3 --profile default \
  --engine threads --out out/result.json

# Date window (max posts ignored) + tops only + comment cap
fbgql scrape --page ronaldo --after 2026-07-30 --before 2026-07-31 \
  --profile tops_only --max-comments 500 --out out/day.json

# Authenticated
fbgql scrape --page ronaldo --posts 3 --cookies cookies.json --out out/result.json

fbgql doctor --page ronaldo            # check doc_ids are still valid (logged out)
fbgql mint-session --out cookies.json   # interactive login (needs [mint] extra)
```

## Auth (how login works)

Most runs need none — anonymous is the default and requires no credentials at all.

When you do want authenticated reach, you never log in on a server. You mint cookies
**once** on a machine with a browser and a residential IP (`fbgql mint-session`), then
inject that `cookies.json` as a secret wherever you run — CLI, Docker, or VPS. The
scraper derives `fb_dtsg` from those cookies over plain HTTP (no browser at scrape time).

The **Apify actor takes no credentials at all** — it is anonymous-only by design, since a
public actor should never ask users to paste a Facebook session into its input.

## Consuming from a separate repo (backend wrapper)

```toml
# your wrapper's pyproject.toml
dependencies = ["fbgql @ git+https://github.com/bsho5/fbgql.git@v0.1.0"]
```

The monorepo layout (core + `apify/` actor) does not constrain consumers — pip
installs only `src/fbgql/`.

## Layout

```
src/fbgql/          core engine (library + CLI)
apify/              public Apify Store actor (thin adapter)
docker/             generic CLI image
tools/mint_session/ interactive login helper
examples/  tests/
```

## doc_id drift

Facebook rotates GraphQL `doc_id`s. They are treated as **config**, overridable via
`FBGQL_DOC_ID_*` env vars without a code release. `fbgql doctor` reports stale ones.
