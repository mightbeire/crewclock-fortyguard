# FortyGuard Agentic Exploration

Team: `btn operations`

Primary track: Agentic AI
Secondary fit: Industrial & Enterprise

This repository is an evidence-building workspace, not a selected product. The final MVP is deliberately unselected.

## Current state

- Preserved the vendored `temperature-api-quickstart` and its cached sample responses.
- Verified the local FortyGuard key against the usage endpoint without printing it: active Hackathon account, 2,000,000 credits, 0 used at verification time.
- Added provider-neutral agent infrastructure under `src/fortyguard_agent/`.
- Added deterministic fixture-backed evaluation spikes for three finalists.
- No hosted LLM account was created and no analysis endpoint was called live.

## Start here next session

1. Read `DECISIONS.md` and `TASKS.md`.
2. Read `docs/FINALIST_EVALUATION.md`.
3. Run `python scripts/run_exploration.py` and `pytest`.
4. Keep `FINAL_MVP_SELECTED = NO` until the humans choose.
