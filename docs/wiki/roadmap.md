# Roadmap and service boundaries

## Foundation present
- Configuration validation and niche/language/tone/approach profiles.
- Hugging Face local provider interface.
- Editorial prompt composition and structured output validation.
- Regional weighted-scoring helper.
- Defensive RSS/Atom parser.
- URL policy helper plus IP-pinned, redirect-validating bounded HTTP fetcher.
- Feed candidate discovery, duplicate filtering and bounded HTML article extraction.
- Non-publishing CLI for configuration checks, feed discovery and one-article extraction.
- CI, static analysis, dependency audit, secret-pattern scanner, CodeQL and Dependabot.

## Remaining before end-to-end use
1. Curated feed catalogue, source-quality policies and real-world fixture coverage.
2. More robust publisher URL canonicalization, freshness checks and durable deduplication.
3. Region/entity detection and evidence-backed inputs to the regional ranking.
4. Structured inference integration, model revision pinning and per-language quality gates.
5. Claim-to-source review and human-review routing for high-impact stories.
6. Durable queue, locks, quotas and idempotent delivery.
7. Shared Telegram webhook, onboarding, installation authentication and channel verification.
8. Telegram publisher, formatting/escaping and rights-aware media-size fallback.
9. Monitoring, backups, support processes and managed premium entitlements.

## Release gates
- A: tests and security analysis pass.
- B: mocked ingestion and draft generation passes without secrets or publishing in CI.
- C: private test bot/channel, with authorization and idempotency scenarios tested.
- D: quota exhaustion, provider outage and rollback tests pass.
- E: limited beta with spending caps and support process.
- F: premium plans only after unit costs, entitlements and current terms are verified.
