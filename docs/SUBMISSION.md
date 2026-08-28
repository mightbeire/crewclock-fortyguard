# CrewClock — Hackathon Submission Summary

**Team:** btn operations  
**Primary track:** Agentic AI  
**Secondary track:** Industrial & Enterprise

CrewClock helps construction superintendents adjust an upcoming shift around hyperlocal modeled heat without breaking the schedule.

A superintendent starts with the work that already exists: crews, headcounts, workfaces, task times, fixed commitments, qualifications, dependencies, deadlines, and employer controls. CrewClock’s AI agent reviews that shift and decides whether thermal investigation is necessary. If it is, the agent selects the relevant workfaces and time windows. Those validated selections control the FortyGuard requests.

CrewClock then converts the returned FortyGuard evidence into a schedule-placement metric called Scheduled High-Heat Crew-Hours, or SHHCH. SHHCH measures how many scheduled crew-hours overlap the configured modeled high-heat window. It is not a medical exposure measure, a heat-dose measure, or a statement of OSHA compliance.

The agent does not control schedule arithmetic. Deterministic code calculates SHHCH, generates schedule alternatives, and checks hard constraints. Fixed work stays fixed. Crew availability, qualifications, dependencies, deadlines, and employer controls must still pass. The agent explains the verified result and stops at a human decision point. The superintendent can approve the proposed plan or keep the current shift. After approval, CrewClock verifies the exact schedule again before it becomes final.

In the final browser acceptance test for Palm Springs, California, CrewClock used previously acquired live FortyGuard evidence that matched the exact site and time identity. It reduced SHHCH from 13 crew-hours to 4 crew-hours by retiming three flexible tasks. All six constraint families passed before and after the change. The superintendent approved the recommendation in the browser, and the final deterministic verification passed.

CrewClock also supports truthful no-change and evidence-unavailable outcomes. If no better feasible plan exists, it keeps the current schedule. If usable evidence is unavailable, it does not invent a zero value or fabricate a recommendation.

The result is not another weather dashboard. CrewClock connects workface-level thermal evidence to the actual construction shift, lets an AI agent decide what evidence to investigate, uses deterministic checks for operational correctness, and keeps the superintendent in control.

**Word count:** 321 words, excluding the title and metadata.