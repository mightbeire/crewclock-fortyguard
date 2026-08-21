import {
  CREWS,
  EMPLOYER_POLICY,
  MINUTE_END,
  MINUTE_START,
  TASKS,
  THERMAL_EVIDENCE,
  WORKFACES,
  type Crew,
  type CrewId,
  type Task,
} from './scenario'
import { calculateScheduledHighHeatCrewHours } from './shhch'

export type Schedule = Record<string, string>
export type EvidenceState = 'ready' | 'missing' | 'stale' | 'tool-failure'
export type PolicyState = 'ready' | 'ambiguous'
export type RecommendationStatus =
  | 'recommended'
  | 'no-improvement'
  | 'missing-evidence'
  | 'stale-evidence'
  | 'tool-failure'
  | 'ambiguous-policy'
  | 'infeasible-original'

export type ConstraintFamily = {
  id: 'fixed' | 'dependencies' | 'qualifications' | 'deadlines' | 'crew-availability' | 'employer-policy'
  label: string
  passed: boolean
  checks: number
  detail: string
}

export type Verification = {
  passed: boolean
  passedFamilies: number
  totalFamilies: number
  totalChecks: number
  families: ConstraintFamily[]
}

export type Investigation = {
  investigatedTaskIds: string[]
  skippedIndoorTaskIds: string[]
  retainedFixedTaskIds: string[]
  workfaceIds: string[]
}

export type SchedulerStats = {
  candidatesConsidered: number
  feasibleCandidates: number
  rejectedCandidates: number
}

export type CrewClockRun = {
  status: RecommendationStatus
  original: Schedule
  recommendation: Schedule | null
  investigation: Investigation
  originalVerification: Verification
  recommendationVerification: Verification | null
  beforeCrewHours: number | null
  afterCrewHours: number | null
  shiftedCrewHours: number
  stats: SchedulerStats
  deterministicId: string
  message: string
  candidateHash: string | null
  evidenceHash: string
  policyVersion: string
  taskStateHash: string
  tasks: Task[]
  crews: Crew[]
}

export const timeToMinutes = (time: string) => {
  const [hours, minutes] = time.split(':').map(Number)
  return hours * 60 + minutes
}

export const minutesToTime = (minutes: number) =>
  `${String(Math.floor(minutes / 60)).padStart(2, '0')}:${String(minutes % 60).padStart(2, '0')}`

const overlapMinutes = (aStart: number, aDuration: number, bStart: number, bEnd: number) =>
  Math.max(0, Math.min(aStart + aDuration, bEnd) - Math.max(aStart, bStart))

export const originalSchedule = (tasks: Task[] = TASKS): Schedule =>
  Object.fromEntries(tasks.map(task => [task.id, task.originalStart]))

export const fixtureRecommendation = (tasks: Task[] = TASKS): Schedule =>
  Object.fromEntries(tasks.map(task => [task.id, task.proposedStart]))

export const selectThermalInvestigation = (tasks: Task[] = TASKS): Investigation => {
  const investigatedTaskIds = tasks
    .filter(task => !task.fixed && task.environment !== 'shaded-support')
    .map(task => task.id)
  return {
    investigatedTaskIds,
    skippedIndoorTaskIds: tasks.filter(task => !task.fixed && task.environment === 'shaded-support').map(task => task.id),
    retainedFixedTaskIds: tasks.filter(task => task.fixed).map(task => task.id),
    workfaceIds: [...new Set(tasks.filter(task => investigatedTaskIds.includes(task.id)).map(task => task.zoneId))],
  }
}

export const peakWindowCrewHoursFor = (
  schedule: Schedule,
  tasks: Task[] = TASKS,
  crews: Crew[] = CREWS,
) => {
  const result = calculateScheduledHighHeatCrewHours(
    schedule,
    tasks,
    crews,
    WORKFACES,
    THERMAL_EVIDENCE.exceedanceWindows,
    THERMAL_EVIDENCE.projectThermalTrigger,
  )
  return result.valid ? result.totalCrewHours ?? Number.NaN : null
}

