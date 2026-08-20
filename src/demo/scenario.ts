export type DemoId = 'shiftshield' | 'coursecorrect' | 'recess-relay'
export type MapKind = 'delivery' | 'race' | 'campus'
export type AgentStep = { label: string; detail: string; tool: string }

export type DemoScenario = {
  id: DemoId; name: string; number: string; mapKind: MapKind; audience: string; problem: string
  hero: [string, string]; lede: string; locationLabel: string; objectLabel: string
  derived: { before: number; after: number; shifted: number; percent: number; unit: string; headline: string; label: string }
  scale: { value: string; label: string }; context: string; constraints: string[]; steps: AgentStep[]
  assumptions: string[]; publicData: string
}

export const MEASURED_EVIDENCE = {
  date: '2025-07-15', maxTemperatureC: 40.1505, averageTemperatureC: 37.0796,
  minTemperatureC: 33.4909, comparisonMaxC: 24.5086, source: 'FortyGuard /v1/heatmap',
  cachePath: '.agent_cache/live_geographies/phoenix_paved_industrial.json', grid: '100 m requested API analysis grid',
  satellite: { buildingsPercent: 73.87, roadsPercent: 12.94, treesPercent: 4.93, sourceCity: 'Las Vegas', cachePath: '.agent_cache/live_geographies/las_vegas_dense_paved.json' },
} as const

