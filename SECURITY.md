# Security policy

This project is an early foundation, not a production multi-tenant publishing service. The shared Telegram control plane and production network fetcher are not implemented yet.

## Reporting a vulnerability
Do not publish exploit details, credentials, or personal information in a public issue. Use GitHub's private vulnerability reporting feature if it is enabled for this repository; otherwise contact the maintainer privately.

## Required before production
- Keep the shared Telegram bot token in private server-side secret storage.
- Authenticate each user/installation and enforce tenant-scoped authorization on every data access.
- Verify registered Telegram channel destinations and bot posting permissions.
- Keep CI read-only; never expose secrets to untrusted pull-request jobs.
- Pin workflow actions to full commit SHAs, maintain dependencies and run vulnerability/static-analysis checks.
- Implement SSRF-resistant fetching with redirect, DNS-rebinding, timeout and size controls.
- Use defensive XML parsing, structured output checks, source attribution and human review for high-impact claims.
- Apply hard per-tenant quotas and global budget circuit breakers; never activate paid fallback silently.
- Verify payment events server-side and make payment webhook processing idempotent.
- Do not rehost media without appropriate reuse permission.

See the [Security Handbook](docs/wiki/security-handbook.md) for the threat model and required controls.
