export type CrewId = 'ground' | 'concrete' | 'electrical'
export type ZoneId = 'north' | 'south' | 'laydown'
export type TaskEnvironment = 'outdoor-heavy' | 'outdoor-moderate' | 'shaded-support'

export type Crew = {
  id: CrewId
  name: string
  trade: string
  headcount: number
  color: string
  qualifications: string[]
}

export type Task = {
  id: string
  name: string
  crewId: CrewId
  zoneId: ZoneId
  durationMinutes: number
  originalStart: string
  proposedStart: string
  fixed: boolean
  environment: TaskEnvironment
  qualification: string
  dependencies: string[]
  deadline: string
}

export type AgentStep = {
  label: string
  detail: string
  tool: string
}

export const CREWS: Crew[] = [
  {
    id: 'ground',
    name: 'Crew A',
    trade: 'Groundworks',
    headcount: 6,
    color: '#ffb25b',
    qualifications: ['competent-person', 'excavation', 'equipment'],
  },
  {
    id: 'concrete',
    name: 'Crew B',
    trade: 'Concrete',
    headcount: 5,
    color: '#6fd0ff',
    qualifications: ['concrete-placement', 'finishing'],
  },
  {
    id: 'electrical',
    name: 'Crew C',
    trade: 'Electrical',
    headcount: 4,
    color: '#d0ff5b',
    qualifications: ['journey-electrician', 'signal-systems'],
  },
]

export const TASKS: Task[] = [
  {
    id: 'G0', name: 'Traffic-control handoff', crewId: 'ground', zoneId: 'north', durationMinutes: 30,
    originalStart: '05:30', proposedStart: '05:30', fixed: true, environment: 'outdoor-moderate',
    qualification: 'competent-person', dependencies: [], deadline: '06:00',
  },
  {
    id: 'G1', name: 'Equipment service & staging', crewId: 'ground', zoneId: 'laydown', durationMinutes: 120,
    originalStart: '06:00', proposedStart: '12:00', fixed: false, environment: 'shaded-support',
    qualification: 'equipment', dependencies: ['G0'], deadline: '14:00',
  },
  {
    id: 'G2', name: 'Signal trench excavation', crewId: 'ground', zoneId: 'north', durationMinutes: 120,
    originalStart: '08:00', proposedStart: '06:00', fixed: false, environment: 'outdoor-heavy',
    qualification: 'excavation', dependencies: ['G0'], deadline: '10:00',
  },
  {
    id: 'G3', name: 'Fine grade & compact', crewId: 'ground', zoneId: 'north', durationMinutes: 120,
    originalStart: '10:00', proposedStart: '08:00', fixed: false, environment: 'outdoor-heavy',
    qualification: 'equipment', dependencies: ['G2'], deadline: '12:00',
  },
  {
    id: 'G4', name: 'Conduit bedding', crewId: 'ground', zoneId: 'north', durationMinutes: 120,
    originalStart: '12:00', proposedStart: '10:00', fixed: false, environment: 'outdoor-heavy',
    qualification: 'excavation', dependencies: ['G3'], deadline: '14:00',
  },
  {
    id: 'C1', name: 'Foundation formwork', crewId: 'concrete', zoneId: 'south', durationMinutes: 120,
    originalStart: '06:00', proposedStart: '06:00', fixed: false, environment: 'outdoor-moderate',
    qualification: 'concrete-placement', dependencies: [], deadline: '08:00',
  },
  {
    id: 'C2', name: 'Rebar & anchor bolts', crewId: 'concrete', zoneId: 'south', durationMinutes: 60,
    originalStart: '08:00', proposedStart: '08:00', fixed: false, environment: 'outdoor-heavy',
    qualification: 'concrete-placement', dependencies: ['C1'], deadline: '09:00',
  },
  {
    id: 'C3', name: 'City inspection hold', crewId: 'concrete', zoneId: 'south', durationMinutes: 30,
    originalStart: '09:00', proposedStart: '09:00', fixed: true, environment: 'shaded-support',
    qualification: 'concrete-placement', dependencies: ['C2'], deadline: '09:30',
  },
  {
    id: 'C4', name: 'Foundation concrete pour', crewId: 'concrete', zoneId: 'south', durationMinutes: 120,
    originalStart: '09:30', proposedStart: '09:30', fixed: true, environment: 'outdoor-heavy',
    qualification: 'concrete-placement', dependencies: ['C3'], deadline: '11:30',
  },
  {
    id: 'C5', name: 'Finish & protect concrete', crewId: 'concrete', zoneId: 'south', durationMinutes: 90,
    originalStart: '11:30', proposedStart: '11:30', fixed: true, environment: 'outdoor-moderate',
    qualification: 'finishing', dependencies: ['C4'], deadline: '13:00',
  },
  {
    id: 'E1', name: 'Cabinet pre-wire', crewId: 'electrical', zoneId: 'laydown', durationMinutes: 120,
    originalStart: '06:00', proposedStart: '10:00', fixed: false, environment: 'shaded-support',
    qualification: 'signal-systems', dependencies: [], deadline: '12:00',
  },
  {
    id: 'E2', name: 'Proof duct & pull line', crewId: 'electrical', zoneId: 'south', durationMinutes: 120,
    originalStart: '08:00', proposedStart: '06:00', fixed: false, environment: 'outdoor-moderate',
    qualification: 'journey-electrician', dependencies: [], deadline: '10:00',
  },
  {
    id: 'E3', name: 'Pull signal conductors', crewId: 'electrical', zoneId: 'south', durationMinutes: 120,
    originalStart: '10:00', proposedStart: '08:00', fixed: false, environment: 'outdoor-heavy',
    qualification: 'journey-electrician', dependencies: ['E2'], deadline: '12:00',
  },
  {
    id: 'E4', name: 'Inspector test window', crewId: 'electrical', zoneId: 'south', durationMinutes: 60,
    originalStart: '13:00', proposedStart: '13:00', fixed: true, environment: 'outdoor-moderate',
    qualification: 'signal-systems', dependencies: ['E1', 'E3'], deadline: '14:00',
  },
]

