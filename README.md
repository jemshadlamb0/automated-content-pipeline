# Automated Content Pipeline

A configurable foundation for multilingual, source-grounded publishing with Hugging Face model support and a shared Telegram control plane.

> **Status: foundation scaffold.** Configuration validation, an optional local Hugging Face adapter and editorial prompt composition are being built first. Production source fetching, the multi-tenant Telegram control plane, persistent job queues, full publishing/media adapters and billing are not implemented yet. Publishing remains disabled by default.

## Goals
- Configure niche, language/locale, tone, editorial approach, region and cadence without maintaining separate code branches.
- Write target-language editorial news, not sentence-by-sentence translations.
- Ground claims in source evidence and retain attribution.
- Use reviewed Hugging Face open-weight models locally where resources allow; never enable paid fallback silently.
- Operate one shared Telegram bot as a control panel while isolating each user's settings and channel.
- Enforce usage caps and fail safely when quotas or providers are unavailable.

## Quick start
Requires Python 3.11+.

```bash
python -m venv .venv
# Windows PowerShell: .venv\Scripts\Activate.ps1
# macOS/Linux: source .venv/bin/activate
python -m pip install -e ".[dev]"
python -m acp.main --check-config
pytest
```

Optional local inference dependencies:
```bash
python -m pip install -e ".[huggingface]"
```
Review the selected model's card, licence, target-language support and RAM/runtime requirements before setting `generation.model_id`. CPU inference may be slow or impractical for longer articles.

## Safety defaults
- Publication disabled; dry-run enabled.
- No secrets or model weights in the repository.
- No paid hosted inference fallback.
- No image/video rehosting without reuse permission.
- Finance, crypto and health content have stricter review requirements.

## Architecture status
The target design separates a central Telegram control plane from a separately budgeted execution plane. Implemented components and planned work are tracked in [the roadmap](docs/ROADMAP.md). See [architecture](docs/ARCHITECTURE.md), [configuration](docs/CONFIGURATION.md), and [security](docs/SECURITY.md).

GitHub should be used for source control, CI, tests, releases and trusted deployment workflows. Do not assume GitHub Actions is an appropriate production runtime for a paid service; review the applicable terms before launch.

## License
No licence has been added yet. Public visibility alone does not grant permission to reuse, modify or redistribute this project. Confirm the intended commercial and contribution policy before adding a licence.
