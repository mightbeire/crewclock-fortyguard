"""Run finalist spikes against the cached successful live env_params response."""

from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from fortyguard_agent.evals import run_deterministic_spike


def main() -> None:
    path = ROOT / ".agent_cache" / "live_validation" / "env_params.json"
    if not path.exists():
        raise SystemExit("Run scripts/live_validate.py first")
    body = json.loads(path.read_text(encoding="utf-8"))
    profile = body["result"]["locations"][0]["parameters"]["apparent_temperature_celsius"]
    results = [
        run_deterministic_spike("Pavement Window Agent (live profile)", profile, baseline_window={"start_hour": 12, "end_hour": 15}, candidate_window={"start_hour": 7, "end_hour": 10}),
        run_deterministic_spike("Thermal Sequence Planner (live profile)", profile, baseline_window={"start_hour": 11, "end_hour": 14}, candidate_window={"start_hour": 8, "end_hour": 11}),
        run_deterministic_spike("DockShift Orchestrator (live profile)", profile, baseline_window={"start_hour": 13, "end_hour": 16}, candidate_window={"start_hour": 9, "end_hour": 12}),
    ]
    print(json.dumps({"source": "cached_successful_live_env_params", "results": [r.__dict__ for r in results]}, indent=2))


if __name__ == "__main__":
    main()
