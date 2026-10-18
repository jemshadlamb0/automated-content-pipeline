# Roadmap and service boundaries

## Foundation present
- Configuration validation and profiles.
- Niche, language, tone and approach catalogues.
- Regional weighted-scoring helper.
- RSS/Atom XML parsing of already-fetched feed bodies.
- Basic structured article validation.
- Editorial prompt composition and optional local Hugging Face adapter.
- URL policy validation primitive and CI.

## Remaining before end-to-end use
1. Safe outbound HTTP fetcher, redirect handling, DNS-rebinding controls, feed retrieval and publisher URL canonicalization.
2. Evidence extraction and a structured source-claim record.
3. Region/entity detection and source-quality inputs for candidate ranking.
4. Structured inference integration, model revision pinning and per-language quality gates.
5. Durable queue, locks, quotas and idempotent delivery.
6. Shared Telegram webhook, onboarding, installation authentication and channel verification.
7. Telegram publisher, formatting/escaping and media-size/licence fallback.
8. Monitoring, backups, operator commands and incident response.
9. Premium entitlements and metered managed execution.
10. Legal/licensing review and production hosting compliant with current provider terms.

## Release gates
- A: tests and security analysis pass.
- B: mocked end-to-end draft passes, with no secrets and no publishing in CI.
- C: private test bot and private channel, with tenant/auth/idempotency scenarios tested.
- D: quota exhaustion, provider outage and rollback tests pass.
- E: limited beta with spending caps and support process.
- F: premium plans only after unit costs, entitlement enforcement and applicable terms are verified.
