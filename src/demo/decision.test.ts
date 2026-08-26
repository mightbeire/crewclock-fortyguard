import { describe, expect, it } from 'vitest'
import { CREWS, WORKFACES, type Task } from './scenario'
import { calculateScheduledHighHeatCrewHours, type ExceedanceWindow } from './shhch'
import { runCrewClock, type ThermalEvidence } from './engine'
import { SYNTHETIC_POSITIVE_EVIDENCE, SYNTHETIC_POSITIVE_POLICY } from './runtime'
import { terminalNoChangeCopy } from './terminalCopy'

const tile = WORKFACES[0].polygon

const window = (start: string, end: string, qualifying: boolean, valueHours: number): ExceedanceWindow => ({
  analyticType: 'exceedance',
  start,
  end,
  units: 'hours',
  status: 'VALID',
  provenance: `SYNTHETIC_DECISION_MATRIX:${start}-${end}`,
  aoi: 'synthetic-decision-matrix-aoi',
  date: '2026-08-21',
  timezone: 'America/Phoenix',
  analyticSource: 'SYNTHETIC_DECISION_MATRIX',
  projectThermalTrigger: { thresholdC: 32, quantity: 'fortyguard_modeled_temperature', thresholdUnits: 'celsius', direction: 'above' },
  resultHash: `decision-matrix-${start}-${end}-${qualifying}`,
  version: 'decision-matrix-v1',
  qualifying,
  tiles: [{ polygon: tile, valueHours }],
})

const evidence = (windows: ExceedanceWindow[]): ThermalEvidence => ({
  source: 'SYNTHETIC_DECISION_MATRIX',
  status: 'SYNTHETIC_TEST_SCENARIO',
  exceedanceEvidenceStatus: 'complete',
  exceedanceWindows: windows,
  forecastStatus: 'SYNTHETIC_TEST_SCENARIO',
  projectThermalTrigger: { thresholdC: 32, quantity: 'fortyguard_modeled_temperature', provenance: 'SYNTHETIC_DECISION_MATRIX', thresholdUnits: 'celsius', direction: 'above' },
})

const splitEvidence = (hotStart = '11:00', hotEnd = '15:00', qualifying = true) => evidence([
  window('06:00', hotStart, false, 0),
  window(hotStart, hotEnd, qualifying, 4),
  window(hotEnd, '16:00', false, 0),
])

const fullHotEvidence = () => evidence([window('06:00', '16:00', true, 10)])

const task = (id: string, originalStart: string, durationMinutes: number, deadline: string, fixed = false): Task => ({
  id,
  name: id,
  crewId: 'ground',
  zoneId: 'north',
  durationMinutes,
  originalStart,
  proposedStart: originalStart,
  fixed,
  environment: 'outdoor-heavy',
  qualification: 'competent-person',
  dependencies: [],
  deadline,
  weatherSensitivity: { precipitation: false },
})

const run = (tasks: Task[], thermalEvidence: ThermalEvidence) => runCrewClock({
  tasks,
  crews: [CREWS[0]],
  workfaces: [WORKFACES[0]],
  thermalEvidence,
  scenarioLabel: 'SYNTHETIC TEST SCENARIO',
})

