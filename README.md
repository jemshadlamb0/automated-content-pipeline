# Automated Content Pipeline

A configurable foundation for multilingual, source-grounded publishing with Hugging Face model support and a shared Telegram control plane.

> **Status: early foundation release, not an end-to-end publisher yet.** Configuration validation, niche/language/tone/approach profiles, regional scoring, RSS/Atom XML parsing, structured output validation, editorial prompt construction, an optional local Hugging Face adapter and secret-free CI are included. Production source fetching, article extraction, the multi-tenant Telegram control plane, persistent production queue, publishing/media adapters and billing are not implemented. Publishing remains disabled by default.

## Included now

- Niche profiles: AI, technology, sports, entertainment, science, health, finance, crypto, photography, automotive, gaming, business, education and environment.
- Locale profiles: Malayalam (India), English (India), Hindi (India), Tamil (India), Spanish and Arabic.
- Tone profiles: broadcast, neutral, conversational and analytical.
- Approach profiles: explainer, news brief, analysis and roundup.
- A deterministic weighted candidate scorer and local/national/global allocation helper. Signal extraction and region detection still need implementation; the weights are configurable starting assumptions, not a validated ranking model.
- An RSS/Atom parser for feed XML that has already been fetched. Safe network fetching and publisher URL resolution are not yet implemented.
- A structured article-output validator. It checks fields, length and the expected source URL; it is not a semantic fact-checker.
- An optional CPU-only local Hugging Face/Transformers adapter. Model downloads and inference may be slow or exceed runner memory.
- CI tests that do not require secrets and do not publish content.

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

Review the model card, licence, target-language support, RAM requirements and quality before setting `generation.model_id`. Downloading an open-weight model is not a guarantee of fast CPU inference or fluent output in every supported language.

## Safety defaults

- Publication disabled; dry-run enabled.
- No secrets or model weights in the repository.
- No automatic paid hosted-inference fallback.
- No image/video rehosting without appropriate reuse permission.
- Finance, crypto and health topics have stricter editorial guardrails.
- Generated output validation does not replace human review or independent fact-checking.

## Target architecture

The intended design separates a central, owner-operated Telegram control plane from a separately budgeted execution plane. The control plane will manage tenants, channel mappings, commands, entitlements and quotas; execution workers will discover sources, extract evidence, generate and validate articles, and publish only to verified user destinations.

See [architecture](docs/ARCHITECTURE.md), [configuration](docs/CONFIGURATION.md), [security](docs/SECURITY.md), and [roadmap](docs/ROADMAP.md).

Use GitHub for source control, CI, tests, releases and trusted deployment workflows. Do not assume GitHub Actions is an appropriate production runtime for a paid service; review the applicable GitHub terms before launch.

## License

No licence has been added yet. Public visibility alone does not grant permission to reuse, modify or redistribute this project. Confirm the intended commercial and contribution policy before adding a licence.
