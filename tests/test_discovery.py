from acp.sources.discovery import discover_candidates, normalize_article_url
from acp.sources.http_fetcher import FetchResponse


FEED_ONE = """<?xml version="1.0"?><rss version="2.0"><channel>
<item><title>New camera launched</title><link>https://news.example.org/camera?utm_source=rss</link>
<description>A new camera announcement with technical details.</description></item>
<item><title>AI research announcement</title><link>https://news.example.org/ai</link>
<description>New research published by a university lab.</description></item>
</channel></rss>"""
FEED_TWO = """<?xml version="1.0"?><rss version="2.0"><channel>
<item><title>New camera launched</title><link>https://news.example.org/camera</link>
<description>Duplicate story through another feed.</description></item>
<item><title>Electric vehicle announcement</title><link>https://news.example.org/ev</link>
<description>A new electric vehicle was announced.</description></item>
</channel></rss>"""


class FakeFetcher:
    def __init__(self, responses):
        self.responses = responses
        self.calls = []

    def fetch(self, url, *, allowed_hosts=None, allowed_content_types=None):
        self.calls.append((url, allowed_hosts, allowed_content_types))
        body = self.responses[url].encode()
        return FetchResponse(
            url=url,
            status=200,
            headers={"content-type": "application/rss+xml"},
            body=body,
            content_type="application/rss+xml",
            redirect_hosts=(),
        )


def test_normalization_removes_tracking_query_and_fragment():
    assert normalize_article_url("https://NEWS.example.org/story/?utm_source=x&ref=mail#top") == (
        "https://news.example.org/story?ref=mail"
    )


def test_discovery_deduplicates_urls_and_headlines_across_feeds():
    feeds = [
        {"name": "Feed A", "url": "https://feeds.example.org/a", "region_tier": "local"},
        {"name": "Feed B", "url": "https://feeds.example.org/b", "region_tier": "global"},
    ]
    fetcher = FakeFetcher({
        "https://feeds.example.org/a": FEED_ONE,
        "https://feeds.example.org/b": FEED_TWO,
    })
    result = discover_candidates(feeds, fetcher)
    assert result.feeds_checked == 2
    assert len(result.failures) == 0
    assert [c.title for c in result.candidates] == [
        "New camera launched", "AI research announcement", "Electric vehicle announcement"
    ]
    assert result.candidates[0].region_tier == "local"


def test_bad_feed_does_not_stop_other_feeds():
    feeds = [
        {"name": "Broken", "url": "https://feeds.example.org/bad"},
        {"name": "Good", "url": "https://feeds.example.org/good"},
    ]
    fetcher = FakeFetcher({
        "https://feeds.example.org/bad": "<broken",
        "https://feeds.example.org/good": FEED_ONE,
    })
    result = discover_candidates(feeds, fetcher)
    assert result.feeds_checked == 2
    assert len(result.failures) == 1
    assert len(result.candidates) == 2


def test_non_https_candidate_links_are_skipped():
    xml = """<rss version="2.0"><channel>
    <item><title>Unsafe article</title><link>http://news.example.org/story</link></item>
    <item><title>Safe article</title><link>https://news.example.org/story</link></item>
    </channel></rss>"""
    fetcher = FakeFetcher({"https://feeds.example.org/feed": xml})
    result = discover_candidates([{"url": "https://feeds.example.org/feed"}], fetcher)
    assert [candidate.title for candidate in result.candidates] == ["Safe article"]



def test_candidate_carries_embedded_content_and_keeps_configured_feed_label():
    xml = """<rss version="2.0" xmlns:content="http://purl.org/rss/1.0/modules/content/">
    <channel><item>
      <title>Full publisher story</title>
      <link>https://news.example.org/full-story</link>
      <source url="https://news.example.org/">Editorial label</source>
      <description>A brief teaser.</description>
      <content:encoded><![CDATA[<article><p>This is publisher-supplied full story content with enough detail to test extraction reliably.</p>
      <p>A second paragraph adds context and lets the downstream pipeline build an evidence-grounded summary.</p></article>]]></content:encoded>
    </item></channel></rss>"""
    fetcher = FakeFetcher({"https://feeds.example.org/feed": xml})
    result = discover_candidates(
        [{
            "name": "Trusted Example Feed",
            "url": "https://feeds.example.org/feed",
            "region_tier": "global",
            "allowed_hosts": ["feeds.example.org", "news.example.org"],
        }],
        fetcher,
    )
    assert len(result.candidates) == 1
    item = result.candidates[0]
    assert item.feed_name == "Trusted Example Feed"
    assert item.publisher_name == "Editorial label"
    assert item.feed_content_type == "text/html"
    assert "publisher-supplied full story content" in item.feed_content
    assert item.summary == "A brief teaser."
