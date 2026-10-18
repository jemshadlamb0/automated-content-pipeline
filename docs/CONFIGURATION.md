# Configuration

Default settings live in `config/settings.yaml`. Validate them with:

```bash
python -m acp.main --check-config
```

Important fields:
- `profile.niche`: profile ID in `config/niches/`.
- `profile.language`: locale ID in `config/languages/`.
- `profile.tone` and `profile.approach`: editorial controls.
- `profile.region`: geographic focus for regional discovery (ranking is not implemented yet).
- `schedule.min_post_interval_minutes`: planned publication cadence; the scheduler is not implemented yet.
- `generation.model_id`: reviewed Hugging Face model ID; empty by default.
- `generation.allow_paid_fallback`: must remain false.
- `publication.enabled`: false by default.
- `publication.dry_run`: true by default.

Add profiles as YAML files with an explicit matching `id`. Niche profiles should define topics, freshness expectations and editorial guardrails. Language profiles should specify native editorial style, not literal-translation rules.

Never store real credentials in tracked YAML, source files, logs or Telegram chats. Production secret handling is not implemented yet.
