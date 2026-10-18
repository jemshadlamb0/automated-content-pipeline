from pathlib import Path
import pytest
from acp.config import ConfigurationError, load_profile, load_settings, validate_language_selection

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "config"


def test_every_language_profile_has_editorial_rules():
    paths = sorted((CONFIG / "languages").glob("*.yaml"))
    assert len(paths) >= 31
    for path in paths:
        profile = load_profile("languages", path.stem, CONFIG)
        assert profile.get("name")
        assert profile.get("editorial_rules")


def test_bihari_and_rajasthani_require_a_variety():
    for profile_id in ("bih", "raj"):
        profile = load_profile("languages", profile_id, CONFIG)
        with pytest.raises(ConfigurationError, match="family/group profile"):
            validate_language_selection(profile, "", "IN")


def test_bengali_requires_an_explicit_region():
    profile = load_profile("languages", "bn", CONFIG)
    with pytest.raises(ConfigurationError, match="explicit profile.region"):
        validate_language_selection(profile, None, "AUTO")
    validate_language_selection(profile, None, "IN-WB")


def test_settings_reject_excessive_custom_instructions(tmp_path):
    source = (CONFIG / "settings.yaml").read_text(encoding="utf-8")
    source = source.replace('custom_instructions: ""', 'custom_instructions: "' + ('x' * 2001) + '"')
    path = tmp_path / "settings.yaml"
    path.write_text(source, encoding="utf-8")
    with pytest.raises(ConfigurationError, match="2000 characters"):
        load_settings(path)
