"""Page vs. single-post routing for a pasted link.

Callers with one input field (the Apify actor, any web form) route on this, so a
misread silently scrapes the wrong thing — a profile URL sent down the post path, or
a feed tab treated as a permalink.
"""

from __future__ import annotations

import pytest

from fbgql.runner import is_post_url


@pytest.mark.parametrize("url", [
    "https://www.facebook.com/ronaldo/posts/122216361518376966",
    "https://www.facebook.com/ronaldo/posts/pfbid02AbCdEf",
    "https://www.facebook.com/permalink.php?story_fbid=12345&id=678",
    "https://www.facebook.com/ronaldo/videos/1234567890",
    "https://www.facebook.com/reel/1234567890",
    "https://www.facebook.com/ronaldo/permalink/1234567890",
    "https://www.facebook.com/permalink.php?story_fbid=pfbid02AbCdEf&id=61561308996622",
    "https://www.facebook.com/share/p/1AbCdEf/",
])
def test_post_urls_route_to_single_post(url):
    assert is_post_url(url) is True


@pytest.mark.parametrize("url", [
    # Profile URLs that happen to contain a pfbid are profiles, not posts.
    "https://www.facebook.com/people/Jetour-South-Africa/pfbid02AbCdEf/",
    "https://www.facebook.com/profile.php?id=61561308996622",
    # Feed tabs, not permalinks — no post id after the marker.
    "https://www.facebook.com/ronaldo/videos/",
    "https://www.facebook.com/ronaldo/videos",
    "https://www.facebook.com/ronaldo/about",
    "https://www.facebook.com/groups/2693577247594660",
    "https://www.facebook.com/ronaldo",
    "ronaldo",
    "",
])
def test_page_and_profile_urls_route_to_feed(url):
    assert is_post_url(url) is False


def test_routed_post_urls_yield_a_post_id():
    """Whatever routes to the post path must survive the next step, id extraction."""
    from fbgql.runner import _post_id_from_url

    for url in (
        "https://www.facebook.com/ronaldo/posts/122216361518376966",
        "https://www.facebook.com/permalink.php?story_fbid=12345&id=678",
        "https://www.facebook.com/ronaldo/videos/1234567890",
        "https://www.facebook.com/reel/1234567890",
    ):
        assert _post_id_from_url(url)
