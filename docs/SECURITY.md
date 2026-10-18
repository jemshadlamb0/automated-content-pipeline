# Security policy

This foundation does not provide a production Telegram control plane or publish content.

Before production:
- Keep the shared Telegram bot token in private server-side secret storage.
- Authenticate each user/installation and authorize every action by tenant and role.
- Bind each installation to its own verified channel destinations.
- Prevent cross-tenant access to settings, usage, channel IDs and publication history.
- Keep CI read-only; never expose secrets to untrusted pull-request jobs.
- Implement request timeouts, size caps, redirect controls and safe outbound-network checks to prevent SSRF.
- Apply bounded retries, per-tenant limits, global circuit breakers and audit logs.
- Treat source text as untrusted and defend against prompt injection.
- Do not publish media without appropriate reuse rights.
- Verify payment events server-side and make billing webhooks idempotent.
- Default to dry run, no paid fallback and no media rehosting unless reviewed and explicitly enabled.

Report security issues privately to the repository maintainer. Never post credentials in public issues.
