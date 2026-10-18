"""Parse RSS 2.0 and Atom XML already fetched by a separate safe HTTP layer."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Optional
from urllib.parse import urlparse
import xml.etree.ElementTree as ET


@dataclass(frozen=True)
class FeedItem:
    title: str
    url: str
    summary: str = ""
    published_at: Optional[str] = None
    source_name: Optional[str] = None


def _text(node: ET.Element | None) -> str:
    if node is None:
        return ""
    return " ".join("".join(node.itertext()).split())


def _valid_http_url(value: str) -> bool:
    parsed = urlparse(value.strip())
    return (
        parsed.scheme in {"https", "http"}
        and bool(parsed.hostname)
        and not parsed.username
        and not parsed.password
    )


def parse_feed(xml_text: str, feed_url: str, max_items: int = 50) -> list[FeedItem]:
    """Parse a bounded feed document; this function intentionally makes no network calls."""
    if not _valid_http_url(feed_url):
        raise ValueError("feed_url must be an absolute HTTP(S) URL")
    if not 1 <= max_items <= 500:
        raise ValueError("max_items must be between 1 and 500")
    try:
        root = ET.fromstring(xml_text)
    except ET.ParseError as exc:
        raise ValueError(f"Invalid feed XML: {exc}") from exc

    items: list[FeedItem] = []
    # RSS 2.0
    rss_nodes = root.findall("./channel/item")
    if rss_nodes:
        for node in rss_nodes[:max_items]:
            title = _text(node.find("title"))
            link = _text(node.find("link"))
            if not title or not _valid_http_url(link):
                continue
            items.append(FeedItem(
                title=title,
                url=link,
                summary=_text(node.find("description")),
                published_at=_text(node.find("pubDate")) or None,
                source_name=_text(node.find("source")) or None,
            ))
        return items

    # Atom 1.0 (common default namespace).
    ns = {"a": "http://www.w3.org/2005/Atom"}
    for node in root.findall("./a:entry", ns)[:max_items]:
        title = _text(node.find("a:title", ns))
        summary = _text(node.find("a:summary", ns)) or _text(node.find("a:content", ns))
        published = _text(node.find("a:published", ns)) or _text(node.find("a:updated", ns)) or None
        link = ""
        for candidate in node.findall("a:link", ns):
            if candidate.attrib.get("rel", "alternate") == "alternate":
                link = candidate.attrib.get("href", "")
                break
        if title and _valid_http_url(link):
            items.append(FeedItem(title=title, url=link, summary=summary, published_at=published))
    return items
