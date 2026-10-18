from scripts.check_secrets import detect_secrets


def test_detects_telegram_token_without_echoing_it():
    synthetic = "123456789:" + ("Abcdefghijklmnopqrstuvwxyz123456789"[:35])
    assert "Telegram bot token" in detect_secrets(synthetic)


def test_detects_huggingface_token():
    synthetic = "hf_" + ("A1" * 15)
    assert "Hugging Face token" in detect_secrets(synthetic)


def test_allows_example_environment_placeholders():
    content = "TELEGRAM_BOT_TOKEN=replace_me_with_your_token"
    assert detect_secrets(content) == []


def test_private_key_pattern_is_detected():
    marker = "-----BEGIN " + "PRIVATE KEY-----"
    assert "Private key material" in detect_secrets(marker)
