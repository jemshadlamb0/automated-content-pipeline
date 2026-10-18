"""Deterministic candidate ranking and regional mix selection."""
from __future__ import annotations
import math
from typing import Any, Iterable

DEFAULT_WEIGHTS = {"niche": 0.30, "region": 0.30, "freshness": 0.15, "authority": 0.15, "language": 0.10}
DEFAULT_REGION_SHARES = {"local": 0.60, "national": 0.25, "global": 0.15}


def weighted_score(signals: dict[str, float], weights: dict[str, float] | None = None) -> float:
    """Return a 0-100 weighted score from caller-computed evidence-based signals."""
    weights = weights or DEFAULT_WEIGHTS
    if set(weights) != set(DEFAULT_WEIGHTS):
        raise ValueError("weights must contain niche, region, freshness, authority and language")
    if any(not isinstance(v, (int, float)) or isinstance(v, bool) or not math.isfinite(v) or v < 0 for v in weights.values()):
        raise ValueError("weights must be finite, non-negative numbers")
    if not math.isclose(sum(weights.values()), 1.0, abs_tol=1e-6):
        raise ValueError("weights must sum to 1.0")
    missing = set(weights) - set(signals)
    if missing:
        raise ValueError(f"missing score signals: {', '.join(sorted(missing))}")
    for name in weights:
        value = signals[name]
        if not isinstance(value, (int, float)) or isinstance(value, bool) or not math.isfinite(value) or not 0 <= value <= 100:
            raise ValueError(f"signal {name} must be a finite number between 0 and 100")
    return round(sum(float(signals[name]) * weights[name] for name in weights), 4)


def rank_candidates(
    candidates: Iterable[dict[str, Any]],
    limit: int,
    region_shares: dict[str, float] | None = None,
    weights: dict[str, float] | None = None,
) -> list[dict[str, Any]]:
    """Rank candidates toward a target regional mix; backfill empty groups by score."""
    if limit < 1:
        raise ValueError("limit must be at least 1")
    shares = region_shares or DEFAULT_REGION_SHARES
    tiers = set(DEFAULT_REGION_SHARES)
    if set(shares) != tiers or any(not isinstance(v, (int, float)) or isinstance(v, bool) or v < 0 for v in shares.values()):
        raise ValueError("region_shares must contain non-negative local, national and global shares")
    if not math.isclose(sum(shares.values()), 1.0, abs_tol=1e-6):
        raise ValueError("region_shares must sum to 1.0")

    prepared: list[dict[str, Any]] = []
    seen_ids: set[str] = set()
    for raw in candidates:
        candidate = dict(raw)
        candidate_id = str(candidate.get("id", "")).strip()
        tier = candidate.get("region_tier")
        if not candidate_id or candidate_id in seen_ids:
            continue
        if tier not in tiers:
            raise ValueError(f"candidate {candidate_id} has invalid region_tier")
        candidate["score"] = weighted_score(candidate.get("signals", {}), weights)
        candidate["id"] = candidate_id
        seen_ids.add(candidate_id)
        prepared.append(candidate)

    prepared.sort(key=lambda item: (-item["score"], item["id"]))
    quota = {tier: int(limit * shares[tier]) for tier in tiers}
    remainder = sorted(tiers, key=lambda tier: (-(limit * shares[tier] - quota[tier]), tier))
    for tier in remainder[: limit - sum(quota.values())]:
        quota[tier] += 1

    selected: list[dict[str, Any]] = []
    selected_ids: set[str] = set()
    for tier in ("local", "national", "global"):
        subset = [item for item in prepared if item["region_tier"] == tier]
        for item in subset[:quota[tier]]:
            selected.append(item)
            selected_ids.add(item["id"])
    remaining = [item for item in prepared if item["id"] not in selected_ids]
    selected.extend(remaining[: max(0, limit - len(selected))])
    return sorted(selected[:limit], key=lambda item: (-item["score"], item["id"]))
