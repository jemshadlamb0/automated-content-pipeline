# Operations and troubleshooting

## Foundation commands
Validate configuration:

~~~bash
python -m acp.main --check-config
~~~

Discover the RSS feeds configured in config/settings.yaml, with no AI generation or publishing:

~~~bash
python -m acp.main --discover-feeds
~~~

Fetch one public HTTPS article and inspect extracted metadata/body evidence, without publishing:

~~~bash
python -m acp.main --fetch-article https://publisher.example/news/story
~~~

These commands perform real outbound HTTPS requests when their options require it. Use trusted publisher domains and inspect the configured feed URLs before running them.

## Safety behaviour
- Non-HTTPS feed/article URLs are rejected by default.
- All DNS answers must be globally routable; a hostname resolving to both public and private addresses is rejected.
- Each redirect is validated independently, the HTTP connection is pinned to a validated address, and HTTPS-to-HTTP redirects are rejected.
- Responses are time/size limited. Compressed responses, unsupported MIME types and oversized bodies are rejected.
- A failed feed is recorded as a failure and discovery continues with other configured feeds.
- Article extraction does not execute JavaScript, skips common non-content elements and refuses pages with too little text rather than inventing missing content.
- No source-ingestion CLI command publishes to Telegram.

## Common problems
**No candidates:** configure at least one public RSS/Atom HTTPS feed. Check that the server permits the feed's domain and the source returns an accepted RSS/Atom MIME type.

**Feed rejected by allowlist:** add the intended publisher host and any legitimate redirect host to that feed's allowed_hosts setting. Avoid broad wildcards unless needed.

**Redirect/private destination rejected:** do not disable the safety checks; verify the publisher feed URL and use an official HTTPS feed URL instead.

**Unsupported content type:** check the publisher's response headers. The initial fetcher is not a generic media downloader.

**Article text is too short:** some pages require JavaScript or paywall access, or expose only a short summary. Do not attempt to bypass paywalls; use an accessible primary source or a permitted publisher feed.

## Logs and metrics needed before production
Measure runs, feed failures, candidate counts, duplicate rate, extracted-text length, HTTP status classes, timeout/size-limit rejections and later model latency. Do not log tokens, credentials, full headers or sensitive payloads.

Production tenant state needs a durable database, backups and a tested restore process. Ephemeral job files, caches and local development state are not production databases.
