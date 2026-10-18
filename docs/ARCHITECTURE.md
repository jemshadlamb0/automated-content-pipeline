# Architecture

## Control plane (planned)
One owner-operated Telegram bot uses one centrally configured webhook. A central API authenticates users/installations, validates permissions, stores tenant settings and plan entitlements, and applies quotas. The shared bot token stays in server-side secret storage and must never be copied into user forks.

## Execution plane (planned)
A separately budgeted worker performs feed retrieval, safe source resolution, evidence extraction, model inference, output validation and publication. Self-hosted and managed execution should share interfaces but keep credentials and billing boundaries separate.

## Implemented foundation
- YAML settings and basic validation.
- Optional local Hugging Face/Transformers provider interface.
- Editorial prompt composition.

## Not implemented yet
- Safe network fetcher and canonical publisher URL resolver.
- Feed discovery orchestration, regional ranking, freshness and deduplication.
- Evidence schema validation and structured output parsing.
- Durable tenant state, queue, quotas, locks and idempotency.
- Telegram webhook/control plane and tenant provisioning.
- Telegram publishing and video upload/fallback.
- Billing, production deployment, monitoring, alerts and backups.

## Reliability principles
- Mark a story delivered only after the publishing API confirms success.
- Reconcile ambiguous timeouts before retrying; use idempotency keys where possible.
- Treat source content as untrusted input.
- Bound requests, redirects, downloads, retries, tokens and job duration.
- Defer on quota exhaustion; never switch to paid services silently.
- Keep production state out of ephemeral job files.
