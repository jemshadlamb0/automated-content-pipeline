# Automated Content Pipeline

A configurable foundation for multilingual, source-grounded news publishing with Hugging Face model support and a shared Telegram control plane.

> **Status: early foundation release, not yet an end-to-end publisher.** This repository includes profile-driven configuration, a local Hugging Face adapter, source-grounded editorial prompt composition, a candidate-ranking helper, defensive RSS/Atom XML parsing, structured output validation, URL policy checks, secret-pattern scanning and CI. Production source fetching/article extraction, multi-tenant Telegram control plane, durable queue, live publishing/media adapters and billing remain unimplemented. Publishing is disabled by default.

## Included profiles

**Niches:** AI, technology, sports, entertainment, science, health, finance, crypto, photography, automotive, gaming, business, education and environment.

**Languages/locales:** Malayalam, English (India), Hindi, Tamil, Spanish, Arabic, French, Bengali, Portuguese, Russian, Indonesian, Urdu, German, Japanese, Nigerian Pidgin, Persian, Marathi, Vietnamese, Telugu, Turkish, Malay (Malaysia), Dutch, Assamese, Italian, Odia, Bihari language family, Rajasthani language group, Punjabi, Bhojpuri, Kannada and Gujarati.

Language does not uniquely identify a region. Users can override the region; Bengali and Arabic require explicit region selection. Bihari and Rajasthani are family/group profiles requiring a specific variety. Language profiles do not guarantee any particular model's writing quality.

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

Optional local Hugging Face inference dependencies:

~~~bash
python -m pip install -e ".[huggingface]"
~~~

Review the model card, licence, provenance, target-language performance, RAM requirements and immutable revision before use. CPU inference may be slow or impractical for long articles.

## Wiki

- [Versioned Wiki source and index](docs/wiki/README.md)
- [Main branch protection guide](docs/BRANCH_PROTECTION.md)
- [Actual GitHub Wiki tab](https://github.com/jemshadlamb0/automated-content-pipeline/wiki)

The GitHub Wiki tab is a separate Git repository and cannot be populated just by committing Markdown under docs/wiki/. To initialize it, click Wiki → Create the first page in GitHub and save it once. Then from a trusted local clone run:

~~~bash
python scripts/publish_wiki.py --dry-run
python scripts/publish_wiki.py
~~~

The script syncs the maintained documentation into the real Wiki using your normal Git credential helper. See [Publishing the actual GitHub Wiki](docs/wiki/publishing-the-wiki.md).

## Security

- Publication is disabled and dry-run is enabled.
- Secrets, model weights, caches and runtime data must not be committed.
- Paid hosted-inference fallback is disabled.
- Feed parsing uses a defensive XML parser and bounded document/item counts.
- URL policy rejects local/private/non-global destinations and suspicious URL structures. A production fetcher still needs redirect-hop validation and DNS-rebinding-resistant connection binding.
- CI runs Ruff, Bandit, pip-audit and a best-effort common-secret pattern scanner. These checks reduce risk but cannot guarantee that a repository is secret-free or invulnerable.
- Public media is not automatically licensed for redistribution.

See [Security policy](SECURITY.md) and [Security Handbook](docs/wiki/security-handbook.md).

Use GitHub for code review, CI, tests, releases and trusted deployment workflows. Do not assume GitHub Actions is an appropriate commercial production runtime; review applicable provider terms before launch.

## License

A licence has not been added yet. Public visibility alone does not grant permission to reuse, modify or redistribute this project. Confirm the intended commercial and contribution policy before adding a licence.