export const verifySchedule = (
  schedule: Schedule,
  tasks: Task[] = TASKS,
  crews: Crew[] = CREWS,
  baseline: Schedule = originalSchedule(tasks),
): Verification => {
  if (!Array.isArray(tasks) || tasks.length === 0 || !schedule || typeof schedule !== 'object' || Object.keys(schedule).length !== tasks.length || new Set(tasks.map(task => task.id)).size !== tasks.length || Object.keys(schedule).some(id => !tasks.some(task => task.id === id))) {
    return { passed: false, passedFamilies: 0, totalFamilies: 6, totalChecks: 1, families: [{ id: 'fixed', label: 'Schedule schema', passed: false, checks: 1, detail: 'Empty, malformed, incomplete, or extra task schedule' }, { id: 'dependencies', label: 'Dependencies', passed: false, checks: 0, detail: 'Not evaluated' }, { id: 'qualifications', label: 'Qualifications', passed: false, checks: 0, detail: 'Not evaluated' }, { id: 'deadlines', label: 'Deadlines + bounds', passed: false, checks: 0, detail: 'Not evaluated' }, { id: 'crew-availability', label: 'Crew availability', passed: false, checks: 0, detail: 'Not evaluated' }, { id: 'employer-policy', label: 'Employer controls', passed: false, checks: 0, detail: 'Not evaluated' }] }
  }
  const fixedTasks = tasks.filter(task => task.fixed)
  const dependencyEdges = tasks.flatMap(task => task.dependencies.map(dependency => ({ dependency, task })))
  const sameCrewPairs = crews.flatMap(crew => {
    const crewTasks = tasks.filter(task => task.crewId === crew.id)
    return crewTasks.flatMap((task, index) => crewTasks.slice(index + 1).map(other => ({ task, other })))
  })
  const outdoorTasks = tasks.filter(task => task.environment !== 'shaded-support')
  const windowStart = timeToMinutes(THERMAL_EVIDENCE.highWindow.start)
  const windowEnd = timeToMinutes(THERMAL_EVIDENCE.highWindow.end)

  const validTimes = tasks.every(task => typeof schedule[task.id] === 'string' && /^\d{2}:\d{2}$/.test(schedule[task.id]) && timeToMinutes(schedule[task.id]) >= MINUTE_START && timeToMinutes(schedule[task.id]) <= MINUTE_END)
  const fixedPass = validTimes && fixedTasks.every(task => schedule[task.id] === baseline[task.id])
  const dependenciesPass = dependencyEdges.every(({ dependency, task }) => {
    const predecessor = tasks.find(item => item.id === dependency)
    return predecessor && schedule[dependency] && schedule[task.id]
      ? timeToMinutes(schedule[dependency]) + predecessor.durationMinutes <= timeToMinutes(schedule[task.id])
      : false
  })
  const qualificationsPass = validTimes && tasks.every(task =>
    crews.find(crew => crew.id === task.crewId)?.qualifications.includes(task.qualification),
  )
  const deadlinesPass = validTimes && tasks.every(task => {
    const start = schedule[task.id]
    return Boolean(start) && timeToMinutes(start) >= MINUTE_START &&
      timeToMinutes(start) + task.durationMinutes <= timeToMinutes(task.deadline) &&
      timeToMinutes(start) + task.durationMinutes <= MINUTE_END
  })
  const availabilityPass = validTimes && sameCrewPairs.every(({ task, other }) => {
    const taskStart = schedule[task.id]
    const otherStart = schedule[other.id]
    if (!taskStart || !otherStart) return false
    return overlapMinutes(timeToMinutes(taskStart), task.durationMinutes, timeToMinutes(otherStart), timeToMinutes(otherStart) + other.durationMinutes) === 0
  })
  const policyPass = validTimes && crews.every(crew => {
    const intervals = tasks.filter(task => task.crewId === crew.id && task.environment !== 'shaded-support').map(task => [timeToMinutes(schedule[task.id]), timeToMinutes(schedule[task.id]) + task.durationMinutes] as [number, number]).map(([start, end]) => [Math.max(start, windowStart), Math.min(end, windowEnd)] as [number, number]).filter(([start, end]) => end > start).sort((a, b) => a[0] - b[0])
    let runEnd = -1; let runStart = -1
    return intervals.every(([start, end]) => { if (start > runEnd) { runStart = start; runEnd = end } else { runEnd = Math.max(runEnd, end) }; return runEnd - runStart <= 90 })
  })

  const families: ConstraintFamily[] = [
    { id: 'fixed', label: 'Fixed commitments', passed: fixedPass, checks: fixedTasks.length, detail: `${fixedTasks.length} anchors unchanged` },
    { id: 'dependencies', label: 'Dependencies', passed: Boolean(dependenciesPass), checks: dependencyEdges.length, detail: `${dependencyEdges.length} precedence links preserved` },
    { id: 'qualifications', label: 'Qualifications', passed: qualificationsPass, checks: tasks.length, detail: `${tasks.length} assignments qualified` },
    { id: 'deadlines', label: 'Deadlines + bounds', passed: deadlinesPass, checks: tasks.length, detail: `${tasks.length} finish times in bounds` },
    { id: 'crew-availability', label: 'Crew availability', passed: availabilityPass, checks: sameCrewPairs.length, detail: `${sameCrewPairs.length} same-crew pairs conflict-free` },
    { id: 'employer-policy', label: 'Employer controls', passed: policyPass, checks: outdoorTasks.length, detail: `${outdoorTasks.length} outdoor tasks checked` },
  ]
  return {
    passed: families.every(family => family.passed),
    passedFamilies: families.filter(family => family.passed).length,
    totalFamilies: families.length,
    totalChecks: families.reduce((sum, family) => sum + family.checks, 0),
    families,
  }
}

