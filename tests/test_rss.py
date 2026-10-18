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
    assert items[0].summary == "Short summary"
    assert items[0].feed_content == ""


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



def test_rss_content_encoded_is_preserved_as_publisher_provided_html():
    xml = """<?xml version="1.0"?>
    <rss version="2.0" xmlns:content="http://purl.org/rss/1.0/modules/content/">
      <channel><item>
        <title>Full story</title>
        <link>https://news.example/story</link>
        <description>Short teaser.</description>
        <content:encoded><![CDATA[
          <article><p>The publisher provides the first complete paragraph with factual detail.</p>
          <p>The publisher provides a second complete paragraph and context for readers.</p></article>
        ]]></content:encoded>
      </item></channel>
    </rss>"""
    item = parse_feed(xml, "https://news.example/rss")[0]
    assert item.summary == "Short teaser."
    assert item.feed_content_type == "text/html"
    assert "<article>" in item.feed_content
    assert "second complete paragraph" in item.feed_content


def test_atom_content_is_retained_separately_from_summary():
    xml = """<?xml version="1.0"?>
    <feed xmlns="http://www.w3.org/2005/Atom">
      <entry>
        <title>Atom story</title>
        <link href="https://news.example/atom-story"/>
        <summary>A short teaser.</summary>
        <content type="html">&lt;p&gt;This is the complete publisher-supplied content, with substantial detail for the story.&lt;/p&gt;</content>
      </entry>
    </feed>"""
    item = parse_feed(xml, "https://news.example/atom-feed")[0]
    assert item.summary == "A short teaser."
    assert item.feed_content_type == "text/html"
    assert "<p>" in item.feed_content
    assert "substantial detail" in item.feed_content


def test_atom_plain_text_content_type_is_preserved():
    xml = """<?xml version="1.0"?>
    <feed xmlns="http://www.w3.org/2005/Atom">
      <entry>
        <title>Plain story</title>
        <link href="https://news.example/plain"/>
        <content type="text">Publisher provided content.</content>
      </entry>
    </feed>"""
    item = parse_feed(xml, "https://news.example/atom-feed")[0]
    assert item.feed_content == "Publisher provided content."
    assert item.feed_content_type == "text/plain"



def test_rss_content_encoded_is_bounded():
    story = "x" * 25_000
    xml = f"""<rss version="2.0" xmlns:content="http://purl.org/rss/1.0/modules/content/">
    <channel><item><title>Long story</title><link>https://news.example/story</link>
    <content:encoded><![CDATA[{story}]]></content:encoded>
    </item></channel></rss>"""
    item = parse_feed(xml, "https://news.example/rss")[0]
    assert len(item.feed_content) == 20_000
