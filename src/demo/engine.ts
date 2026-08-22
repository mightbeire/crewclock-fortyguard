import {
  CREWS,
  BREAK_POLICY,
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
import { calculateScheduledHighHeatCrewHours, type ExceedanceWindow } from './shhch'
import {
  ARTIFACT_VERSION,
  candidateHash as canonicalCandidateHash,
  evidenceBundleHash,
  policyContentHash,
  projectStateHash,
  recommendationId,
  sourceScheduleHash,
  verificationResultHash,
} from './integrity'

export type Schedule = Record<string, string>
export type ThermalEvidence = {
  source: string
  status: string
  exceedanceEvidenceStatus: 'none' | 'partial' | 'complete'
  exceedanceWindows: ReadonlyArray<ExceedanceWindow>
  forecastStatus: string
  projectThermalTrigger: typeof THERMAL_EVIDENCE.projectThermalTrigger
  [key: string]: unknown
}
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
  recommendationId: string | null
  evidenceHash: string
  thermalEvidence: ThermalEvidence
  sourceScheduleHash: string
  policyHash: string
  verificationHash: string | null
  artifactVersion: string
  policyVersion: string
  taskStateHash: string
  tasks: Task[]
  crews: Crew[]
}

export const timeToMinutes = (time: string) => {
  const [hours, minutes, seconds = 0] = time.split(':').map(Number)
  return hours * 60 + minutes + seconds / 60
}

const validTime = (value: unknown) => typeof value === 'string' && /^(?:[01]\d|2[0-3]):[0-5]\d(?::[0-5]\d)?$/.test(value)

const schemaFailure = (detail: string): Verification => ({
  passed: false,
  passedFamilies: 0,
  totalFamilies: 6,
  totalChecks: 1,
  families: [
    { id: 'fixed', label: 'Schedule schema', passed: false, checks: 1, detail: `INVALID_SCHEDULE_SCHEMA: ${detail}` },
    { id: 'dependencies', label: 'Dependencies', passed: false, checks: 0, detail: 'Not evaluated' },
    { id: 'qualifications', label: 'Qualifications', passed: false, checks: 0, detail: 'Not evaluated' },
    { id: 'deadlines', label: 'Deadlines + bounds', passed: false, checks: 0, detail: 'Not evaluated' },
    { id: 'crew-availability', label: 'Crew availability', passed: false, checks: 0, detail: 'Not evaluated' },
    { id: 'employer-policy', label: 'Employer controls', passed: false, checks: 0, detail: 'Not evaluated' },
  ],
})

export type BreakReservation = { crewId: string; start: string; end: string }

export const verifyBreakPolicy = (
  schedule: Schedule,
  tasks: Task[],
  crews: Crew[],
  breakReservations: BreakReservation[] = [],
) => {
  if (!schedule || typeof schedule !== 'object' || !Array.isArray(tasks) || !Array.isArray(crews) || tasks.some(task => !task || !validTime(schedule[task.id]))) return false
  const triggerStart = timeToMinutes(BREAK_POLICY.triggerStart)
  const triggerEnd = timeToMinutes(BREAK_POLICY.triggerEnd)
  const required = BREAK_POLICY.durationMinutes
  const outdoorIntervals = (crewId: string) => tasks
    .filter(task => task.crewId === crewId && task.environment !== 'shaded-support')
    .map(task => [timeToMinutes(schedule[task.id]), timeToMinutes(schedule[task.id]) + task.durationMinutes] as [number, number])
    .map(([start, end]) => [Math.max(start, triggerStart), Math.min(end, triggerEnd)] as [number, number])
    .filter(([start, end]) => end > start)
    .sort((a, b) => a[0] - b[0])

  const continuousPass = crews.every(crew => {
    let runStart = -1
    let runEnd = -1
    return outdoorIntervals(crew.id).every(([start, end]) => {
      if (runStart < 0 || start - runEnd >= required) {
        runStart = start
        runEnd = end
      } else {
        runEnd = Math.max(runEnd, end)
      }
      return runEnd - runStart <= BREAK_POLICY.afterContinuousMinutes
    })
  })
  const reservationsPass = breakReservations.every(reservation => {
    if (!reservation || typeof reservation.crewId !== 'string' || !validTime(reservation.start) || !validTime(reservation.end)) return false
    const start = timeToMinutes(reservation.start)
    const end = timeToMinutes(reservation.end)
    if (!crews.some(crew => crew.id === reservation.crewId) || end - start < required || start < triggerStart || end > triggerEnd) return false
      return tasks.filter(task => task.crewId === reservation.crewId).every(task => {
        const taskStart = timeToMinutes(schedule[task.id])
      return overlapMinutes(start, end - start, taskStart, taskStart + task.durationMinutes) === 0
      })
  })
  return continuousPass && reservationsPass
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
  thermalEvidence = THERMAL_EVIDENCE as ThermalEvidence,
) => {
  const result = calculateScheduledHighHeatCrewHours(
    schedule,
    tasks,
    crews,
    WORKFACES,
    thermalEvidence.exceedanceWindows,
    thermalEvidence.projectThermalTrigger,
  )
  return result.valid ? result.totalCrewHours ?? Number.NaN : null
}

