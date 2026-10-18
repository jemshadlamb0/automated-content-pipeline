import pytest
from acp.ranking import rank_candidates, weighted_score

SIGNALS = {"niche": 90, "region": 90, "freshness": 80, "authority": 85, "language": 70}


def test_weighted_score_uses_expected_weights():
    assert weighted_score(SIGNALS) == 85.75


def test_bad_scores_are_rejected():
    with pytest.raises(ValueError):
        weighted_score({**SIGNALS, "region": 101})


def test_region_mix_targets_local_content_when_available():
    candidates = [
        {"id": f"local-{i}", "region_tier": "local", "signals": SIGNALS} for i in range(8)
    ] + [
        {"id": f"global-{i}", "region_tier": "global", "signals": {**SIGNALS, "niche": 100}} for i in range(8)
    ]
    ranked = rank_candidates(candidates, limit=5)
    assert len(ranked) == 5
    assert sum(item["region_tier"] == "local" for item in ranked) >= 2


def test_region_shares_must_sum_to_one():
    with pytest.raises(ValueError):
        rank_candidates([], limit=5, region_shares={"local": 0.5, "national": 0.5, "global": 0.5})
