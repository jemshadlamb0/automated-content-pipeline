# Roadmap

## Foundation stage — implemented
- [x] Repository structure and CI with read-only token permissions.
- [x] Bounded configuration validation.
- [x] Niche, locale, tone and editorial approach catalogues.
- [x] Family-level language profiles require a selected variety; ambiguous locales require an explicit region.
- [x] Optional local Hugging Face provider with revision pinning support and safetensors loading.
- [x] Editorial prompt builder and structured output checks.
- [x] Weighted regional ranking helper.
- [x] RSS/Atom XML parsing with defensive parser and document/item bounds.
- [x] URL policy primitive for rejecting local/private/non-global addresses.
- [x] Wiki-style docs under docs/wiki/.
- [x] SHA-pinned CI actions, static analysis, dependency audit and Dependabot configuration.

## Phase 1 — safe source ingestion
- [ ] Production outbound HTTP client with SSRF protections, per-redirect validation and DNS-rebinding-resistant connection handling.
- [ ] RSS retrieval, publisher URL canonicalization, freshness and deduplication.
- [ ] HTML/article extraction and evidence schema.
- [ ] Mocked tests with no live publisher fetches in CI.

## Phase 2 — editorial inference
- [ ] Benchmark quantized Hugging Face models in each enabled language.
- [ ] Add stricter structured JSON parsing, claim-to-source checks and human-review routing.
- [ ] Track CPU/RAM, cold start, generation speed, output failure and factuality review.

## Phase 3 — shared Telegram control plane
- [ ] One owner-operated webhook and bot.
- [ ] Per-user onboarding, installation credentials and channel verification.
- [ ] Tenant-isolated database, quotas and command authorization.
- [ ] Telegram menus for niche, language, region, tone, approach, schedule and sources.

## Phase 4 — publishing and reliability
- [ ] Durable queue, quota counters, locks and idempotency.
- [ ] Telegram publisher with strict output escaping and bounded retries.
- [ ] Rights-aware image/video handling and publisher-page fallback.
- [ ] Per-tenant delivery receipts, audit trail, monitoring and backups.

## Phase 5 — managed/premium service
- [ ] Review applicable GitHub/provider terms; keep commercial production execution on an appropriate runtime.
- [ ] Usage metering, entitlements and hard global/user spending limits.
- [ ] Payment verification, support/refunds, privacy and terms.
- [ ] Load tests, incident response and rollback runbook.
