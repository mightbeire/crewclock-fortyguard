# FortyGuard Agentic Exploration

Team: `btn operations`

Primary track: Agentic AI
Secondary fit: Industrial & Enterprise

This repository is an evidence-building workspace, not a selected product. The final MVP is deliberately unselected.

## Current state

- Preserved the vendored `temperature-api-quickstart` and its cached sample responses.
- Audited the supplied participant handbook ZIP; it is now authoritative for scope, tracks, judging, conduct, and submission requirements.
- Verified the local FortyGuard key against the usage endpoint without printing it: active Hackathon account, 2,000,000 credits, 0 used at verification time. Controlled live analysis tests now measure 204,500 used and 1,795,500 remaining after caching successful responses.
- Expanded live discovery with eight geography pairs and seven targeted follow-ups; measured account usage is now 204,500 with 1,795,500 remaining.
- Verified live `/v1/heatmap`, `/v1/env_params`, and satellite segmentation; spatial/temporal schemas and limitations are recorded in `docs/LIVE_API_VALIDATION.md`.
- Added second-wave concepts, public duplication attack, realistic public input research, geography research, and v2 bakeoff. Surface-conditioned Road Repair Queue is the tentative evidence leader; no MVP is selected.
- Added provider-neutral agent infrastructure under `src/fortyguard_agent/`.
- Added deterministic fixture-backed and cached-live evaluation spikes for three finalists. The live operational windows remain synthetic.
- No hosted LLM account was created. No final MVP, demo geography, or finalist has been selected.

## Start here next session

1. Read `DECISIONS.md` and `TASKS.md`.
2. Read `docs/FINALIST_EVALUATION.md`.
3. Run `python scripts/run_exploration.py` and `pytest`.
4. Keep `FINAL_MVP_SELECTED = NO` until the humans choose.
