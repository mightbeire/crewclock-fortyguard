# Hackathon rules and verified constraints

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

## Verified from current official FortyGuard documentation

- API key authentication uses the `api-key` request header; no OAuth exchange is required.
- Analysis calls submit an asynchronous activity and return an `activity_id`; results are retrieved from `GET /v1/status/{activity_id}`.
- Status values documented include Processing, Completed, and Failed; failed runs are not charged credits.
- `/v1/heatmap` accepts GeoJSON polygon AOIs, filter types 1–4, and 60/80/100 m granularity.
- Heatmap analytics include `tcm`, `time_of_measure`, `exceedance`, and `persistence`.
- `/v1/env_params` accepts a point, a Celsius temperature anchor, and filter types 1–3; output is time-aligned environmental parameter arrays plus solar irradiance.
- Premium-only endpoints include satellite segmentation, street-view segmentation, and heat-intelligence reports.
- Usage reporting endpoints exist for current-cycle and custom-range credit usage.

Sources: [Authentication](https://docs-api.fortyguard.com/docs/authentication), [Quickstart](https://docs-api.fortyguard.com/docs/quickstart), [Heatmap](https://docs-api.fortyguard.com/docs/create-heatmap), [Environmental Parameters](https://docs-api.fortyguard.com/docs/environmental-parameters), [Status](https://docs-api.fortyguard.com/docs/check-status), [Release Notes](https://docs-api.fortyguard.com/docs/release-notes).

## Verified locally

- `.env` exists and is ignored by the repository ignore policy. Its contents were not printed or committed.
- Live usage check passed on August 19, 2026.
- Live account response reported plan type `Hackathon`, 2,000,000 total/remaining credits, and 0 used at verification time.
- The vendored quickstart includes Python client code, notebooks, and cached JSON responses for heatmaps, environmental parameters, satellite, and street-view examples.

## Assumptions

- The hackathon account can be used for a U.S. demonstration location.
- The official public docs are the appropriate current source even where the older vendored quickstart differs.
- The final demo can use cached responses to avoid unnecessary credit use, with a clearly labeled live path if needed.
- Human approval is required for schedule, dispatch, maintenance-window, or alert actions.

## Unanswered questions

- Exact hackathon submission form, demo format, eligibility, and disclosure requirements were not available in the local workspace or official FortyGuard docs located in this run.
- Exact per-endpoint credit pricing and rate limits for the Hackathon account remain unverified.
- Whether Premium-only endpoints are enabled for this account remains unverified; do not depend on them without a safe capability check.
- Whether the organizer provides official Slack announcements accessible to this session remains unverified.
