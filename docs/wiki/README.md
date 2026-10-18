# Automated Content Pipeline Wiki

Welcome to the repository-backed wiki. These pages are versioned with the code so users can read documentation matching the installed revision. They are stored under docs/wiki/; this is not a separately hosted GitHub Wiki tab.

## Start here
- [Project overview](project-overview.md) — goals, boundaries and current implementation status.
- [Getting started](getting-started.md) — environment, setup, tests and common mistakes.
- [Language catalogue](languages.md) — locales, script variants, region selection and known limitations.
- [Niches and editorial policy](niches-editorial.md) — topic-specific requirements and high-impact coverage.
- [Regional news ranking](regional-ranking.md) — scoring signals and local/national/global allocation.

## Engineering and operations
- [Security handbook](security-handbook.md) — threat model, token protection, SSRF, prompt injection, tenant isolation and CI.
- [Operations and troubleshooting](operations.md) — diagnosis, quota behaviour, logs and recovery.
- [Roadmap and service boundaries](roadmap.md) — implementation status and future managed-service boundaries.

## Documentation principle
A language profile indicates desired editorial behaviour; it does not certify that every inference model can write that language reliably. Each language/model pair needs evaluation fixtures and a quality threshold before unattended publishing is enabled.
