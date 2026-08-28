import type { CrewClockRun } from './engine'
import { CREWS, EMPLOYER_POLICY, TASKS, THERMAL_EVIDENCE, WORKFACES, type Crew, type Task } from './scenario'
import type { ExceedanceWindow } from './shhch'

export type UiEventName =
  | 'SHIFT_INSPECTION_STARTED' | 'SHIFT_INSPECTION_COMPLETED' | 'NO_THERMAL_INVESTIGATION'
  | 'THERMAL_INVESTIGATION_REQUIRED' | 'THERMAL_EVIDENCE_REQUESTED' | 'THERMAL_EVIDENCE_UNAVAILABLE'
  | 'THERMAL_EVIDENCE_PROCESSING' | 'THERMAL_EVIDENCE_RETRY' | 'THERMAL_EVIDENCE_READY' | 'OPTIMIZATION_STARTED' | 'CANDIDATES_GENERATED'
  | 'VERIFICATION_STARTED' | 'VERIFICATION_FAILED' | 'VERIFICATION_PASSED'
  | 'NO_FEASIBLE_IMPROVEMENT' | 'NO_FEASIBLE_CORRECTION' | 'OPERATOR_ATTENTION_REQUIRED' | 'RUN_COMPLETED'
  | 'CURRENT_PLAN_PRESERVED' | 'RECHECK_AVAILABLE' | 'AWAITING_APPROVAL'
  | 'APPROVAL_RECEIVED' | 'FINAL_VERIFICATION_FAILED' | 'APPROVED' | 'AI_ANALYSIS_UNAVAILABLE' | 'CLIENT_TRANSPORT_FAILURE'

export type RuntimeUiEvent = {
  event_id: string; run_id: string; timestamp: string; stage: string; status: UiEventName; summary: string
  source: string; provider: string; tool?: string; terminal_state?: string; metadata: Record<string, unknown>
}

export type RuntimeSession = {
  run: CrewClockRun; runId: string; events: RuntimeUiEvent[]; approved: boolean; status: string
  provider?: Record<string, unknown>
}

export type ProductionScenario = 'synthetic-positive' | 'canonical-replay' | 'evidence-unavailable' | 'all-indoor' | 'new-site'
export class ProductionReviewStartError extends Error {
  status: number
  code?: string
  reason?: string

  constructor(status: number, code?: string, reason?: string) {
    super(`review_start_failed:${status}:${reason || code || 'unknown'}`)
    this.name = 'ProductionReviewStartError'
    this.status = status
    this.code = code
    this.reason = reason
  }
}


const syntheticBase: ExceedanceWindow = {
  analyticType: 'exceedance', start: '11:00', end: '15:00', units: 'hours', status: 'VALID',
  provenance: 'SYNTHETIC_TEST_SCENARIO_ONLY', aoi: 'synthetic-construction-aoi', date: '2026-08-27',
  timezone: 'America/Phoenix', analyticSource: 'SYNTHETIC_TEST_EVIDENCE_PROVIDER',
  projectThermalTrigger: { thresholdC: 32, quantity: 'fortyguard_modeled_temperature', thresholdUnits: 'celsius', direction: 'above' },
  resultHash: 'synthetic-exceedance-window-v2', version: 'synthetic-v2', tiles: WORKFACES.map(face => ({ polygon: face.polygon, valueHours: 4 })),
}

export const SYNTHETIC_POSITIVE_EVIDENCE = {
  ...THERMAL_EVIDENCE, status: 'SYNTHETIC_TEST_SCENARIO', exceedanceEvidenceStatus: 'complete' as const,
  exceedanceWindows: [
    { ...syntheticBase, start: '06:00', end: '11:00', qualifying: false, resultHash: 'synthetic-cool-am', tiles: WORKFACES.map(face => ({ polygon: face.polygon, valueHours: 0 })) },
    syntheticBase,
    { ...syntheticBase, start: '15:00', end: '16:00', qualifying: false, resultHash: 'synthetic-cool-pm', tiles: WORKFACES.map(face => ({ polygon: face.polygon, valueHours: 0 })) },
  ],
  forecastStatus: 'SYNTHETIC_TEST_SCENARIO', decisionGradeThermalEvidence: true,
  primarySignal: 'Synthetic test evidence only; never canonical Phoenix evidence.',
}

