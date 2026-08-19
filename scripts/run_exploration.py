from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from fortyguard_agent.evals import run_fixture_spikes


def main() -> None:
    results = run_fixture_spikes()
    print(json.dumps({"mode": "deterministic_fixture", "results": [r.__dict__ for r in results]}, indent=2))


if __name__ == "__main__":
    main()
