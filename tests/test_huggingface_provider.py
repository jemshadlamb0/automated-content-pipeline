import pytest
from acp.providers.huggingface_local import HuggingFaceLocalProvider


def test_local_provider_requires_a_model_id():
    with pytest.raises(ValueError, match="model_id"):
        HuggingFaceLocalProvider(model_id="", revision="a" * 40)


@pytest.mark.parametrize("revision", ["", "main", "v1.0", "a" * 39, "g" * 40, "a" * 41])
def test_local_provider_rejects_mutable_or_invalid_revision_before_import(revision):
    with pytest.raises(ValueError, match="immutable Hugging Face commit SHA"):
        HuggingFaceLocalProvider(model_id="someorg/somemodel", revision=revision)


def test_local_provider_rejects_non_cpu_device():
    with pytest.raises(ValueError, match="CPU only"):
        HuggingFaceLocalProvider(model_id="someorg/somemodel", revision="a" * 40, device="cuda")
