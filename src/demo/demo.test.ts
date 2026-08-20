import { describe, expect, it } from 'vitest'
import { DEMO_SCENARIO, validateScenario } from './scenario'
describe('deterministic demo', () => {
  it('recomputes its hero metric and stays cached', () => {
    expect(validateScenario()).toBe(true)
    expect(DEMO_SCENARIO.measured.source).toContain('FortyGuard')
    expect(DEMO_SCENARIO.assumptions.length).toBeGreaterThan(0)
  })
})
