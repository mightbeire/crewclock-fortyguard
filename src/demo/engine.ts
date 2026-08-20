import {
  CREWS,
  EMPLOYER_POLICY,
  MINUTE_END,
  MINUTE_START,
  TASKS,
  THERMAL_EVIDENCE,
  type Crew,
  type CrewId,
  type Task,
} from './scenario'

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
  beforeCrewHours: number
  afterCrewHours: number | null
  shiftedCrewHours: number
  stats: SchedulerStats
  deterministicId: string
  message: string
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
  const windowStart = timeToMinutes(THERMAL_EVIDENCE.highWindow.start)
  const windowEnd = timeToMinutes(THERMAL_EVIDENCE.highWindow.end)
  return tasks
    .filter(task => !task.fixed && task.environment !== 'shaded-support')
    .reduce((total, task) => {
      const crew = crews.find(item => item.id === task.crewId)
      const start = schedule[task.id]
      if (!crew || !start) return Number.POSITIVE_INFINITY
      return total + overlapMinutes(timeToMinutes(start), task.durationMinutes, windowStart, windowEnd) / 60 * crew.headcount
    }, 0)
}

export const verifySchedule = (
  schedule: Schedule,
  tasks: Task[] = TASKS,
  crews: Crew[] = CREWS,
  baseline: Schedule = originalSchedule(tasks),
): Verification => {
  const fixedTasks = tasks.filter(task => task.fixed)
  const dependencyEdges = tasks.flatMap(task => task.dependencies.map(dependency => ({ dependency, task })))
  const sameCrewPairs = crews.flatMap(crew => {
    const crewTasks = tasks.filter(task => task.crewId === crew.id)
    return crewTasks.flatMap((task, index) => crewTasks.slice(index + 1).map(other => ({ task, other })))
  })
  const outdoorTasks = tasks.filter(task => task.environment !== 'shaded-support')
  const windowStart = timeToMinutes(THERMAL_EVIDENCE.highWindow.start)
  const windowEnd = timeToMinutes(THERMAL_EVIDENCE.highWindow.end)

  const fixedPass = fixedTasks.every(task => schedule[task.id] === baseline[task.id])
  const dependenciesPass = dependencyEdges.every(({ dependency, task }) => {
    const predecessor = tasks.find(item => item.id === dependency)
    return predecessor && schedule[dependency] && schedule[task.id]
      ? timeToMinutes(schedule[dependency]) + predecessor.durationMinutes <= timeToMinutes(schedule[task.id])
      : false
  })
  const qualificationsPass = tasks.every(task =>
    crews.find(crew => crew.id === task.crewId)?.qualifications.includes(task.qualification),
  )
  const deadlinesPass = tasks.every(task => {
    const start = schedule[task.id]
    return Boolean(start) && timeToMinutes(start) >= MINUTE_START &&
      timeToMinutes(start) + task.durationMinutes <= timeToMinutes(task.deadline) &&
      timeToMinutes(start) + task.durationMinutes <= MINUTE_END
  })
  const availabilityPass = sameCrewPairs.every(({ task, other }) => {
    const taskStart = schedule[task.id]
    const otherStart = schedule[other.id]
    if (!taskStart || !otherStart) return false
    return overlapMinutes(timeToMinutes(taskStart), task.durationMinutes, timeToMinutes(otherStart), timeToMinutes(otherStart) + other.durationMinutes) === 0
  })
  const policyPass = outdoorTasks.every(task => {
    const start = schedule[task.id]
    return Boolean(start) && overlapMinutes(timeToMinutes(start), task.durationMinutes, windowStart, windowEnd) <= 90
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
          heat: peakWindowCrewHoursFor({ ...baseline, ...full }, crewTasks, crews),
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
  const base = { original, investigation, originalVerification, beforeCrewHours, deterministicId: 'CC-PHX-0716-v1' }

  if (!originalVerification.families.filter(family => family.id !== 'employer-policy').every(family => family.passed)) {
    return { ...base, status: 'infeasible-original', recommendation: null, recommendationVerification: null, afterCrewHours: null, shiftedCrewHours: 0, stats: emptyStats, message: 'The upcoming-shift source plan is infeasible. Resolve operational constraints before optimization.' }
  }
  if (policyState === 'ambiguous') {
    return { ...base, status: 'ambiguous-policy', recommendation: null, recommendationVerification: null, afterCrewHours: null, shiftedCrewHours: 0, stats: emptyStats, message: 'Employer controls are ambiguous. Superintendent clarification is required.' }
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

  const enumerations = crews.map(crew => enumerateCrew(crew.id, tasks, crews, original))
  const bestByCrew = enumerations.map(({ candidates }) => [...candidates].sort((a, b) => a.heat - b.heat || a.movement - b.movement)[0])
  const recommendation = bestByCrew.reduce<Schedule>((schedule, candidate) => ({ ...schedule, ...candidate?.schedule }), {})
  const recommendationVerification = verifySchedule(recommendation, tasks, crews, original)
  const afterCrewHours = recommendationVerification.passed ? peakWindowCrewHoursFor(recommendation, tasks, crews) : beforeCrewHours
  const feasibleCandidates = enumerations.reduce((sum, item) => sum + item.candidates.length, 0)
  const candidatesConsidered = enumerations.reduce((sum, item) => sum + item.considered, 0)
  const stats = { candidatesConsidered, feasibleCandidates, rejectedCandidates: candidatesConsidered - feasibleCandidates }
  const shiftedCrewHours = beforeCrewHours - afterCrewHours

  if (!recommendationVerification.passed || shiftedCrewHours <= 0) {
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
    message: `${shiftedCrewHours} scheduled high-heat crew-hours can be removed from the employer trigger overlap.`,
  }
}

export const CANONICAL_RUN = runCrewClock()

export const approveRecommendation = (run: CrewClockRun) => {
  if (run.status !== 'recommended' || !run.recommendation || !run.recommendationVerification?.passed) {
    return { approved: false, plan: run.original, verification: run.originalVerification, auditAction: 'Approval blocked; no verified recommendation exists' }
  }
  const verification = verifySchedule(run.recommendation)
  return {
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
  const entries = [
    { time: '06:42', action: `Loaded the upcoming shift: ${TASKS.length} tasks across ${CREWS.length} crews`, source: 'DEMO INPUT' },
    { time: '06:42', action: `Selected ${run.investigation.investigatedTaskIds.length} movable outdoor tasks; skipped ${run.investigation.skippedIndoorTaskIds.length} shaded tasks and held ${run.investigation.retainedFixedTaskIds.length} fixed commitments`, source: 'AGENT' },
    { time: '06:43', action: `Loaded approved cached-live Phoenix evidence for ${run.investigation.workfaceIds.length} affected workfaces`, source: 'FORTYGUARD · CACHED LIVE' },
  ]
  if (run.stats.candidatesConsidered > 0) {
    entries.push(
      { time: '06:43', action: `Evaluated ${run.stats.candidatesConsidered.toLocaleString()} deterministic crew schedules`, source: 'SCHEDULER' },
      { time: '06:43', action: `Rejected ${run.stats.rejectedCandidates.toLocaleString()} schedules that failed modeled constraints`, source: 'VERIFIER' },
    )
  }
  entries.push({ time: '06:44', action: run.message, source: run.status === 'recommended' ? 'DERIVED' : 'GUARDRAIL' })
  if (run.status === 'recommended') {
    entries.push({ time: '06:44', action: approved ? 'Superintendent approved plan; final verification passed' : 'Awaiting superintendent approval', source: approved ? 'HUMAN + VERIFIER' : 'APPROVAL' })
  }
  return entries
}

export const POLICY_LABEL = EMPLOYER_POLICY.name
