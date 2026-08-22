import { calculateScheduledHighHeatCrewHours } from './shhch'

export type CrewId = 'ground' | 'concrete' | 'electrical'
export type ZoneId = 'north' | 'south' | 'laydown' | 'access'
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
  weatherSensitivity: { precipitation: boolean }
}

export type Workface = { id: ZoneId; label: string; polygon: Array<[number, number]> }

export const PHOENIX_PROJECT_AOI = {
  type: 'FeatureCollection' as const,
  features: [{
    type: 'Feature' as const,
    properties: {},
    geometry: {
      type: 'Polygon' as const,
      coordinates: [[
        [-112.01845, 33.43355], [-112.01755, 33.43355], [-112.01755, 33.43445],
        [-112.01845, 33.43445], [-112.01845, 33.43355],
      ]],
    },
  }],
} as const

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
    originalStart: '06:00', proposedStart: '06:00', fixed: true, environment: 'outdoor-moderate',
    qualification: 'competent-person', dependencies: [], deadline: '06:30', weatherSensitivity: { precipitation: false },
  },
  {
    id: 'G1', name: 'Equipment service & staging', crewId: 'ground', zoneId: 'laydown', durationMinutes: 120,
    originalStart: '06:30', proposedStart: '13:00', fixed: false, environment: 'shaded-support',
    qualification: 'equipment', dependencies: ['G0'], deadline: '16:00', weatherSensitivity: { precipitation: false },
  },
  {
    id: 'G2', name: 'Signal trench excavation', crewId: 'ground', zoneId: 'north', durationMinutes: 120,
    originalStart: '08:30', proposedStart: '06:30', fixed: false, environment: 'outdoor-heavy',
    qualification: 'excavation', dependencies: ['G0'], deadline: '12:00', weatherSensitivity: { precipitation: true },
  },
  {
    id: 'G3', name: 'Fine grade & compact', crewId: 'ground', zoneId: 'north', durationMinutes: 120,
    originalStart: '10:30', proposedStart: '08:30', fixed: false, environment: 'outdoor-heavy',
    qualification: 'equipment', dependencies: ['G2'], deadline: '14:00', weatherSensitivity: { precipitation: true },
  },
  {
    id: 'G4', name: 'Conduit bedding', crewId: 'ground', zoneId: 'north', durationMinutes: 120,
    originalStart: '12:30', proposedStart: '10:30', fixed: false, environment: 'outdoor-heavy',
    qualification: 'excavation', dependencies: ['G3'], deadline: '16:00', weatherSensitivity: { precipitation: true },
  },
  {
    id: 'C1', name: 'Foundation formwork', crewId: 'concrete', zoneId: 'south', durationMinutes: 120,
    originalStart: '06:00', proposedStart: '06:00', fixed: false, environment: 'outdoor-moderate',
    qualification: 'concrete-placement', dependencies: [], deadline: '08:00', weatherSensitivity: { precipitation: true },
  },
  {
    id: 'C2', name: 'Rebar & anchor bolts', crewId: 'concrete', zoneId: 'south', durationMinutes: 60,
    originalStart: '08:00', proposedStart: '08:00', fixed: false, environment: 'outdoor-heavy',
    qualification: 'concrete-placement', dependencies: ['C1'], deadline: '09:00', weatherSensitivity: { precipitation: true },
  },
  {
    id: 'C3', name: 'City inspection hold', crewId: 'concrete', zoneId: 'south', durationMinutes: 30,
    originalStart: '09:00', proposedStart: '09:00', fixed: true, environment: 'shaded-support',
    qualification: 'concrete-placement', dependencies: ['C2'], deadline: '09:30', weatherSensitivity: { precipitation: false },
  },
  {
    id: 'C4', name: 'Foundation concrete pour', crewId: 'concrete', zoneId: 'south', durationMinutes: 120,
    originalStart: '09:30', proposedStart: '09:30', fixed: true, environment: 'outdoor-heavy',
    qualification: 'concrete-placement', dependencies: ['C3'], deadline: '11:30', weatherSensitivity: { precipitation: true },
  },
  {
    id: 'C5', name: 'Finish & protect concrete', crewId: 'concrete', zoneId: 'south', durationMinutes: 90,
    originalStart: '13:00', proposedStart: '13:00', fixed: true, environment: 'outdoor-moderate',
    qualification: 'finishing', dependencies: ['C4'], deadline: '14:30', weatherSensitivity: { precipitation: true },
  },
  {
    id: 'E1', name: 'Cabinet pre-wire', crewId: 'electrical', zoneId: 'laydown', durationMinutes: 120,
    originalStart: '06:00', proposedStart: '10:00', fixed: false, environment: 'shaded-support',
    qualification: 'signal-systems', dependencies: [], deadline: '12:00', weatherSensitivity: { precipitation: false },
  },
  {
    id: 'E2', name: 'Proof duct & pull line', crewId: 'electrical', zoneId: 'south', durationMinutes: 120,
    originalStart: '08:00', proposedStart: '06:00', fixed: false, environment: 'outdoor-moderate',
    qualification: 'journey-electrician', dependencies: [], deadline: '10:00', weatherSensitivity: { precipitation: false },
  },
  {
    id: 'E3', name: 'Pull signal conductors', crewId: 'electrical', zoneId: 'south', durationMinutes: 120,
    originalStart: '10:00', proposedStart: '08:00', fixed: false, environment: 'outdoor-heavy',
    qualification: 'journey-electrician', dependencies: ['E2'], deadline: '12:00', weatherSensitivity: { precipitation: false },
  },
  {
    id: 'E4', name: 'Inspector test window', crewId: 'electrical', zoneId: 'south', durationMinutes: 60,
    originalStart: '13:00', proposedStart: '13:00', fixed: true, environment: 'outdoor-moderate',
    qualification: 'signal-systems', dependencies: ['E1', 'E3'], deadline: '14:00', weatherSensitivity: { precipitation: false },
  },
]

