import { describe, expect, it } from 'vitest'
import {
  CREWS,
  BREAK_POLICY,
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
  agentAudit,
  approveRecommendation,
  fixtureRecommendation,
  originalSchedule,
  runCrewClock,
  resetDemoState,
  selectThermalInvestigation,
  verifySchedule,
  verifyBreakPolicy,
} from './engine'
import { calculateScheduledHighHeatCrewHours, type ExceedanceWindow } from './shhch'
import { candidateHash, policyContentHash, sha256 } from './integrity'
import { SYNTHETIC_POSITIVE_EVIDENCE } from './runtime'

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
    expect(THERMAL_EVIDENCE.status).toBe('EVIDENCE_UNAVAILABLE')
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

  it('reports truthful evidence provenance for unavailable and provider-error states', () => {
    expect(agentAudit(runCrewClock({ evidenceState: 'missing' }), false).map(entry => entry.source)).toContain('EVIDENCE_UNAVAILABLE')
    expect(agentAudit(runCrewClock({ evidenceState: 'stale' }), false).map(entry => entry.source)).toContain('EVIDENCE_UNAVAILABLE')
    expect(agentAudit(runCrewClock({ evidenceState: 'tool-failure' }), false).map(entry => entry.source)).toContain('PROVIDER_ERROR')
    expect(agentAudit(CANONICAL_RUN, false).map(entry => entry.source)).toContain('SYNTHETIC')
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
      analyticType: 'exceedance', start: '12:00', end: '14:00', units: 'hours', status: 'VALID', provenance: 'CACHED_LIVE_FORTYGUARD:test', aoi: 'phoenix-test-aoi', date: '2025-07-15', timezone: 'America/Phoenix', analyticSource: 'FortyGuard:/v1/heatmap', projectThermalTrigger: { thresholdC: 32, quantity: 'fortyguard_modeled_temperature', thresholdUnits: 'celsius', direction: 'above' }, resultHash: 'hash-test-window', version: 'v1',
      tiles: [
        { polygon: [[0, 0], [5, 0], [5, 10], [0, 10]], valueHours: 2 },
        { polygon: [[5, 0], [10, 0], [10, 10], [5, 10]], valueHours: 0 },
      ],
    }
    const coolWindow: ExceedanceWindow = { ...window, start: '14:00', end: '16:00', resultHash: 'hash-cool', qualifying: false, tiles: window.tiles.map(tile => ({ ...tile, valueHours: 0 })) }
    const result = calculateScheduledHighHeatCrewHours(
      { full: '12:00', partial: '13:00' },
      [
        { id: 'full', durationMinutes: 120, crewId: 'ground', zoneId: 'north', environment: 'outdoor-heavy', fixed: false },
        { id: 'partial', durationMinutes: 120, crewId: 'ground', zoneId: 'north', environment: 'outdoor-heavy', fixed: false },
      ],
      [{ id: 'ground', headcount: 5 }],
      [{ id: 'north', polygon: [[0, 0], [10, 0], [10, 10], [0, 10]] }],
      [window, coolWindow],
      { thresholdC: 32, quantity: 'fortyguard_modeled_temperature', provenance: 'PROJECT_THERMAL_TRIGGER:test', thresholdUnits: 'celsius', direction: 'above' },
    )
    expect(result.valid).toBe(true)
    expect(result.totalCrewHours).toBe(7.5)
  })

  it('uses cryptographic canonical identities for policy and schedules', () => {
    expect(sha256('abc')).toBe('ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad')
    expect(candidateHash({ tasks: [{ id: 'A', start: '06:00' }], schedule: { A: '06:00', B: '07:00' }, crews: [{ id: 'ground' }], policy: { breakRules: [] } })).toBe(
      candidateHash({ crews: [{ id: 'ground' }], schedule: { B: '07:00', A: '06:00' }, tasks: [{ start: '06:00', id: 'A' }], policy: { breakRules: [] } }),
    )
    expect(policyContentHash({ ...EMPLOYER_POLICY, breakRules: [{ ...BREAK_POLICY, durationMinutes: 30 }] })).not.toBe(policyContentHash({ ...EMPLOYER_POLICY, breakRules: [{ ...BREAK_POLICY, durationMinutes: 45 }] }))
  })

  it.each([
    [1, false], [29, false], [30, true], [45, true],
  ])('enforces the full %s-minute inferred break duration', (gap, expected) => {
    const makeTask = (id: string, start: string) => ({ id, name: id, crewId: 'ground' as const, zoneId: 'north' as const, durationMinutes: 90, originalStart: start, proposedStart: start, fixed: false, environment: 'outdoor-heavy' as const, qualification: 'competent-person', dependencies: [], deadline: '16:00', weatherSensitivity: { precipitation: false } })
    const secondStart = 12 * 60 + 30 + gap
    const tasks = [makeTask('A', '11:00'), makeTask('B', `${String(Math.floor(secondStart / 60)).padStart(2, '0')}:${String(secondStart % 60).padStart(2, '0')}`)]
    const schedule = Object.fromEntries(tasks.map(task => [task.id, task.originalStart]))
    expect(verifyBreakPolicy(schedule, tasks, CREWS)).toBe(expected)
    expect(verifySchedule(schedule, tasks, CREWS, schedule).passed).toBe(expected)
  })

  it('rejects a reserved break with the wrong policy window, crew, or overlapping work', () => {
    const tasks = [
      { id: 'A', name: 'A', crewId: 'ground' as const, zoneId: 'north' as const, durationMinutes: 90, originalStart: '11:00', proposedStart: '11:00', fixed: false, environment: 'outdoor-heavy' as const, qualification: 'competent-person', dependencies: [], deadline: '16:00', weatherSensitivity: { precipitation: false } },
      { id: 'B', name: 'B', crewId: 'ground' as const, zoneId: 'north' as const, durationMinutes: 90, originalStart: '13:00', proposedStart: '13:00', fixed: false, environment: 'outdoor-heavy' as const, qualification: 'competent-person', dependencies: [], deadline: '16:00', weatherSensitivity: { precipitation: false } },
    ]
    const schedule = { A: '11:00', B: '13:00' }
    expect(verifySchedule(schedule, tasks, CREWS, schedule, [{ crewId: 'ground', start: '10:00', end: '10:30' }])).toMatchObject({ passed: false })
    expect(verifySchedule({ A: '11:00', B: '12:31' }, tasks, CREWS, { A: '11:00', B: '12:31' }, [{ crewId: 'concrete', start: '12:00', end: '12:30' }])).toMatchObject({ passed: false })
    expect(verifySchedule(schedule, tasks, CREWS, schedule, [{ crewId: 'ground', start: '12:00', end: '12:30' }])).toMatchObject({ passed: false })
    expect(verifySchedule(fixtureRecommendation()).passed).toBe(true)
  })

  it('rejects a reservation whose later portion overlaps work', () => {
    const tasks = [
      { id: 'A', name: 'A', crewId: 'ground' as const, zoneId: 'north' as const, durationMinutes: 90, originalStart: '11:00', proposedStart: '11:00', fixed: false, environment: 'outdoor-heavy' as const, qualification: 'competent-person', dependencies: [], deadline: '16:00', weatherSensitivity: { precipitation: false } },
      { id: 'B', name: 'B', crewId: 'ground' as const, zoneId: 'north' as const, durationMinutes: 30, originalStart: '12:45', proposedStart: '12:45', fixed: false, environment: 'outdoor-heavy' as const, qualification: 'competent-person', dependencies: [], deadline: '16:00', weatherSensitivity: { precipitation: false } },
    ]
    expect(verifySchedule({ A: '11:00', B: '12:45' }, tasks, CREWS, { A: '11:00', B: '12:45' }, [{ crewId: 'ground', start: '12:00', end: '13:00' }]).passed).toBe(false)
  })

  it('rejects a 29m59s idle gap and accepts exactly 30 minutes', () => {
    const makeTask = (id: string, start: string) => ({ id, name: id, crewId: 'ground' as const, zoneId: 'north' as const, durationMinutes: 90, originalStart: start, proposedStart: start, fixed: false, environment: 'outdoor-heavy' as const, qualification: 'competent-person', dependencies: [], deadline: '16:00', weatherSensitivity: { precipitation: false } })
    const tasks = [makeTask('A', '11:00:00'), makeTask('B', '12:59:59')]
    expect(verifyBreakPolicy({ A: '11:00:00', B: '12:59:59' }, tasks, CREWS)).toBe(false)
    expect(verifyBreakPolicy({ A: '11:00:00', B: '13:00:00' }, tasks.map(task => ({ ...task, originalStart: task.id === 'B' ? '13:00:00' : task.originalStart, proposedStart: task.id === 'B' ? '13:00:00' : task.proposedStart })), CREWS)).toBe(true)
  })

  it.each([
    null, 'not-a-task', { id: 'A' },
  ])('fails malformed task input closed before business rules', badTask => {
    const malformed = [badTask] as unknown as typeof TASKS
    expect(verifySchedule({ A: '06:00' }, malformed, CREWS, {})).toMatchObject({ passed: false })
  })

  it('blocks approval after the displayed candidate is mutated', () => {
    const run = runCrewClock({ thermalEvidence: SYNTHETIC_POSITIVE_EVIDENCE, scenarioLabel: 'SYNTHETIC TEST SCENARIO' })
    const identity = { recommendationId: run.recommendationId!, candidateHash: run.candidateHash! }
    run.recommendation!.G2 = run.recommendation!.G2 === '07:00' ? '07:30' : '07:00'
    expect(approveRecommendation(run, identity).approved).toBe(false)
  })
})