export const verifySchedule = (
  schedule: Schedule,
  tasks: Task[] = TASKS,
  crews: Crew[] = CREWS,
  baseline: Schedule = originalSchedule(tasks),
  breakReservations: BreakReservation[] = [],
): Verification => {
  if (!Array.isArray(tasks) || tasks.length === 0) return schemaFailure('tasks must be a non-empty array')
  if (!schedule || typeof schedule !== 'object' || Array.isArray(schedule)) return schemaFailure('schedule must be an object')
  const taskIds = tasks.map(task => task && typeof task === 'object' ? task.id : '')
  if (taskIds.some(id => typeof id !== 'string' || id.length === 0) || new Set(taskIds).size !== taskIds.length) return schemaFailure('task IDs must be unique non-empty strings')
  if (Object.keys(schedule).length !== tasks.length || Object.keys(schedule).some(id => !taskIds.includes(id))) return schemaFailure('schedule must contain exactly one entry per task')
  if (!tasks.every(task => task && typeof task === 'object' && Number.isFinite(task.durationMinutes) && task.durationMinutes > 0 && typeof task.crewId === 'string' && typeof task.qualification === 'string' && validTime(task.deadline) && Array.isArray(task.dependencies) && task.dependencies.every(id => typeof id === 'string') && typeof task.fixed === 'boolean' && typeof task.environment === 'string' && typeof task.zoneId === 'string')) return schemaFailure('task rows contain invalid fields')
  if (!crews.every(crew => crew && typeof crew === 'object' && typeof crew.id === 'string' && Array.isArray(crew.qualifications) && crew.qualifications.every(item => typeof item === 'string')) || new Set(crews.map(crew => crew.id)).size !== crews.length) return schemaFailure('crew schema is invalid')
  if (!tasks.every(task => crews.some(crew => crew.id === task.crewId))) return schemaFailure('unknown crew')
  if (!tasks.every(task => task.dependencies.every(id => taskIds.includes(id)))) return schemaFailure('unknown dependency')
  if (!tasks.every(task => validTime(schedule[task.id]))) return schemaFailure('invalid task timestamp')
  if (!Array.isArray(breakReservations)) return schemaFailure('break reservations must be an array')
  const fixedTasks = tasks.filter(task => task.fixed)
  const dependencyEdges = tasks.flatMap(task => task.dependencies.map(dependency => ({ dependency, task })))
  const sameCrewPairs = crews.flatMap(crew => {
    const crewTasks = tasks.filter(task => task.crewId === crew.id)
    return crewTasks.flatMap((task, index) => crewTasks.slice(index + 1).map(other => ({ task, other })))
  })
  const outdoorTasks = tasks.filter(task => task.environment !== 'shaded-support')
  const validTimes = tasks.every(task => validTime(schedule[task.id]) && timeToMinutes(schedule[task.id]) >= MINUTE_START && timeToMinutes(schedule[task.id]) <= MINUTE_END)
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
  const policyPass = validTimes && verifyBreakPolicy(schedule, tasks, crews, breakReservations)

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
  thermalEvidence: ThermalEvidence,
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
          heat: peakWindowCrewHoursFor({ ...baseline, ...full }, crewTasks, crews, thermalEvidence) ?? Number.POSITIVE_INFINITY,
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
  thermalEvidence?: ThermalEvidence
  scenarioLabel?: string
}

