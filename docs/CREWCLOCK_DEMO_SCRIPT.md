# CrewClock three-minute demo script

## Stage contract

- Total target: **2:50**, leaving ten seconds of recovery.
- One user: Construction Superintendent.
- One decision: approve the upcoming-shift revised field plan.
- One transformation: 14 tasks visibly reorder across three crews.
- One hero metric: **scheduled high-heat crew-hours, 22 before → 6 proposed in the deterministic historical replay**.
- No chain-of-thought. Show only high-level actions, inputs, constraints and results.
- No safety certification claim. Say “planning evidence,” “modeled window,” and “employer policy.”

## Before walking on stage

1. Run `npm run dev` and open the CrewClock page.
2. Click **Reset**.
3. Confirm the status is `READY TO PLAN`, the schedule toggle is `Original 22h`, and the header says `FORTYGUARD CACHE READY · CACHED-LIVE REPLAY`.
4. Confirm the inspector is closed.
5. Do not use a live FortyGuard call during the demo.

## Exact arc

### 0:00–0:20 — Problem

**Screen:** hero and original schedule.

**Say:**

> “The upcoming-shift construction plan is valid on paper. Fourteen tasks, three qualified crews, every inspection and deadline accounted for. But the heaviest movable work is scheduled in Phoenix’s worst modeled heat window. CrewClock fixes the timing without blowing the day.”

Point to `22h` on the Before toggle. Do not discuss regulation.

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

### 1:30–2:00 — Schedule transforms

**Screen:** proposal automatically slides into view.

**Say:**

> “The work moves, not the obligations. Groundworks and signal pulls shift earlier. Sheltered equipment service and cabinet pre-wire move into the peak period. The concrete delivery and inspection windows stay locked.”

Toggle **Before** then **Proposed** once if the audience needs the contrast. End on Proposed.

### 2:00–2:25 — Verification

Point to constraint strip and agent card.

**Say:**

> “CrewClock retained all 14 tasks, all three crew qualification sets, every dependency, five fixed commitments, and every deadline. Missing or conflicting required evidence would stop here as unknown.”

### 2:25–2:45 — Human approval

Click **Approve the upcoming-shift plan**.

**Say:**

> “The construction superintendent—not the model—approves. CrewClock changes no external schedule in this MVP. Onsite WBGT, company policy and field judgment still control the shift.”

### 2:45–3:00 — Hero metric

Point to the verified result in the right rail; no scrolling is required at 1440×900.

**Say:**

> “Same jobs. Same crews. Same deadlines. Movable outdoor work in the highest modeled heat window drops from 22 crew-hours to 6: sixteen crew-hours better timed. That is a planning metric—not a claim that anyone is sixteen hours safer.”

End on the three numbers: **22 → 6 → 16**.

## Judge answers

### “Isn’t this just Weather.com?”

> “A forecast identifies a hot day. CrewClock identifies which work zones and tasks need investigation, uses FortyGuard timing and spatial evidence, generates only feasible alternatives, and verifies the actual field plan.”

### “Isn’t this a spreadsheet?”

> “A superintendent can manually solve a small day. CrewClock automates the evidence, policy, crew, dependency, inspection and deadline cross-check—and leaves an auditable recommendation. The spreadsheet baseline is part of final validation.”

### “Is this a safety system?”

> “No. It is pre-shift planning support. Onsite measurement, employer policy, trained supervision and professional judgment remain authoritative.”

### “What is real?”

> “The Phoenix FortyGuard responses are cached-live, the construction context is grounded in public ADOT and OSHA/NIOSH sources, and the 14-task look-ahead is a labelled synthetic work package.”

### “Why an agent?”

> “The optimizer does math. The agent decides what needs investigation, gathers heterogeneous evidence, manages uncertainty, explains the recommendation, verifies it, and routes approval.”

## Failure-safe stage path

- If animation stalls, click **CrewClock proposed plan**; the deterministic plan remains available.
- If approval does not animate, open the Evidence drawer and state the already-computed `22 → 6` result.
- If asked for current weather, say this is an intentionally reproducible historical replay; do not imply it is a current forecast.
- If asked to certify safety, refuse the premise and point to the onsite-authority boundary.

`THREE_MINUTE_DEMO = PASS`

## Foundation language

Say “upcoming shift” and “scheduled high-heat crew-hours”. Explain that the historical Phoenix replay is cached-live evidence, while the schedule and employer policy are synthetic operational inputs. Do not call the environmental parameter curve a forecast, call wet bulb WBGT, or claim OSHA compliance.
