from pathlib import Path
import re

import pytest

from acp.config import ConfigurationError, load_settings

ROOT = Path(__file__).resolve().parents[1]
DEFAULT = ROOT / "config" / "settings.yaml"


def _write_settings(tmp_path, replacement_from, replacement_to):
    text = DEFAULT.read_text(encoding="utf-8")
    # Keep validation tests independent from any trusted feeds configured for live runs.
    text = re.sub(
        r"(?ms)^  feeds:.*?(?=^[A-Za-z0-9_-]+:|\\Z)",
        "  feeds: []\n",
        text,
        count=1,
    )
    assert replacement_from in text
    path = tmp_path / "settings.yaml"
    path.write_text(text.replace(replacement_from, replacement_to), encoding="utf-8")
    return path


@pytest.mark.parametrize(("key", "value"), [
    ("max_redirects", "6"),
    ("max_retries", "3"),
    ("max_response_bytes", "200000000"),
    ("max_candidates_per_run", "0"),
])
def test_out_of_range_source_limits_are_rejected(tmp_path, key, value):
    path = _write_settings(tmp_path, f"  {key}: " + {
        "max_redirects": "3",
        "max_retries": "1",
        "max_response_bytes": "2000000",
        "max_candidates_per_run": "30",
    }[key], f"  {key}: {value}")
    with pytest.raises(ConfigurationError):
        load_settings(path)


def test_configured_feed_must_be_https(tmp_path):
    path = _write_settings(
        tmp_path,
        "  feeds: []",
        '  feeds:\\n    - name: Bad feed\\n      url: http://news.example.org/rss\\n',
    )
    with pytest.raises(ConfigurationError, match="HTTPS URL"):
        load_settings(path)


def test_configured_feed_cannot_embed_credentials(tmp_path):
    path = _write_settings(
        tmp_path,
        "  feeds: []",
        '  feeds:\\n    - name: Bad feed\\n      url: https://user:pass@news.example.org/rss\\n',
    )
    with pytest.raises(ConfigurationError, match="HTTPS URL"):
        load_settings(path)
