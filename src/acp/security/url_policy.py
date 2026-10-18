"""SSRF-resistant URL resolution primitives.

A production downloader must validate each redirect hop and bind the socket to
one of the validated IP addresses while verifying TLS against the original host.
"""
from __future__ import annotations

import ipaddress
import socket
from dataclasses import dataclass
from typing import Callable, Iterable
from urllib.parse import urlsplit, urlunsplit


class UnsafeURLError(ValueError):
    """Raised when a URL violates outbound-network policy."""


Resolver = Callable[[str, int], Iterable[str]]


@dataclass(frozen=True)
class ResolvedPublicURL:
    url: str
    scheme: str
    host: str
    port: int
    addresses: tuple[str, ...]
    request_target: str


def _resolve_public_addresses(host: str, port: int) -> list[str]:
    try:
        answers = socket.getaddrinfo(host, port, type=socket.SOCK_STREAM)
    except OSError as exc:
        raise UnsafeURLError("DNS resolution failed") from exc
    return list(dict.fromkeys(answer[4][0] for answer in answers))


def resolve_public_http_url(
    value: str,
    *,
    allow_http: bool = False,
    resolver: Resolver | None = None,
) -> ResolvedPublicURL:
    """Validate a public HTTP(S) URL and return the exact validated addresses.

    HTTPS is mandatory unless the caller explicitly allows HTTP. Only standard
    ports are accepted. Every DNS A/AAAA answer must be globally routable. The
    caller must connect to a returned address rather than resolving the hostname
    again, and must repeat this process for every redirect.
    """
    if not isinstance(value, str) or not value or len(value) > 4096:
        raise UnsafeURLError("URL must be a non-empty string of at most 4096 characters")
    if any(ord(char) < 0x20 or char.isspace() for char in value):
        raise UnsafeURLError("URL must not contain whitespace or control characters")
    if "\\" in value:
        raise UnsafeURLError("URL must not contain backslashes")

    try:
        parsed = urlsplit(value)
        scheme = parsed.scheme.lower()
        host = parsed.hostname
        port = parsed.port
    except ValueError as exc:
        raise UnsafeURLError("Malformed URL") from exc

    authority = value.split("://", 1)[1].split("/", 1)[0].split("?", 1)[0].split("#", 1)[0] if "://" in value else ""
    if "%" in authority:
        raise UnsafeURLError("Percent-encoding is not allowed in URL authority")
    if parsed.fragment:
        # Fragments are not sent to the server; reject to avoid ambiguous identities.
        raise UnsafeURLError("URL fragments are not accepted")

    if scheme != "https" and not (allow_http and scheme == "http"):
        raise UnsafeURLError("HTTPS is required unless HTTP is explicitly enabled for a trusted feed")
    if not host or parsed.username is not None or parsed.password is not None:
        raise UnsafeURLError("URL must have a hostname and must not contain embedded credentials")

    try:
        ascii_host = host.rstrip(".").encode("idna").decode("ascii").lower()
    except UnicodeError as exc:
        raise UnsafeURLError("Invalid internationalized hostname") from exc
    if not ascii_host or ascii_host == "localhost" or ascii_host.endswith(
        (".localhost", ".local", ".internal", ".test", ".invalid", ".example")
    ):
        raise UnsafeURLError("Local or reserved hostname is not allowed")

    expected_port = 443 if scheme == "https" else 80
    if port is not None and port != expected_port:
        raise UnsafeURLError(f"Only port {expected_port} is allowed for {scheme}")
    effective_port = port or expected_port

    try:
        literal_ip = ipaddress.ip_address(ascii_host)
        addresses = [str(literal_ip)]
    except ValueError:
        addresses = list((resolver or _resolve_public_addresses)(ascii_host, effective_port))

    if not addresses:
        raise UnsafeURLError("Hostname did not resolve to an address")
    validated: list[str] = []
    for address in addresses:
        try:
            parsed_ip = ipaddress.ip_address(address)
        except ValueError as exc:
            raise UnsafeURLError("Resolver returned an invalid IP address") from exc
        if not parsed_ip.is_global:
            raise UnsafeURLError("URL resolves to a non-public IP address")
        normalized = str(parsed_ip)
        if normalized not in validated:
            validated.append(normalized)

    target = urlunsplit(("", "", parsed.path or "/", parsed.query, ""))
    return ResolvedPublicURL(
        url=value,
        scheme=scheme,
        host=ascii_host,
        port=effective_port,
        addresses=tuple(validated),
        request_target=target,
    )


def validate_public_http_url(
    value: str,
    *,
    allow_http: bool = False,
    resolver: Resolver | None = None,
) -> str:
    """Compatibility helper that validates and returns the original URL."""
    resolve_public_http_url(value, allow_http=allow_http, resolver=resolver)
    return value
