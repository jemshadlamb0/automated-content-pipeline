# Project overview

## What this project is
A reusable content-processing engine designed to find public news sources, assess relevance and freshness, build a source-grounded evidence record, generate original editorial news in a chosen language, validate the structured output, and publish it to a user's configured Telegram channel.

It is not yet an end-to-end news publisher. Current components include configuration/profile foundations, a local Hugging Face provider interface, editorial prompt builder, regional scoring helper, RSS/Atom XML parser, structured output validator, URL policy primitive and CI. Production article extraction, shared multi-tenant Telegram control plane, durable queue/state and working publisher adapter remain future work.

## Product boundaries
- The shared Telegram bot and its token belong to the operator, not to each user's fork.
- Every installation needs a distinct credential and tenant record.
- The control plane makes authorization and plan decisions; the execution plane performs bounded work.
- Free inference must not silently fall back to a paid API.
- The public repository is not a place to store user settings, bot secrets, model weights or fetched media.
- Use GitHub for source control, CI, tests, releases and trusted deployment workflows; production commercial execution belongs on infrastructure appropriate to the service and applicable terms.

## Core pipeline
1. Discover candidate stories from configured feeds.
2. Validate outbound destinations and source provenance.
3. Deduplicate and classify niche, geography, freshness and source reliability.
4. Extract facts, claims and uncertainty from source material.
5. Generate original target-language news based on that evidence.
6. Validate structure, attribution, lengths and risk flags.
7. Publish only when entitlement, cadence, quotas and review policy allow it.
8. Store durable delivery receipt only after the destination confirms success.

## Key constraints
- LLM output can contain errors even if JSON validation passes.
- Local CPU models may be too slow or too weak for specific languages.
- Feed coverage and regional labels are imperfect; source detection must be measured.
- Public media is not automatically licensed for republication.
- Quota caps must fail closed and avoid surprise bills.
