# Source content acquisition and use policy

This project must distinguish **finding a story** from **having enough permitted source text to summarize it**.

## Retrieval order

1. **Publisher-provided RSS/Atom content.** Prefer a feed entry's explicit RSS `content:encoded` or Atom `content` element. The parser retains this separately from the entry's short `description`/`summary`, and labels its MIME type. Some feeds include only metadata and a short teaser; that must not be described as a full article.
2. **Ordinary publisher article page.** If the feed has no usable embedded content, the bounded HTTPS fetcher may request the publisher URL using its configured hostname allowlist and response limits. A successful HTTP response still must pass the conservative extraction threshold.
3. **Documented publisher API, partner feed, or licensed provider.** When pages consistently block automated access, integrate an official API or licensed feed only after reviewing its current terms, authentication method, quotas, attribution and permitted downstream use. Use documented endpoints rather than guessing private APIs. Keep any API credentials in GitHub Actions or runtime secrets, never in source control.
4. **Metadata-only fallback.** If no permitted body text is available, retain the headline, publisher-provided description, date and canonical URL for editorial review. Do not invent missing facts or silently pass a short teaser off as a complete article.

## HTTP 403 and other restrictions

Treat HTTP 401/403, paywalls, robots restrictions, access controls, and explicit rate limits as restrictions—not as puzzles to defeat. Do not spoof browsers, rotate proxies, reuse session cookies, call guessed hidden endpoints, or retry the same blocked article indefinitely. Record the status/reason and stop that route. A separate reference page can test that the HTML parser works, but it must never be substituted as source evidence for the original story.

## Content provenance and quality

Every item used downstream should retain:
- original publisher URL and headline;
- configured source/feed identity, separate from any publisher label inside the item;
- published date when supplied;
- retrieval method (`publisher_feed_content`, `publisher_article_page`, official API/partner feed, or metadata-only);
- text type and length; and
- any retrieval restriction or extraction failure.

Feed-supplied content is useful evidence, not automatically permission to republish it verbatim or permission to send it to every external model service. Confirm the publisher's terms/licence and the project's legal basis for commercial use. Prefer short original summaries, attribution and links when permitted; don't redistribute article bodies unless rights allow it. Public availability alone is not a licence.

## Current implementation

- The RSS/Atom parser recognizes RSS `content:encoded` and Atom `content`, preserving them separately from short summaries.
- Discovered candidates retain the configured feed name for allowlist lookup; an optional publisher label is stored separately.
- `python -m acp.main --discover-feeds` reports embedded-content length without printing the entire body by default.
- `python -m acp.main --discover-feeds --include-feed-content` is an explicit opt-in for development/test code that needs the actual feed-supplied text. Avoid sending this output to public logs.
- The online smoke test tries publisher-supplied content before the article page, never bypasses 403, and reports any separate parser-only reference-page test distinctly.
- Official API and licensed-provider adapters remain future work. There is no universal free source that legally supplies full text from every publisher.
