import pytest

from acp.security.url_policy import UnsafeURLError, resolve_public_http_url

PUBLIC_IPS = ["93.184.216.34", "1.1.1.1"]


def test_resolver_returns_the_validated_addresses_for_ip_pinning():
    calls = []

    def resolver(host, port):
        calls.append((host, port))
        return PUBLIC_IPS

    destination = resolve_public_http_url(
        "https://NEWS.example.org/story?x=1",
        resolver=resolver,
    )
    assert destination.host == "news.example.org"
    assert destination.port == 443
    assert destination.addresses == tuple(PUBLIC_IPS)
    assert destination.request_target == "/story?x=1"
    assert calls == [("news.example.org", 443)]


def test_rejects_fragment_in_fetch_url():
    with pytest.raises(UnsafeURLError, match="fragments"):
        resolve_public_http_url("https://news.example.org/story#section", resolver=lambda *_: PUBLIC_IPS)


def test_rejects_any_private_answer_in_dns_set():
    with pytest.raises(UnsafeURLError, match="non-public"):
        resolve_public_http_url(
            "https://mixed.example.org/",
            resolver=lambda *_: ["93.184.216.34", "10.0.0.4"],
        )


def test_rejects_dns_answer_with_invalid_address():
    with pytest.raises(UnsafeURLError, match="invalid IP"):
        resolve_public_http_url(
            "https://bad-dns.example.org/",
            resolver=lambda *_: ["not-an-ip"],
        )
