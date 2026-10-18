# Roadmap

## Phase 0 — Foundation
- [x] Public repository skeleton and CI.
- [x] Configuration validation.
- [x] Hugging Face local provider interface (optional dependencies).
- [x] Editorial prompt builder.
- [ ] Confirm licence and contribution policy.

## Phase 1 — Safe source ingestion
- [ ] Outbound HTTP client with SSRF and redirect protection.
- [ ] RSS/Atom discovery, URL canonicalization, freshness and deduplication.
- [ ] Evidence schema and article extraction.
- [ ] Mocked tests with no live publishing.

## Phase 2 — Editorial inference
- [ ] Benchmark quantized Hugging Face models in each supported language.
- [ ] Structured output parsing, factuality validation and human-review routing.
- [ ] Measure CPU/RAM, cold start, token speed and failure rate.

## Phase 3 — Shared Telegram control plane
- [ ] One webhook and owner-operated shared bot.
- [ ] Per-user onboarding, installation credentials and channel verification.
- [ ] Worker + database prototype with tenant isolation and quotas.
- [ ] Telegram controls for niche, language, region, tone, approach, schedule and sources.

## Phase 4 — Publication and reliability
- [ ] Durable queue, quotas, concurrency locks and idempotency.
- [ ] Telegram publisher and bounded retry handling.
- [ ] Rights-aware video handling and publisher-page fallback.
- [ ] Per-tenant delivery receipts and audit history.

## Phase 5 — Managed premium service
- [ ] Review current GitHub terms and keep paid production execution off Actions unless explicitly permitted.
- [ ] Managed execution, usage metering, entitlements and hard spending limits.
- [ ] Payment integration, support/refund process, privacy and terms.
- [ ] Load tests, alerts, backups and operational runbooks.