type CrewCandidate = { schedule: Schedule; heat: number; movement: number }

const movementMinutes = (schedule: Schedule, baseline: Schedule, tasks: Task[]) =>
  tasks.reduce((sum, task) => sum + Math.abs(timeToMinutes(schedule[task.id]) - timeToMinutes(baseline[task.id])), 0)

const enumerateCrew = (
  crewId: CrewId,
  tasks: Task[],
  crews: Crew[],
  baseline: Schedule,
): { candidates: CrewCandidate[]; considered: number } => {
  const crewTasks = tasks.filter(task => task.crewId === crewId)
  const fixed = crewTasks.filter(task => task.fixed)
  const movable = crewTasks.filter(task => !task.fixed)
  const partial: Schedule = Object.fromEntries(fixed.map(task => [task.id, baseline[task.id]]))
  const candidates: CrewCandidate[] = []
  let considered = 0

  const recurse = (index: number) => {
    if (index === movable.length) {
      considered += 1
      const full = { ...partial }
      const verification = verifySchedule(full, crewTasks, crews, baseline)
      const crewRelevant = verification.families.filter(family => family.id !== 'fixed')
      if (crewRelevant.every(family => family.passed)) {
        candidates.push({
          schedule: full,
          heat: peakWindowCrewHoursFor({ ...baseline, ...full }, crewTasks, crews) ?? Number.POSITIVE_INFINITY,
          movement: movementMinutes(full, baseline, movable),
        })
      }
      return
    }

    const task = movable[index]
    const latest = Math.min(timeToMinutes(task.deadline) - task.durationMinutes, MINUTE_END - task.durationMinutes)
    for (let start = MINUTE_START; start <= latest; start += 30) {
      const conflicts = crewTasks.some(other => {
        if (other.id === task.id || !partial[other.id]) return false
        const otherStart = timeToMinutes(partial[other.id])
        return overlapMinutes(start, task.durationMinutes, otherStart, otherStart + other.durationMinutes) > 0
      })
      if (conflicts) continue
      const assignedDependenciesPass = task.dependencies.every(id => {
        const dependency = tasks.find(item => item.id === id)
        return !partial[id] || (dependency && timeToMinutes(partial[id]) + dependency.durationMinutes <= start)
      })
      if (!assignedDependenciesPass) continue
      partial[task.id] = minutesToTime(start)
      recurse(index + 1)
      delete partial[task.id]
    }
  }

  recurse(0)
  return { candidates, considered }
}

export type RunOptions = {
  tasks?: Task[]
  crews?: Crew[]
  evidenceState?: EvidenceState
  policyState?: PolicyState
}

