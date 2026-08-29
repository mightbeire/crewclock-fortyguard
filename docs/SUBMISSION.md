# CrewClock — FortyGuard Hackathon 2026

**Team:** btn operations  
**Primary track:** Agentic AI  
**Secondary track:** Industrial & Enterprise

CrewClock targets a heat-exposed industry. U.S. construction spending ran at a $2.17 trillion annual rate in June 2026, while the industry employed 8.343 million people in July. NIOSH recommends changes to tasks and schedules as workplace heat controls. EPA projects that outdoor workers could lose up to 34 labor hours per person each year to high-temperature days, contributing to as much as $46 billion in lost wages across the U.S. economy by mid-century. Construction, however, cannot simply stop when heat rises; crews, dependencies, deadlines, and fixed commitments must still line up.

The user is the construction superintendent who coordinates those constraints before crews deploy. The buyer is the contractor that wants fewer heat-related disruptions without giving up operational control. CrewClock therefore turns a heat warning into a bounded pre-shift decision: what should move, what must stay, and whether the revised plan still works.

FortyGuard makes that decision possible. Instead of a weather signal, FortyGuard gives CrewClock workface-scale environmental intelligence for the job. CrewClock sends polygons and schedule windows to FortyGuard, uses the `exceedance` analytic with a 32 °C trigger, and checks destination windows before it credits a move. FortyGuard turns heat into operational evidence; CrewClock turns that evidence into a schedule decision. An explicit zero is valid, but missing evidence is never treated as zero.

Moreover, CrewClock limits the AI's authority. The AI chooses the investigation path, workfaces, and time windows. Deterministic code owns arithmetic, SHHCH, schedule feasibility, and six hard-constraint families. The AI cannot set schedule times or approve its recommendation. The superintendent decides, and CrewClock re-verifies the result.

The authoritative San Diego run on August 28 reduced Scheduled High-Heat Crew-Hours (SHHCH) from 18 to 9, a 50% reduction. It moved 3 flexible tasks, moved 0 fixed tasks, preserved 6/6 constraints, received human approval, and passed final reverification. Furthermore, an independent Tucson run on August 29 used fresh FortyGuard evidence with 0 cache reuse and reduced SHHCH from 60 to 24, a 60% reduction, while moving 3 flexible tasks, 0 fixed tasks, and preserving 6/6 constraints. SHHCH is a schedule-placement metric, not a medical exposure score, safety certification, heat-dose measure, or compliance statement.

We also tested FortyGuard. Across 84 controlled requests at 13 U.S. coordinates, 52 returned decision-grade evidence and 32 completed empty; none failed, timed out, or produced client errors. The study is documented in the repository.

Finally, CrewClock's commercial path starts with superintendent approval and can extend into Procore or Primavera P6. A pilot can measure SHHCH change, accepted recommendations, schedule disruption, and superintendent time saved without asking contractors to surrender control.

Most heat tools stop at a forecast or alert. CrewClock combines FortyGuard's hyperlocal environmental intelligence with agentic investigation, deterministic schedule checks, and human approval. CrewClock does not stop at “How hot will it be?” It answers the harder question: “Given tomorrow's actual work, what should move, what must stay, and does the new plan still work?”