# Regional news ranking

## Purpose
A selected language can suggest a default region, but users must be able to override it. Discovery should query local/regional, national and global source groups. It must not assume all speakers of a language live in one country.

## Initial score
The current helper accepts caller-computed signals between 0 and 100:

~~~text
score = 0.30*niche
      + 0.30*region
      + 0.15*freshness
      + 0.15*authority
      + 0.10*language
~~~

These are starting weights, not empirically validated weights. Regional relevance should come from the story's location/entities and user preferences, not from a publisher's domain suffix alone.

## Initial discovery mix
The helper targets 60% local/regional, 25% national and 15% global candidates. These are soft candidate-selection quotas, not a promise that every published story will follow that distribution. If a tier has too few credible stories, backfill from the remaining candidates and widen source discovery rather than inventing local news.

## Known limitations
The ranking helper does not fetch feeds, detect locations, calculate freshness decay, evaluate publisher credibility or classify articles automatically. Its caller must provide evidence-backed signal values. Those components need independent tests before ranking controls unattended publishing.

## Evaluation plan
Label representative candidate stories by niche fit, region, freshness and source quality. Compare the ranking against editor choices; measure how often relevant regional items appear in the top N. Tune weights based on results and review false positives separately for each language and niche.
