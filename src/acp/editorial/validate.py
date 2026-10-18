"""Validation helpers for structured output from an editorial model."""
from __future__ import annotations
import json
from typing import Any
from urllib.parse import urlparse


class ArticleValidationError(ValueError):
    """Raised when generated article output fails basic editorial checks."""


def _valid_http_url(value: str) -> bool:
    parsed = urlparse(value)
    return (
        parsed.scheme in {"http", "https"}
        and bool(parsed.hostname)
        and parsed.username is None
        and parsed.password is None
        and len(value) <= 4096
        and not any(ord(char) < 0x20 or char.isspace() for char in value)
    )


def validate_article_output(
    raw_output: str | dict[str, Any],
    expected_source_url: str,
    max_body_chars: int = 16000,
) -> dict[str, Any]:
    """Parse and validate required fields; these checks are not semantic fact-checking."""
    if not 1 <= max_body_chars <= 100000:
        raise ValueError("max_body_chars must be between 1 and 100000")
    if not _valid_http_url(expected_source_url):
        raise ValueError("expected_source_url must be a valid HTTP(S) URL")

    if isinstance(raw_output, str):
        text = raw_output.strip()
        fence = chr(96) * 3
        if text.startswith(fence):
            lines = text.splitlines()
            if lines and lines[0].startswith(fence):
                lines = lines[1:]
            if lines and lines[-1].strip() == fence:
                lines = lines[:-1]
            text = "\n".join(lines).strip()
        try:
            data = json.loads(text)
        except json.JSONDecodeError as exc:
            raise ArticleValidationError(f"Model output is not valid JSON: {exc.msg}") from exc
    else:
        data = raw_output

    if not isinstance(data, dict):
        raise ArticleValidationError("Model output must be a JSON object")
    for key in ("headline", "standfirst", "body", "source_url"):
        if not isinstance(data.get(key), str) or not data[key].strip():
            raise ArticleValidationError(f"Required field '{key}' must be a non-empty string")
    if len(data["headline"]) > 300:
        raise ArticleValidationError("headline exceeds 300 characters")
    if len(data["standfirst"]) > 1000:
        raise ArticleValidationError("standfirst exceeds 1000 characters")
    if len(data["body"]) > max_body_chars:
        raise ArticleValidationError(f"body exceeds configured maximum of {max_body_chars} characters")
    if not _valid_http_url(data["source_url"]):
        raise ArticleValidationError("source_url is not a valid HTTP(S) URL")
    if data["source_url"].strip() != expected_source_url.strip():
        raise ArticleValidationError("generated source_url does not match the expected publisher URL")

    for key in ("key_facts", "uncertainties"):
        if key in data and (
            not isinstance(data[key], list)
            or len(data[key]) > 100
            or any(not isinstance(value, str) or len(value) > 2000 for value in data[key])
        ):
            raise ArticleValidationError(f"'{key}' must be a bounded list of strings when provided")
    if "requires_human_review" in data and not isinstance(data["requires_human_review"], bool):
        raise ArticleValidationError("'requires_human_review' must be a boolean")
    return data
