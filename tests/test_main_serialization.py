from acp.main import _candidate_json
from acp.sources.discovery import DiscoveredCandidate


def _candidate():
    return DiscoveredCandidate(
        candidate_id="abc123",
        title="Example story",
        url="https://news.example/story",
        normalized_url="https://news.example/story",
        summary="Short teaser",
        published_at=None,
        feed_name="Example RSS",
        feed_url="https://news.example/rss",
        region_tier="global",
        publisher_name="Example Publisher",
        feed_content="<p>Publisher-supplied full text.</p>",
        feed_content_type="text/html",
    )


def test_candidate_json_omits_embedded_body_by_default():
    payload = _candidate_json(_candidate())
    assert "feed_content" not in payload
    assert payload["feed_content_chars"] == len("<p>Publisher-supplied full text.</p>")
    assert payload["summary"] == "Short teaser"


def test_candidate_json_includes_embedded_body_only_on_explicit_opt_in():
    payload = _candidate_json(_candidate(), include_feed_content=True)
    assert payload["feed_content"] == "<p>Publisher-supplied full text.</p>"
    assert payload["feed_content_type"] == "text/html"
