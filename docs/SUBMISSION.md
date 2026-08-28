# CrewClock — Hackathon Submission Summary

**Team:** btn operations  
**Primary track:** Agentic AI  
**Secondary track:** Industrial & Enterprise

## Problem

Tomorrow’s jobsite can be hot while the day is already locked around crews, inspections, deliveries, equipment, and deadlines. A heat alert tells a superintendent it is hot. It does not answer the operational question: what work can move, where can it move, and will the new sequence still work?

The problem has national scale. U.S. construction spending reached about $2.17 trillion at an annual rate in June 2026, and construction employed about 8.34 million people in July. EPA projects that high-temperature days could cost outdoor U.S. workers up to 34 labor hours per worker each year and contribute to as much as $46 billion in lost wages by mid-century. CrewClock closes the gap between knowing heat is coming and knowing what to do.

## User

CrewClock is built for the construction superintendent who coordinates the next shift. It helps find movable outdoor work, test a better sequence, and see why the proposed change works.

The superintendent uses CrewClock; the contractor has a reason to pay for it. A first deployment can run on one project in approval-only mode. Later versions can import schedules from Procore or Primavera. Contractors can measure planning time, SHHCH, overtime, idle labor, schedule variance, and plan reliability.

## FortyGuard usage

FortyGuard is the environmental intelligence that makes CrewClock’s core decision possible.

The agent selects the workfaces and schedule windows that need thermal investigation. CrewClock sends those selections to FortyGuard through `POST /v1/heatmap`, using polygon AOIs, exact date and time windows, a 32 °C project threshold, and the `exceedance` analytic. CrewClock retrieves the result through `GET /v1/status/{activity_id}`.

CrewClock combines FortyGuard’s exceedance evidence with workface geometry, outdoor task timing, and crew headcount to calculate Scheduled High-Heat Crew-Hours (SHHCH). Deterministic code searches alternatives and verifies fixed commitments, dependencies, qualifications, deadlines, crew availability, and employer controls. Without usable FortyGuard evidence, CrewClock will not make a thermal rescheduling recommendation.

## Measured result

In our final browser-only Palm Springs acceptance test, CrewClock cut SHHCH from 13 crew-hours to 4. That is 9 fewer scheduled crew-hours inside modeled high-heat windows, a 69 percent reduction in schedule overlap.

CrewClock retimed three flexible tasks while all six constraint families remained valid. Fixed commitments stayed fixed. The superintendent approved the recommendation, and CrewClock completed final deterministic reverification.

In a separate real Miami integration test, CrewClock reduced SHHCH from 21.09 to 5.03 crew-hours, about a 76 percent reduction. Both results showed the same behavior: use local thermal evidence to find a lower-overlap schedule without letting the AI override hard operational constraints.

When usable evidence was unavailable, CrewClock preserved the original schedule instead of inventing a zero. The final build passed 196 automated tests, build and type checks, secret scanning, and independent browser acceptance.

CrewClock does not stop at “How hot will it be?” It answers the harder question: “Given tomorrow’s actual work, what should move, what must stay, and does the new plan still work?”

That is what FortyGuard makes actionable: hyperlocal environmental intelligence becomes a measurable, constraint-checked construction decision, while the superintendent keeps final authority.

**Word count:** 495 words, including section headings and excluding the title and team metadata.