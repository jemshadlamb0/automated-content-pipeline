"""Configuration validation and safe, non-publishing source-ingestion CLI."""
from __future__ import annotations

import argparse
import json
import os
from dataclasses import asdict
from pathlib import Path

from acp.config import (
    ConfigurationError,
    effective_region,
    load_profile,
    load_settings,
    validate_language_selection,
)
from acp.sources.article import extract_article
from acp.sources.discovery import discover_candidates
from acp.sources.http_fetcher import SafeHTTPFetcher


def _fetcher_from_settings(settings: dict) -> SafeHTTPFetcher:
    sources = settings["sources"]
    return SafeHTTPFetcher(
        timeout_seconds=float(sources["timeout_seconds"]),
        max_response_bytes=sources["max_response_bytes"],
        max_redirects=sources["max_redirects"],
        max_retries=sources["max_retries"],
        allow_http=False,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Automated Content Pipeline foundation tools")
    parser.add_argument("--settings", default=os.getenv("ACP_SETTINGS", "config/settings.yaml"))
    actions = parser.add_mutually_exclusive_group(required=True)
    actions.add_argument("--check-config", action="store_true", help="Validate settings and selected profiles")
    actions.add_argument("--discover-feeds", action="store_true", help="Fetch configured RSS feeds safely; never publish")
    actions.add_argument("--fetch-article", metavar="HTTPS_URL", help="Safely fetch and extract one public HTML article; never publish")
    parser.add_argument("--publisher-name", default="", help="Optional publisher label for --fetch-article")
    args = parser.parse_args()

    try:
        settings_path = Path(args.settings)
        settings = load_settings(settings_path)
        config_dir = settings_path.resolve().parent
        profile_settings = settings["profile"]
        niche = load_profile("niches", profile_settings["niche"], config_dir)
        language = load_profile("languages", profile_settings["language"], config_dir)
        tone = load_profile("tones", profile_settings["tone"], config_dir)
        approach = load_profile("approaches", profile_settings["approach"], config_dir)
        validate_language_selection(language, profile_settings.get("language_variant"), profile_settings.get("region"))
        region = effective_region(language, profile_settings.get("region"))
    except ConfigurationError as exc:
        parser.error(str(exc))

    if args.check_config:
        print(json.dumps({
            "status": "valid",
            "niche": niche["id"],
            "language": language["id"],
            "language_variant": profile_settings.get("language_variant") or None,
            "region": region,
            "tone": tone["id"],
            "approach": approach["id"],
            "publication_enabled": settings["publication"]["enabled"],
            "dry_run": settings["publication"]["dry_run"],
            "generation_provider": settings["generation"]["provider"],
            "model_configured": bool(settings["generation"].get("model_id")),
            "configured_feeds": len(settings["sources"]["feeds"]),
        }, indent=2))
        return 0

    fetcher = _fetcher_from_settings(settings)
    if args.discover_feeds:
        sources = settings["sources"]
        result = discover_candidates(
            sources["feeds"],
            fetcher,
            max_candidates=sources["max_candidates_per_run"],
            max_items_per_feed=sources["max_items_per_feed"],
        )
        print(json.dumps({
            "status": "completed_with_failures" if result.failures else "completed",
            "feeds_configured": len(sources["feeds"]),
            "feeds_checked": result.feeds_checked,
            "candidate_count": len(result.candidates),
            "candidates": [asdict(item) for item in result.candidates],
            "failures": [asdict(item) for item in result.failures],
            "publishing_performed": False,
        }, ensure_ascii=False, indent=2))
        return 0 if not result.failures else 2

    response = fetcher.fetch(args.fetch_article, allowed_content_types={"text/html", "application/xhtml+xml"})
    evidence = extract_article(
        response.text(),
        response.url,
        source_name=args.publisher_name,
        content_type=response.content_type,
    )
    print(json.dumps({
        "status": "extracted",
        "evidence": asdict(evidence),
        "publishing_performed": False,
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