export const WORKFACES: Workface[] = [
  { id: 'north', label: 'North workface', polygon: [[-112.01840, 33.43400], [-112.01800, 33.43400], [-112.01800, 33.43440], [-112.01840, 33.43440]] },
  { id: 'south', label: 'South workface', polygon: [[-112.01840, 33.43360], [-112.01800, 33.43360], [-112.01800, 33.43400], [-112.01840, 33.43400]] },
  { id: 'laydown', label: 'Laydown / shaded support', polygon: [[-112.01795, 33.43360], [-112.01760, 33.43360], [-112.01760, 33.43395], [-112.01795, 33.43395]] },
  { id: 'access', label: 'Access / traffic control', polygon: [[-112.01795, 33.43405], [-112.01760, 33.43405], [-112.01760, 33.43440], [-112.01795, 33.43440]] },
]

export const THERMAL_EVIDENCE = {
  source: 'FortyGuard /v1/heatmap analytic_type=exceedance · /v1/env_params (optional context)',
  status: 'EVIDENCE_UNAVAILABLE',
  exceedanceEvidenceStatus: 'none' as 'none' | 'partial' | 'complete',
  exceedanceWindows: [],
  forecastStatus: 'NOT_DEMONSTRATED',
  projectThermalTrigger: { thresholdC: 32, quantity: 'fortyguard_modeled_temperature', provenance: 'synthetic employer project trigger; FortyGuard threshold quantity is modeled temperature, not heat index', thresholdUnits: 'celsius' as const, direction: 'above' as const },
  location: 'Phoenix planning AOI · 33.434° N, 112.018° W',
  aoi: PHOENIX_PROJECT_AOI,
  observationDate: '2025-07-15',
  timezone: 'America/Phoenix · UTC−07:00',
  grid: '100 m requested analysis grid',
  primarySignal: 'No Phoenix schedule-aligned exceedance windows currently cached; TCM/time_of_measure/persistence are contextual evidence only',
  environmentalContextRole: 'Selective context only; never the SHHCH duration source, forecast, or spatial ranking engine.',
  evidenceClass: 'CONTEXTUAL_ENVIRONMENTAL_EVIDENCE' as const,
  decisionGradeThermalEvidence: false,
  maxTemperatureC: 40.1505,
  averageTemperatureC: 37.0796,
  apparentTemperatureC: [32.0,31.0,30.3,30.0,29.5,28.9,30.6,31.4,33.3,35.1,37.0,39.6,41.3,42.5,40.7,39.3,34.8,37.3,38.6,38.0,36.9,36.1,35.3,32.7],
  highWindow: { start: '11:00', end: '15:00', basis: 'employer-configured project trigger window; not inferred from an env_params range artifact' },
  timeOfMeasureCells: 99,
  timeOfMeasureRangeHours: [4, 16],
  cachePaths: [
    '.agent_cache/live_geographies/phoenix_paved_industrial.json',
    '.agent_cache/live_followups/env_phoenix.json',
    '.agent_cache/live_followups/phoenix_time_of_measure.json',
  ],
} as const

