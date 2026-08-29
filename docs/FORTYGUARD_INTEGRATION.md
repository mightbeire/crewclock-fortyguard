# FortyGuard integration

FortyGuard provides the modeled environmental evidence that CrewClock uses to screen a shift. It is not a safety certification service.

## Request path

1. The agent reviews the submitted shift.
2. It selects movable outdoor work, affected workfaces, and relevant schedule windows.
3. The trusted backend binds each request to a workface polygon and local time window.
4. CrewClock sends the selected request to `POST /v1/heatmap`.
5. The backend polls `GET /v1/status/{activity_id}` for the asynchronous result.
6. CrewClock validates the analytic, date, timezone, geometry, threshold, and coverage.
7. The scheduler checks every reachable destination window before it credits a task move.

## Decision contract

The project trigger is 32 °C. The decision analytic is `exceedance`. CrewClock uses schedule-aligned exceedance duration over workface polygons. Optional context, such as an environmental-parameter result, cannot supply SHHCH duration.

Each evidence item carries provenance and an availability state. Missing, stale, empty, or mismatched evidence stays unavailable. It never becomes zero. Without usable evidence for the required origin and destination windows, CrewClock keeps the current shift.

## Why this is load-bearing

A general weather value cannot show whether a specific task can move to a reachable time window. Workface polygons and schedule windows bind the environmental result to the operational choice. Destination coverage prevents CrewClock from claiming a lower result for an unmeasured window.

## Boundary

FortyGuard is modeled environmental intelligence. SHHCH is a schedule-placement metric. It is not a physiological exposure score, medical advice, a heat-dose measure, or a compliance statement. Onsite measurement, the employer heat plan, worker condition, workload, PPE, and professional judgment remain authoritative.
