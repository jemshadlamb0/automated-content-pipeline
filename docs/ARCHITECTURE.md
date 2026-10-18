# Architecture

## Boundaries

### Control plane (planned)
One owner-operated Telegram bot uses one central webhook. A central API authenticates users/installations, validates permissions, stores tenant settings and plan entitlements, and applies quotas. The shared bot token stays in server-side secret storage and must never be copied into user forks.

### Execution plane (planned)
A separately budgeted worker performs feed retrieval, safe source resolution, evidence extraction, model inference, output validation and publication. Self-hosted and managed execution should share interfaces but keep credentials and billing boundaries separate.

### Implemented foundation
- YAML configuration validation, including bounded custom instructions, token limits and post caps.
- Niche, language, tone and approach profiles.
- Local Hugging Face/Transformers adapter with optional immutable revision and safe-tensor loading.
- Editorial prompt composition and structured-output shape/URL validation.
- Regional weighted-scoring helper.
- RSS/Atom parsing via a defensive XML parser with document-size and item-count limits.
- SSRF URL-policy primitive for public destinations; it validates DNS answers but is not itself a complete HTTP fetcher.
- CI with least-privilege permissions, SHA-pinned Actions, static analysis and dependency auditing.

### Not yet implemented
- Production outbound HTTP client with redirect checks and DNS-rebinding-resistant connection handling.
- Feed orchestration, canonical publisher URL resolution, freshness and persistent deduplication.
- Article extraction and evidence schema/fact checks.
- Region/entity detection and source-quality scoring inputs.
- Durable tenant state, queue, quotas, locks and idempotency.
- Telegram webhook/control plane and tenant provisioning.
- Telegram publisher, formatting/escaping and video upload/fallback.
- Billing, production deployment, monitoring, alerting and backups.

## Reliability and security principles
- Mark a story delivered only after the publishing API confirms success.
- Reconcile ambiguous timeouts before retrying; use idempotency keys where possible.
- Treat source content as untrusted input.
- Bound requests, redirects, downloads, retries, tokens and job duration.
- Validate every redirect and the actual connection destination; DNS checking alone cannot fully prevent rebinding.
- Defer work on quota exhaustion; never switch to paid services silently.
- Keep production state out of ephemeral job files.