export const BREAK_POLICY = {
  triggerStart: '11:00',
  triggerEnd: '15:00',
  afterContinuousMinutes: 90,
  durationMinutes: 30,
  source: 'SYNTHETIC_EMPLOYER_POLICY',
  version: 'v1.4',
} as const

export type BreakPolicy = { triggerStart: string; triggerEnd: string; afterContinuousMinutes: number; durationMinutes: number; source: string; version: string }
export type EmployerPolicy = { name: string; status: string; planningRules: string[]; breakRules: BreakPolicy[]; authorityBoundary: string }

export const EMPLOYER_POLICY: EmployerPolicy = {
  name: 'Desert Build Co. · demo policy v1.4',
  status: 'synthetic employer policy' as string,
  planningRules: [
    'Prefer movable moderate/heavy outdoor work outside the modeled 11:00–15:00 peak window.',
    'Preserve fixed delivery, inspection, access, and traffic-control commitments.',
    'Keep every task with a crew holding its required qualification.',
    'Plan a shaded recovery after 90 minutes of continuous outdoor work during the peak window.',
    'Flag new or returning workers for the employer’s acclimatization procedure.',
  ],
  breakRules: [BREAK_POLICY],
  authorityBoundary: 'Onsite supervisor applies the employer plan using current onsite WBGT, workload, PPE, worker condition, and professional judgment.',
}

export const createManualPolicy = (location: string) => ({
  ...EMPLOYER_POLICY,
  name: `${location} · user-defined shift policy`,
  status: 'user-defined shift policy',
  planningRules: [
    'Keep fixed commitments and stated deadlines intact.',
    'Use location-specific evidence before making environmental changes.',
    'Keep every task with a crew holding its required qualification.',
  ],
  breakRules: [{ ...BREAK_POLICY, source: 'USER_DEFINED_SHIFT_POLICY', version: 'user-v1' }],
})

export const createLocalWorkfaces = (): Workface[] => [
  { id: 'north', label: 'North workface', polygon: [[0, 0], [40, 0], [40, 40], [0, 40]] },
  { id: 'south', label: 'South workface', polygon: [[0, -40], [40, -40], [40, 0], [0, 0]] },
  { id: 'laydown', label: 'Laydown / support', polygon: [[45, -40], [80, -40], [80, -5], [45, -5]] },
  { id: 'access', label: 'Access / traffic control', polygon: [[45, 5], [80, 5], [80, 40], [45, 40]] },
]

