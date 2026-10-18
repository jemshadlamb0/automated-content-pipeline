"""SSRF-resistant URL validation primitives.

A production downloader must validate every redirect and ensure the actual
connected peer matches an approved public IP; checking a URL string alone is
not enough to prevent DNS rebinding.
"""
from __future__ import annotations

import ipaddress
import socket
from typing import Callable, Iterable
from urllib.parse import urlsplit


class UnsafeURLError(ValueError):
    """Raised when a URL violates outbound-network policy."""


Resolver = Callable[[str, int], Iterable[str]]


def _resolve_public_addresses(host: str, port: int) -> list[str]:
    try:
        answers = socket.getaddrinfo(host, port, type=socket.SOCK_STREAM)
    except OSError as exc:
        raise UnsafeURLError(f"DNS resolution failed for host: {host}") from exc
    return list(dict.fromkeys(answer[4][0] for answer in answers))


def validate_public_http_url(
    value: str,
    *,
    allow_http: bool = False,
    resolver: Resolver | None = None,
) -> str:
    """Validate an absolute public URL.

    HTTPS is required by default. Only ports 443 (HTTPS) and, if explicitly
    allowed, 80 (HTTP) are accepted. All resolved addresses must be global.
    The resolver argument supports deterministic tests; production callers
    must additionally bind the connection to a validated address.
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

    # Percent-encoding in the authority is ambiguous and is unnecessary for DNS names.
    authority = value.split("://", 1)[1].split("/", 1)[0].split("?", 1)[0].split("#", 1)[0] if "://" in value else ""
    if "%" in authority:
        raise UnsafeURLError("Percent-encoding is not allowed in URL authority")

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

    try:
        literal_ip = ipaddress.ip_address(ascii_host)
        addresses = [str(literal_ip)]
    except ValueError:
        addresses = list((resolver or _resolve_public_addresses)(ascii_host, expected_port))

    if not addresses:
        raise UnsafeURLError("Hostname did not resolve to an address")
    for address in addresses:
        try:
            parsed_ip = ipaddress.ip_address(address)
        except ValueError as exc:
            raise UnsafeURLError("Resolver returned an invalid IP address") from exc
        if not parsed_ip.is_global:
            raise UnsafeURLError("URL resolves to a non-public IP address")
    return value
