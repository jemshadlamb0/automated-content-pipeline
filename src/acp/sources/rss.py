"""Parse RSS 2.0 and Atom XML already fetched by a separate safe HTTP layer."""
from __future__ import annotations

from dataclasses import dataclass
from html import escape
from typing import Optional
from urllib.parse import urlparse

from defusedxml import ElementTree as ET
from defusedxml.common import DefusedXmlException

CONTENT_MODULE_NS = "{http://purl.org/rss/1.0/modules/content/}encoded"
MAX_EMBEDDED_CONTENT_CHARS = 20_000


@dataclass(frozen=True)
class FeedItem:
    title: str
    url: str
    summary: str = ""
    published_at: Optional[str] = None
    source_name: Optional[str] = None
    feed_content: str = ""
    feed_content_type: str = "text/plain"


def _text(node: ET.Element | None) -> str:
    if node is None:
        return ""
    return " ".join("".join(node.itertext()).split())


def _serialize_content_node(node: ET.Element) -> str:
    """Serialize feed-supplied XHTML as an attribute-free HTML fragment.

    Dropping XML namespace prefixes lets the conservative HTML parser recognize
    standard elements (for example, xhtml:p) without trusting feed attributes.
    """
    tag = node.tag.rsplit("}", 1)[-1].lower()
    if not tag or not tag[0].isalpha() or not all(char.isalnum() or char in "-_:" for char in tag):
        return escape("".join(node.itertext()), quote=False)
    parts = [f"<{tag}>", escape(node.text or "", quote=False)]
    for child in node:
        parts.append(_serialize_content_node(child))
        parts.append(escape(child.tail or "", quote=False))
    parts.append(f"</{tag}>")
    return "".join(parts)


def _inner_content(node: ET.Element | None) -> str:
    """Return bounded feed-supplied content, preserving HTML markup when present."""
    if node is None:
        return ""
    if len(node) == 0:
        return (node.text or "")[:MAX_EMBEDDED_CONTENT_CHARS]
    parts: list[str] = []
    size = 0
    if node.text:
        parts.append(node.text[:MAX_EMBEDDED_CONTENT_CHARS])
        size = len(parts[0])
    for child in node:
        if size >= MAX_EMBEDDED_CONTENT_CHARS:
            break
        markup = _serialize_content_node(child)
        tail = child.tail or ""
        remaining = MAX_EMBEDDED_CONTENT_CHARS - size
        parts.append(markup[:remaining])
        size += min(len(markup), remaining)
        if size < MAX_EMBEDDED_CONTENT_CHARS and tail:
            remaining = MAX_EMBEDDED_CONTENT_CHARS - size
            parts.append(tail[:remaining])
            size += min(len(tail), remaining)
    return "".join(parts)


def _atom_content_type(value: str | None) -> str:
    value = (value or "text").strip().lower()
    if value in {"html", "text/html"}:
        return "text/html"
    if value in {"xhtml", "application/xhtml+xml"}:
        return "application/xhtml+xml"
    if value in {"text", "text/plain"}:
        return "text/plain"
    return "text/plain"


def _valid_http_url(value: str) -> bool:
    parsed = urlparse(value.strip())
    return parsed.scheme in {"https", "http"} and bool(parsed.hostname) and not parsed.username and not parsed.password


def parse_feed(xml_text: str, feed_url: str, max_items: int = 50) -> list[FeedItem]:
    """Parse a bounded feed document; this function intentionally makes no network calls."""
    if not _valid_http_url(feed_url):
        raise ValueError("feed_url must be an absolute HTTP(S) URL")
    if not 1 <= max_items <= 500:
        raise ValueError("max_items must be between 1 and 500")
    if len(xml_text) > 2_000_000:
        raise ValueError("feed body exceeds 2 MB limit")
    try:
        root = ET.fromstring(xml_text)
    except (ET.ParseError, DefusedXmlException) as exc:
        raise ValueError(f"Invalid or unsafe feed XML: {exc}") from exc

    items: list[FeedItem] = []
    # RSS 2.0, including the publisher-provided content:encoded extension.
    rss_nodes = root.findall("./channel/item")
    if rss_nodes:
        for node in rss_nodes[:max_items]:
            title = _text(node.find("title"))
            link = _text(node.find("link"))
            if not title or not _valid_http_url(link):
                continue
            encoded = node.find(CONTENT_MODULE_NS)
            if encoded is not None:
                feed_content = _inner_content(encoded)
                declared = (encoded.attrib.get("type") or "html").strip().lower()
                feed_content_type = _atom_content_type(declared)
            else:
                feed_content = ""
                feed_content_type = "text/plain"
            items.append(FeedItem(
                title=title,
                url=link,
                summary=_text(node.find("description")),
                published_at=_text(node.find("pubDate")) or None,
                source_name=_text(node.find("source")) or None,
                feed_content=feed_content,
                feed_content_type=feed_content_type,
            ))
        return items

    # Atom 1.0 (common default namespace). <summary> stays a summary; <content>
    # is retained separately only when the publisher explicitly includes it.
    ns = {"a": "http://www.w3.org/2005/Atom"}
    for node in root.findall("./a:entry", ns)[:max_items]:
        title = _text(node.find("a:title", ns))
        summary = _text(node.find("a:summary", ns))
        content_node = node.find("a:content", ns)
        feed_content = _inner_content(content_node)
        feed_content_type = _atom_content_type(
            content_node.attrib.get("type") if content_node is not None else None
        )
        published = _text(node.find("a:published", ns)) or _text(node.find("a:updated", ns)) or None
        link = ""
        for candidate in node.findall("a:link", ns):
            if candidate.attrib.get("rel", "alternate") == "alternate":
                link = candidate.attrib.get("href", "")
                break
        if title and _valid_http_url(link):
            items.append(FeedItem(
                title=title,
                url=link,
                summary=summary,
                published_at=published,
                feed_content=feed_content,
                feed_content_type=feed_content_type,
            ))
    return items