const buildCrewClockRun = ({
  tasks = TASKS,
  crews = CREWS,
  evidenceState = 'ready',
  policyState = 'ready',
  thermalEvidence = THERMAL_EVIDENCE as ThermalEvidence,
  scenarioLabel,
}: RunOptions = {}): CrewClockRun => {
  const taskRows = tasks as unknown
  const crewRows = crews as unknown
  const validEnvironments = new Set(['outdoor-heavy', 'outdoor-moderate', 'shaded-support'])
  const validZones = new Set(WORKFACES.map(workface => workface.id))
  const validRuntimeSchema = Array.isArray(taskRows) && taskRows.length > 0 && Array.isArray(crewRows) && crewRows.length > 0 &&
    crewRows.every(crew => crew && typeof crew === 'object' && typeof (crew as Crew).id === 'string' && Array.isArray((crew as Crew).qualifications) && (crew as Crew).qualifications.every(item => typeof item === 'string')) &&
    new Set(crewRows.map(crew => crew && typeof crew === 'object' ? (crew as Crew).id : '')).size === crewRows.length &&
    taskRows.every(task => {
      if (!task || typeof task !== 'object') return false
      const row = task as Task
      return typeof row.id === 'string' && row.id.length > 0 && typeof row.name === 'string' && typeof row.crewId === 'string' &&
        crewRows.some(crew => crew && typeof crew === 'object' && (crew as Crew).id === row.crewId) && typeof row.zoneId === 'string' && validZones.has(row.zoneId) &&
        Number.isFinite(row.durationMinutes) && row.durationMinutes > 0 && validTime(row.originalStart) && validTime(row.proposedStart) &&
        typeof row.fixed === 'boolean' && validEnvironments.has(row.environment) && typeof row.qualification === 'string' &&
        Array.isArray(row.dependencies) && row.dependencies.every(id => typeof id === 'string') && validTime(row.deadline) &&
        row.weatherSensitivity && typeof row.weatherSensitivity === 'object' && typeof row.weatherSensitivity.precipitation === 'boolean'
    }) &&
    new Set(taskRows.map(task => task && typeof task === 'object' ? (task as Task).id : '')).size === taskRows.length &&
    taskRows.every(task => task && typeof task === 'object' && (task as Task).dependencies.every(id => taskRows.some(other => other && typeof other === 'object' && (other as Task).id === id)))
  if (!validRuntimeSchema) {
    const safeTasks = Array.isArray(taskRows) ? taskRows.filter(task => task && typeof task === 'object') as Task[] : []
    const safeCrews = Array.isArray(crewRows) ? crewRows.filter(crew => crew && typeof crew === 'object') as Crew[] : []
    const verification = verifySchedule({}, safeTasks, safeCrews, {})
    const evidenceHash = evidenceBundleHash(thermalEvidence)
    const taskStateHash = projectStateHash(safeTasks, safeCrews)
    return {
      status: 'infeasible-original', original: {}, recommendation: null, investigation: { investigatedTaskIds: [], skippedIndoorTaskIds: [], retainedFixedTaskIds: [], workfaceIds: [] }, originalVerification: verification, recommendationVerification: null, beforeCrewHours: null, afterCrewHours: null, shiftedCrewHours: 0, stats: { candidatesConsidered: 0, feasibleCandidates: 0, rejectedCandidates: 0 }, deterministicId: 'CC-PHX-0716-v1', message: 'INVALID_SCHEDULE_SCHEMA: runtime input was malformed; current plan preserved.', candidateHash: null, recommendationId: null, evidenceHash, thermalEvidence, sourceScheduleHash: '', policyHash: policyContentHash(EMPLOYER_POLICY), verificationHash: null, artifactVersion: ARTIFACT_VERSION, policyVersion: String(EMPLOYER_POLICY.name), taskStateHash, tasks: safeTasks, crews: safeCrews,
    }
  }
  const original = originalSchedule(tasks)
  const investigation = selectThermalInvestigation(tasks)
  const originalVerification = verifySchedule(original, tasks, crews, original)
  const beforeCrewHours = peakWindowCrewHoursFor(original, tasks, crews, thermalEvidence)
  const emptyStats = { candidatesConsidered: 0, feasibleCandidates: 0, rejectedCandidates: 0 }
  const evidenceHash = evidenceBundleHash(thermalEvidence)
  const taskStateHash = projectStateHash(tasks, crews)
  const sourceHash = sourceScheduleHash(original) ?? ''
  const policyHash = policyContentHash(EMPLOYER_POLICY)
  const policyVersion = String(EMPLOYER_POLICY.name)
  const base = { original, investigation, originalVerification, beforeCrewHours, deterministicId: 'CC-PHX-0716-v1', candidateHash: null, recommendationId: null, evidenceHash, thermalEvidence, sourceScheduleHash: sourceHash, policyHash, verificationHash: null, artifactVersion: ARTIFACT_VERSION, policyVersion, taskStateHash, tasks, crews }

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
  if (thermalEvidence.exceedanceEvidenceStatus !== 'complete') {
    return { ...base, status: 'missing-evidence', recommendation: null, recommendationVerification: null, afterCrewHours: null, shiftedCrewHours: 0, stats: emptyStats, message: 'Phoenix schedule-aligned FortyGuard exceedance evidence is not demonstrated. No recommendation issued.' }
  }
  if (scenarioLabel !== 'SYNTHETIC TEST SCENARIO') {
    return { ...base, status: 'missing-evidence', recommendation: null, recommendationVerification: null, afterCrewHours: null, shiftedCrewHours: 0, stats: emptyStats, message: 'Synthetic decision-grade evidence requires the explicitly labeled synthetic test scenario. No recommendation issued.' }
  }

  const enumerations = crews.map(crew => enumerateCrew(crew.id, tasks, crews, original, thermalEvidence))
  const bestByCrew = enumerations.map(({ candidates }) => [...candidates].sort((a, b) => a.heat - b.heat || a.movement - b.movement)[0])
  const recommendation = bestByCrew.reduce<Schedule>((schedule, candidate) => ({ ...schedule, ...candidate?.schedule }), {})
  const recommendationVerification = verifySchedule(recommendation, tasks, crews, original)
  const afterCrewHours = recommendationVerification.passed ? peakWindowCrewHoursFor(recommendation, tasks, crews, thermalEvidence) : beforeCrewHours
  const feasibleCandidates = enumerations.reduce((sum, item) => sum + item.candidates.length, 0)
  const candidatesConsidered = enumerations.reduce((sum, item) => sum + item.considered, 0)
  const stats = { candidatesConsidered, feasibleCandidates, rejectedCandidates: candidatesConsidered - feasibleCandidates }
  const shiftedCrewHours = beforeCrewHours !== null && afterCrewHours !== null ? beforeCrewHours - afterCrewHours : 0

  if (!recommendationVerification.passed || shiftedCrewHours <= 0 || beforeCrewHours === null || afterCrewHours === null) {
    return { ...base, status: 'no-improvement', recommendation: null, recommendationVerification, afterCrewHours: beforeCrewHours, shiftedCrewHours: 0, stats, message: 'No defensible improvement found. The original plan remains the operational plan.' }
  }
  const finalVerificationHash = verificationResultHash({
    status: 'VERIFIED',
    valid: recommendationVerification.passed,
    checks: recommendationVerification,
    candidate_hash: canonicalCandidateHash({ tasks, schedule: recommendation, crews, policy: EMPLOYER_POLICY, sourceSchedule: original }),
    source_schedule_hash: sourceHash,
    evidence_hash: evidenceHash,
    policy_hash: policyHash,
    project_state_hash: taskStateHash,
  })
  const sealedCandidateHash = canonicalCandidateHash({ tasks, schedule: recommendation, crews, policy: EMPLOYER_POLICY, sourceSchedule: original })
  return {
    ...base,
    status: 'recommended',
    recommendation,
    recommendationVerification,
    afterCrewHours,
    shiftedCrewHours,
    stats,
    candidateHash: sealedCandidateHash,
    recommendationId: recommendationId({
      candidateHash: sealedCandidateHash,
      sourceScheduleHash: sourceHash,
      evidenceHash,
      policyHash,
      projectStateHash: taskStateHash,
      verificationHash: finalVerificationHash,
      artifactVersion: ARTIFACT_VERSION,
    }),
    verificationHash: finalVerificationHash,
    message: `${shiftedCrewHours} scheduled high-heat crew-hours can be removed from the employer trigger overlap.`,
  }
}

