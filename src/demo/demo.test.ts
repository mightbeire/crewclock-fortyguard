import { describe, expect, it } from 'vitest'
import {
  CREWS,
  EMPLOYER_POLICY,
  HERO_METRIC,
  TASKS,
  THERMAL_EVIDENCE,
  peakWindowCrewHours,
  validatePlan,
  validatePolicy,
  validateScenario,
} from './scenario'
import {
  CANONICAL_RUN,
  approveRecommendation,
  fixtureRecommendation,
  originalSchedule,
  runCrewClock,
  resetDemoState,
  selectThermalInvestigation,
  verifySchedule,
} from './engine'
import { calculateScheduledHighHeatCrewHours, type ExceedanceWindow } from './shhch'

describe('CrewClock deterministic demo', () => {
  it('recomputes the hero metric from tasks and crew sizes', () => {
    expect(peakWindowCrewHours('original')).toBeNull()
    expect(peakWindowCrewHours('proposed')).toBeNull()
    expect(HERO_METRIC.moved).toBeNull()
    expect(HERO_METRIC.status).toBe('none')
    expect(validateScenario()).toBe(true)
  })

  it('preserves hard schedule constraints in both plans', () => {
    expect(validatePlan('original')).toBe(true)
    expect(validatePlan('proposed')).toBe(true)
    expect(TASKS.filter(task => task.fixed).every(task => task.originalStart === task.proposedStart)).toBe(true)
    expect(CREWS).toHaveLength(3)
    expect(validatePolicy('original')).toBe(false)
    expect(validatePolicy('proposed')).toBe(true)
    expect(CANONICAL_RUN.originalVerification.families.filter(item => item.id !== 'employer-policy').every(item => item.passed)).toBe(true)
  })

  it('keeps evidence and policy provenance explicit', () => {
    expect(THERMAL_EVIDENCE.status).toBe('cached-live-context-only')
    expect(THERMAL_EVIDENCE.cachePaths).toHaveLength(3)
    expect(EMPLOYER_POLICY.status).toBe('synthetic employer policy')
    expect(EMPLOYER_POLICY.authorityBoundary).toContain('Onsite')
  })

  it('derives the locked recommendation instead of trusting fixture timestamps', () => {
    expect(CANONICAL_RUN.status).toBe('missing-evidence')
    expect(CANONICAL_RUN.recommendation).toBeNull()
    expect(CANONICAL_RUN.beforeCrewHours).toBeNull()
    expect(CANONICAL_RUN.afterCrewHours).toBeNull()
    expect(CANONICAL_RUN.message).toContain('schedule-aligned')
  })

  it('verifies every hard-constraint family for the recommendation', () => {
    const verification = verifySchedule(fixtureRecommendation())
    expect(verification.passed).toBe(true)
    expect(verification.passedFamilies).toBe(verification.totalFamilies)
    expect(verification.families.find(item => item.id === 'fixed')?.passed).toBe(true)
    expect(verification.families.find(item => item.id === 'dependencies')?.passed).toBe(true)
    expect(verification.families.find(item => item.id === 'qualifications')?.passed).toBe(true)
    expect(verification.families.find(item => item.id === 'deadlines')?.passed).toBe(true)
    expect(verification.families.find(item => item.id === 'crew-availability')?.passed).toBe(true)
    expect(verification.families.find(item => item.id === 'employer-policy')?.passed).toBe(true)
  })

  it('selectively investigates only movable outdoor work', () => {
    const selection = selectThermalInvestigation()
    expect(selection.investigatedTaskIds).toHaveLength(7)
    expect(selection.skippedIndoorTaskIds).toEqual(['G1', 'E1'])
    expect(selection.retainedFixedTaskIds).toHaveLength(5)
    expect(selection.investigatedTaskIds).not.toContain('C4')
  })

  it('preserves fixed times, dependency order, qualifications, and deadlines', () => {
    const baseline = originalSchedule()
    const proposal = fixtureRecommendation()
    expect(TASKS.filter(task => task.fixed).every(task => proposal[task.id] === baseline[task.id])).toBe(true)
    expect(verifySchedule(fixtureRecommendation()).passed).toBe(true)
  })

  it('fails closed when evidence is missing', () => {
    const run = runCrewClock({ evidenceState: 'missing' })
    expect(run.status).toBe('missing-evidence')
    expect(run.recommendation).toBeNull()
    expect(run.message).toContain('No defensible improvement')
  })

  it.each([
    ['stale' as const, 'stale-evidence'],
    ['tool-failure' as const, 'tool-failure'],
  ])('fails closed for %s evidence', (evidenceState, status) => {
    const run = runCrewClock({ evidenceState })
    expect(run.status).toBe(status)
    expect(run.recommendation).toBeNull()
  })

  it('blocks an ambiguous employer policy', () => {
    const run = runCrewClock({ policyState: 'ambiguous' })
    expect(run.status).toBe('ambiguous-policy')
    expect(run.recommendation).toBeNull()
  })

  it('returns no improvement when all work is immovable', () => {
    const fixedTasks = TASKS.map(task => ({ ...task, fixed: true, proposedStart: task.originalStart }))
    const run = runCrewClock({ tasks: fixedTasks })
    expect(run.status).toBe('no-improvement')
    expect(run.recommendation).toBeNull()
    expect(run.shiftedCrewHours).toBe(0)
  })

  it('replays byte-for-byte deterministically', () => {
    expect(runCrewClock()).toEqual(runCrewClock())
    expect(runCrewClock().deterministicId).toBe('CC-PHX-0716-v1')
  })

  it('records approval only for a verified recommendation', () => {
    const approved = approveRecommendation(CANONICAL_RUN)
    expect(approved.approved).toBe(false)
    expect(approved.plan).toEqual(CANONICAL_RUN.original)
    expect(approved.verification.passed).toBe(false)
    expect(approveRecommendation(runCrewClock({ evidenceState: 'missing' })).approved).toBe(false)
  })

  it('resets to the reproducible original plan', () => {
    expect(resetDemoState()).toEqual({
      stage: -1,
      approved: false,
      planView: 'original',
      schedule: originalSchedule(),
      deterministicId: 'CC-PHX-0716-v1',
    })
  })

  it('uses the same evidence window for temporal and area-weighted SHHCH', () => {
    const window: ExceedanceWindow = {
      analyticType: 'exceedance', start: '12:00', end: '14:00', units: 'hours', status: 'VALID', provenance: 'CACHED_LIVE_FORTYGUARD:test',
      tiles: [
        { polygon: [[0, 0], [5, 0], [5, 10], [0, 10]], valueHours: 2 },
        { polygon: [[5, 0], [10, 0], [10, 10], [5, 10]], valueHours: 0 },
      ],
    }
    const result = calculateScheduledHighHeatCrewHours(
      { full: '12:00', partial: '13:00' },
      [
        { id: 'full', durationMinutes: 120, crewId: 'ground', zoneId: 'north', environment: 'outdoor-heavy', fixed: false },
        { id: 'partial', durationMinutes: 120, crewId: 'ground', zoneId: 'north', environment: 'outdoor-heavy', fixed: false },
      ],
      [{ id: 'ground', headcount: 5 }],
      [{ id: 'north', polygon: [[0, 0], [10, 0], [10, 10], [0, 10]] }],
      [window],
      { thresholdC: 32, quantity: 'fortyguard_modeled_temperature', provenance: 'PROJECT_THERMAL_TRIGGER:test' },
    )
    expect(result.valid).toBe(true)
    expect(result.totalCrewHours).toBe(7.5)
  })
})
