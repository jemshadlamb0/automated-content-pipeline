import pytest
from acp.sources.rss import parse_feed


def test_parse_rss_entry():
    xml = """<?xml version="1.0"?><rss version="2.0"><channel>
    <item><title>Example headline</title><link>https://news.example/story</link>
    <description>Short summary</description><pubDate>Sun, 18 Oct 2026 08:00:00 GMT</pubDate></item>
    </channel></rss>"""
    items = parse_feed(xml, "https://news.example/rss")
    assert len(items) == 1
    assert items[0].title == "Example headline"
    assert items[0].url == "https://news.example/story"


def test_invalid_feed_xml_raises():
    with pytest.raises(ValueError):
        parse_feed("<rss>", "https://news.example/rss")


def test_non_http_item_link_is_skipped():
    xml = """<rss version="2.0"><channel><item><title>Bad</title>
    <link>javascript:alert(1)</link></item></channel></rss>"""
    assert parse_feed(xml, "https://news.example/rss") == []


def test_feed_url_must_be_http():
    with pytest.raises(ValueError):
        parse_feed("<rss/>", "file:///etc/passwd")
