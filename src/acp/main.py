"""CLI for validating the foundation configuration."""
from __future__ import annotations
import argparse
import json
import os
from pathlib import Path
from acp.config import ConfigurationError, load_profile, load_settings


def main() -> int:
    parser = argparse.ArgumentParser(description="Automated Content Pipeline foundation tools")
    parser.add_argument("--settings", default=os.getenv("ACP_SETTINGS", "config/settings.yaml"))
    parser.add_argument("--check-config", action="store_true", help="Validate settings and selected profiles")
    args = parser.parse_args()
    try:
        settings_path = Path(args.settings)
        settings = load_settings(settings_path)
        config_dir = settings_path.resolve().parent
        niche = load_profile("niches", settings["profile"]["niche"], config_dir)
        language = load_profile("languages", settings["profile"]["language"], config_dir)
        tone = load_profile("tones", settings["profile"]["tone"], config_dir)
        approach = load_profile("approaches", settings["profile"]["approach"], config_dir)
    except ConfigurationError as exc:
        parser.error(str(exc))
    if args.check_config:
        print(json.dumps({
            "status": "valid",
            "niche": niche["id"],
            "language": language["id"],
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