export const SCENARIOS: Record<DemoId, DemoScenario> = {
  shiftshield: {
    id: 'shiftshield', name: 'ShiftShield', number: '01', mapKind: 'delivery', audience: 'Delivery operations managers',
    problem: 'Stop drivers spending avoidable time in the hottest parts of their routes.', hero: ['Move the stops.', 'Miss the peak.'],
    lede: 'The agent finds flexible deliveries, changes only their sequence, preserves every promise—and proves the thermal difference.',
    locationLabel: 'PHX DELIVERY ZONE · 33.45° N', objectLabel: '7 stops · 3 flexible',
    derived: { before: 168, after: 94, shifted: 74, percent: 44, unit: 'hot-cell minutes', headline: '−44%', label: 'peak-window route exposure' },
    scale: { value: '7', label: 'delivery stops' }, context: 'A fixed sequence crosses the hottest modeled cells during their peak. Three stops have valid alternate positions.',
    constraints: ['7/7 promises kept', 'Shift ends 16:30', 'Cold-chain stop locked', 'Dispatcher approval'],
    steps: [
      { label: 'Reading today’s route', detail: '7 stops · 3 marked flexible', tool: 'route.inspect' },
      { label: 'Selecting thermal evidence', detail: '4 relevant cells requested from cache', tool: 'fortyguard.heatmap' },
      { label: 'Testing stop sequences', detail: '12 feasible orders compared', tool: 'route.compare' },
      { label: 'Checking promises', detail: 'Time windows, shift and locked stop pass', tool: 'constraints.verify' },
      { label: 'Proposing sequence 1·2·5·4·3·6·7', detail: 'Awaiting dispatcher approval', tool: 'recommendation.prepare' },
      { label: 'Verifying approved route', detail: '168 → 94 hot-cell minutes', tool: 'result.verify' },
    ],
    assumptions: ['Stops, durations, time windows and route ordering are deterministic scenario data.', 'Hot-cell minutes are a planning proxy, not a health or safety measure.', 'Street geometry is illustrative scenario geometry.'],
    publicData: 'No external public dataset is presented as production input in this micro-demo.',
  },
  coursecorrect: {
    id: 'coursecorrect', name: 'CourseCorrect', number: '02', mapKind: 'race', audience: 'Race organizers',
    problem: 'Stop thousands of participants being sent through avoidably hot parts of a race course.', hero: ['Reroute one block.', 'Move 2,400 people.'],
    lede: 'The agent tests course and wave alternatives, protects distance and event constraints, then quantifies the crowd-scale change.',
    locationLabel: 'PHX 10K COURSE · 33.45° N', objectLabel: '2,400 runners · 4 waves',
    derived: { before: 38400, after: 16800, shifted: 21600, percent: 56, unit: 'participant-minutes', headline: '21,600', label: 'participant-minutes shifted' },
    scale: { value: '2.4k', label: 'participants' }, context: 'Four waves spend 16 modeled minutes on the hottest course segment; an equal-distance alternative cuts that overlap to 7.',
    constraints: ['10.0 km ± 50 m', '4 closures unchanged', '3 aid stations retained', 'Race director approval'],
    steps: [
      { label: 'Reading course and waves', detail: '2,400 runners · 4 start waves', tool: 'event.inspect' },
      { label: 'Selecting thermal segments', detail: '6 course cells inspected from cache', tool: 'fortyguard.heatmap' },
      { label: 'Testing course alternatives', detail: '8 detour/time combinations compared', tool: 'course.compare' },
      { label: 'Checking event constraints', detail: 'Distance, closures and aid stations pass', tool: 'constraints.verify' },
      { label: 'Proposing one-block detour', detail: 'Awaiting race director approval', tool: 'recommendation.prepare' },
      { label: 'Verifying approved course', detail: '21,600 participant-minutes shifted', tool: 'result.verify' },
    ],
    assumptions: ['Participant count, pace, waves, closures and aid stations are deterministic scenario data.', 'Participant-minutes are arithmetic exposure overlap, not a clinical-risk measure.', 'Course geometry is illustrative scenario geometry.'],
    publicData: 'The workflow is compatible with public street/course geometry; none is represented as live production data here.',
  },
  'recess-relay': {
    id: 'recess-relay', name: 'Recess Relay', number: '03', mapKind: 'campus', audience: 'School administrators',
    problem: 'Stop outdoor activities being scheduled in the hottest parts of campus.', hero: ['One campus.', 'Three temperatures.'],
    lede: 'The agent pairs the timetable with campus thermal evidence, swaps compatible activities, and checks every supervision rule.',
    locationLabel: 'PHX CAMPUS · 33.45° N', objectLabel: '180 students · 3 spaces',
    derived: { before: 5400, after: 1800, shifted: 3600, percent: 67, unit: 'student-minutes', headline: '3,600', label: 'student-minutes shifted' },
    scale: { value: '180', label: 'students scheduled' }, context: 'The largest group is assigned to the modeled hottest asphalt court. Two compatible space/time swaps preserve the school day.',
    constraints: ['6/6 activities kept', 'Supervision covered', 'Capacity respected', 'Accessible route retained'],
    steps: [
      { label: 'Reading campus timetable', detail: '180 students · 6 outdoor activities', tool: 'schedule.inspect' },
      { label: 'Selecting campus evidence', detail: 'Court, field and green zone inspected', tool: 'fortyguard.heatmap' },
      { label: 'Testing activity swaps', detail: '9 compatible space/time pairs compared', tool: 'schedule.compare' },
      { label: 'Checking school constraints', detail: 'Supervision, capacity and access pass', tool: 'constraints.verify' },
      { label: 'Proposing two swaps', detail: 'Awaiting administrator approval', tool: 'recommendation.prepare' },
      { label: 'Verifying approved timetable', detail: '3,600 student-minutes shifted', tool: 'result.verify' },
    ],
    assumptions: ['Students, activities, timetable, capacity and supervision are deterministic scenario data.', 'Student-minutes are a planning proxy, not a claim of safety or health benefit.', 'Campus geometry and zone temperatures are illustrative allocations of cached evidence.'],
    publicData: 'The workflow can use public campus footprints; this micro-demo uses clearly synthetic campus geometry.',
  },
}

export const DEMO_IDS = Object.keys(SCENARIOS) as DemoId[]
export const PROPOSAL_STEP = 4
export const VERIFY_STEP = 5

export function validateScenario(scenario: DemoScenario) {
  const d = scenario.derived
  return d.before - d.after === d.shifted && Math.round((d.shifted / d.before) * 100) === d.percent && scenario.steps.length === 6 && scenario.assumptions.some(value => value.includes('not a'))
}

export function validateAllScenarios() { return DEMO_IDS.every(id => validateScenario(SCENARIOS[id])) }
