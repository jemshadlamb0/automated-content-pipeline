# Operations and troubleshooting

## Expected behaviour
The foundation CLI validates configuration; it does not yet run a full news pipeline or Telegram post. Publishing is off and dry-run is on by default.

## Configuration check
~~~bash
python -m acp.main --check-config
pytest
~~~

## Common problems
**Unknown profile:** check the profile filename and ID match exactly, including case and hyphens.

**Bihari/Rajasthani selection:** choose a specific variety before unattended publication. Family-level names are intentionally ambiguous.

**Model download too slow or out of memory:** choose a smaller reviewed model, use a tested quantization format, or use a properly budgeted inference service. Do not solve this by silently calling a paid endpoint.

**Fluent but inaccurate draft:** strengthen source evidence, remove unsupported context, validate claims and route high-impact stories to human review. Fluency is not factual correctness.

**Feed contains invalid data:** cap size/time, use the safe XML parser, reject unsafe URLs, and preserve only the minimum safe diagnostics required.

## Logs and metrics required before production
- Jobs completed, failed, deferred and retried.
- Candidate counts: discovered, filtered, selected and published.
- Model cold-start and generation latency, output validation failures and approximate token usage.
- Usage per tenant and global budget.
- Telegram send result and idempotency key.
- Sanitized error class and correlation ID; never log secrets or sensitive payloads.

## Backups and recovery
Production configuration, tenant mappings and delivery receipts require durable database backups and tested restore procedures. Ephemeral job files, Actions caches and local development JSON are not production databases. Define data-retention limits.
