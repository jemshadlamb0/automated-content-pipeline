# Roadmap

## Foundation stage — implemented
- [x] Repository structure and CI with read-only permissions.
- [x] Bounded configuration validation and profile catalogues.
- [x] Optional local Hugging Face provider with immutable revision support and safe-tensor loading.
- [x] Editorial prompt builder and structured output checks.
- [x] Weighted regional-ranking helper.
- [x] Defensive RSS/Atom XML parsing.
- [x] SSRF URL-policy primitives.
- [x] Security scans, secret-pattern scan, CodeQL and Wiki documentation.

## Phase 1 — secure source ingestion (current branch)
- [x] Direct HTTP/HTTPS retrieval pinned to a validated public IP.
- [x] Validate every redirect; reject HTTPS-to-HTTP downgrade.
- [x] Bound network timeout, response size, redirects, retries and content types.
- [x] Parse configured RSS/Atom feeds and deduplicate candidate URLs/headlines within a run.
- [x] Extract bounded HTML metadata and paragraph text without executing scripts.
- [x] Add non-publishing CLI commands to validate config, discover feeds and extract one article.
- [ ] Pass full CI and security checks on this feature branch and merge only after review.
- [ ] Add curated feed profiles and measured freshness/canonicalization tests.

## Phase 2 — editorial inference
- [ ] Benchmark quantized Hugging Face models in each enabled language.
- [ ] Integrate evidence records with structured generation and model-output validation.
- [ ] Add claim-to-source checks and human-review routing.
- [ ] Measure CPU/RAM, cold start, generation speed, output failure and factuality review.

## Phase 3 — shared Telegram control plane
- [ ] One owner-operated webhook and bot.
- [ ] Per-user onboarding, installation credentials and channel verification.
- [ ] Tenant-isolated database, queue, quotas and command authorization.
- [ ] Telegram menus for niche, language, region, tone, approach, schedule and sources.

## Phase 4 — publishing and reliability
- [ ] Durable queue, quota counters, locks and idempotency.
- [ ] Telegram publisher with strict output escaping and bounded retries.
- [ ] Rights-aware image/video handling and publisher-page fallback.
- [ ] Delivery receipts, audit trail, monitoring and backups.

## Phase 5 — managed/premium service
- [ ] Review applicable GitHub/provider terms; keep commercial production execution on an appropriate runtime.
- [ ] Usage metering, entitlements and hard global/user spending limits.
- [ ] Payment verification, support/refunds, privacy and terms.
- [ ] Load tests, incident response and rollback runbook.
