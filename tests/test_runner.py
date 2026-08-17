from __future__ import annotations

import pytest

from fbgql import runner
from fbgql.models import Session

_SESSION = Session(cookies={"c_user": "111", "xs": "y"}, fb_dtsg="d", c_user="111")


class _FakeGet:
    def __init__(self, html):
        self.html = html
        self.urls: list[str] = []

    def get(self, url, cookies, proxy=None, headers=None):
        self.urls.append(url)
        return self.html


def test_numeric_page_passes_through():
    assert runner._resolve_page_id("100064", _SESSION, _FakeGet("")) == "100064"


def test_resolve_page_id_from_applink_meta():
    html = '<meta property="al:android:url" content="fb://page/?id=987654321" />'
    assert runner._resolve_page_id("ZainSudan", _SESSION, _FakeGet(html)) == "987654321"


def test_resolve_candidates_prefer_feed_owner_over_page_id():
    # The timeline query needs the feed-owner id (userID/profile, 100064…), NOT the
    # classic Page id from delegate_page (which returns an empty node). Both must be
    # offered as candidates, feed-owner first, so the query-probe tries the right one.
    html = '"userID":"100064", ... "delegate_page":{"id":"193805"} ... fb://page/193805'
    cands = runner._resolve_page_id_candidates("ZainSudan", _SESSION, _FakeGet(html))
    assert cands[0] == "100064"          # feed-owner id leads
    assert "193805" in cands             # page id still available as a fallback
    # Back-compat single-id accessor returns the best (feed-owner) candidate.
    assert runner._resolve_page_id("ZainSudan", _SESSION, _FakeGet(html)) == "100064"


def test_resolve_page_id_escaped_slashes():
    html = r'{"url":"fb:\/\/profile\/555000"}'
    assert runner._resolve_page_id("ZainSudan", _SESSION, _FakeGet(html)) == "555000"


def test_resolve_page_id_not_found_tries_about_then_raises():
    fake = _FakeGet("nothing useful here")
    with pytest.raises(ValueError, match="numeric id"):
        runner._resolve_page_id("ZainSudan", _SESSION, fake)
    assert any("/about" in u for u in fake.urls)  # fell back to /about


def test_classify_target_group_url():
    assert runner._classify_target(
        "https://www.facebook.com/groups/2693577247594660"
    ) == ("group", "2693577247594660")
    assert runner._classify_target("groups/2693577247594660") == ("group", "2693577247594660")
    assert runner._classify_target("ronaldo") == ("page", "ronaldo")
    assert runner._classify_target("mohamed.ayuop.5") == ("page", "mohamed.ayuop.5")


@pytest.mark.parametrize("url", [
    # The form Facebook serves for profiles with no vanity handle: the id is in the
    # query string, so a path-only reading resolves the script name "profile.php".
    "https://www.facebook.com/profile.php?id=61561308996622",
    "https://m.facebook.com/profile.php?id=61561308996622",
    "www.facebook.com/profile.php?id=61561308996622",
    "https://www.facebook.com/profile.php?id=61561308996622&sk=about",
    "https://www.facebook.com/profile.php?locale=en_GB&id=61561308996622",
    # Same identity, other shapes Facebook links to.
    "https://www.facebook.com/people/Jetour-South-Africa/61561308996622/",
    "https://www.facebook.com/pages/Jetour/61561308996622",
])
def test_classify_target_extracts_numeric_id_from_url(url):
    assert runner._classify_target(url) == ("page", "61561308996622")


@pytest.mark.parametrize("url,handle", [
    # A tab hanging off the profile must not be mistaken for the handle.
    ("https://www.facebook.com/ronaldo/about", "ronaldo"),
    ("https://www.facebook.com/ronaldo/photos", "ronaldo"),
    ("https://www.facebook.com/ronaldo/", "ronaldo"),
    ("https://web.facebook.com/ronaldo", "ronaldo"),
    ("https://mbasic.facebook.com/ronaldo", "ronaldo"),
    ("https://fb.com/ronaldo", "ronaldo"),
    ("facebook.com/ronaldo", "ronaldo"),
    ("https://www.facebook.com/ronaldo?mibextid=LQQJ4d", "ronaldo"),
    ("https://www.facebook.com/pg/ronaldo/posts", "ronaldo"),
    ("@ronaldo", "ronaldo"),
])
def test_classify_target_handles_url_variants(url, handle):
    assert runner._classify_target(url) == ("page", handle)


def test_classify_target_group_url_variants():
    assert runner._classify_target(
        "https://m.facebook.com/groups/2693577247594660/?sorting_setting=CHRONOLOGICAL"
    ) == ("group", "2693577247594660")
    assert runner._classify_target(
        "https://www.facebook.com/groups/?id=2693577247594660"
    ) == ("group", "2693577247594660")


def test_profile_php_url_needs_no_html_fetch():
    """The id is in the URL, so resolution must not hit the network at all."""
    fake = _FakeGet("should not be fetched")
    cands = runner._resolve_page_id_candidates(
        "https://www.facebook.com/profile.php?id=61561308996622", _SESSION, fake
    )
    assert cands == ["61561308996622"]
    assert fake.urls == []