type SealedRecommendation = {
  candidateHash: string
  recommendationId: string
  verificationHash: string
  sourceScheduleHash: string
  evidenceHash: string
  policyHash: string
  taskStateHash: string
  artifactVersion: string
}

// The UI-facing run object is intentionally inspectable, but approval must
// compare it with a binding captured outside that mutable presentation state.
// A WeakMap keeps the binding private to this module and survives the normal
// session cloning performed by the React UI.
const sealedRecommendations = new WeakMap<CrewClockRun, SealedRecommendation>()

export const runCrewClock = (options: RunOptions = {}) => {
  const run = buildCrewClockRun(options)
  if (run.status === 'recommended' && run.recommendationId && run.candidateHash && run.verificationHash) {
    sealedRecommendations.set(run, {
      candidateHash: run.candidateHash,
      recommendationId: run.recommendationId,
      verificationHash: run.verificationHash,
      sourceScheduleHash: run.sourceScheduleHash,
      evidenceHash: run.evidenceHash,
      policyHash: run.policyHash,
      taskStateHash: run.taskStateHash,
      artifactVersion: run.artifactVersion,
    })
  }
  return run
}

export const CANONICAL_RUN = runCrewClock()

export const approveRecommendation = (run: CrewClockRun, identity?: { recommendationId: string; candidateHash: string }) => {
  const sealed = sealedRecommendations.get(run)
  if (run.status !== 'recommended' || !run.recommendation || !run.recommendationVerification?.passed || !sealed) {
    return { state: 'FINAL_VERIFICATION_FAILED' as const, approved: false, plan: run.original, verification: run.originalVerification, auditAction: 'Approval blocked; no verified recommendation exists' }
  }
  const currentCandidateHash = canonicalCandidateHash({ tasks: run.tasks, schedule: run.recommendation, crews: run.crews, policy: EMPLOYER_POLICY, sourceSchedule: run.original })
  if (!identity || identity.recommendationId !== sealed.recommendationId || identity.candidateHash !== sealed.candidateHash || run.recommendationId !== sealed.recommendationId || run.candidateHash !== sealed.candidateHash || currentCandidateHash !== sealed.candidateHash) {
    return { state: 'FINAL_VERIFICATION_FAILED' as const, approved: false, plan: run.original, verification: run.originalVerification, auditAction: 'Approval blocked; recommendation identity was missing or mismatched' }
  }
  const received = { state: 'APPROVAL_RECEIVED' as const, candidateHash: currentCandidateHash }
  const currentPolicyHash = policyContentHash(EMPLOYER_POLICY)
  const currentEvidenceHash = evidenceBundleHash(run.thermalEvidence)
  const currentTaskStateHash = projectStateHash(run.tasks, run.crews)
  const currentSourceHash = sourceScheduleHash(run.original)
  const currentRecommendationId = recommendationId({ candidateHash: received.candidateHash, sourceScheduleHash: currentSourceHash, evidenceHash: currentEvidenceHash, policyHash: currentPolicyHash, projectStateHash: currentTaskStateHash, verificationHash: sealed.verificationHash, artifactVersion: sealed.artifactVersion })
  if (run.evidenceHash !== sealed.evidenceHash || run.taskStateHash !== sealed.taskStateHash || run.sourceScheduleHash !== sealed.sourceScheduleHash || run.policyHash !== sealed.policyHash || run.verificationHash !== sealed.verificationHash || run.artifactVersion !== sealed.artifactVersion || currentEvidenceHash !== sealed.evidenceHash || currentTaskStateHash !== sealed.taskStateHash || currentSourceHash !== sealed.sourceScheduleHash || currentPolicyHash !== sealed.policyHash || currentRecommendationId !== sealed.recommendationId || sealed.artifactVersion !== ARTIFACT_VERSION) {
    return { ...received, state: 'FINAL_VERIFICATION_FAILED' as const, approved: false, plan: run.original, verification: run.originalVerification, auditAction: 'Approval blocked; recommendation context is stale' }
  }
  const verification = verifySchedule(run.recommendation, run.tasks, run.crews, run.original)
  const finalVerificationHash = verificationResultHash({
    status: 'VERIFIED',
    valid: verification.passed,
    checks: verification,
    candidate_hash: received.candidateHash,
    source_schedule_hash: currentSourceHash,
    evidence_hash: currentEvidenceHash,
    policy_hash: currentPolicyHash,
    project_state_hash: currentTaskStateHash,
  })
  return {
    state: verification.passed && finalVerificationHash === sealed.verificationHash ? 'APPROVED' as const : 'FINAL_VERIFICATION_FAILED' as const,
    approved: verification.passed && finalVerificationHash === sealed.verificationHash,
    plan: verification.passed ? run.recommendation : run.original,
    verification,
    auditAction: verification.passed && finalVerificationHash === sealed.verificationHash ? 'Superintendent approved plan; final verification passed' : 'Approval blocked; final verification failed',
  }
}

export const resetDemoState = (run: CrewClockRun = CANONICAL_RUN) => ({
  stage: -1,
  approved: false,
  planView: 'original' as const,
  schedule: run.original,
  deterministicId: run.deterministicId,
})

// TEST/DEMO FIXTURE UTILITY ONLY. The canonical UI consumes runtime.ts events.
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