export const CANONICAL_SAMPLE_PROJECT = {
  name: 'PHOENIX INDUSTRIAL PROJECT',
  label: 'Sample Project',
  shift: { start: '06:00', end: '16:00', timezone: 'America/Phoenix' },
  tasks: TASKS,
  crews: CREWS,
  workfaces: WORKFACES,
  employerPolicy: EMPLOYER_POLICY,
  projectThermalTrigger: THERMAL_EVIDENCE.projectThermalTrigger,
  fortyguardEvidence: { status: THERMAL_EVIDENCE.exceedanceEvidenceStatus, forecastStatus: THERMAL_EVIDENCE.forecastStatus },
  operationalInputs: 'SYNTHETIC',
  calculations: 'DERIVED',
} as const

// TEST/DEMO FIXTURE ONLY. The canonical UI consumes runtime.ts events.
export const AGENT_STEPS: AgentStep[] = [
  { label: 'Read the upcoming shift plan', detail: '14 tasks · 3 crews · 4 polygon workfaces', tool: 'inspect_shift_plan' },
  { label: 'Select work needing investigation', detail: '7 flexible outdoor tasks; 5 fixed commitments retained', tool: 'work.classify' },
  { label: 'Load selective thermal evidence', detail: 'Cached Phoenix heatmap cells · shared AOI · 100 m grid', tool: 'get_workface_heatmap' },
  { label: 'Generate feasible alternatives', detail: 'Deterministic scheduler tests crew-safe sequences', tool: 'schedule.optimize' },
  { label: 'Verify plan and policy constraints', detail: 'Qualifications, logic, deadlines, fixed work, controls', tool: 'constraints.verify' },
  { label: 'Prepare superintendent decision', detail: 'Evidence, exceptions, metric, and rollback ready', tool: 'recommendation.prepare' },
  { label: 'Recompute approved result', detail: 'Scheduled high-heat crew-hours · constraints rechecked', tool: 'verify_schedule' },
]

const toMinutes = (time: string) => {
  const [hours, minutes] = time.split(':').map(Number)
  return hours * 60 + minutes
}

const overlaps = (start: number, duration: number, windowStart: number, windowEnd: number) =>
  Math.max(0, Math.min(start + duration, windowEnd) - Math.max(start, windowStart))

export const isMetricEligible = (task: Task) => !task.fixed && task.environment !== 'shaded-support'

export const peakWindowCrewHours = (plan: 'original' | 'proposed'): number | null => {
  const schedule = Object.fromEntries(TASKS.map(task => [task.id, plan === 'original' ? task.originalStart : task.proposedStart]))
  const result = calculateScheduledHighHeatCrewHours(schedule, TASKS, CREWS, WORKFACES, THERMAL_EVIDENCE.exceedanceWindows, THERMAL_EVIDENCE.projectThermalTrigger)
  return result.valid ? result.totalCrewHours : null
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
  moved: null,
  type: 'FortyGuard exceedance-derived schedule metric',
  label: 'scheduled high-heat crew-hours',
  status: THERMAL_EVIDENCE.exceedanceEvidenceStatus,
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
  WORKFACES.length === 4 &&
  TASKS.every(task => typeof task.weatherSensitivity.precipitation === 'boolean') &&
  HERO_METRIC.before === null &&
  HERO_METRIC.after === null &&
  validatePlan('original') &&
  validatePlan('proposed') &&
  !validatePolicy('original') &&
  validatePolicy('proposed') &&
  THERMAL_EVIDENCE.status === 'EVIDENCE_UNAVAILABLE' &&
  THERMAL_EVIDENCE.exceedanceEvidenceStatus === 'none' &&
  EMPLOYER_POLICY.status === 'synthetic employer policy'

export const MINUTE_START = 6 * 60
export const MINUTE_END = 16 * 60
export const timelinePosition = (time: string) => ((toMinutes(time) - MINUTE_START) / (MINUTE_END - MINUTE_START)) * 100
export const timelineWidth = (durationMinutes: number) => (durationMinutes / (MINUTE_END - MINUTE_START)) * 100
