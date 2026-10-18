# Architecture

## Control plane (planned)
One owner-operated Telegram bot uses one central webhook. A central API authenticates users/installations, validates permissions, stores tenant settings and plan entitlements, and applies quotas. The shared bot token stays in server-side secret storage and must never be copied into user forks.

## Execution plane (planned)
A separately budgeted worker performs feed retrieval, safe source resolution, evidence extraction, model inference, output validation and publication. Self-hosted and managed execution should share interfaces but keep credentials and billing boundaries separate.

## Implemented foundation
- YAML settings and profile validation, including bounded source-fetch limits and HTTPS-only feed URL syntax.
- Optional local Hugging Face/Transformers adapter with immutable model revision support.
- Editorial prompt composition and structured output validation.
- Regional weighted-scoring helper.
- Defensive RSS/Atom XML parsing.
- SSRF URL policy that resolves A/AAAA results and rejects non-global destinations.
- Bounded HTTP fetcher that pins connections to the validated address, verifies TLS against the original hostname, revalidates each redirect, prevents HTTPS-to-HTTP downgrade, disallows ambient proxies/credentials, bounds response size and duration, and restricts MIME types.
- RSS feed candidate discovery, URL normalization/deduplication, and conservative HTML article metadata/paragraph extraction.
- CLI commands to validate configuration, discover configured feeds, or extract a single public HTTPS article. These commands never publish messages.
- Tests, static analysis, dependency audit, secret-pattern scan and pinned CI Actions.

## Security boundary for the fetcher
The fetcher is designed for bounded text/feed retrieval only, not media downloads. It does not support proxies, cookies, authentication headers, compression, non-standard ports or HTTP by default. Feed source URLs should use an explicit host allowlist where practical. This reduces attack surface but does not guarantee publisher availability or correct article extraction.

## Not yet implemented
- Production feed catalogue and source-specific reliability policies.
- Strong canonical publisher URL resolution and date/freshness evaluation.
- Region/entity detection and credibility scoring inputs.
- Durable cross-run deduplication and job state.
- Evidence claim extraction/verification and model orchestration.
- Shared Telegram webhook/control plane and tenant provisioning.
- Telegram publisher, formatting/escaping and rights-aware video handling.
- Billing, production deployment, monitoring, alerting and backups.

## Reliability principles
- Mark a story delivered only after the publishing API confirms success.
- Reconcile ambiguous timeouts before retrying; use idempotency keys where possible.
- Treat source content as untrusted input.
- Bound requests, redirects, downloads, retries, tokens and job duration.
- Validate every redirect and pin the connection to a validated IP.
- Defer work on quota exhaustion; never switch to paid services silently.
- Keep production state out of ephemeral job files.
