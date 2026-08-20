# Winner blueprint

## What the final MVP must do

1. Name one recognizable operator and one loss in the first sentence.
2. Show a single operational canvas—preferably a map—rather than a dashboard grid.
3. Make the agent visibly cross the full loop: observe → investigate → compare → check → recommend → approve → verify.
4. Use FortyGuard to change the selected place, time, route or allocation. If removing FortyGuard leaves the decision unchanged, kill the concept.
5. End on one recomputed metric or completed operational artifact.
6. Separate measured cached-live values from derived metrics and synthetic constraints at all times.
7. Keep action authority with a named human and show the gate on stage.

## Pitch rules

- Open with the human problem; mention agents and FortyGuard only after the stakes are clear.
- Say “cached FortyGuard analysis from 2025-07-15,” never “live,” during deterministic mode.
- Do not claim health, safety, injury or productivity outcomes from an exposure proxy.
- Do not explain API filters, HFST, WBGT, RNT or specialized specifications in the opening.
- Do not claim uniqueness. State the wedge and show the integration.
- Technical depth belongs in the action rail and evidence drawer, not in the headline.

## UI principles

- One dark cinematic operational stage; one lime action color; amber only for thermal evidence.
- Map first, activity rail second, evidence on demand.
- Motion communicates state transition, never decorative busyness.
- A full-screen hero metric appears only after verification.
- Provenance is one click away and distinguishes `MEASURED`, `DERIVED`, `ASSUMPTION`, and `CACHED`.
- Avoid endless cards, rainbow gradients, opaque glass, fake terminal output and model “thinking.”

## Demo principles

- Deterministic rehearsal is the default and consumes zero API credits.
- Use an identical seed/scenario, fixed timing and recomputable metric on every run.
- Start with a visibly bad plan. A neutral baseline makes the transformation weak.
- Every agent line is a tool/action status; never expose private reasoning.
- Let the map or primary artifact change before explaining the architecture.
- The last 20 seconds belong to the number, impact boundary and expansion path.

## Rubric strategy

| Rubric | Stage proof |
|---|---|
| Impact & Relevance — 40% | A recognizable operator, obvious stakes, public workflow evidence and a concrete before/after metric |
| Technical Execution — 35% | Cached-live FortyGuard evidence, tool orchestration, constraints, deterministic verification, approval and provenance |
| Innovation — 15% | A less-obvious operational reallocation wedge, not another alert or heat dashboard |
| Communication — 10% | Ten-second one-liner, single visual canvas, six-step action rail and one hero metric |

## Architecture of the reusable shell

```text
Fixed demo scenario
  ├─ cached-live measured evidence
  ├─ labelled operational assumptions
  └─ deterministic task constraints
             ↓
Six-state activity sequencer
             ↓
Map / thermal layer + before/after artifact
             ↓
Human approval gate
             ↓
Recomputed hero metric
             ↓
Evidence drawer + high-level audit trace
```

The shell lives in `src/App.tsx`, its deterministic scenario in `src/demo/scenario.ts`, and presentation styling in `src/styles.css`. It has no FortyGuard client dependency and cannot make a live request.

## Evidence-derived north star

The winning pattern is not “more intelligence on screen.” It is a familiar bad decision visibly changing because the agent obtained sponsor-specific evidence, acted within constraints, and proved the result.

`FINAL_MVP_SELECTED = NO`

