import { describe, expect, it } from 'vitest'
import { DEMO_IDS, MEASURED_EVIDENCE, SCENARIOS, validateAllScenarios, validateScenario } from './scenario'
describe('deterministic demo', () => {
  it('recomputes every hero metric and stays cached', () => {
    expect(validateAllScenarios()).toBe(true)
    expect(MEASURED_EVIDENCE.source).toContain('FortyGuard')
    expect(DEMO_IDS).toHaveLength(3)
    DEMO_IDS.forEach(id => expect(validateScenario(SCENARIOS[id])).toBe(true))
  })
  it('keeps all operational inputs explicitly non-production', () => {
    DEMO_IDS.forEach(id => {
      expect(SCENARIOS[id].assumptions.join(' ')).toContain('deterministic scenario data')
      expect(SCENARIOS[id].publicData).toBeTruthy()
    })
  })
})
