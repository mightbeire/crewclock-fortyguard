import { describe, expect, it, vi } from 'vitest'
import { emptyRuntimeSession, fetchProductionReview, startProductionReview, SYNTHETIC_POSITIVE_EVIDENCE } from './runtime'
import { CREWS, TASKS } from './scenario'

describe('browser production runtime boundary', () => {
  it('starts with baseline display state and no precomputed recommendation or events', () => {
    const session = emptyRuntimeSession()
    expect(session.events).toEqual([])
    expect(session.run.recommendation).toBeNull()
    expect(session.run.beforeCrewHours).toBeNull()
    expect(session.run.stats.candidatesConsidered).toBe(0)
  })

  it('posts the shift to the production API and renders only returned events', async () => {
    const response = { sessionId: 'server-session', status: 'RUNNING', events: [{ event_id: 'one', run_id: 'server-session', timestamp: '2026-08-26T00:00:00Z', stage: 'inspect', status: 'SHIFT_INSPECTION_STARTED', summary: 'Started', source: 'RUNTIME', provider: 'GROQ', metadata: {} }], run: null }
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue({ ok: true, json: async () => response }))
    const session = await startProductionReview('synthetic-positive', TASKS, CREWS)
    expect(fetch).toHaveBeenCalledWith('/api/reviews', expect.objectContaining({ method: 'POST' }))
    expect(session.runId).toBe('server-session')
    expect(session.events).toHaveLength(1)
    expect(session.run.recommendation).toBeNull()
    vi.unstubAllGlobals()
  })

  it('does not invent future events while polling', async () => {
    const current = emptyRuntimeSession()
    current.runId = 'server-session'
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue({ ok: true, json: async () => ({ sessionId: 'server-session', status: 'RUNNING', events: [], run: null }) }))
    const next = await fetchProductionReview(current)
    expect(next.events).toEqual([])
    vi.unstubAllGlobals()
  })

  it('keeps synthetic evidence explicitly classified', () => {
    expect(SYNTHETIC_POSITIVE_EVIDENCE.status).toBe('SYNTHETIC_TEST_SCENARIO')
    expect(SYNTHETIC_POSITIVE_EVIDENCE.exceedanceEvidenceStatus).toBe('complete')
  })
})
