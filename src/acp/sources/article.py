"""Extract bounded article evidence from already-fetched HTML.

This conservative parser does not execute markup. Extracted text remains
untrusted evidence, not verified facts.
"""
from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass
from datetime import datetime, timezone
from html.parser import HTMLParser
from typing import Any
from urllib.parse import urlsplit


class ArticleExtractionError(ValueError):
    """Raised when an HTML page has insufficient usable article evidence."""


@dataclass(frozen=True)
class ArticleEvidence:
    source_name: str
    source_url: str
    title: str
    published_at: str | None
    description: str
    body_text: str
    fetched_at: str
    content_type: str

    def as_prompt_evidence(self) -> dict[str, Any]:
        return {
            "source_name": self.source_name,
            "source_url": self.source_url,
            "title": self.title,
            "published_at": self.published_at or "Unknown",
            "source_text": self.body_text,
            "facts": [],
            "claims": [],
            "uncertainties": [],
            "description": self.description,
        }


_SKIP_TAGS = frozenset({
    "script", "style", "noscript", "svg", "canvas", "iframe", "nav",
    "footer", "header", "aside", "form", "button", "select", "textarea",
    "template", "dialog",
})
_VOID_TAGS = frozenset({
    "area", "base", "br", "col", "embed", "hr", "img", "input", "link",
    "meta", "param", "source", "track", "wbr",
})
_CONTAINER_TAGS = frozenset({"article", "main"})
_CONTROL_RE = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")


def _clean(value: str, limit: int) -> str:
    value = unicodedata.normalize("NFKC", value)
    value = _CONTROL_RE.sub("", value)
    return re.sub(r"\s+", " ", value).strip()[:limit]


def _valid_source_url(value: str) -> bool:
    if not isinstance(value, str) or not value or len(value) > 4096:
        return False
    if any(ord(char) < 0x20 or char.isspace() for char in value) or "\\" in value:
        return False
    try:
        parsed = urlsplit(value)
        port = parsed.port
    except ValueError:
        return False
    if (
        parsed.scheme.lower() != "https"
        or not parsed.hostname
        or parsed.username is not None
        or parsed.password is not None
        or parsed.fragment
        or port not in (None, 443)
    ):
        return False
    authority = value.split("://", 1)[1].split("/", 1)[0].split("?", 1)[0].split("#", 1)[0]
    return "%" not in authority


class _ArticleHTMLParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.metadata: dict[str, str] = {}
        self.page_title_parts: list[str] = []
        self._in_title = False
        self._skip_stack: list[str] = []
        self._containers: list[str] = []
        self._paragraph: list[str] | None = None
        self._paragraph_in_article = False
        self.paragraphs_all: list[tuple[str, bool]] = []
        self.published_at: str | None = None
        self.canonical_hint: str | None = None

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        tag = tag.lower()
        attr = {key.lower(): (value or "") for key, value in attrs}
        if self._skip_stack:
            if tag not in _VOID_TAGS:
                self._skip_stack.append(tag)
            return
        if tag in _SKIP_TAGS:
            if tag not in _VOID_TAGS:
                self._skip_stack.append(tag)
            return

        if tag == "meta":
            key = (attr.get("property") or attr.get("name") or attr.get("itemprop") or "").strip().lower()
            value = _clean(attr.get("content", ""), 2000)
            if key and value and key not in self.metadata:
                self.metadata[key] = value
        elif tag == "link" and "canonical" in attr.get("rel", "").lower().split():
            self.canonical_hint = _clean(attr.get("href", ""), 4096) or self.canonical_hint
        elif tag == "title":
            self._in_title = True
        elif tag == "time" and attr.get("datetime") and not self.published_at:
            self.published_at = _clean(attr["datetime"], 120)

        if tag in _CONTAINER_TAGS or attr.get("itemprop", "").lower() == "articlebody":
            self._containers.append(tag)
        if tag == "p":
            self._paragraph = []
            self._paragraph_in_article = bool(self._containers)

    def handle_endtag(self, tag: str) -> None:
        tag = tag.lower()
        if self._skip_stack:
            if tag in self._skip_stack:
                index = len(self._skip_stack) - 1 - self._skip_stack[::-1].index(tag)
                del self._skip_stack[index:]
            return
        if tag == "title":
            self._in_title = False
        if tag == "p" and self._paragraph is not None:
            paragraph = _clean(" ".join(self._paragraph), 12000)
            if paragraph:
                self.paragraphs_all.append((paragraph, self._paragraph_in_article))
            self._paragraph = None
            self._paragraph_in_article = False
        if tag in _CONTAINER_TAGS or any(item == tag for item in self._containers):
            for index in range(len(self._containers) - 1, -1, -1):
                if self._containers[index] == tag:
                    del self._containers[index:]
                    break

    def handle_data(self, data: str) -> None:
        if self._skip_stack:
            return
        if self._in_title:
            self.page_title_parts.append(data)
        if self._paragraph is not None:
            self._paragraph.append(data)


def extract_article(
    html: str,
    source_url: str,
    *,
    source_name: str = "",
    fallback_title: str = "",
    content_type: str = "text/html",
    min_body_chars: int = 80,
    max_body_chars: int = 20000,
) -> ArticleEvidence:
    if content_type.lower().split(";", 1)[0].strip() not in {"text/html", "application/xhtml+xml"}:
        raise ArticleExtractionError("Only HTML article content is supported")
    if not _valid_source_url(source_url):
        raise ArticleExtractionError("Invalid or unsafe source URL")
    if not isinstance(html, str) or not html.strip() or len(html) > 2_000_000:
        raise ArticleExtractionError("HTML is empty or exceeds the 2 MB character limit")
    if not 1 <= min_body_chars <= max_body_chars <= 100000:
        raise ValueError("Invalid article extraction length limits")

    parser = _ArticleHTMLParser()
    try:
        parser.feed(html)
        parser.close()
    except Exception as exc:
        raise ArticleExtractionError("Malformed HTML could not be parsed") from exc

    metadata = parser.metadata
    title = (
        metadata.get("og:title")
        or metadata.get("twitter:title")
        or " ".join(parser.page_title_parts)
        or fallback_title
    )
    title = _clean(title, 500)
    description = (
        metadata.get("og:description")
        or metadata.get("description")
        or metadata.get("twitter:description")
        or ""
    )
    description = _clean(description, 2000)

    article_paragraphs = [text for text, in_article in parser.paragraphs_all if in_article]
    chosen = article_paragraphs if sum(map(len, article_paragraphs)) >= min_body_chars else [
        text for text, _ in parser.paragraphs_all
    ]
    deduplicated: list[str] = []
    seen: set[str] = set()
    for paragraph in chosen:
        fingerprint = paragraph.casefold()
        if fingerprint not in seen:
            seen.add(fingerprint)
            deduplicated.append(paragraph)
    body = _clean("\n\n".join(deduplicated), max_body_chars)
    if not title:
        raise ArticleExtractionError("No usable article title was found")
    if len(body) < min_body_chars:
        raise ArticleExtractionError("Insufficient article text; refusing to invent missing content")

    published_at = (
        metadata.get("article:published_time")
        or metadata.get("datepublished")
        or metadata.get("date")
        or parser.published_at
    )
    published_at = _clean(published_at, 120) if published_at else None
    return ArticleEvidence(
        source_name=_clean(source_name, 200) or "Unknown publisher",
        source_url=source_url,
        title=title,
        published_at=published_at,
        description=description,
        body_text=body,
        fetched_at=datetime.now(timezone.utc).isoformat(),
        content_type=content_type.lower().split(";", 1)[0].strip(),
    )