describe('CrewClock canonical decision hierarchy', () => {
  it('selects a stronger feasible thermal improvement for a valid baseline', () => {
    const result = run([task('A', '13:00', 60, '15:00')], splitEvidence())
    expect(result.baselineValid).toBe(true)
    expect(result.decisionKind).toBe('thermal-improvement')
    expect(result.status).toBe('recommended')
    expect(result.shiftedCrewHours).toBeGreaterThan(0)
    expect(result.recommendationVerification?.passed).toBe(true)
  })

  it('keeps a valid baseline when the only feasible candidates have equal SHHCH', () => {
    const result = run([task('A', '06:00', 60, '16:00')], splitEvidence())
    expect(result.baselineValid).toBe(true)
    expect(result.status).toBe('no-improvement')
    expect(result.decisionKind).toBe('no-improvement')
    expect(result.recommendation).toBeNull()
    expect(result.message).not.toContain('invalid')
  })

  it('accepts an equal-SHHCH correction when the baseline violates employer controls', () => {
    const result = run([task('A', '11:00', 60, '15:00'), task('B', '12:00', 60, '15:00')], fullHotEvidence())
    expect(result.baselineValid).toBe(false)
    expect(result.originalVerification.passedFamilies).toBe(5)
    expect(result.status).toBe('recommended')
    expect(result.decisionKind).toBe('operational-correction')
    expect(result.recommendationVerification?.passedFamilies).toBe(6)
    expect(result.beforeCrewHours).toBe(result.afterCrewHours)
    expect(result.shiftedCrewHours).toBe(0)
    expect(result.message).toContain('least-disruptive feasible correction')
  })

  it('accepts a lower-SHHCH correction when an invalid baseline can be repaired', () => {
    const result = run([task('A', '11:00', 90, '15:00'), task('B', '12:30', 60, '14:00')], splitEvidence('11:00', '13:30'))
    expect(result.baselineValid).toBe(false)
    expect(result.status).toBe('recommended')
    expect(result.decisionKind).toBe('operational-correction')
    expect(result.recommendationVerification?.passed).toBe(true)
    expect(result.afterCrewHours).toBeLessThan(result.beforeCrewHours ?? Infinity)
    expect(result.shiftedCrewHours).toBeGreaterThan(0)
  })

  it('surfaces operator attention when an invalid baseline has no feasible correction', () => {
    const result = run([task('A', '11:00', 60, '12:00', true), task('B', '12:00', 60, '13:00', true)], fullHotEvidence())
    expect(result.baselineValid).toBe(false)
    expect(result.status).toBe('no-feasible-correction')
    expect(result.decisionKind).toBe('no-feasible-correction')
    expect(result.recommendation).toBeNull()
    expect(result.message).toContain('not declared valid')
  })

  it('does not discard fixed-work-only SHHCH or treat it as movable improvement', () => {
    const result = calculateScheduledHighHeatCrewHours(
      { A: '12:00' },
      [{ id: 'A', durationMinutes: 60, crewId: 'ground', zoneId: 'north', environment: 'outdoor-heavy', fixed: true }],
      [{ id: 'ground', headcount: 6 }],
      [WORKFACES[0]],
      [window('06:00', '16:00', true, 10)],
      { thresholdC: 32, quantity: 'fortyguard_modeled_temperature', provenance: 'SYNTHETIC_DECISION_MATRIX', thresholdUnits: 'celsius', direction: 'above' },
    )
    expect(result.valid).toBe(true)
    expect(result.totalCrewHours).toBe(6)
    expect(result.movableCrewHours).toBe(0)
    expect(result.fixedCrewHours).toBe(6)
  })

  it('fails closed when evidence is unavailable', () => {
    const result = runCrewClock({ evidenceState: 'missing' })
    expect(result.status).toBe('missing-evidence')
    expect(result.decisionKind).toBe('evidence-unavailable')
    expect(result.recommendation).toBeNull()
  })

  it('keeps valid no-improvement semantics when no qualifying overlap exists', () => {
    const result = run([task('A', '13:00', 60, '15:00')], splitEvidence('11:00', '15:00', false))
    expect(result.baselineValid).toBe(true)
    expect(result.beforeCrewHours).toBe(0)
    expect(result.status).toBe('no-improvement')
    expect(result.recommendation).toBeNull()
    const copy = terminalNoChangeCopy(result)
    expect(copy.heading).toBe('No thermal schedule change needed.')
    expect(`${copy.heading} ${copy.detail}`).not.toMatch(/fails? a hard constraint|hard operational constraint requires attention/i)
  })

  it('distinguishes positive-SHHCH no-improvement and invalid-baseline terminal copy', () => {
    const positive = run([task('A', '11:00', 60, '16:00')], fullHotEvidence())
    expect(positive.baselineValid).toBe(true)
    expect(positive.beforeCrewHours).toBeGreaterThan(0)
    expect(positive.status).toBe('no-improvement')
    expect(terminalNoChangeCopy(positive).heading).toBe('No feasible thermal improvement found.')

    const invalid = run([task('A', '11:00', 60, '12:00', true), task('B', '12:00', 60, '13:00', true)], fullHotEvidence())
    expect(invalid.baselineValid).toBe(false)
    expect(invalid.status).toBe('no-feasible-correction')
    expect(terminalNoChangeCopy(invalid).heading).toBe('A hard operational constraint requires attention.')
  })

  it('orders equivalent candidates deterministically', () => {
    const tasks = [task('A', '11:00', 60, '15:00'), task('B', '12:00', 60, '15:00')]
    expect(run(tasks, fullHotEvidence())).toEqual(run(tasks, fullHotEvidence()))
  })

  it('locks the submitted synthetic capability result to engine output', () => {
    const result = runCrewClock({ thermalEvidence: SYNTHETIC_POSITIVE_EVIDENCE, policy: SYNTHETIC_POSITIVE_POLICY, scenarioLabel: 'SYNTHETIC TEST SCENARIO' })
    const moved = result.tasks.filter(item => result.recommendation?.[item.id] !== result.original[item.id])
    expect(result.beforeCrewHours).toBe(39)
    expect(result.afterCrewHours).toBe(20)
    expect(moved.map(item => item.id)).toEqual(['G1', 'G2', 'G3', 'G4', 'E1', 'E2', 'E3'])
    expect(result.originalVerification.passedFamilies).toBe(6)
    expect(result.recommendationVerification?.passedFamilies).toBe(6)
  })
})
