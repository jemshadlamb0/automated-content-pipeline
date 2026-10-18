# Configuration

The default settings file is config/settings.yaml. Validate it with:

~~~bash
python -m acp.main --check-config
~~~

## Key fields
- profile.niche: profile ID under config/niches/.
- profile.language: locale/profile ID under config/languages/.
- profile.language_variant: required for the Bihari and Rajasthani family/group placeholders.
- profile.region: set AUTO to use an unambiguous locale default, or provide an explicit region. Bengali, Spanish and Arabic require a region choice because their language profiles do not specify a single default.
- profile.tone and profile.approach: IDs under config/tones/ and config/approaches/.
- schedule.min_post_interval_minutes: intended publication cadence; production scheduling is not implemented.
- generation.model_id: reviewed Hugging Face model ID; empty by default.
- generation.model_revision: use an approved immutable model revision in production.
- generation.allow_paid_fallback: must remain false by default.
- publication.enabled: false by default.
- publication.dry_run: true by default.

## Profile design
Niche profiles define topics, freshness expectations, source preferences and guardrails. Language profiles define natural editorial conventions rather than literal-translation rules. Tone and approach are independent of language and niche.

## Secrets and production
Never store credentials in tracked YAML, source files, logs, issue comments or ordinary Telegram chat. Production secret handling and the shared Telegram service are not implemented. Follow the [Security Handbook](wiki/security-handbook.md) before deployment.
