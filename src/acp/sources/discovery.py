"""Feed retrieval, URL normalization and candidate deduplication."""
from __future__ import annotations

import hashlib
import re
import unicodedata
from dataclasses import dataclass
from typing import Any, Iterable
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

from acp.security.url_policy import UnsafeURLError
from acp.sources.http_fetcher import HTTPFetchError, SafeHTTPFetcher
from acp.sources.rss import parse_feed

FEED_CONTENT_TYPES = frozenset({
    "application/atom+xml", "application/rss+xml", "application/xml", "text/xml", "text/plain",
})
REGION_TIERS = frozenset({"local", "national", "global"})
_TRACKING_KEYS = frozenset({"fbclid", "gclid", "dclid", "mc_cid", "mc_eid", "igshid"})
_NON_WORDS = re.compile(r"[^\w]+", re.UNICODE)


@dataclass(frozen=True)
class DiscoveredCandidate:
    candidate_id: str
    title: str
    url: str
    normalized_url: str
    summary: str
    published_at: str | None
    feed_name: str
    feed_url: str
    region_tier: str


@dataclass(frozen=True)
class FeedFailure:
    feed_name: str
    reason: str


@dataclass(frozen=True)
class DiscoveryResult:
    candidates: tuple[DiscoveredCandidate, ...]
    failures: tuple[FeedFailure, ...]
    feeds_checked: int


def normalize_article_url(value: str) -> str:
    """Normalize an HTTPS article URL for deduplication without fetching it."""
    if not isinstance(value, str) or not value or len(value) > 4096:
        raise ValueError("Article URL is empty or too long")
    if any(ord(char) < 0x20 or char.isspace() for char in value) or "\\" in value:
        raise ValueError("Article URL contains whitespace, control characters or backslashes")
    try:
        parsed = urlsplit(value)
        host = parsed.hostname
        port = parsed.port
    except ValueError as exc:
        raise ValueError("Malformed article URL") from exc
    if parsed.scheme.lower() != "https" or not host or parsed.username is not None or parsed.password is not None:
        raise ValueError("Article candidates must have an HTTPS URL without embedded credentials")
    authority = value.split("://", 1)[1].split("/", 1)[0].split("?", 1)[0].split("#", 1)[0]
    if "%" in authority:
        raise ValueError("Percent-encoding is not allowed in the URL authority")
    if port not in (None, 443):
        raise ValueError("Non-standard article URL ports are not accepted")
    try:
        ascii_host = host.rstrip(".").encode("idna").decode("ascii").lower()
    except UnicodeError as exc:
        raise ValueError("Invalid article hostname") from exc
    if not ascii_host:
        raise ValueError("Article URL has no hostname")
    query_items = []
    for key, val in parse_qsl(parsed.query, keep_blank_values=True, max_num_fields=200):
        lower_key = key.lower()
        if lower_key.startswith("utm_") or lower_key in _TRACKING_KEYS:
            continue
        query_items.append((key, val))
    normalized_query = urlencode(sorted(query_items))
    path = parsed.path.rstrip("/") or "/"
    return urlunsplit(("https", ascii_host, path, normalized_query, ""))


def _headline_fingerprint(title: str) -> str:
    normalized = unicodedata.normalize("NFKC", title).casefold()
    return _NON_WORDS.sub(" ", normalized).strip()


def _candidate_id(normalized_url: str) -> str:
    return hashlib.sha256(normalized_url.encode("utf-8")).hexdigest()[:24]


def discover_candidates(
    feeds: Iterable[dict[str, Any]],
    fetcher: SafeHTTPFetcher,
    *,
    max_candidates: int = 30,
    max_items_per_feed: int = 50,
) -> DiscoveryResult:
    """Retrieve configured feeds, deduplicate candidates, and continue after feed-local errors."""
    if not 1 <= max_candidates <= 500:
        raise ValueError("max_candidates must be between 1 and 500")
    if not 1 <= max_items_per_feed <= 500:
        raise ValueError("max_items_per_feed must be between 1 and 500")

    candidates: list[DiscoveredCandidate] = []
    failures: list[FeedFailure] = []
    seen_urls: set[str] = set()
    seen_headlines: set[str] = set()
    feeds_checked = 0
    feed_list = list(feeds)
    if len(feed_list) > 100:
        raise ValueError("A discovery run may process at most 100 feed definitions")

    for feed in feed_list:
        if not isinstance(feed, dict):
            failures.append(FeedFailure("Unknown feed", "Feed definition must be a mapping"))
            continue
        feed_name = str(feed.get("name") or "Unnamed feed")[:200]
        feed_url = feed.get("url")
        if not isinstance(feed_url, str):
            failures.append(FeedFailure(feed_name, "Feed definition has no valid URL"))
            continue
        region_tier = str(feed.get("region_tier") or "global").lower()
        allowed_hosts = feed.get("allowed_hosts")
        if region_tier not in REGION_TIERS:
            failures.append(FeedFailure(feed_name, "region_tier must be local, national or global"))
            continue
        if allowed_hosts is not None and (
            not isinstance(allowed_hosts, list)
            or any(not isinstance(host, str) for host in allowed_hosts)
        ):
            failures.append(FeedFailure(feed_name, "allowed_hosts must be a list of host patterns"))
            continue
        try:
            response = fetcher.fetch(
                feed_url,
                allowed_hosts=allowed_hosts or None,
                allowed_content_types=FEED_CONTENT_TYPES,
            )
            feeds_checked += 1
            items = parse_feed(response.text(), response.url, max_items=max_items_per_feed)
            for item in items:
                try:
                    normalized_url = normalize_article_url(item.url)
                except ValueError:
                    continue
                title = re.sub(r"\s+", " ", item.title).strip()[:500]
                if not title:
                    continue
                url_fp = normalized_url.casefold()
                title_fp = _headline_fingerprint(title)
                if url_fp in seen_urls or not title_fp or title_fp in seen_headlines:
                    continue
                seen_urls.add(url_fp)
                seen_headlines.add(title_fp)
                candidates.append(DiscoveredCandidate(
                    candidate_id=_candidate_id(normalized_url),
                    title=title,
                    url=item.url,
                    normalized_url=normalized_url,
                    summary=re.sub(r"\s+", " ", item.summary).strip()[:5000],
                    published_at=item.published_at[:120] if item.published_at else None,
                    feed_name=str(item.source_name or feed_name)[:200],
                    feed_url=response.url,
                    region_tier=region_tier,
                ))
                if len(candidates) >= max_candidates:
                    return DiscoveryResult(tuple(candidates), tuple(failures), feeds_checked)
        except (HTTPFetchError, UnsafeURLError, ValueError) as exc:
            failures.append(FeedFailure(feed_name, f"{type(exc).__name__}: {str(exc)[:300]}"))
    return DiscoveryResult(tuple(candidates), tuple(failures), feeds_checked)
