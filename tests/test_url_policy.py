import pytest
from acp.security.url_policy import UnsafeURLError, validate_public_http_url


def public_resolver(host, port):
    return ["93.184.216.34"]


def private_resolver(host, port):
    return ["93.184.216.34", "127.0.0.1"]


def test_allows_https_public_host():
    assert validate_public_http_url("https://news.example.org/story", resolver=public_resolver).startswith("https://")


@pytest.mark.parametrize("url", [
    "http://news.example.org/story",
    "https://user:pass@example.org/",
    "https://localhost/",
    "https://service.local/",
    "https://127.0.0.1/",
    "https://10.1.2.3/",
    "https://169.254.169.254/latest/meta-data/",
    "https://example.org:8443/",
    " https://example.org/",
    "https://example.org%2f@evil.example.net/",
    "https://example.org/\\\\evil.example.net/",
])
def test_rejects_dangerous_urls(url):
    with pytest.raises(UnsafeURLError):
        validate_public_http_url(url, resolver=public_resolver)


def test_explicit_http_allowance_is_limited_to_port_80():
    assert validate_public_http_url("http://news.example.org/feed", allow_http=True, resolver=public_resolver)
    with pytest.raises(UnsafeURLError):
        validate_public_http_url("http://news.example.org:8080/feed", allow_http=True, resolver=public_resolver)


def test_rejects_mixed_public_and_private_dns_answers():
    with pytest.raises(UnsafeURLError):
        validate_public_http_url("https://rebind.example.org/", resolver=private_resolver)


def test_rejects_empty_dns_answer():
    with pytest.raises(UnsafeURLError):
        validate_public_http_url("https://nxdomain.example.org/", resolver=lambda host, port: [])
