"""Load and validate file-based application configuration."""
from __future__ import annotations
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit
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


def _bounded_int(mapping: dict[str, Any], key: str, minimum: int, maximum: int, prefix: str) -> int:
    value = mapping.get(key)
    if not isinstance(value, int) or isinstance(value, bool) or not minimum <= value <= maximum:
        raise ConfigurationError(f"{prefix}.{key} must be an integer between {minimum} and {maximum}")
    return value


def _validate_feed_url(value: str, index: int) -> None:
    if not isinstance(value, str) or not value.strip() or len(value) > 4096:
        raise ConfigurationError(f"sources.feeds[{index}].url must be a non-empty URL")
    if any(ord(char) < 0x20 or char.isspace() for char in value) or "\\" in value:
        raise ConfigurationError(f"sources.feeds[{index}].url contains whitespace, control characters or backslashes")
    try:
        parsed = urlsplit(value)
        port = parsed.port
    except ValueError as exc:
        raise ConfigurationError(f"sources.feeds[{index}].url is malformed") from exc
    if (
        parsed.scheme.lower() != "https"
        or not parsed.hostname
        or parsed.username is not None
        or parsed.password is not None
        or parsed.fragment
        or port not in (None, 443)
    ):
        raise ConfigurationError(f"sources.feeds[{index}].url must be an HTTPS URL on the standard port without credentials or fragments")
    authority = value.split("://", 1)[1].split("/", 1)[0].split("?", 1)[0].split("#", 1)[0]
    if "%" in authority:
        raise ConfigurationError(f"sources.feeds[{index}].url must not percent-encode the authority")


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

    sources = settings["sources"]
    _bounded_int(sources, "max_candidates_per_run", 1, 500, "sources")
    _bounded_int(sources, "max_items_per_feed", 1, 500, "sources")
    _bounded_int(sources, "freshness_hours", 1, 8760, "sources")
    _bounded_int(sources, "max_response_bytes", 1024, 10_000_000, "sources")
    _bounded_int(sources, "max_redirects", 0, 5, "sources")
    _bounded_int(sources, "max_retries", 0, 2, "sources")
    timeout_value = sources.get("timeout_seconds")
    if (
        not isinstance(timeout_value, (int, float))
        or isinstance(timeout_value, bool)
        or not 0.5 <= timeout_value <= 30
    ):
        raise ConfigurationError("sources.timeout_seconds must be between 0.5 and 30")
    feeds = sources.get("feeds")
    if not isinstance(feeds, list) or len(feeds) > 100:
        raise ConfigurationError("sources.feeds must be a list containing at most 100 feed definitions")
    for index, feed in enumerate(feeds):
        if not isinstance(feed, dict):
            raise ConfigurationError(f"sources.feeds[{index}] must be a mapping")
        _validate_feed_url(feed.get("url"), index)
        name = feed.get("name", "Unnamed feed")
        if not isinstance(name, str) or len(name) > 200:
            raise ConfigurationError(f"sources.feeds[{index}].name must be text up to 200 characters")
        if feed.get("region_tier", "global") not in {"local", "national", "global"}:
            raise ConfigurationError(f"sources.feeds[{index}].region_tier must be local, national or global")
        allowed_hosts = feed.get("allowed_hosts")
        if allowed_hosts is not None and (
            not isinstance(allowed_hosts, list)
            or len(allowed_hosts) > 50
            or any(not isinstance(host, str) or not host.strip() or len(host) > 253 for host in allowed_hosts)
        ):
            raise ConfigurationError(f"sources.feeds[{index}].allowed_hosts must be a list of at most 50 host patterns")

    limits = settings["limits"]
    _bounded_int(limits, "max_model_requests_per_run", 1, 500, "limits")
    _bounded_int(limits, "max_model_requests_per_day", 1, 10000, "limits")
    _bounded_int(limits, "max_publications_per_month", 1, 10000, "limits")
    _bounded_int(limits, "max_media_download_bytes", 1, 50_000_000, "limits")

    generation = settings["generation"]
    _bounded_int(generation, "max_new_tokens", 1, 4096, "generation")
    _bounded_int(generation, "max_input_characters", 100, 50000, "generation")
    temperature = generation.get("temperature")
    if not isinstance(temperature, (int, float)) or isinstance(temperature, bool) or not 0 <= temperature <= 2:
        raise ConfigurationError("generation.temperature must be between 0 and 2")
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
    """Resolve AUTO to a locale default; ambiguous languages require an override."""
    if isinstance(requested_region, str) and requested_region.strip() and requested_region.upper() != "AUTO":
        return requested_region.strip()
    default = language_profile.get("default_region")
    if not default:
        raise ConfigurationError(
            f"{language_profile.get('name', 'Selected language')} has no default region; choose one explicitly."
        )
    return str(default)
