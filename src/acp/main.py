"""CLI for validating the foundation configuration."""
from __future__ import annotations
import argparse
import json
import os
from pathlib import Path
from acp.config import ConfigurationError, effective_region, load_profile, load_settings, validate_language_selection


def main() -> int:
    parser = argparse.ArgumentParser(description="Automated Content Pipeline foundation tools")
    parser.add_argument("--settings", default=os.getenv("ACP_SETTINGS", "config/settings.yaml"))
    parser.add_argument("--check-config", action="store_true", help="Validate settings and selected profiles")
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
        }, indent=2))
        return 0
    parser.print_help()
    print("\nNo live publishing is implemented in this foundation release.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
