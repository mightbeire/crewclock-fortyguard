# CrewClock end-to-end hostile finding reproduction

Base: `ccd718472864b8afdc7ab0e3cebc85223900a4ae`.

| # | Finding | Classification | Evidence at base |
|---|---|---|---|
| 1 | Browser computed the complete run before visible investigation | REPRODUCED | `App.tsx` called synchronous `createRuntimeSession`; that called `runCrewClock`. |
| 2 | Runtime events existed before tool completion | REPRODUCED | `buildRuntimeEvents` created the complete array from the finished run. |
| 3 | Timers revealed precomputed events | REPRODUCED | A `setTimeout` advanced `eventIndex` through the completed array. |
| 4 | Python/provider agent absent from browser review | REPRODUCED | The browser imported only TypeScript runtime/engine modules. |
| 5 | Synthetic fixture produced 39 → 36, not 39 → 20 | REPRODUCED | Direct engine execution returned 39 and 36. |
| 6 | One task, not seven, was retimed | REPRODUCED | Direct engine execution selected only `G4`. |
| 7 | Model could effectively author the schedule passed to verification | REPRODUCED | `verify_schedule` accepted a model-supplied schedule object. |
| 8 | Evaluation registries substituted for production scheduling in gates | REPRODUCED | `runtime_evals.py` and real-agent scripts used evaluation-specific handlers. |
| 9 | Production provider limits were below successful workflow depth | REPRODUCED | Default failover budget was 3 turns / 15 seconds; older gates used up to 8 turns / 180 seconds. |
| 10 | Model-facing evidence tool accepted arbitrary fixture paths | REPRODUCED | Registry exposed a free-form `fixture` string. |
| 11 | New Shift discarded scheduling facts | REPRODUCED | Serialization replaced dependencies and weather sensitivity and reassigned qualifications. |
| 12 | Narrow-phone schedule readability was poor | REPRODUCED | 390px retained the desktop Gantt with 8px/6px task text. |
| 13 | Raw runtime/recommendation/candidate IDs appeared on operator surfaces | REPRODUCED | Runtime ID appeared in the footer; all IDs appeared in the evidence view. |

The closure replaces the browser runtime with `POST /api/reviews` plus factual polling, uses a two-turn real-provider orchestration loop, resolves evidence only by approved ID, delegates schedule generation/selection/sealing/verification to the single TypeScript engine, and runs final deterministic re-verification after human approval.