export const runCrewClock = ({
  tasks = TASKS,
  crews = CREWS,
  evidenceState = 'ready',
  policyState = 'ready',
}: RunOptions = {}): CrewClockRun => {
  const original = originalSchedule(tasks)
  const investigation = selectThermalInvestigation(tasks)
  const originalVerification = verifySchedule(original, tasks, crews, original)
  const beforeCrewHours = peakWindowCrewHoursFor(original, tasks, crews)
  const emptyStats = { candidatesConsidered: 0, feasibleCandidates: 0, rejectedCandidates: 0 }
  const stableHash = (value: unknown) => {
    const text = JSON.stringify(value)
    let hash = 2166136261
    for (let index = 0; index < text.length; index += 1) hash = Math.imul(hash ^ text.charCodeAt(index), 16777619)
    return (hash >>> 0).toString(16)
  }
  const evidenceHash = stableHash(THERMAL_EVIDENCE)
  const taskStateHash = stableHash({ tasks, crews })
  const policyVersion = String(EMPLOYER_POLICY.name)
  const base = { original, investigation, originalVerification, beforeCrewHours, deterministicId: 'CC-PHX-0716-v1', candidateHash: null, evidenceHash, policyVersion, taskStateHash, tasks, crews }

  if (!originalVerification.families.filter(family => family.id !== 'employer-policy').every(family => family.passed)) {
    return { ...base, status: 'infeasible-original', recommendation: null, recommendationVerification: null, afterCrewHours: null, shiftedCrewHours: 0, stats: emptyStats, message: 'The upcoming-shift source plan is infeasible. Resolve operational constraints before optimization.' }
  }
  if (policyState === 'ambiguous') {
    return { ...base, status: 'ambiguous-policy', recommendation: null, recommendationVerification: null, afterCrewHours: null, shiftedCrewHours: 0, stats: emptyStats, message: 'Employer controls are ambiguous. Superintendent clarification is required.' }
  }
  if (investigation.investigatedTaskIds.length === 0) {
    return { ...base, status: 'no-improvement', recommendation: null, recommendationVerification: null, afterCrewHours: beforeCrewHours, shiftedCrewHours: 0, stats: emptyStats, message: 'No movable outdoor work requires a schedule change. The current plan remains the operational plan.' }
  }
  if (evidenceState !== 'ready') {
    const status: RecommendationStatus = evidenceState === 'missing' ? 'missing-evidence' : evidenceState === 'stale' ? 'stale-evidence' : 'tool-failure'
    const messages = {
      'missing-evidence': 'Thermal evidence is missing. No defensible improvement found.',
      'stale-evidence': 'Cached thermal evidence is outside the approved freshness window. No recommendation issued.',
      'tool-failure': 'The evidence tool failed. The original plan remains unchanged.',
    }
    return { ...base, status, recommendation: null, recommendationVerification: null, afterCrewHours: null, shiftedCrewHours: 0, stats: emptyStats, message: messages[status] }
  }
  if (THERMAL_EVIDENCE.exceedanceEvidenceStatus !== 'complete') {
    return { ...base, status: 'missing-evidence', recommendation: null, recommendationVerification: null, afterCrewHours: null, shiftedCrewHours: 0, stats: emptyStats, message: 'Phoenix schedule-aligned FortyGuard exceedance evidence is not demonstrated. No recommendation issued.' }
  }

  const enumerations = crews.map(crew => enumerateCrew(crew.id, tasks, crews, original))
  const bestByCrew = enumerations.map(({ candidates }) => [...candidates].sort((a, b) => a.heat - b.heat || a.movement - b.movement)[0])
  const recommendation = bestByCrew.reduce<Schedule>((schedule, candidate) => ({ ...schedule, ...candidate?.schedule }), {})
  const recommendationVerification = verifySchedule(recommendation, tasks, crews, original)
  const afterCrewHours = recommendationVerification.passed ? peakWindowCrewHoursFor(recommendation, tasks, crews) : beforeCrewHours
  const feasibleCandidates = enumerations.reduce((sum, item) => sum + item.candidates.length, 0)
  const candidatesConsidered = enumerations.reduce((sum, item) => sum + item.considered, 0)
  const stats = { candidatesConsidered, feasibleCandidates, rejectedCandidates: candidatesConsidered - feasibleCandidates }
  const shiftedCrewHours = beforeCrewHours !== null && afterCrewHours !== null ? beforeCrewHours - afterCrewHours : 0

  if (!recommendationVerification.passed || shiftedCrewHours <= 0 || beforeCrewHours === null || afterCrewHours === null) {
    return { ...base, status: 'no-improvement', recommendation: null, recommendationVerification, afterCrewHours: beforeCrewHours, shiftedCrewHours: 0, stats, message: 'No defensible improvement found. The original plan remains the operational plan.' }
  }
  return {
    ...base,
    status: 'recommended',
    recommendation,
    recommendationVerification,
    afterCrewHours,
    shiftedCrewHours,
    stats,
    candidateHash: stableHash(recommendation),
    message: `${shiftedCrewHours} scheduled high-heat crew-hours can be removed from the employer trigger overlap.`,
  }
}

export const CANONICAL_RUN = runCrewClock()