def test_post_id_from_shared_permalink_is_the_post_not_the_profile():
    """``?story_fbid=pfbid…&id=<profile id>`` is the shape Facebook's share sheet emits.

    A bare-digit fallback matched too early grabs the trailing profile id and the run
    then scrapes an unrelated feedback target — silently, with 0 comments.
    """
    url = ("https://www.facebook.com/permalink.php?story_fbid=pfbid02bmcvB5TVUt"
           "caagWK1cevGJ3d3KxDoM5As&id=61561308996622")
    assert runner._post_id_from_url(url) == "pfbid02bmcvB5TVUtcaagWK1cevGJ3d3KxDoM5As"


@pytest.mark.parametrize("url,post_id", [
    ("https://www.facebook.com/ronaldo/posts/122216361518376966", "122216361518376966"),
    ("https://www.facebook.com/permalink.php?story_fbid=122216361518376966&id=615613089",
     "122216361518376966"),
    ("https://www.facebook.com/reel/1655075679339828/", "1655075679339828"),
    ("https://www.facebook.com/ronaldo/videos/1234567890", "1234567890"),
    ("https://www.facebook.com/photo/?fbid=122216361518376966&set=a.1", "122216361518376966"),
])
def test_post_id_from_numeric_urls(url, post_id):
    assert runner._post_id_from_url(url) == post_id


def test_resolve_opaque_post_id_from_permalink_html():
    html = '{"top_level_post_id":"122217064718376966","post_id":"122217064718376966"}'
    fake = _FakeGet(html)
    url = "https://www.facebook.com/permalink.php?story_fbid=pfbid0xyz&id=615613089"
    assert runner._resolve_opaque_post_id(url, _SESSION, fake) == "122217064718376966"
    assert fake.urls == [url]  # the full URL, query intact — it identifies the post


def test_resolve_opaque_post_id_raises_with_actionable_message():
    with pytest.raises(ValueError, match="numeric permalink"):
        runner._resolve_opaque_post_id(
            "https://www.facebook.com/share/p/1AbCdEf/", _SESSION, _FakeGet("login wall")
        )


def test_candidate_html_urls_keep_id_query():
    """A non-numeric ``?id=`` still needs the query kept, or the URL identifies nobody."""
    urls = runner._candidate_html_urls(
        "https://www.facebook.com/profile.php?id=pfbid0xyz", "page", "pfbid0xyz"
    )
    assert urls[0] == "https://www.facebook.com/profile.php?id=pfbid0xyz"


def test_resolve_group_candidates_from_group_html():
    html = '"groupID":"2693577247594660","name":"Test Group"'
    fake = _FakeGet(html)
    cands = runner._resolve_page_id_candidates(
        "https://www.facebook.com/groups/AlzeriAlsudani", _SESSION, fake
    )
    assert cands == ["2693577247594660"]
    assert any("/groups/AlzeriAlsudani" in u for u in fake.urls)


def test_numeric_group_url_skips_html():
    fake = _FakeGet("should not be fetched")
    cands = runner._resolve_page_id_candidates(
        "https://www.facebook.com/groups/2693577247594660", _SESSION, fake
    )
    assert cands == ["2693577247594660"]
    assert fake.urls == []


def test_usable_posts_filters_empty_shells():
    from fbgql.models import Post

    posts = [
        Post(post_id="1", feedback_id=None, text="", permalink=None, comment_count=0),
        Post(post_id="2", feedback_id="fid", text="hi", permalink=None, comment_count=1),
    ]
    usable = runner._usable_posts(posts)
    assert [p.post_id for p in usable] == ["2"]


def test_date_window_ignores_max_posts_cap():
    from fbgql.models import Post, ScrapeJob

    # Newest-first pages; after=100 keeps ts>=100, before=1000 drops ts>=1000.
    pages = [
        ([Post(post_id="a", feedback_id="1", text="a", permalink=None, comment_count=0,
               created_time=900),
          Post(post_id="b", feedback_id="1", text="b", permalink=None, comment_count=0,
               created_time=800)], "c1"),
        ([Post(post_id="c", feedback_id="1", text="c", permalink=None, comment_count=0,
               created_time=200),
          Post(post_id="d", feedback_id="1", text="d", permalink=None, comment_count=0,
               created_time=50)], None),  # 50 is past after_time → stop
    ]
    calls = {"n": 0}

    def fetch(_uid, _cursor):
        i = calls["n"]
        calls["n"] += 1
        return pages[i]

    job = ScrapeJob(max_posts=1, after_time=100, before_time=1000)
    posts, chosen = runner._paginate_feed(fetch, ["UID"], job)
    assert chosen == "UID"
    assert [p.post_id for p in posts] == ["a", "b", "c"]  # d filtered + stop; max_posts=1 ignored
    assert calls["n"] == 2


def test_without_date_window_honors_max_posts():
    from fbgql.models import Post, ScrapeJob

    pages = [
        ([Post(post_id="a", feedback_id="1", text="a", permalink=None, comment_count=1,
               created_time=9),
          Post(post_id="b", feedback_id="1", text="b", permalink=None, comment_count=1,
               created_time=8)], "c1"),
    ]
    calls = {"n": 0}

    def fetch(_uid, _cursor):
        i = calls["n"]
        calls["n"] += 1
        return pages[i]

    job = ScrapeJob(max_posts=1)
    posts, _ = runner._paginate_feed(fetch, ["UID"], job)
    assert [p.post_id for p in posts] == ["a"]
    assert calls["n"] == 1