export const THERMAL_EVIDENCE = {
  source: 'FortyGuard /v1/env_params and /v1/heatmap',
  status: 'cached-live',
  location: 'Phoenix planning AOI · 33.434° N, 112.018° W',
  observationDate: '2025-07-15',
  timezone: 'GMT−7',
  grid: '100 m requested analysis grid',
  maxTemperatureC: 40.1505,
  averageTemperatureC: 37.0796,
  apparentTemperatureC: [32.0,31.0,30.3,30.0,29.5,28.9,30.6,31.4,33.3,35.1,37.0,39.6,41.3,42.5,40.7,39.3,34.8,37.3,38.6,38.0,36.9,36.1,35.3,32.7],
  highWindow: { start: '11:00', end: '15:00', basis: 'five-hour modeled apparent-temperature peak window' },
  timeOfMeasureCells: 99,
  timeOfMeasureRangeHours: [4, 16],
  cachePaths: [
    '.agent_cache/live_geographies/phoenix_paved_industrial.json',
    '.agent_cache/live_followups/env_phoenix.json',
    '.agent_cache/live_followups/phoenix_time_of_measure.json',
  ],
} as const

export const EMPLOYER_POLICY = {
  name: 'Desert Build Co. · demo policy v1.4',
  status: 'synthetic employer policy',
  planningRules: [
    'Prefer movable moderate/heavy outdoor work outside the modeled 11:00–15:00 peak window.',
    'Preserve fixed delivery, inspection, access, and traffic-control commitments.',
    'Keep every task with a crew holding its required qualification.',
    'Plan a shaded recovery after 90 minutes of continuous outdoor work during the peak window.',
    'Flag new or returning workers for the employer’s acclimatization procedure.',
  ],
  authorityBoundary: 'Onsite supervisor applies the employer plan using current onsite WBGT, workload, PPE, worker condition, and professional judgment.',
} as const

