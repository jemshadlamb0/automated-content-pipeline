# Automated Content Pipeline Wiki

Welcome to the versioned documentation for Automated Content Pipeline.

## Start here
- [Project overview](project-overview.md) — goals, boundaries and implementation status.
- [Getting started](getting-started.md) — environment, setup, tests and common mistakes.
- [Language catalogue](languages.md) — locale profiles, script variants, region selection and limitations.
- [Niches and editorial policy](niches-editorial.md) — topic-specific and high-impact requirements.
- [Regional news ranking](regional-ranking.md) — ranking signals and local/national/global allocation.

## Engineering and operations
- [Security handbook](security-handbook.md) — threat model, secrets, SSRF, prompt injection, tenant isolation and CI.
- [Operations and troubleshooting](operations.md) — diagnosis, quotas, logs and recovery.
- [Roadmap and service boundaries](roadmap.md) — implementation status and managed-service boundaries.
- [Publishing the actual GitHub Wiki](publishing-the-wiki.md) — initialize the Wiki tab once, then sync these pages into it.

## Two different places
The files in docs/wiki/ are the version-controlled source documentation. The separate GitHub Wiki tab is a different Git repository, so it must first be initialized from the web UI. Once initialized, run scripts/publish_wiki.py from a trusted local clone to sync the maintained pages into the actual Wiki tab.

## Documentation principle
A language profile expresses editorial intentions; it does not certify that every model can write that language reliably. Each language/model pair needs evaluation fixtures and a quality threshold before unattended publishing is enabled.
