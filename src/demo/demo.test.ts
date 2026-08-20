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

describe('CrewClock deterministic demo', () => {
  it('recomputes the hero metric from tasks and crew sizes', () => {
    expect(peakWindowCrewHours('original')).toBe(22)
    expect(peakWindowCrewHours('proposed')).toBe(6)
    expect(HERO_METRIC.moved).toBe(16)
    expect(validateScenario()).toBe(true)
  })

  it('preserves hard schedule constraints in both plans', () => {
    expect(validatePlan('original')).toBe(true)
    expect(validatePlan('proposed')).toBe(true)
    expect(TASKS.filter(task => task.fixed).every(task => task.originalStart === task.proposedStart)).toBe(true)
    expect(CREWS).toHaveLength(3)
    expect(validatePolicy('original')).toBe(false)
    expect(validatePolicy('proposed')).toBe(true)
  })

  it('keeps evidence and policy provenance explicit', () => {
    expect(THERMAL_EVIDENCE.status).toBe('cached-live')
    expect(THERMAL_EVIDENCE.cachePaths).toHaveLength(3)
    expect(EMPLOYER_POLICY.status).toBe('synthetic employer policy')
    expect(EMPLOYER_POLICY.authorityBoundary).toContain('Onsite')
  })
})
