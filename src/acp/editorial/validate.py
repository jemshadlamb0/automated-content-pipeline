"""Validation helpers for structured output from an editorial model."""
from __future__ import annotations
import json
from typing import Any
from urllib.parse import urlparse


class ArticleValidationError(ValueError):
    """Raised when generated article output fails basic editorial checks."""


def validate_article_output(
    raw_output: str | dict[str, Any],
    expected_source_url: str,
    max_body_chars: int = 16000,
) -> dict[str, Any]:
    """Parse and validate required fields; this is not semantic fact-checking."""
    if max_body_chars < 1:
        raise ValueError("max_body_chars must be positive")
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
    if len(data["body"]) > max_body_chars:
        raise ArticleValidationError(f"body exceeds configured maximum of {max_body_chars} characters")

    source = urlparse(data["source_url"])
    if source.scheme not in {"http", "https"} or not source.hostname or source.username or source.password:
        raise ArticleValidationError("source_url is not a valid HTTP(S) URL")
    if data["source_url"].strip() != expected_source_url.strip():
        raise ArticleValidationError("generated source_url does not match the expected publisher URL")

    for key in ("key_facts", "uncertainties"):
        if key in data and (not isinstance(data[key], list) or any(not isinstance(value, str) for value in data[key])):
            raise ArticleValidationError(f"'{key}' must be a list of strings when provided")
    if "requires_human_review" in data and not isinstance(data["requires_human_review"], bool):
        raise ArticleValidationError("'requires_human_review' must be a boolean")
    return data
