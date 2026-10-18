import pytest
from acp.config import ConfigurationError, effective_region, load_profile, validate_language_selection

CONFIG = "config"


def test_auto_region_uses_locale_default():
    language = load_profile("languages", "ml-IN", CONFIG)
    validate_language_selection(language, None, "AUTO")
    assert effective_region(language, "AUTO") == "IN-KL"


def test_ambiguous_language_requires_explicit_region():
    language = load_profile("languages", "bn", CONFIG)
    with pytest.raises(ConfigurationError):
        validate_language_selection(language, None, "AUTO")
    assert effective_region(language, "IN-WB") == "IN-WB"


def test_language_with_no_region_default_requires_selection():
    language = load_profile("languages", "es", CONFIG)
    with pytest.raises(ConfigurationError):
        effective_region(language, "AUTO")


def test_family_profile_needs_explicit_variety():
    language = load_profile("languages", "raj", CONFIG)
    with pytest.raises(ConfigurationError):
        validate_language_selection(language, "", "IN-RJ")
