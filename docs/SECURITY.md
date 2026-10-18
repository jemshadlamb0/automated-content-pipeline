# Security policy

This foundation release does not provide a production Telegram control plane or publish content. Review the detailed [Security Handbook](wiki/security-handbook.md) before contributing or deploying.

## Reporting
Report suspected vulnerabilities privately to the repository maintainer. Do not include tokens, personal data, or exploit payloads in public issues.

## Before production
- Keep the shared Telegram bot token in private server-side secret storage.
- Authenticate each user/installation and enforce tenant-scoped authorization in every data access.
- Verify registered Telegram channel destinations and bot posting permissions.
- Keep CI read-only and never expose secrets to untrusted pull-request jobs.
- Use pinned GitHub Actions, dependency updates, static analysis and dependency audits.
- Implement SSRF-resistant fetching with redirect, DNS-rebinding, timeout and size controls.
- Use safe XML parsing, structured model-output validation, source attribution and human review for high-impact claims.
- Apply hard per-tenant and global quotas; never silently enable paid fallback.
- Verify payment events server-side and make webhook handling idempotent.
- Do not rehost unlicensed media.