export const AGENT_STEPS: AgentStep[] = [
  { label: 'Read tomorrow’s work plan', detail: '14 tasks · 3 crews · 2 field zones', tool: 'lookahead.inspect' },
  { label: 'Select work needing investigation', detail: '7 flexible outdoor tasks; 5 fixed commitments retained', tool: 'work.classify' },
  { label: 'Load thermal evidence', detail: 'Cached Phoenix hourly profile + 100 m analysis cells', tool: 'fortyguard.cached_evidence' },
  { label: 'Generate feasible alternatives', detail: 'Deterministic scheduler tests crew-safe sequences', tool: 'schedule.optimize' },
  { label: 'Verify plan and policy constraints', detail: 'Qualifications, logic, deadlines, fixed work, controls', tool: 'constraints.verify' },
  { label: 'Prepare superintendent decision', detail: 'Evidence, exceptions, metric, and rollback ready', tool: 'recommendation.prepare' },
  { label: 'Recompute approved result', detail: '22 → 6 modeled peak-window crew-hours', tool: 'result.verify' },
]

const toMinutes = (time: string) => {
  const [hours, minutes] = time.split(':').map(Number)
  return hours * 60 + minutes
}

const overlaps = (start: number, duration: number, windowStart: number, windowEnd: number) =>
  Math.max(0, Math.min(start + duration, windowEnd) - Math.max(start, windowStart))

export const isMetricEligible = (task: Task) => !task.fixed && task.environment !== 'shaded-support'

export const peakWindowCrewHours = (plan: 'original' | 'proposed') => {
  const windowStart = toMinutes(THERMAL_EVIDENCE.highWindow.start)
  const windowEnd = toMinutes(THERMAL_EVIDENCE.highWindow.end)
  return TASKS.filter(isMetricEligible).reduce((total, task) => {
    const crew = CREWS.find(item => item.id === task.crewId)!
    const start = toMinutes(plan === 'original' ? task.originalStart : task.proposedStart)
    return total + overlaps(start, task.durationMinutes, windowStart, windowEnd) / 60 * crew.headcount
  }, 0)
}

export const validatePolicy = (plan: 'original' | 'proposed') => {
  const windowStart = toMinutes(THERMAL_EVIDENCE.highWindow.start)
  const windowEnd = toMinutes(THERMAL_EVIDENCE.highWindow.end)
  return TASKS.filter(task => task.environment !== 'shaded-support').every(task => {
    const start = toMinutes(plan === 'original' ? task.originalStart : task.proposedStart)
    return overlaps(start, task.durationMinutes, windowStart, windowEnd) <= 90
  })
}

export const HERO_METRIC = {
  before: peakWindowCrewHours('original'),
  after: peakWindowCrewHours('proposed'),
  moved: peakWindowCrewHours('original') - peakWindowCrewHours('proposed'),
  type: 'derived planning proxy',
  label: 'movable outdoor crew-hours in the highest modeled heat window',
} as const

const taskEnd = (task: Task, plan: 'original' | 'proposed') =>
  toMinutes(plan === 'original' ? task.originalStart : task.proposedStart) + task.durationMinutes

export const validatePlan = (plan: 'original' | 'proposed') => TASKS.every(task => {
  const crew = CREWS.find(item => item.id === task.crewId)
  const start = toMinutes(plan === 'original' ? task.originalStart : task.proposedStart)
  const dependenciesPass = task.dependencies.every(id => {
    const dependency = TASKS.find(item => item.id === id)
    return dependency ? taskEnd(dependency, plan) <= start : false
  })
  const qualificationPass = crew?.qualifications.includes(task.qualification) ?? false
  const deadlinePass = taskEnd(task, plan) <= toMinutes(task.deadline)
  const fixedPass = !task.fixed || task.originalStart === task.proposedStart
  return dependenciesPass && qualificationPass && deadlinePass && fixedPass
})

export const validateScenario = () =>
  TASKS.length === 14 &&
  CREWS.length === 3 &&
  HERO_METRIC.before === 22 &&
  HERO_METRIC.after === 6 &&
  HERO_METRIC.moved === 16 &&
  validatePlan('original') &&
  validatePlan('proposed') &&
  !validatePolicy('original') &&
  validatePolicy('proposed') &&
  THERMAL_EVIDENCE.status === 'cached-live' &&
  EMPLOYER_POLICY.status === 'synthetic employer policy'

export const MINUTE_START = 5 * 60 + 30
export const MINUTE_END = 14 * 60 + 30
export const timelinePosition = (time: string) => ((toMinutes(time) - MINUTE_START) / (MINUTE_END - MINUTE_START)) * 100
export const timelineWidth = (durationMinutes: number) => (durationMinutes / (MINUTE_END - MINUTE_START)) * 100