export const SYNTHETIC_POSITIVE_POLICY = {
  ...EMPLOYER_POLICY,
  name: 'Desert Build Co. · synthetic capability policy v2',
  status: 'synthetic employer policy',
  breakRules: [{ ...EMPLOYER_POLICY.breakRules[0], afterContinuousMinutes: 300, version: 'synthetic-v2' }],
}

const baseline = (tasks: Task[]) => Object.fromEntries(tasks.map(task => [task.id, task.originalStart]))

export const emptyRuntimeSession = (tasks: Task[] = TASKS, crews: Crew[] = CREWS): RuntimeSession => ({
  runId: '', events: [], approved: false, status: 'IDLE',
  run: {
    status: 'missing-evidence', decisionKind: 'evidence-unavailable', baselineValid: false,
    original: baseline(tasks), recommendation: null,
    investigation: {
      investigatedTaskIds: tasks.filter(task => !task.fixed && task.environment !== 'shaded-support').map(task => task.id),
      skippedIndoorTaskIds: tasks.filter(task => task.environment === 'shaded-support').map(task => task.id),
      retainedFixedTaskIds: tasks.filter(task => task.fixed).map(task => task.id), workfaceIds: [],
    },
    originalVerification: { passed: false, passedFamilies: 0, totalFamilies: 6, totalChecks: 0, families: [] },
    recommendationVerification: null, beforeCrewHours: null, afterCrewHours: null, shiftedCrewHours: 0,
    stats: { candidatesConsidered: 0, feasibleCandidates: 0, rejectedCandidates: 0 }, deterministicId: 'not-reviewed',
    message: 'Review has not started.', candidateHash: null, recommendationId: null, evidenceHash: '',
    thermalEvidence: THERMAL_EVIDENCE, sourceScheduleHash: '', policyHash: '', verificationHash: null,
    artifactVersion: 'crewclock.runtime.v1', policyVersion: EMPLOYER_POLICY.name, taskStateHash: '',
    tasks, crews, policy: EMPLOYER_POLICY, workfaces: WORKFACES, shiftStart: '06:00', shiftEnd: '16:00',
  },
})

type Snapshot = { sessionId: string; status: string; events?: RuntimeUiEvent[]; run?: CrewClockRun | null; approved?: boolean; provider?: Record<string, unknown> }
const parseSnapshot = (value: Snapshot, fallback: RuntimeSession): RuntimeSession => ({
  runId: value.sessionId, status: value.status, events: value.events ?? [], run: value.run ?? fallback.run,
  approved: Boolean(value.approved), provider: value.provider,
})

export type ProductionShiftContext = {
  id?: string; location: string; timezone: string; date: string; start: string; end: string
  location_anchor: { latitude: number; longitude: number }; site_dimensions_m: { width: number; height: number }
  aoi: Record<string, unknown>; workfaces: Array<Record<string, unknown>>
}

export const startProductionReview = async (scenario: ProductionScenario, tasks: Task[], crews: Crew[], context?: ProductionShiftContext): Promise<RuntimeSession> => {
  const fallback = emptyRuntimeSession(tasks, crews)
  const response = await fetch('/api/reviews', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ scenario, tasks, crews, ...context }) })
  if (!response.ok) {
    let body: { error?: string; reason?: string } = {}
    try { body = await response.json() as { error?: string; reason?: string } } catch { /* response may not be JSON */ }
    throw new ProductionReviewStartError(response.status, body.error, body.reason)
  }
  return parseSnapshot(await response.json(), fallback)
}

export const fetchProductionReview = async (session: RuntimeSession): Promise<RuntimeSession> => {
  const response = await fetch(`/api/reviews/${encodeURIComponent(session.runId)}`, { cache: 'no-store' })
  if (!response.ok) throw new Error(`review_fetch_failed:${response.status}`)
  return parseSnapshot(await response.json(), session)
}

export const approveProductionReview = async (session: RuntimeSession): Promise<RuntimeSession> => {
  const response = await fetch(`/api/reviews/${encodeURIComponent(session.runId)}/approve`, {
    method: 'POST', headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ recommendationId: session.run.recommendationId, candidateHash: session.run.candidateHash }),
  })
  if (!response.ok) throw new Error(`approval_failed:${response.status}`)
  const body = await response.json()
  return parseSnapshot(body.session, session)
}

export const emittedRuntimeEvents = (session: RuntimeSession) => session.events
export const visibleRuntimeEvent = (event: RuntimeUiEvent) => event.summary
