# CrewClock — FortyGuard Hackathon 2026

**Team:** btn operations  
**Primary track:** Agentic AI  
**Secondary track:** Industrial & Enterprise

CrewClock helps construction superintendents adjust an upcoming shift around hyperlocal modeled heat without breaking the schedule.

A superintendent starts with crews, workfaces, tasks, fixed commitments, dependencies, qualifications, deadlines, and employer controls. A heat alert does not answer which task can move, where it can move, or whether the new sequence still works. CrewClock connects that operational plan to selected FortyGuard evidence.

The agent chooses the investigation path, workfaces, and schedule windows. CrewClock binds those choices to polygon geometry and local time windows, then uses FortyGuard's `exceedance` analytic with a 32 °C project trigger. It checks reachable destination windows before it credits a move. Without usable evidence, it keeps the current shift.

Deterministic code calculates Scheduled High-Heat Crew-Hours (SHHCH), enumerates feasible alternatives, checks six hard-constraint families, and verifies the exact approved result. The AI cannot set schedule times or approve its own recommendation. The superintendent makes the final decision.

The authoritative San Diego run on August 28, 2026, from 12:00 to 17:00, reduced SHHCH from **18 to 9**, a **50% reduction**. It moved **3 flexible tasks**, moved **0 fixed tasks**, preserved **6/6 constraints**, received **human approval**, and passed **final reverification**. The run used fresh live FortyGuard evidence. The run summary and focused screenshots are in `evidence/san-diego-final-positive/`.

SHHCH is a schedule-placement metric. It is not a medical exposure score, heat-dose measure, safety certification, or compliance statement. Onsite measurement, employer policy, worker condition, workload, PPE, and professional judgment remain authoritative.

**Live demo:** https://crewclock.oluwatomireoluwa.chatgpt.site

**Demo video:** YouTube URL pending
