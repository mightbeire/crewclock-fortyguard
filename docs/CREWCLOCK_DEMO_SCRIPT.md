# CrewClock Final Demo Script

## Demo target

- Target duration: **2:48–2:55**.
- Hard stop: **2:58**.
- The submission portal requires the **project actually working**. Slides do not count.
- Keep the real CrewClock application visible from **0:00 to the final frame**.
- Do not use title slides, architecture slides, external screenshots, or presentation cards.
- Use the verified Palm Springs browser path for the stable on-screen walkthrough.
- State clearly that the Palm Springs walkthrough reuses previously acquired live FortyGuard evidence after an exact site-and-time identity match.
- Do not depend on a fresh provider call during recording.
- The fresh-future San Diego run is supporting proof in narration, not a slide cutaway.

## 0:00–0:16 — Cold open: the contradiction

Start **inside CrewClock** with the Palm Springs shift already loaded. The schedule itself should fill the screen. Do not show a logo card first.

> “This construction schedule is valid. **That is the problem.** Every operational constraint can pass, and the shift can still place crew-hours inside modeled high-heat windows.”

Point briefly at the actual schedule.

> “A superintendent cannot just move work around and hope the rest of the day survives. CrewClock has to find a lower-overlap plan **without breaking the job.**”

Immediately click **Review shift**.

## 0:16–0:34 — State the promise while the product starts working

Keep the live application visible as the review begins.

> “CrewClock is an AI pre-shift operations agent for construction superintendents. It starts with the schedule that already exists, finds the outdoor work that can actually move, and turns hyperlocal thermal evidence into one verified decision.”

## 0:34–1:04 — Show the agent making consequential choices

Let the real runtime activity progress. Do not read every event.

> “The agent first inspects the shift. It decides whether thermal investigation is needed, which workfaces matter, and which time windows need evidence. Those choices are consequential: they determine what CrewClock asks FortyGuard to investigate.”

> “The AI does not invent the schedule math, and it cannot approve its own answer.”

## 1:04–1:32 — Make FortyGuard visibly load-bearing

Open **Evidence & audit** or pause on the real evidence stage inside CrewClock. Keep the application visible.

> “This is the core of the product. CrewClock sends the selected polygon workfaces and schedule windows to FortyGuard using the project’s modeled-temperature trigger and the exceedance analytic.”

> “It also acquires the reachable destination windows. If a task could move to 3 p.m., CrewClock needs evidence for 3 p.m. Unknown evidence never becomes zero.”

> “FortyGuard’s modeled exceedance evidence is then bound to the actual outdoor task, its workface, its timing, and its crew size. That produces Scheduled High-Heat Crew-Hours — SHHCH.”

Return to the schedule before the recommendation appears.

## 1:32–1:56 — Watch CrewClock act

Let **I found a better sequence** appear and allow the real task movement animation to play.

> “Now deterministic scheduling code tests the feasible alternatives. Fixed commitments stay anchored. Dependencies, qualifications, deadlines, crew availability, and employer controls still have to pass.”

As the blocks move:

> “Three flexible tasks move. The fixed work does not.”

## 1:56–2:17 — The money shot

Keep **13h → 4h** visible for several seconds.

> “The result: **13 scheduled high-heat crew-hours becomes 4**. That is nine fewer crew-hours scheduled inside modeled high-heat windows, while all six operational constraint families still pass.”

> “SHHCH is deliberately narrow. It is a schedule-placement metric, not a medical exposure score or a safety certification.”

## 2:17–2:35 — Prove it inside the product

Open **Why this plan?** inside CrewClock. Do not switch to a slide.

> “And CrewClock shows its work: FortyGuard evidence, workface and time coverage, SHHCH, the alternative schedule, and deterministic verification are all visible in the same decision chain.”

Return to the decision screen.

## 2:35–2:48 — Human authority

Show **Approve plan** and **Keep current shift**.

> “The AI still does not get the final word. The superintendent does.”

Click **Approve plan**.

Hold **APPROVED · VERIFIED** on screen.

> “After approval, CrewClock verifies the exact recommendation again before the shift becomes final.”

## 2:48–2:55 — Final proof and close

Keep the approved CrewClock state visible. Do not cut to a screenshot or slide.

> “We also proved this end to end on a genuinely future San Diego shift with fresh live FortyGuard evidence: **18 SHHCH to 9, three flexible tasks moved, zero fixed tasks moved, and 6 out of 6 constraints preserved.**”

Final line:

> “A weather dashboard tells a superintendent how hot tomorrow will be. **CrewClock uses FortyGuard to tell them what can move without breaking tomorrow’s job.**”

## If there is 5–8 seconds spare

Only use this if the take is safely below 2:55. Keep the product visible.

> “And when there is nowhere lower-overlap to move the work, CrewClock says so instead of inventing an improvement.”

## Recording choreography

- Start with the working CrewClock schedule already loaded.
- No title card.
- No slides.
- No architecture diagram.
- No terminal.
- No external screenshot cutaway.
- No editor or code window.
- Every click must advance the same real user story.
- Keep the cursor still while important numbers are on screen.
- Let the task movement animation finish before speaking over the result.
- Hold the **13 → 4** result for at least 3 seconds.
- Hold **APPROVED · VERIFIED** for at least 2 seconds.
- Do not wait on a fresh FortyGuard request during the recording.
- Do not call SHHCH “exposure,” “risk,” “heat dose,” or “safety.”
- If the take reaches **2:58**, cut the San Diego support sentence before cutting the final line.

## Why this hook is stronger

The opening does not explain heat or construction in the abstract. It creates a contradiction the judge can understand immediately:

**the schedule is operationally valid, but still thermally poor.**

That gives CrewClock a concrete job to perform on screen: improve the thermal placement without breaking the six operational constraint families.

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
