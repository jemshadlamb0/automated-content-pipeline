# Automated Content Pipeline

A configurable foundation for multilingual, source-grounded news publishing with Hugging Face model support and a shared Telegram control plane.

> **Status: early foundation release; the safe source-ingestion slice is under development.** The repository includes profile-driven configuration, a local Hugging Face adapter, editorial prompt composition, regional-scoring utilities, defensive RSS/Atom parsing, structured output validation, SSRF URL-policy primitives, security checks and CI. The complete multi-tenant Telegram control plane, durable job queue, live publishing/media adapter and billing are not implemented. Publishing is disabled by default.

## Included profiles

**Niches:** AI, technology, sports, entertainment, science, health, finance, crypto, photography, automotive, gaming, business, education and environment.

**Languages/locales:** Malayalam, English (India), Hindi, Tamil, Spanish, Arabic, French, Bengali, Portuguese, Russian, Indonesian, Urdu, German, Japanese, Nigerian Pidgin, Persian, Marathi, Vietnamese, Telugu, Turkish, Malay (Malaysia), Dutch, Assamese, Italian, Odia, Bihari language family, Rajasthani language group, Punjabi, Bhojpuri, Kannada and Gujarati.

Language does not uniquely identify a region. Users can override the region; ambiguous languages require an explicit region. Bihari and Rajasthani require a specific variety before unattended use. Language profiles do not guarantee a model's editorial quality.

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

Review the model card, licence, provenance, target-language performance, RAM requirements and immutable revision before use. CPU inference may be slow or unsuitable for long articles.

## Safe source-ingestion CLI

The secure HTTP fetcher and source discovery are included in the Phase 1 implementation. These local commands inspect feeds and source text without generating AI articles or publishing:

~~~bash
# Fetch configured RSS feeds, deduplicate candidates and print JSON; no publishing.
python -m acp.main --discover-feeds

# Fetch one public HTTPS article and extract bounded evidence; no publishing.
python -m acp.main --fetch-article https://publisher.example/news/story

# Validate settings/profiles.
python -m acp.main --check-config
~~~

To use feed discovery, add trusted source definitions to sources.feeds in config/settings.yaml. Example schema:

~~~yaml
sources:
  feeds:
    - name: Example publisher RSS
      url: https://publisher.example/rss.xml
      region_tier: local
      allowed_hosts:
        - publisher.example
~~~

Only HTTPS is accepted by default. The hostname allowlist constrains the feed and any redirect destinations. Do not add feed URLs you do not trust. These CLI operations do not generate AI articles or publish to Telegram.

The parser retains publisher-provided RSS `content:encoded` and Atom `content` separately from short descriptions. Full embedded text is omitted from CLI JSON unless explicitly requested with `--include-feed-content`. If a publisher page responds with HTTP 403 or another access restriction, the pipeline must not try to bypass it; use permitted embedded content, an official documented API/licensed feed, or keep the item metadata-only. See [Source content acquisition and use policy](docs/wiki/source-content-policy.md).

## Wiki

- [Versioned Wiki source](docs/wiki/README.md)
- [Main branch protection guide](docs/BRANCH_PROTECTION.md)
- [Actual GitHub Wiki tab](https://github.com/jemshadlamb0/automated-content-pipeline/wiki)

The actual Wiki is separate from the source repository. Initialize it once in the GitHub UI, then sync prepared pages from a trusted local clone using the dry-run mode of scripts/publish_wiki.py, followed by scripts/publish_wiki.py.

## Security

- Publication is disabled and dry-run is enabled.
- Never commit tokens, model weights, caches, private data or fetched media.
- No automatic paid inference fallback.
- Feed parsing uses a defensive XML parser and bounded document/item counts.
- The source fetcher validates every redirect, connects to a validated IP, checks TLS against the original hostname, disallows downgrade redirects, limits response size and time, and restricts content types.
- URL/fetcher tests use mocked responses; CI does not crawl real publishers.
- The best-effort secret scanner, Bandit, pip-audit and CodeQL reduce risk but cannot prove the repository is invulnerable.

The URL fetcher is only for bounded text/feed requests, not video downloads. Public media is not automatically licensed for redistribution. See [Security policy](SECURITY.md) and [Security Handbook](docs/wiki/security-handbook.md).

## Architecture status

The intended design separates one owner-operated Telegram bot/control plane from a separately budgeted execution plane. Source ingestion must be reliable before inference or publishing is activated. See [roadmap](docs/ROADMAP.md).

## Licence

A licence has not been added yet. Public visibility alone does not grant permission to reuse, modify or redistribute the code. Confirm the intended commercial and contribution policy before adding one.
