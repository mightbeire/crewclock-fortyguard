# CrewClock Final Demo Script

## Demo target

- Target duration: **2:48–2:55**.
- Hard stop: **2:58**.
- Build the demo around one story: **a superintendent has a locked shift, heat changes the decision, CrewClock shows what can move without breaking the plan**.
- Use the verified Palm Springs browser path for the stable on-screen walkthrough.
- State clearly that the Palm Springs walkthrough reuses previously acquired live FortyGuard evidence after an exact site-and-time identity match.
- Do not depend on a fresh provider call during the recording.
- Use the fresh-future San Diego run as the strongest proof point near the end.

## 0:00–0:20 — Make the judge care

Show the upcoming shift before review. Do not begin on a title slide.

> “Tomorrow’s construction shift is already locked around crews, equipment, inspections, qualifications, and deadlines. Then the heat changes. A superintendent does not need another weather alert. They need to know: **what can I move without breaking tomorrow’s job?**”

Pause for one beat.

> “That is what CrewClock answers.”

## 0:20–0:38 — Show the user and promise

Keep the shift visible. Point briefly at the existing task plan.

> “CrewClock is built for the construction superintendent coordinating the next shift. It takes the plan that already exists, finds the outdoor work that can actually move, and turns hyperlocal environmental evidence into one constraint-checked decision.”

Click **Review shift**.

## 0:38–1:05 — Let the agent investigate

Show the live activity stream. Keep this moving; do not narrate every event.

> “The agent first inspects the shift. It decides whether thermal investigation is needed and which workfaces and time windows matter. Those choices control what evidence CrewClock requests. The AI is choosing the investigation path — not inventing schedule times and not approving its own answer.”

## 1:05–1:30 — Make FortyGuard visibly indispensable

Pause on the evidence stage or open the evidence view enough to show workface and time coverage.

> “This is where FortyGuard becomes essential. CrewClock sends the selected polygon workfaces and exact schedule windows to FortyGuard’s heatmap API using the project’s modeled-temperature trigger and the exceedance analytic.”

> “It also acquires the reachable destination windows. If we move a task later, we must have evidence for the place and time we move it to. Unknown evidence never becomes zero.”

> “CrewClock binds FortyGuard’s modeled exceedance evidence to the actual outdoor task, its workface, its time, and its crew size. That gives us Scheduled High-Heat Crew-Hours — SHHCH.”

## 1:30–1:55 — Watch the product act

Return to the schedule as **I found a better sequence** appears. Let the task movement animation play.

> “Now deterministic scheduling code searches the feasible alternatives. Fixed work stays anchored. Dependencies, qualifications, deadlines, crew availability, and employer controls still have to pass.”

As the blocks move:

> “Here, three flexible tasks move. The fixed commitments do not.”

## 1:55–2:15 — The money shot

Keep the before/after result visible for several seconds.

> “The result is **13 scheduled high-heat crew-hours down to 4**. That is nine fewer crew-hours scheduled inside modeled high-heat windows, while all six operational constraint families still pass.”

> “SHHCH is deliberately narrow. It is a schedule-placement metric, not a medical exposure score or a safety certification.”

## 2:15–2:33 — Prove it, then hand control back

Open **Why this plan?** briefly. Show the causal chain, then return to the decision screen.

> “The proof chain is visible: FortyGuard evidence, workface and time overlap, SHHCH, the alternative schedule, and deterministic verification.”

Show **Approve plan** and **Keep current shift**.

> “And the AI still does not get the final word. The superintendent does.”

Click **Approve plan**.

Keep **APPROVED · VERIFIED** visible.

> “After approval, CrewClock verifies the exact recommendation again before the shift becomes final.”

## 2:33–2:47 — Strongest real-time proof

Use the approved state or a prepared San Diego evidence screenshot. Do not switch into a long second walkthrough.

> “We then proved the complete path on a genuinely future San Diego shift using **fresh live FortyGuard evidence**. CrewClock reduced SHHCH from **18 to 9**, moved three flexible tasks, moved zero fixed tasks, kept the schedule at **6 out of 6 constraints**, received superintendent approval, and passed final reverification.”

## 2:47–2:55 — Show judgment and close

> “CrewClock also knows when not to force a change. If the measured shift has no lower-overlap time, it says so instead of calling the schedule optimal or inventing an improvement.”

Final line. Keep CrewClock or the approved schedule visible.

> “A weather dashboard tells a superintendent how hot tomorrow will be. **CrewClock uses FortyGuard to answer the harder question: given tomorrow’s actual work, what should move, what must stay, and does the new plan still work?**”

## Recording rules

- **One user, one problem, one transformation.** Do not turn this into a feature tour.
- Be inside the product by about **20 seconds**.
- Keep the strongest visible number on screen long enough to register.
- Do not explain architecture before the transformation happens.
- Do not mention Groq, TokenRouter, polling bugs, test counts, schemas, or implementation history in the main video. Save those for Q&A.
- Speak naturally. Do not rush to hit every word exactly.
- Prioritize the visible product over reading the script verbatim.
- Keep cursor movement deliberate. Avoid terminals and technical consoles.
- Do not wait on a fresh FortyGuard call during recording.
- Do not call SHHCH “exposure,” “risk,” “heat dose,” or “safety.”
- If the take reaches **2:58**, cut the no-change sentence before cutting the final line.

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
