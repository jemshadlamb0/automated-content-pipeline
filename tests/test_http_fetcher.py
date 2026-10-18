import pytest

from acp.security.url_policy import UnsafeURLError
from acp.sources.http_fetcher import HTTPFetchError, RawHTTPResponse, SafeHTTPFetcher

PUBLIC_IP = "93.184.216.34"
HTML_HEADERS = {"content-type": "text/html; charset=utf-8"}


def resolver(host, port):
    return [PUBLIC_IP]


def test_fetch_is_pinned_to_validated_public_address():
    seen = []

    def requester(destination, timeout, max_bytes):
        seen.append((destination.host, destination.addresses, timeout, max_bytes))
        return RawHTTPResponse(200, HTML_HEADERS, b"<html>Hello</html>")

    client = SafeHTTPFetcher(resolver=resolver, requester=requester, max_response_bytes=4096)
    response = client.fetch("https://news.example.org/story")
    assert response.text() == "<html>Hello</html>"
    assert seen[0][0:2] == ("news.example.org", (PUBLIC_IP,))


def test_redirect_to_private_ip_is_rejected_before_second_request():
    calls = []

    def requester(destination, timeout, max_bytes):
        calls.append(destination.host)
        return RawHTTPResponse(302, {"location": "https://127.0.0.1/admin"}, b"")

    client = SafeHTTPFetcher(resolver=resolver, requester=requester, max_response_bytes=4096)
    with pytest.raises(UnsafeURLError):
        client.fetch("https://news.example.org/story")
    assert calls == ["news.example.org"]


def test_redirect_to_http_is_rejected():
    def requester(destination, timeout, max_bytes):
        return RawHTTPResponse(302, {"location": "http://news.example.org/story"}, b"")

    client = SafeHTTPFetcher(resolver=resolver, requester=requester, max_response_bytes=4096)
    with pytest.raises(HTTPFetchError, match="HTTPS-to-HTTP"):
        client.fetch("https://news.example.org/story")


def test_redirect_allowlist_is_enforced_on_every_hop():
    def requester(destination, timeout, max_bytes):
        return RawHTTPResponse(302, {"location": "https://other.example.org/story"}, b"")

    client = SafeHTTPFetcher(resolver=resolver, requester=requester, max_response_bytes=4096)
    with pytest.raises(HTTPFetchError, match="allowlist"):
        client.fetch("https://news.example.org/story", allowed_hosts=["news.example.org"])


def test_retries_transient_status_once():
    statuses = iter([503, 200])

    def requester(destination, timeout, max_bytes):
        return RawHTTPResponse(next(statuses), HTML_HEADERS, b"ok")

    client = SafeHTTPFetcher(
        resolver=resolver, requester=requester, sleeper=lambda _: None,
        max_retries=1, max_response_bytes=4096,
    )
    assert client.fetch("https://news.example.org/story").body == b"ok"


def test_rejects_unexpected_content_type():
    client = SafeHTTPFetcher(
        resolver=resolver,
        requester=lambda *_: RawHTTPResponse(200, {"content-type": "video/mp4"}, b"video"),
        max_response_bytes=4096,
    )
    with pytest.raises(HTTPFetchError, match="Unexpected content type"):
        client.fetch("https://news.example.org/story")


def test_rejects_encoded_response_to_avoid_decompression_bombs():
    client = SafeHTTPFetcher(
        resolver=resolver,
        requester=lambda *_: RawHTTPResponse(
            200, {"content-type": "text/html", "content-encoding": "gzip"}, b"not-decoded"
        ),
        max_response_bytes=4096,
    )
    with pytest.raises(HTTPFetchError, match="Compressed"):
        client.fetch("https://news.example.org/story")


def test_rejects_mocked_response_above_configured_body_cap():
    client = SafeHTTPFetcher(
        resolver=resolver,
        requester=lambda *_: RawHTTPResponse(200, HTML_HEADERS, b"x" * 2048),
        max_response_bytes=1024,
    )
    with pytest.raises(HTTPFetchError, match="size limit"):
        client.fetch("https://news.example.org/story")


def test_enforces_redirect_count():
    def requester(destination, timeout, max_bytes):
        return RawHTTPResponse(302, {"location": "/again"}, b"")

    client = SafeHTTPFetcher(
        resolver=resolver, requester=requester, max_redirects=1, max_response_bytes=4096
    )
    with pytest.raises(HTTPFetchError, match="redirect count"):
        client.fetch("https://news.example.org/story")


def test_rejects_invalid_fetcher_limits():
    with pytest.raises(ValueError):
        SafeHTTPFetcher(timeout_seconds=100)
    with pytest.raises(ValueError):
        SafeHTTPFetcher(max_redirects=100)
