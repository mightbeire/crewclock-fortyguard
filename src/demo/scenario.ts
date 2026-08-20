export type AgentStep = { label: string; detail: string; tool: string }

export const DEMO_SCENARIO = {
  id: 'cached-2025-07-15',
  mode: 'CACHED DEMO',
  city: 'Phoenix operations zone',
  measured: {
    date: '2025-07-15',
    maxTemperatureC: 40.1505,
    averageTemperatureC: 37.0796,
    minTemperatureC: 33.4909,
    comparisonMaxC: 24.5086,
    source: 'FortyGuard /v1/heatmap',
    cachePath: '.agent_cache/live_geographies/phoenix_paved_industrial.json',
    grid: 'API response; requested analysis geometry',
  },
  satelliteContext: { buildings: 73.87, roads: 12.94, trees: 4.93, sourceCity: 'Las Vegas' },
  derived: {
    baselineExposedMinutes: 168,
    recommendedExposedMinutes: 94,
    avoidedExposedMinutes: 74,
    improvementPercent: 44,
    label: 'Scenario-derived exposure proxy',
  },
  assumptions: [
    'Operational jobs, durations and constraints are a deterministic demonstration scenario.',
    'Temperature values are cached-live FortyGuard evidence, not a current forecast.',
    'The exposure proxy is illustrative and is not a medical or safety threshold.',
  ],
  steps: [
    { label: 'Analyzing sites', detail: '3 work zones · 7 movable tasks', tool: 'portfolio.inspect' },
    { label: 'Requesting thermal evidence', detail: 'Cached FortyGuard heatmap located', tool: 'fortyguard.heatmap' },
    { label: 'Comparing alternatives', detail: '12 feasible sequences evaluated', tool: 'schedule.compare' },
    { label: 'Checking constraints', detail: 'Crew, deadline and approval gates passed', tool: 'constraints.verify' },
    { label: 'Preparing recommendation', detail: 'Move 3 flexible tasks before peak', tool: 'recommendation.prepare' },
    { label: 'Verifying result', detail: 'Exposure proxy recomputed: −44%', tool: 'result.verify' },
  ] satisfies AgentStep[],
} as const

export function validateScenario() {
  const d = DEMO_SCENARIO.derived
  return d.baselineExposedMinutes - d.recommendedExposedMinutes === d.avoidedExposedMinutes &&
    Math.round((d.avoidedExposedMinutes / d.baselineExposedMinutes) * 100) === d.improvementPercent &&
    DEMO_SCENARIO.mode === 'CACHED DEMO'
}
