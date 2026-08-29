# CrewClock — Hackathon Submission Summary

**Team:** btn operations  
**Primary track:** Agentic AI  
**Secondary track:** Industrial & Enterprise

Tomorrow’s jobsite can be hot while the day is already locked around crews, inspections, deliveries, equipment, and deadlines. A heat alert tells a superintendent it is hot. It does not answer the operational question: what work can move, where can it move, and will the new sequence still work? NIOSH already recommends changes to tasks and schedules as a workplace heat control.

June 2026 U.S. construction spending was about $2.17 trillion annualized, and July construction employment was about 8.34 million. EPA projects high-temperature days could cost outdoor U.S. workers up to 34 labor hours each year and contribute to as much as $46 billion in lost wages by mid-century. CrewClock closes the gap between knowing heat is coming and knowing what to do.

CrewClock is built for the **construction superintendent** who coordinates the next shift. It helps that person find movable outdoor work, test a better sequence, and see why the proposed change still works.

The contractor is the buyer. A first deployment can run on one project in approval-only mode, with the superintendent keeping final authority. A production version can import look-ahead schedules from systems such as Procore or Primavera and return approved changes through existing workflows. Contractors can measure value with their own records: planning time, SHHCH, overtime, idle labor, schedule variance, and plan reliability.

FortyGuard is the environmental intelligence that makes CrewClock’s core decision possible. The agent selects the workfaces and time windows that need investigation. CrewClock sends those selections to `POST /v1/heatmap` using one polygon AOI per workface, local windows, a 32 °C trigger, and the `exceedance` analytic. It retrieves results through `GET /v1/status/{activity_id}` and checks reachable destination windows. Without usable schedule-aligned FortyGuard evidence, CrewClock makes no thermal rescheduling recommendation.

CrewClock joins FortyGuard evidence with workface geometry, task timing, and crew headcount to calculate Scheduled High-Heat Crew-Hours (SHHCH). Deterministic code searches alternatives and verifies fixed commitments, dependencies, qualifications, deadlines, crew availability, and employer controls. Unknown evidence is never treated as zero, and the AI cannot override hard constraints.

In a fresh-future San Diego browser run on August 28, 2026, CrewClock reduced SHHCH from 18 to 9 crew-hours, a 50 percent reduction. It retimed three flexible tasks, moved zero fixed tasks, preserved all six constraint families, received superintendent approval, and passed reverification. Palm Springs produced a second reduction from 13 to 4 using cached-live FortyGuard evidence.

If complete FortyGuard evidence shows the configured trigger across the measured shift for every investigated workface, CrewClock says retiming inside that shift cannot reduce SHHCH. It does not call the schedule optimal or make a safety determination. The superintendent uses the employer heat plan to decide whether to delay, modify, or keep the work.

CrewClock does not stop at **“How hot will it be?”** It answers the harder question: **“Given tomorrow’s actual work, what should move, what must stay, and does the new plan still work?”** FortyGuard makes that question answerable with modeled evidence, while deterministic verification and human approval keep the decision grounded.

**Word count:** 499 words, excluding the title and team metadata.