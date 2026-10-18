# Automated Content Pipeline

A configurable foundation for multilingual, source-grounded news publishing with Hugging Face model support and a shared Telegram control plane.

> **Status: early foundation release, not yet an end-to-end publisher.** This repository includes profile-driven configuration, a local Hugging Face adapter, source-grounded editorial prompt composition, a candidate-ranking helper, RSS/Atom XML parsing, structured output validation, an SSRF URL-policy primitive, security tests and CI. Production source fetching/article extraction, multi-tenant Telegram control plane, durable queue, live publishing/media adapters and billing remain unimplemented. Publishing is disabled by default.

## Included profiles

**Niches:** AI, technology, sports, entertainment, science, health, finance, crypto, photography, automotive, gaming, business, education and environment.

**Languages/locales:** Malayalam, English (India), Hindi, Tamil, Spanish, Arabic, French, Bengali, Portuguese, Russian, Indonesian, Urdu, German, Japanese, Nigerian Pidgin, Persian, Marathi, Vietnamese, Telugu, Turkish, Malay (Malaysia), Dutch, Assamese, Italian, Odia, Bihari language family, Rajasthani language group, Punjabi, Bhojpuri, Kannada and Gujarati.

Language does not uniquely identify a region. Users must be able to override regional defaults; Bengali and Arabic require region selection. Bihari and Rajasthani are family/group placeholders and require a specific variety before use. Language profiles do not guarantee that a particular model writes that language accurately.

## Quick start

Requires Python 3.11+.

~~~bash
python -m venv .venv
# Windows PowerShell: .venv\Scripts\Activate.ps1
# macOS/Linux: source .venv/bin/activate
python -m pip install -e ".[dev]"
python -m acp.main --check-config
pytest
~~~

Optional local inference dependencies:

~~~bash
python -m pip install -e ".[huggingface]"
~~~

Review the Hugging Face model card, licence, provenance, target-language performance, RAM requirements and revision before use. CPU inference may be slow or impractical for long articles. Production should pin an approved immutable model revision.

## Safety defaults

- Publication is disabled and dry-run is enabled.
- Real tokens, model weights, caches and runtime data must not be committed.
- Paid hosted-inference fallback is disabled.
- RSS parsing uses a defensive XML parser and bounded input size.
- URL policy rejects private/non-global destinations, credentials, unexpected ports and unsafe schemes. A production fetcher must additionally validate every redirect and prevent DNS rebinding at connection time.
- Public images/videos are not automatically licensed for redistribution.
- Health, finance and crypto need stronger review policies.

## Wiki

Start with the [repository wiki index](docs/wiki/README.md). It includes setup, all language profiles, editorial policy, regional ranking, security, operations and the roadmap. These versioned pages are stored in the repository; they are not a separately hosted GitHub Wiki tab.

## Architecture and status

The intended design separates one owner-operated Telegram bot/control plane from a separately budgeted execution plane. The bot manages users and settings; the execution plane retrieves sources, extracts evidence, runs the selected model, validates output and publishes only to verified destinations.

See [architecture](docs/ARCHITECTURE.md), [configuration](docs/CONFIGURATION.md), [security policy](docs/SECURITY.md), and [roadmap](docs/ROADMAP.md).

Use GitHub for source control, CI, tests, releases and trusted deployment workflows. Do not assume GitHub Actions is an appropriate commercial production runtime; review the applicable terms before launch.

## Licence

A licence has not been added yet. Public repository visibility alone does not grant permission to reuse, modify or redistribute the code. Confirm the intended commercial and contribution policy before adding one.
