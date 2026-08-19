# Decisions

## 2026-08-19 — Preserve the vendored quickstart

The existing FortyGuard quickstart contains the most valuable local research, client wrapper, notebooks, and sanitized fixtures. It is retained as a vendor/reference layer rather than rewritten.

## 2026-08-19 — Use official docs as the current API authority

The local quickstart and current official docs disagree on a few details, notably date coverage and some unit wording. We record both, prefer current official docs for request construction, and treat cached fixture values as evidence with explicit provenance.

## 2026-08-19 — Handbook supersedes earlier assumptions

The supplied participant handbook is authoritative for the U.S.-only scope, 2021-present date range, twelve-hour forecast horizon, team/submission rules, tracks, judging, conduct, and API endpoint plan access. The handbook’s approximate 2 m platform claim is not treated as API output precision because the API contract and live test expose 60/80/100 m grid granularity.

## 2026-08-19 — Use a bounded live validation budget

After the non-billable usage check, five distinct analysis calls were made and cached: heatmap `tcm`, env params, satellite segmentation, exceedance, and multi-tile `tcm`. Measured deltas are recorded in `docs/LIVE_API_VALIDATION.md`; successful requests are not repeated.

## 2026-08-19 — Premium access is capability-specific

Satellite segmentation completed for the Hackathon account. Street-view and heat-intelligence access were not tested, so no finalist may depend on them.

## 2026-08-19 — Live evidence favors temporal scheduling over unsupported spatial claims

The live environmental profile supports a real hourly temporal workflow. A 96-tile test showed only small daily temperature variation and uniform one-hour exceedance in the selected AOI/date. This does not falsify the concepts, but it does falsify any claim that this test already proves strong spatial ranking; finalist confidence is downgraded and the MVP remains unselected.

## 2026-08-19 — Live analysis calls are cached and idempotent

Authentication was verified with the usage endpoint. Cached responses are sufficient for schema and metric work; repeating identical analysis requests would waste credits and create no new evidence.

## 2026-08-19 — Mock-first agent core

The agent loop is provider-neutral and deterministic by default. A hosted LLM may propose tool calls later, but it cannot bypass the registry, budgets, repeat-call protection, or human approval.

## 2026-08-19 — Do not select the MVP

The exploration run ranks three finalists but intentionally stops before product selection, as required by the brief.
