import pytest
from acp.sources.rss import parse_feed


def test_feed_xml_size_is_bounded():
    with pytest.raises(ValueError, match="2 MB"):
        parse_feed(" " * (2_000_001), "https://news.example.org/rss")


def test_dtd_and_entity_expansion_are_rejected():
    payload = """<?xml version="1.0"?>
    <!DOCTYPE rss [<!ENTITY xxe SYSTEM "file:///etc/passwd">]>
    <rss version="2.0"><channel><item><title>&xxe;</title>
    <link>https://news.example.org/story</link></item></channel></rss>"""
    with pytest.raises(ValueError, match="unsafe feed XML"):
        parse_feed(payload, "https://news.example.org/rss")
