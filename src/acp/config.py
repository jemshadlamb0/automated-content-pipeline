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

    profile = settings["profile"]
    for key in ("niche", "language", "tone", "approach"):
        value = profile.get(key)
        if not isinstance(value, str) or not value.strip():
            raise ConfigurationError(f"profile.{key} must be a non-empty string")
    custom = profile.get("custom_instructions", "")
    if not isinstance(custom, str) or len(custom) > 2000:
        raise ConfigurationError("profile.custom_instructions must be text with a maximum of 2000 characters")

    schedule = settings["schedule"]
    for key in ("poll_interval_minutes", "min_post_interval_minutes", "max_posts_per_run", "max_posts_per_day"):
        value = schedule.get(key)
        if not isinstance(value, int) or isinstance(value, bool) or value < 1:
            raise ConfigurationError(f"schedule.{key} must be a positive integer")
    if schedule["poll_interval_minutes"] > 1440:
        raise ConfigurationError("schedule.poll_interval_minutes must not exceed 1440")
    if schedule["max_posts_per_run"] > 20 or schedule["max_posts_per_day"] > 500:
        raise ConfigurationError("Post caps exceed the safe configured maximum")

    limits = settings["limits"]
    for key in ("max_model_requests_per_run", "max_model_requests_per_day", "max_publications_per_month"):
        value = limits.get(key)
        if not isinstance(value, int) or isinstance(value, bool) or value < 1:
            raise ConfigurationError(f"limits.{key} must be a positive integer")
    media_cap = limits.get("max_media_download_bytes")
    if not isinstance(media_cap, int) or isinstance(media_cap, bool) or not 1 <= media_cap <= 50_000_000:
        raise ConfigurationError("limits.max_media_download_bytes must be between 1 and 50000000")

    generation = settings["generation"]
    for key, minimum, maximum in (("max_new_tokens", 1, 4096), ("max_input_characters", 100, 50000)):
        value = generation.get(key)
        if not isinstance(value, int) or isinstance(value, bool) or not minimum <= value <= maximum:
            raise ConfigurationError(f"generation.{key} must be between {minimum} and {maximum}")
    if generation.get("allow_paid_fallback") is not False:
        raise ConfigurationError("generation.allow_paid_fallback must remain false by default")

    publication = settings["publication"]
    if publication.get("enabled") is True and publication.get("dry_run") is True:
        raise ConfigurationError("publication.enabled cannot be true while publication.dry_run is true")
    if settings["safety"].get("publish_unlicensed_media") is not False:
        raise ConfigurationError("safety.publish_unlicensed_media must remain false")
    return settings


def load_profile(kind: str, profile_id: str, config_dir: str | Path = "config") -> dict[str, Any]:
    """Load a known profile ID and reject path traversal."""
    allowed = {"niches", "languages", "tones", "approaches", "sources"}
    if kind not in allowed:
        raise ConfigurationError(f"Unsupported profile kind: {kind}")
    if not profile_id or len(profile_id) > 64 or any(
        c not in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_" for c in profile_id
    ):
        raise ConfigurationError("Invalid profile identifier")
    path = Path(config_dir) / kind / f"{profile_id}.yaml"
    profile = _read_yaml(path)
    if profile.get("id") != profile_id:
        raise ConfigurationError(f"Profile id mismatch in {path}")
    return profile


def validate_language_selection(
    language_profile: dict[str, Any],
    variant: str | None,
    region: str | None,
) -> None:
    """Fail closed when a family-level language or ambiguous region is unresolved."""
    if language_profile.get("requires_variant"):
        selected = variant.strip() if isinstance(variant, str) else ""
        if not selected:
            raise ConfigurationError(
                f"{language_profile.get('name', 'Selected language')} is a family/group profile; "
                "set profile.language_variant to a specific variety before use."
            )
        if len(selected) > 100:
            raise ConfigurationError("profile.language_variant must not exceed 100 characters")
    explicit_region = isinstance(region, str) and bool(region.strip()) and region.upper() != "AUTO"
    if (language_profile.get("region_selection_required") or not language_profile.get("default_region")) and not explicit_region:
        raise ConfigurationError(
            f"{language_profile.get('name', 'Selected language')} needs an explicit profile.region selection."
        )


def effective_region(language_profile: dict[str, Any], requested_region: str | None) -> str:
    """Resolve AUTO to the locale default; ambiguous languages must be set explicitly."""
    if isinstance(requested_region, str) and requested_region.strip() and requested_region.upper() != "AUTO":
        return requested_region.strip()
    default = language_profile.get("default_region")
    if not default:
        raise ConfigurationError(
            f"{language_profile.get('name', 'Selected language')} has no default region; choose one explicitly."
        )
    return str(default)
