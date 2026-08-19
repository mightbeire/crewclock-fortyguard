from pathlib import Path

from fortyguard_agent.cache import JsonCache, request_hash


def test_request_hash_is_order_independent(tmp_path: Path) -> None:
    assert request_hash("/v1/heatmap", {"b": 2, "a": 1}) == request_hash("/v1/heatmap", {"a": 1, "b": 2})


def test_cache_round_trip(tmp_path: Path) -> None:
    cache = JsonCache(tmp_path)
    cache.put("abc", {"data": {"value": 4}, "assumptions": ["fixture"]})
    assert cache.get("abc")["data"]["value"] == 4
