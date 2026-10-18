# Security policy

This project is an early foundation, not a production multi-tenant publishing service. The shared Telegram control plane and production downloader are not implemented.

## Reporting
Do not publish exploit details, tokens or personal data in a public issue. Use GitHub's private vulnerability reporting feature if it is enabled; otherwise contact the maintainer privately.

## Baseline controls
- Keep the shared Telegram token in private server-side secret storage.
- Authenticate each user/installation and enforce tenant-scoped authorization on every database access.
- Verify Telegram channel destinations and bot posting permissions.
- Keep CI read-only and never expose secrets to untrusted pull-request jobs.
- Pin workflow Actions to full commit SHAs.
- Run tests, Ruff, Bandit, pip-audit and the best-effort tracked-file secret scanner.
- Use defensive XML parsing and SSRF-resistant fetching with redirect, DNS-rebinding, timeout and size controls.
- Use structured-output validation, source attribution and human review for high-impact claims.
- Apply hard per-tenant quotas and a global spending circuit breaker; never enable paid fallback silently.
- Verify payment events server-side and make webhook handling idempotent.
- Do not republish media without appropriate reuse rights.

The secret-pattern scanner is not a substitute for GitHub Secret Scanning and push protection or dedicated scanning. Pattern scanners can miss encoded, split, encrypted or unknown credentials.

See the [Security Handbook](wiki/security-handbook.md) and [main branch protection guide](BRANCH_PROTECTION.md).
