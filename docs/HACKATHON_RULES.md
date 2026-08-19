# Hackathon rules and verified constraints

## Authoritative handbook audit

The participant handbook supplied at `reference/fortyguard hackathon.zip` is now the controlling source for event rules and submission requirements. The extracted screenshots were audited on August 19, 2026; page numbers below refer to the handbook screenshot sequence.

- Registration: June 20–August 17, 2026; kickoff: August 18; submission deadline: August 30 at 11:59 PM GST; judging: September 1–14; winners: September 16 (p. 4).
- The event is free to enter, open globally, and fully online, but the analysis/data coverage is U.S.-only. Individuals or teams of 1–3 may participate, and every team member must register (pp. 4, 20).
- Work must be original and created during the hackathon unless the rules otherwise permit it. Do not copy another project, reverse-engineer models, cheat, harass, or abuse the service (pp. 4, 20).
- Use FortyGuard API/data only for the hackathon project, keep the API key private, and do not assume access continues after the event. The project and its code remain ours; the submission grants FortyGuard permission to show/share the project and team names (p. 20).
- Required submission package: live demo link; public or judge-accessible repository with code and README; demo video of approximately 3 minutes maximum; written summary of at most 500 words covering problem → user → FortyGuard endpoints/features → measured result. Add `Hackathon-FG (hackathon@fortyguard.com)` as a GitHub collaborator (pp. 17–18, 20).
- Support routes are `support@fortyguard.com` for technical issues and `hackathon@fortyguard.com` for event matters. Judge decisions are final (p. 20).

## Verified from the team brief

- Team: `btn operations`.
- Primary track: Agentic AI.
- Strong secondary fit: Industrial & Enterprise.
- Judging weights: Impact & Relevance 40%, Technical Execution 35%, Innovation 15%, Communication 10%.
- Build sprint: August 18–30, 2026.
- Submission deadline: August 30, 11:59 PM GST.
- FortyGuard must be central; a chatbot over a heatmap is insufficient.
- The product must answer user, problem, why agent, why FortyGuard, and measurement.
- Potentially consequential actions should be recommendations with human approval.
- Do not spend money, submit, publish unfinished work, push secrets, or select the final MVP during exploration.

## Verified from handbook/API materials

- API key authentication uses the `api-key` request header; no OAuth exchange is required.
- Analysis calls submit an asynchronous activity and return an `activity_id`; results are retrieved from `GET /v1/status/{activity_id}`.
- Status values documented include Processing, Completed, and Failed; failed runs are not charged credits.
- `/v1/heatmap` accepts GeoJSON polygon AOIs, filter types 1–5, and 60/80/100 m granularity. Handbook guidance caps an AOI at roughly 130 km² / 50 mi² and recommends splitting larger areas.
- Heatmap analytics include `tcm`, `time_of_measure`, `exceedance`, and `persistence`.
- `/v1/env_params` accepts a point, a Celsius temperature anchor, and filter types 1–3; output is time-aligned environmental parameter arrays plus solar irradiance.
- Premium-only endpoints include satellite segmentation, street-view segmentation, and heat-intelligence reports.
- Usage reporting endpoints exist for current-cycle and custom-range credit usage.

Sources: [Authentication](https://docs-api.fortyguard.com/docs/authentication), [Quickstart](https://docs-api.fortyguard.com/docs/quickstart), [Heatmap](https://docs-api.fortyguard.com/docs/create-heatmap), [Environmental Parameters](https://docs-api.fortyguard.com/docs/environmental-parameters), [Status](https://docs-api.fortyguard.com/docs/check-status), [Release Notes](https://docs-api.fortyguard.com/docs/release-notes).

## Verified locally and live

- `.env` exists and is ignored by the repository ignore policy. Its contents were not printed or committed.
- Live usage check passed on August 19, 2026.
- Live account response reported plan type `Hackathon`, 2,000,000 total/remaining credits, and 0 used at verification time. After five distinct analysis tests, measured usage was 29,960 with 1,970,040 remaining.
- `/v1/heatmap` completed live and returned `map_data`/`stats_data`; a granularity-100 test produced approximately 100 m tiles. Full-day `tcm` returned per-tile daily minimum/average/maximum values, not hourly feature values.
- `/v1/env_params` completed live and returned a 24-point hourly profile plus environmental and solar fields.
- `/v1/satellite` completed live, so satellite segmentation access is verified for this account. Street-view and heat-intelligence access remain untested and must not be assumed.
- Successful live responses are sanitized and cached under `.agent_cache/live_validation/`; the validation scripts are idempotent and avoid repeating an identical paid request.
- The vendored quickstart includes Python client code, notebooks, and cached JSON responses for heatmaps, environmental parameters, satellite, and street-view examples.

## Remaining assumptions and limitations

- The final demo can use cached responses to avoid unnecessary credit use, with a clearly labeled live path if needed.
- Human approval is required for schedule, dispatch, maintenance-window, or alert actions.
- The handbook marketing page describes the platform as approximately 2 m hyperlocal, while the API request schema exposes 60/80/100 m output granularity. The product must describe the selected API grid, not claim 2 m API output.

## Closed questions and still-open questions

- Handbook submission, eligibility, disclosure, and conduct requirements are now verified above.
- Measured analysis deltas for this account are recorded in `docs/LIVE_API_VALIDATION.md`; exact pricing may still vary by request complexity.
- Satellite Premium access is verified. Street-view and heat-intelligence Premium access remain unverified.
- Organizer Slack announcements are not treated as authoritative unless captured in the supplied handbook or a future official message.
