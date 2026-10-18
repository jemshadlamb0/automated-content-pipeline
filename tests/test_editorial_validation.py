import pytest
from acp.editorial.validate import ArticleValidationError, validate_article_output

ARTICLE = {
    "headline": "A development",
    "standfirst": "A short summary.",
    "body": "The source reports a development.",
    "source_name": "Example Publisher",
    "source_url": "https://example.com/story",
    "key_facts": ["One source-supported fact."],
    "uncertainties": [],
    "requires_human_review": False,
}


def test_valid_article_is_accepted():
    result = validate_article_output(ARTICLE, "https://example.com/story")
    assert result["headline"] == "A development"


def test_source_url_must_match_expected_url():
    with pytest.raises(ArticleValidationError):
        validate_article_output({**ARTICLE, "source_url": "https://other.example/story"}, "https://example.com/story")


def test_body_limit_is_enforced():
    with pytest.raises(ArticleValidationError):
        validate_article_output({**ARTICLE, "body": "x" * 20}, "https://example.com/story", max_body_chars=10)


def test_markdown_json_fence_is_supported():
    import json
    wrapped = chr(96) * 3 + "json\n" + json.dumps(ARTICLE) + "\n" + chr(96) * 3
    assert validate_article_output(wrapped, "https://example.com/story")["source_url"] == ARTICLE["source_url"]
