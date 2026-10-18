"""Bounded outbound HTTP fetcher with redirect-by-redirect SSRF controls.

Requests use no ambient proxy or credentials. Each redirect is DNS-resolved and
validated again; connections pin to a validated IP while HTTPS still validates
the original hostname. This fetcher is for text/feed retrieval, not media files.
"""
from __future__ import annotations

import http.client
import re
import socket
import ssl
import time
from dataclasses import dataclass
from typing import Callable, Iterable
from urllib.parse import urljoin, urlsplit

from acp.security.url_policy import ResolvedPublicURL, resolve_public_http_url

DEFAULT_ACCEPTED_CONTENT_TYPES = frozenset({
    "application/atom+xml", "application/json", "application/rss+xml",
    "application/xhtml+xml", "application/xml", "text/html", "text/plain", "text/xml",
})
REDIRECT_STATUSES = frozenset({301, 302, 303, 307, 308})
RETRYABLE_STATUSES = frozenset({408, 425, 429, 500, 502, 503, 504})


class HTTPFetchError(RuntimeError):
    """Raised when a safe, bounded HTTP retrieval fails."""


@dataclass(frozen=True)
class RawHTTPResponse:
    status: int
    headers: dict[str, str]
    body: bytes = b""


@dataclass(frozen=True)
class FetchResponse:
    url: str
    status: int
    headers: dict[str, str]
    body: bytes
    content_type: str
    redirect_hosts: tuple[str, ...]

    def text(self) -> str:
        """Decode a bounded text response, preferring a declared charset."""
        charset = "utf-8"
        match = re.search(r"(?:^|;)\s*charset\s*=\s*['\"]?([^;'\"]+)", self.headers.get("content-type", ""), re.I)
        if match:
            candidate = match.group(1).strip()
            if candidate and len(candidate) <= 40:
                charset = candidate
        try:
            return self.body.decode(charset, errors="replace")
        except (LookupError, UnicodeError):
            return self.body.decode("utf-8", errors="replace")


def _normalize_allowlist(allowed_hosts: Iterable[str] | None) -> tuple[str, ...] | None:
    if allowed_hosts is None:
        return None
    if isinstance(allowed_hosts, (str, bytes)):
        raise ValueError("allowed_hosts must be a collection of host patterns, not a string")
    result: list[str] = []
    for item in allowed_hosts:
        if not isinstance(item, str) or not item.strip():
            raise ValueError("allowed_hosts must contain non-empty host patterns")
        pattern = item.strip().rstrip(".").lower()
        wildcard = pattern.startswith("*.")
        bare = pattern[2:] if wildcard else pattern
        if "/" in bare or ":" in bare or "@" in bare or " " in bare:
            raise ValueError("allowed_hosts entries must be hostnames or *.hostname patterns")
        try:
            bare = bare.encode("idna").decode("ascii")
        except UnicodeError as exc:
            raise ValueError("allowed_hosts contains an invalid hostname") from exc
        result.append("*." + bare if wildcard else bare)
    return tuple(result)


def _host_allowed(host: str, allowlist: tuple[str, ...] | None) -> bool:
    if allowlist is None:
        return True
    normalized = host.lower().rstrip(".")
    for pattern in allowlist:
        if pattern.startswith("*."):
            suffix = pattern[1:]
            if normalized.endswith(suffix) and normalized != pattern[2:]:
                return True
        elif normalized == pattern:
            return True
    return False


class _PinnedHTTPConnection(http.client.HTTPConnection):
    """HTTP connection pinned to an already-validated destination IP."""

    def __init__(self, destination: ResolvedPublicURL, timeout: float) -> None:
        super().__init__(destination.host, destination.port, timeout=timeout)
        self._pinned_ip = destination.addresses[0]

    def connect(self) -> None:
        if self._tunnel_host:
            raise HTTPFetchError("Proxy tunnelling is not supported")
        self.sock = socket.create_connection((self._pinned_ip, self.port), self.timeout, self.source_address)


