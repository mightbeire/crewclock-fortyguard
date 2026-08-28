# CrewClock — Hackathon Submission Draft

**Team:** btn operations  
**Primary track:** Agentic AI  
**Secondary track:** Industrial & Enterprise

## Summary

Construction superintendents already have a schedule, crews, fixed commitments, qualifications, and employer operating controls. What they often lack is a fast way to translate hyperlocal modeled heat into a feasible pre-shift decision without breaking that plan.

**CrewClock is an AI pre-shift operations agent that helps a superintendent adjust an upcoming construction shift around hyperlocal modeled heat.**

The agent reads the shift, chooses the bounded workfaces and schedule windows that need investigation, and requests only that evidence. Validated selections causally control the actual FortyGuard geometry and local-time windows sent to the provider. CrewClock then intersects the returned exceedance evidence with outdoor task timing and crew headcount to calculate **Scheduled High-Heat Crew-Hours (SHHCH)**.

The LLM does not control the math or author the final schedule. A deterministic engine generates feasible alternatives and verifies crew assignments, qualifications, dependencies, deadlines, fixed commitments, employer controls, and break/recovery rules. The agent interprets the result and presents it, but the superintendent keeps final authority. Approval is identity-bound and followed by deterministic re-verification.

CrewClock also fails closed. Missing evidence, invalid model actions, provider failure, stale evidence, or failed verification preserve the current shift instead of fabricating a recommendation.

### Real FortyGuard proof

In a preregistered live test on a previously unseen Miami project, CrewClock acquired segmented FortyGuard evidence with zero initial cache reuse and reduced SHHCH from **21.086303 to 5.032994** by retiming two tasks while preserving **6/6 modeled constraint families**. Human approval and final re-verification both passed.

A separate canonical Phoenix replay produced **91.5 → 91.5 SHHCH** while correcting an employer-configured operational constraint from **5/6 → 6/6**. CrewClock correctly made no thermal-improvement claim.

Fresh-site generalization was also tested without preloaded evidence. In Albuquerque, the real agent selected three workfaces and five two-hour windows; those exact selections controlled five live FortyGuard acquisitions. The truthful result was **0 → 0 SHHCH / no improvement**.

CrewClock's distinction is not another heat dashboard. It turns **workface- and time-specific environmental evidence into a deterministically verified construction decision, with the superintendent still in control.**

SHHCH is a schedule-placement metric, not physiological exposure, injury risk, WBGT, or proof of OSHA compliance.
