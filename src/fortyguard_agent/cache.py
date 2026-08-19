from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
from typing import Any


def request_hash(endpoint: str, payload: dict[str, Any]) -> str:
    canonical = json.dumps({"endpoint": endpoint, "payload": payload}, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


class JsonCache:
    """Small content-addressed cache. Writes are atomic and JSON-only."""

    def __init__(self, root: str | Path = ".agent_cache") -> None:
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)

    def path_for(self, key: str) -> Path:
        return self.root / f"{key}.json"

    def get(self, key: str) -> dict[str, Any] | None:
        path = self.path_for(key)
        if not path.exists():
            return None
        with path.open("r", encoding="utf-8") as handle:
            return json.load(handle)

    def put(self, key: str, value: dict[str, Any]) -> Path:
        target = self.path_for(key)
        temporary = target.with_suffix(".tmp")
        with temporary.open("w", encoding="utf-8") as handle:
            json.dump(value, handle, indent=2, sort_keys=True)
        os.replace(temporary, target)
        return target