class _PinnedHTTPSConnection(http.client.HTTPSConnection):
    """HTTPS connection pinned to an IP while preserving hostname TLS checks."""

    def __init__(self, destination: ResolvedPublicURL, timeout: float) -> None:
        super().__init__(
            destination.host, destination.port, timeout=timeout, context=ssl.create_default_context()
        )
        self._pinned_ip = destination.addresses[0]

    def connect(self) -> None:
        if self._tunnel_host:
            raise HTTPFetchError("Proxy tunnelling is not supported")
        raw_socket = socket.create_connection((self._pinned_ip, self.port), self.timeout, self.source_address)
        try:
            # self.host remains the DNS hostname for certificate validation and SNI.
            self.sock = self._context.wrap_socket(raw_socket, server_hostname=self.host)
        except Exception:
            raw_socket.close()
            raise


class SafeHTTPFetcher:
    """Fetch bounded public text resources with strict URL and redirect policy."""

    def __init__(
        self,
        *,
        timeout_seconds: float = 8.0,
        max_response_bytes: int = 2_000_000,
        max_redirects: int = 3,
        max_retries: int = 1,
        allow_http: bool = False,
        resolver: Callable[[str, int], Iterable[str]] | None = None,
        requester: Callable[[ResolvedPublicURL, float, int], RawHTTPResponse] | None = None,
        sleeper: Callable[[float], None] = time.sleep,
    ) -> None:
        if not 0.5 <= timeout_seconds <= 30:
            raise ValueError("timeout_seconds must be between 0.5 and 30")
        if not 1024 <= max_response_bytes <= 10_000_000:
            raise ValueError("max_response_bytes must be between 1024 and 10000000")
        if not 0 <= max_redirects <= 5:
            raise ValueError("max_redirects must be between 0 and 5")
        if not 0 <= max_retries <= 2:
            raise ValueError("max_retries must be between 0 and 2")
        self.timeout_seconds = timeout_seconds
        self.max_response_bytes = max_response_bytes
        self.max_redirects = max_redirects
        self.max_retries = max_retries
        self.allow_http = allow_http
        self.resolver = resolver
        self.requester = requester or self._request_once
        self.sleeper = sleeper

    def fetch(
        self,
        url: str,
        *,
        allowed_hosts: Iterable[str] | None = None,
        allowed_content_types: Iterable[str] | None = None,
    ) -> FetchResponse:
        """Fetch a resource with bounded redirects/retries and no ambient credentials."""
        allowlist = _normalize_allowlist(allowed_hosts)
        content_types = frozenset(
            item.split(";", 1)[0].strip().lower()
            for item in (
                allowed_content_types if allowed_content_types is not None
                else DEFAULT_ACCEPTED_CONTENT_TYPES
            )
        )
        if not content_types or any(not item or "/" not in item for item in content_types):
            raise ValueError("allowed_content_types must contain valid MIME types")

        current_url = url
        previous_scheme: str | None = None
        redirect_hosts: list[str] = []
        for redirect_index in range(self.max_redirects + 1):
            destination = resolve_public_http_url(current_url, allow_http=self.allow_http, resolver=self.resolver)
            if previous_scheme == "https" and destination.scheme != "https":
                raise HTTPFetchError("HTTPS-to-HTTP redirect is forbidden")
            if not _host_allowed(destination.host, allowlist):
                raise HTTPFetchError("Destination host is not on the configured allowlist")

            raw: RawHTTPResponse | None = None
            for attempt in range(self.max_retries + 1):
                try:
                    raw = self.requester(destination, self.timeout_seconds, self.max_response_bytes)
                except (OSError, ssl.SSLError, http.client.HTTPException, TimeoutError) as exc:
                    if attempt >= self.max_retries:
                        raise HTTPFetchError(f"Upstream transport failed ({type(exc).__name__})") from exc
                    self.sleeper(0.25 * (2 ** attempt))
                    continue
                if raw.status not in RETRYABLE_STATUSES or attempt >= self.max_retries:
                    break
                self.sleeper(0.25 * (2 ** attempt))

            if raw is None:
                raise HTTPFetchError("Upstream returned no response")
            raw_headers = {key.lower(): value.strip() for key, value in raw.headers.items()}
            if raw.status in REDIRECT_STATUSES:
                location = raw_headers.get("location", "")
                if not location:
                    raise HTTPFetchError("Redirect response did not include a Location header")
                if redirect_index >= self.max_redirects:
                    raise HTTPFetchError("Maximum redirect count exceeded")
                next_url = urljoin(current_url, location)
                try:
                    next_scheme = urlsplit(next_url).scheme.lower()
                except ValueError as exc:
                    raise HTTPFetchError("Malformed redirect target") from exc
                if destination.scheme == "https" and next_scheme != "https":
                    raise HTTPFetchError("HTTPS-to-HTTP redirect is forbidden")
                redirect_hosts.append(destination.host)
                previous_scheme = destination.scheme
                current_url = next_url
                continue

            if raw.status in RETRYABLE_STATUSES:
                raise HTTPFetchError(f"Upstream returned retryable HTTP {raw.status} after retries")
            if raw.status != 200:
                raise HTTPFetchError(f"Upstream returned HTTP {raw.status}")
            transfer_encoding = raw_headers.get("transfer-encoding", "").lower()
            if transfer_encoding and (
                transfer_encoding != "chunked" or "content-length" in raw_headers
            ):
                raise HTTPFetchError("Unsupported or ambiguous upstream transfer encoding")
            encoding = raw_headers.get("content-encoding", "identity").lower()
            if encoding not in {"", "identity"}:
                raise HTTPFetchError("Compressed upstream responses are not accepted")
            declared_type = raw_headers.get("content-type", "application/octet-stream").split(";", 1)[0].strip().lower()
            if declared_type not in content_types:
                raise HTTPFetchError(f"Unexpected content type: {declared_type or 'missing'}")
            if len(raw.body) > self.max_response_bytes:
                raise HTTPFetchError("Upstream response exceeded configured size limit")
            return FetchResponse(
                url=current_url, status=raw.status, headers=raw_headers, body=raw.body,
                content_type=declared_type, redirect_hosts=tuple(redirect_hosts),
            )
        raise HTTPFetchError("Could not retrieve resource")

    def _request_once(self, destination: ResolvedPublicURL, timeout: float, max_bytes: int) -> RawHTTPResponse:
        """Make one direct, IP-pinned request and read only a bounded response."""
        connection_class = _PinnedHTTPSConnection if destination.scheme == "https" else _PinnedHTTPConnection
        connection = connection_class(destination, timeout)
        request_headers = {
            "User-Agent": "AutomatedContentPipeline/0.1 (+https://github.com/jemshadlamb0/automated-content-pipeline)",
            "Accept": ", ".join(sorted(DEFAULT_ACCEPTED_CONTENT_TYPES)),
            "Accept-Encoding": "identity",
            "Connection": "close",
        }
        deadline = time.monotonic() + timeout

        def set_remaining_timeout() -> None:
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                raise HTTPFetchError("Upstream total deadline exceeded")
            if connection.sock is not None:
                connection.sock.settimeout(remaining)

        try:
            connection.request("GET", destination.request_target, headers=request_headers)
            set_remaining_timeout()
            response = connection.getresponse()
            response_headers: dict[str, str] = {}
            for name, value in response.getheaders():
                lower_name = name.lower()
                if lower_name in response_headers and response_headers[lower_name] != value:
                    if lower_name in {"content-length", "content-type", "content-encoding", "location"}:
                        raise HTTPFetchError(f"Ambiguous upstream {lower_name} header")
                response_headers.setdefault(lower_name, value)

            if response.status in REDIRECT_STATUSES or response.status != 200:
                return RawHTTPResponse(response.status, response_headers, b"")

            content_length = response_headers.get("content-length")
            if content_length is not None:
                if not content_length.isdigit():
                    raise HTTPFetchError("Invalid upstream Content-Length")
                if int(content_length) > max_bytes:
                    raise HTTPFetchError("Upstream response exceeded configured size limit")

            transfer_encoding = response_headers.get("transfer-encoding", "").lower()
            if transfer_encoding and (
                transfer_encoding != "chunked" or "content-length" in response_headers
            ):
                raise HTTPFetchError("Unsupported or ambiguous upstream transfer encoding")
            encoding = response_headers.get("content-encoding", "identity").lower()
            if encoding not in {"", "identity"}:
                raise HTTPFetchError("Compressed upstream responses are not accepted")

            body = bytearray()
            while True:
                set_remaining_timeout()
                chunk = response.read(min(65536, max_bytes - len(body) + 1))
                if not chunk:
                    break
                body.extend(chunk)
                if len(body) > max_bytes:
                    raise HTTPFetchError("Upstream response exceeded configured size limit")
            return RawHTTPResponse(response.status, response_headers, bytes(body))
        finally:
            connection.close()
