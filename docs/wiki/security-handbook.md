# Security handbook

This is a security checklist, not a claim that the system is already production-secure. The control plane, production fetcher and publishing adapter remain unimplemented.

## Threat model
Protect the shared Telegram token, installation credentials, user/channel mappings, configuration, premium entitlements, source provenance and publishing privileges.

Threats include malicious pull requests, leaked credentials, cross-tenant access, Telegram user spoofing, SSRF through source/redirect URLs, DNS rebinding, malformed feeds, source prompt injection, poisoned model repositories, duplicate publishing, quota abuse, malicious media and billing-webhook replay.

## GitHub and dependency supply chain
- Grant only read permissions to CI; never expose production secrets to pull-request code.
- Pin GitHub Actions to verified full commit SHAs. Tags are mutable.
- Use Dependabot for Python and Actions updates.
- Run tests, linting, static analysis and dependency audits.
- Keep model weights, downloaded media, environment files and runtime data out of Git history.
- Protect the default branch and require review/status checks before accepting changes.
- Never run untrusted contribution code in workflows with publishing credentials.
- Do not use CI as a production multi-tenant runtime.

## Secrets and tenant isolation
- Keep the shared bot token in server-side secret storage only.
- Users must never send tokens through normal bot messages.
- Generate unique high-entropy installation credentials and support rotation/revocation.
- Authorize every command, callback and query against a trusted Telegram user ID and tenant ID.
- Do not trust a channel ID supplied by chat alone; verify its registration and bot posting rights.
- Enforce authorization in the data-access layer, not just the user interface.
- Store minimal personal data, define retention periods and audit privileged changes.
- Redact tokens, headers and secrets from logs and error messages.

## SSRF and network fetching
- Require HTTPS by default; reject embedded URL credentials, local/reserved hosts and private, loopback, link-local or non-global IPs.
- Resolve DNS and reject a hostname if any answer is non-public.
- Revalidate every redirect; cap redirect count, response size, timeout and decompression.
- Prevent DNS rebinding by connecting to a validated address or verifying the actual connected peer. URL validation before a separate DNS lookup is insufficient alone.
- Block cloud metadata addresses and internal/private ranges at the network layer as defence in depth.
- Allow only required ports and content types; never fetch arbitrary callback-supplied URLs without the same policy.
- Use safe XML parsing and input-size limits for feeds.
- The current URL policy helper is a validation primitive; a production HTTP client must enforce the full policy.

## Prompt injection and factuality
- Treat article text, feed contents, HTML metadata, captions and user instructions as untrusted data.
- Source content must never change tools, credentials, policy, target channel or account settings.
- Pass evidence as bounded data and keep control instructions separate.
- Require schema validation, source URL matching and claim checks before publication.
- Model-based review is fallible; a second model is not proof of truth.
- Use human review for high-impact or weakly sourced health, finance and crypto claims.

## Model supply chain
- Review the model card, licence, provenance, architecture and limitations.
- Pin an approved immutable model revision in production.
- Avoid trust_remote_code=True unless code has been reviewed and there is a compelling need.
- Prefer safe tensor formats where supported; public model weights are not automatically trustworthy.
- Bound tokens, memory, runtime and concurrency; never commit weights to Git.

## Publishing and media
- Keep publishing disabled until tenant isolation, quota checks and idempotency are implemented.
- Verify destination ownership and the bot's administrator permission.
- Record delivery only after confirmation; reconcile uncertain timeouts before retrying.
- Do not download or rehost media without appropriate rights.
- Oversized/unsupported videos should use the original publisher-page URL.
- Escape text sent to Telegram HTML/Markdown formatting and test malformed markup.

## Incident response
1. Pause affected publishing jobs.
2. Revoke and rotate exposed credentials.
3. Determine affected tenants, destinations and time range from audit records.
4. Remove secrets from active systems and repository history where necessary; rotation remains required after history rewriting.
5. Notify affected users where appropriate, patch the root cause and add a regression test.
