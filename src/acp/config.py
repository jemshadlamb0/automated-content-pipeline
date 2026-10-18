"""Load and validate file-based application configuration."""
from __future__ import annotations
from pathlib import Path
from typing import Any
import yaml


class ConfigurationError(ValueError):
    """Raised when project configuration is invalid."""


def _read_yaml(path: Path) -> dict[str, Any]:
    try:
        with path.open("r", encoding="utf-8") as handle:
            value = yaml.safe_load(handle)
    except FileNotFoundError as exc:
        raise ConfigurationError(f"Configuration file not found: {path}") from exc
    except yaml.YAMLError as exc:
        raise ConfigurationError(f"Invalid YAML in {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise ConfigurationError(f"Expected a YAML mapping in {path}")
    return value


def load_settings(path: str | Path = "config/settings.yaml") -> dict[str, Any]:
    settings = _read_yaml(Path(path))
    sections = ("app", "profile", "schedule", "sources", "generation", "publication", "limits", "safety", "state")
    missing = [key for key in sections if not isinstance(settings.get(key), dict)]
    if missing:
        raise ConfigurationError(f"Missing or invalid sections: {', '.join(missing)}")
    for key in ("niche", "language", "tone", "approach"):
        value = settings["profile"].get(key)
        if not isinstance(value, str) or not value.strip():
            raise ConfigurationError(f"profile.{key} must be a non-empty string")
    for key in ("poll_interval_minutes", "min_post_interval_minutes", "max_posts_per_run", "max_posts_per_day"):
        value = settings["schedule"].get(key)
        if not isinstance(value, int) or isinstance(value, bool) or value < 1:
            raise ConfigurationError(f"schedule.{key} must be a positive integer")
    for key in ("max_model_requests_per_run", "max_model_requests_per_day", "max_publications_per_month"):
        value = settings["limits"].get(key)
        if not isinstance(value, int) or isinstance(value, bool) or value < 1:
            raise ConfigurationError(f"limits.{key} must be a positive integer")
    publication = settings["publication"]
    if publication.get("enabled") is True and publication.get("dry_run") is True:
        raise ConfigurationError("publication.enabled cannot be true while publication.dry_run is true")
    if settings["generation"].get("allow_paid_fallback") is not False:
        raise ConfigurationError("generation.allow_paid_fallback must remain false by default")
    if settings["safety"].get("publish_unlicensed_media") is not False:
        raise ConfigurationError("safety.publish_unlicensed_media must remain false")
    return settings


def load_profile(kind: str, profile_id: str, config_dir: str | Path = "config") -> dict[str, Any]:
    """Load a known profile ID and reject path traversal."""
    allowed = {"niches", "languages", "tones", "approaches", "sources"}
    if kind not in allowed:
        raise ConfigurationError(f"Unsupported profile kind: {kind}")
    if not profile_id or any(c not in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_" for c in profile_id):
        raise ConfigurationError("Invalid profile identifier")
    path = Path(config_dir) / kind / f"{profile_id}.yaml"
    profile = _read_yaml(path)
    if profile.get("id") != profile_id:
        raise ConfigurationError(f"Profile id mismatch in {path}")
    return profile