export const approveRecommendation = (run: CrewClockRun) => {
  const stableHash = (value: unknown) => {
    const text = JSON.stringify(value); let hash = 2166136261
    for (let index = 0; index < text.length; index += 1) hash = Math.imul(hash ^ text.charCodeAt(index), 16777619)
    return (hash >>> 0).toString(16)
  }
  if (run.status !== 'recommended' || !run.recommendation || !run.recommendationVerification?.passed) {
    return { state: 'FINAL_VERIFICATION_FAILED' as const, approved: false, plan: run.original, verification: run.originalVerification, auditAction: 'Approval blocked; no verified recommendation exists' }
  }
  const received = { state: 'APPROVAL_RECEIVED' as const, candidateHash: stableHash(run.recommendation) }
  if (received.candidateHash !== run.candidateHash || run.evidenceHash !== stableHash(THERMAL_EVIDENCE) || run.taskStateHash !== stableHash({ tasks: run.tasks, crews: run.crews }) || run.policyVersion !== String(EMPLOYER_POLICY.name)) {
    return { ...received, state: 'FINAL_VERIFICATION_FAILED' as const, approved: false, plan: run.original, verification: run.originalVerification, auditAction: 'Approval blocked; recommendation context is stale' }
  }
  const verification = verifySchedule(run.recommendation, run.tasks, run.crews, run.original)
  return {
    state: verification.passed ? 'APPROVED' as const : 'FINAL_VERIFICATION_FAILED' as const,
    approved: verification.passed,
    plan: verification.passed ? run.recommendation : run.original,
    verification,
    auditAction: verification.passed ? 'Superintendent approved plan; final verification passed' : 'Approval blocked; final verification failed',
  }
}

export const resetDemoState = (run: CrewClockRun = CANONICAL_RUN) => ({
  stage: -1,
  approved: false,
  planView: 'original' as const,
  schedule: run.original,
  deterministicId: run.deterministicId,
})

export const agentAudit = (run: CrewClockRun, approved: boolean) => {
  const evidenceSource = run.status === 'tool-failure' ? 'PROVIDER_ERROR' : run.status === 'recommended' ? 'CACHED_LIVE_FORTYGUARD' : 'EVIDENCE_UNAVAILABLE'
  const entries = [
    { time: '06:42', action: `Loaded the upcoming shift: ${TASKS.length} tasks across ${CREWS.length} crews`, source: 'SYNTHETIC' },
    { time: '06:42', action: `Selected ${run.investigation.investigatedTaskIds.length} movable outdoor tasks; skipped ${run.investigation.skippedIndoorTaskIds.length} shaded tasks and held ${run.investigation.retainedFixedTaskIds.length} fixed commitments`, source: 'DERIVED' },
    { time: '06:43', action: evidenceSource === 'CACHED_LIVE_FORTYGUARD' ? `Loaded compatible cached-live evidence for ${run.investigation.workfaceIds.length} affected workfaces` : 'Thermal evidence is unavailable; no recommendation may be issued', source: evidenceSource },
  ]
  if (run.stats.candidatesConsidered > 0) {
    entries.push(
      { time: '06:43', action: `Evaluated ${run.stats.candidatesConsidered.toLocaleString()} deterministic crew schedules`, source: 'DERIVED' },
      { time: '06:43', action: `Rejected ${run.stats.rejectedCandidates.toLocaleString()} schedules that failed modeled constraints`, source: 'DERIVED' },
    )
  }
  entries.push({ time: '06:44', action: run.message, source: run.status === 'recommended' ? 'DERIVED' : 'EVIDENCE_UNAVAILABLE' })
  if (run.status === 'recommended') {
    entries.push({ time: '06:44', action: approved ? 'Superintendent approval received; final verification passed' : 'Awaiting superintendent approval', source: approved ? 'HUMAN + VERIFIER' : 'APPROVAL' })
  }
  return entries
}

export const RECHECK_THERMAL_EVIDENCE = 'RECHECK_THERMAL_EVIDENCE' as const
export const recheckThermalEvidence = (run: CrewClockRun): CrewClockRun => ({ ...run, recommendation: null, candidateHash: null, status: run.status === 'tool-failure' ? 'tool-failure' : 'missing-evidence', message: 'Thermal evidence remains unavailable. Current schedule preserved; invoke recheck when the provider is available.' })

export const POLICY_LABEL = EMPLOYER_POLICY.name
