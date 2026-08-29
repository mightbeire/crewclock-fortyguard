# CrewClock Final Demo Script

## Demo target

- Target duration: **2:45–2:55**.
- Hard stop: **2:58**. Leave a small upload/editing buffer under the three-minute limit.
- Use the verified Palm Springs browser path for the stable on-screen walkthrough.
- State clearly that the Palm Springs demo reuses previously acquired live FortyGuard evidence after an exact site-and-time identity match.
- Do not depend on a fresh provider call during the recording.
- Keep the superintendent approval and final reverification visible.
- Close with the fresh-future San Diego proof: **18 → 9 SHHCH, 3 flexible tasks moved, 0 fixed tasks moved, 6/6 → 6/6, approval PASS, final reverification PASS**.

## 0:00–0:22 — Problem and user

Show the upcoming Palm Springs shift before review.

> “Construction superintendents already have to coordinate crews, inspections, deliveries, equipment, qualifications, and deadlines. Heat adds another constraint, but a weather alert still does not tell them what work can actually move. NIOSH already recommends task and schedule changes as a workplace heat control. CrewClock turns that idea into a pre-shift operational decision.”

## 0:22–0:48 — What the agent does

Start **Review shift** and briefly show the live activity stream.

> “The AI agent first inspects the real shift and decides whether thermal investigation is needed. It selects the workfaces and time windows that matter. Those choices control the evidence path. The AI does not calculate the schedule or approve its own recommendation.”

## 0:48–1:18 — Make FortyGuard central

Open or pause on the FortyGuard evidence step and the workface/time coverage.

> “This is where FortyGuard becomes central to CrewClock. For each selected polygon workface and schedule window, CrewClock requests FortyGuard heatmap evidence using the project’s 32-degree modeled-temperature trigger and the exceedance analytic. It also measures reachable destination windows, because moving a task only counts if we have evidence for where it may move. Missing evidence never becomes zero.”

> “CrewClock then binds FortyGuard’s modeled exceedance evidence to the actual outdoor task time, workface, and crew headcount. That produces Scheduled High-Heat Crew-Hours, or SHHCH.”

## 1:18–1:43 — Show the recommendation

Let **I found a better sequence** appear. Show the moved task blocks.

> “Deterministic scheduling code now searches feasible alternatives. Fixed commitments stay anchored. Dependencies, qualifications, deadlines, crew availability, and employer controls still have to pass. In this verified Palm Springs path, three flexible tasks move and all six constraint families remain valid.”

## 1:43–2:03 — Show the measured change

Point to **13h → 4h** and the evidence chain.

> “SHHCH falls from 13 to 4 crew-hours. That is nine fewer scheduled crew-hours inside modeled high-heat windows. SHHCH is deliberately narrow: it is a schedule-placement metric, not a physiological exposure score, medical-risk prediction, or safety certification.”

## 2:03–2:25 — Human authority and final verification

Show **Approve plan** and **Keep current shift**.

> “CrewClock stops before changing the shift. The superintendent keeps final authority.”

Click **Approve plan**. Keep **APPROVED · VERIFIED** visible.

> “After approval, CrewClock verifies the exact recommendation again against the same schedule, evidence, policy, and hard constraints before it becomes final.”

## 2:25–2:43 — Strongest fresh-live proof

Keep the approved state visible, or briefly show the final San Diego evidence screenshot if it is already prepared for the recording.

> “We then proved the full path on a genuinely future San Diego shift using fresh live FortyGuard evidence. CrewClock reduced SHHCH from 18 to 9, a 50 percent reduction, moved three flexible tasks, moved zero fixed tasks, preserved all six constraint families, received superintendent approval, and passed final deterministic reverification.”

## 2:43–2:55 — Boundary and close

> “And CrewClock does not force a change. If the complete measured shift stays above the configured trigger, it says retiming inside that shift cannot reduce SHHCH and returns the decision to the superintendent and employer heat plan. If evidence is unavailable, it fails closed.”

> “CrewClock answers the question a weather dashboard cannot: given tomorrow’s actual work, what should move, what must stay, and does the new plan still work?”

## Recording rules

- Speak naturally. Do not rush to hit every word exactly.
- Prioritize the visible product over reading the script verbatim.
- Keep cursor movement deliberate and avoid opening technical consoles.
- Do not wait on a fresh FortyGuard call during the recording.
- Do not call SHHCH “exposure,” “risk,” “heat dose,” or “safety.”
- If the take reaches **2:58**, cut the final sentence rather than exceed three minutes.

## Judge questions

### Why use AI?

> “The agent decides whether investigation is needed and which workfaces and time windows need evidence. Those choices materially control the FortyGuard evidence path. Deterministic code owns schedule arithmetic and verification.”

### Why is FortyGuard essential?

> “Without FortyGuard, CrewClock has no decision-grade environmental evidence for the workface and time windows. FortyGuard supplies the modeled exceedance evidence that CrewClock binds to task timing and crew size. Without usable FortyGuard evidence, CrewClock will not issue a thermal rescheduling recommendation.”

### Why is this not a weather dashboard?

> “A dashboard reports conditions. CrewClock connects workface-level FortyGuard evidence to the actual construction shift, searches feasible schedule alternatives, checks six hard operational constraint families, and hands one verified decision to the superintendent.”

### What is the strongest live proof?

> “On August 28, 2026, a fresh-future San Diego run reduced SHHCH from 18 to 9. Three flexible tasks moved, fixed work did not move, constraints stayed 6/6, and both human approval and final reverification passed.”

### What is SHHCH?

> “Scheduled High-Heat Crew-Hours measures scheduled crew-hours that overlap the configured modeled high-heat window. It is a planning metric, not a physiological exposure measure.”

### What if the whole measured shift is above the trigger?

> “CrewClock says there is no lower-overlap time inside the measured shift. It does not call the schedule optimal or make a safety determination. The superintendent uses the employer heat plan to decide whether to delay, modify, or keep the work.”

### What happens when evidence is missing?

> “CrewClock preserves the current schedule and reports that evidence is unavailable. It does not fabricate a recommendation or convert missing evidence into zero.”
