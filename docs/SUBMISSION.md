# CrewClock — Hackathon Submission Summary

**Team:** btn operations  
**Primary track:** Agentic AI  
**Secondary track:** Industrial & Enterprise

## Problem

Tomorrow’s jobsite can be hot while the day is already locked around crews, inspections, deliveries, equipment, and deadlines. A heat alert tells a superintendent it is hot. It does not answer the operational question: what work can move, where can it move, and will the new sequence still work?

U.S. construction spending reached about $2.17 trillion at an annual rate in June 2026, and construction employed about 8.34 million people in July. EPA projects that high-temperature days could cost outdoor U.S. workers up to 34 labor hours per worker each year and contribute to as much as $46 billion in lost wages by mid-century. CrewClock closes the gap between knowing heat is coming and knowing what to do.

## User

CrewClock is built for the construction superintendent who coordinates the next shift. The superintendent uses CrewClock; the contractor has a reason to pay for it. A first deployment can run on one project in approval-only mode, then add read-only schedule imports from Procore or Primavera.

## FortyGuard usage

FortyGuard is the environmental intelligence that makes CrewClock’s core decision possible.

The agent selects the workfaces and time windows that need thermal investigation. CrewClock sends those validated selections to `POST /v1/heatmap` with polygon AOIs, exact time windows, a 32 °C project trigger, and the `exceedance` analytic. It also acquires evidence across reachable destination windows inside the submitted shift.

CrewClock combines that evidence with workface geometry, outdoor task timing, and crew headcount to calculate Scheduled High-Heat Crew-Hours (SHHCH). Deterministic code searches alternatives and verifies fixed commitments, dependencies, qualifications, deadlines, crew availability, and employer controls. Unknown evidence is never treated as zero.

## Measured result

In a fresh-future San Diego browser run on August 28, 2026, CrewClock reduced SHHCH from **18 to 9 crew-hours**, a **50 percent reduction**. It retimed three flexible tasks, changed zero fixed tasks, preserved all six constraint families, received superintendent approval, and passed final deterministic reverification.

The same product also reduced SHHCH from **13 to 4** in Palm Springs using exact-identity cached-live evidence and from **21.09 to 5.03** in a separate real Miami integration run.

Final live testing exposed and fixed three defects: provider polling was too short, baseline validation happened too late, and destination evidence did not cover the full reachable shift horizon.

CrewClock also distinguishes “no improvement” from “the schedule is optimal.” If complete evidence shows the configured trigger across the full measured shift for every investigated workface, CrewClock says that retiming inside the shift cannot reduce SHHCH. It does not make a safety determination. The superintendent uses the employer heat plan to decide whether to delay, modify, or keep the work.

CrewClock turns hyperlocal environmental intelligence into a measurable, constraint-checked construction decision while the superintendent keeps final authority.

**Word count:** 464 words, including section headings and excluding the title and team metadata.