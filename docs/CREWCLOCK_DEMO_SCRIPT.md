# CrewClock three-minute demo script

## Stage contract

- Total target: **2:50**, leaving ten seconds of recovery.
- One user: Construction Superintendent.
- One decision: approve the upcoming-shift revised field plan.
- One transformation: 14 tasks visibly reorder across three crews.
- One hero metric: **scheduled high-heat crew-hours, shown only when validated schedule-aligned exceedance evidence is cached**.
- No chain-of-thought. Show only high-level actions, inputs, constraints and results.
- No safety certification claim. Say “planning evidence,” “modeled window,” and “employer policy.”

## Before walking on stage

1. Run `npm run dev` and open the CrewClock page.
2. Click **Reset**.
3. Confirm the status is `READY TO PLAN` and the header says `THERMAL EVIDENCE UNAVAILABLE · PROVIDER INVESTIGATION`. Do not present a before/after SHHCH number.
4. Confirm the inspector is closed.
5. Do not use a live FortyGuard call during the demo.

## Exact arc

### 0:00–0:20 — Problem

**Screen:** hero and original schedule.

**Say:**

> “The upcoming-shift construction plan is valid on paper. Fourteen tasks, three qualified crews, every inspection and deadline accounted for. But the heaviest movable work is scheduled in Phoenix’s worst modeled heat window. CrewClock fixes the timing without blowing the day.”

Point to the evidence state and the original schedule. Do not discuss regulation or present an unvalidated SHHCH number.

### 0:20–0:40 — Original plan and evidence

**Screen:** schedule, thermal profile and workface map.

**Say:**

> “The superintendent sees the real decision surface: the upcoming-shift tasks, fixed commitments, crews, two workfaces, and cached FortyGuard evidence. This replay peaks at 40.2°C TCM tile maximum; env_params is selective context only around 1 p.m. The task and crew data are clearly labelled demo inputs.”

Point once to the orange 11:00–15:00 band and once to locked tasks.

### 0:40–1:30 — Agent investigates

Click **Run the upcoming-shift plan**.

**Say while the activity rail advances:**

> “CrewClock reads the look-ahead, selects only flexible outdoor work that deserves thermal investigation, loads the relevant evidence, and hands the math to a deterministic scheduler. It then checks qualifications, dependencies, deadlines, fixed work, and the company’s own planned controls.”

Do not narrate hidden reasoning. Let the seven high-level stages land.

### 1:30–2:00 — Schedule transforms (only when evidence is valid)

**Screen:** proposal automatically slides into view only after valid exceedance evidence and deterministic verification.

**Say:**

> “The work moves, not the obligations. Any proposed movement is derived from validated exceedance windows and deterministic feasibility checks. Fixed delivery and inspection commitments stay locked.”

Toggle **Before** then **Proposed** once if the audience needs the contrast. End on Proposed.

### 2:00–2:25 — Verification

Point to constraint strip and agent card.

**Say:**

> “CrewClock retained all 14 tasks, all three crew qualification sets, every dependency, five fixed commitments, and every deadline. Missing or conflicting required evidence would stop here as unknown.”

### 2:25–2:45 — Human approval (only when a verified recommendation exists)

Click **Approve the upcoming-shift plan**.

**Say:**

> “The construction superintendent—not the model—approves. CrewClock changes no external schedule in this MVP. Onsite WBGT, company policy and field judgment still control the shift.”

### 2:45–3:00 — Hero metric (only when evidence is complete)

Point to the verified result in the right rail; if the evidence is incomplete, keep the run in its safe evidence-unavailable state.

**Say:**

> “The metric is derived from the same jobs, crews, deadlines, workface geometry, validated exceedance duration, exact task overlap, and crew headcount. It is a planning metric—not a safety outcome.”

End on the validated evidence state and the derived metric only if the complete window set is present.

## Judge answers

### “Isn’t this just Weather.com?”

> “A forecast identifies a hot day. CrewClock identifies which work zones and tasks need investigation, uses FortyGuard timing and spatial evidence, generates only feasible alternatives, and verifies the actual field plan.”

### “Isn’t this a spreadsheet?”

> “A superintendent can manually solve a small day. CrewClock automates the evidence, policy, crew, dependency, inspection and deadline cross-check—and leaves an auditable recommendation. The spreadsheet baseline is part of final validation.”

### “Is this a safety system?”

> “No. It is pre-shift planning support. Onsite measurement, employer policy, trained supervision and professional judgment remain authoritative.”

### “What is real?”

> “The Phoenix contextual responses are cached-live, but compatible decision-grade exceedance evidence is unavailable. The construction context is grounded in public ADOT and OSHA/NIOSH sources, and the 14-task look-ahead is a labelled synthetic work package.”

### “Why an agent?”

> “The optimizer does math. The agent decides what needs investigation, gathers heterogeneous evidence, manages uncertainty, explains the recommendation, verifies it, and routes approval.”

## Failure-safe stage path

- If animation stalls, keep the evidence-unavailable state visible; do not substitute a placeholder metric.
- If approval does not animate, open the Evidence drawer and state the exact evidence gap.
- If asked for current weather, say this is an intentionally reproducible historical replay; do not imply it is a current forecast.
- If asked to certify safety, refuse the premise and point to the onsite-authority boundary.

`THREE_MINUTE_DEMO = PASS`

## Foundation language

Say “upcoming shift” and “scheduled high-heat crew-hours”. Explain that the Phoenix contextual replay is cached-live, while SHHCH is unavailable pending compatible exceedance evidence and the schedule/employer policy are synthetic operational inputs. Do not call the environmental parameter curve a forecast, call wet bulb WBGT, or claim OSHA compliance.
