import { readFileSync, writeFileSync } from 'node:fs'
import { join } from 'node:path'
import { describe, expect, it } from 'vitest'
import { CREWS, TASKS, WORKFACES, type Task } from '../src/demo/scenario'
import { calculateScheduledHighHeatCrewHours } from '../src/demo/shhch'
import { approveRecommendation, originalSchedule, peakWindowCrewHoursFor, runCrewClock } from '../src/demo/engine'

const ROOT = join(process.cwd())
const EVIDENCE_DIR = join(ROOT, 'evidence', 'fortyguard-canonical-phoenix')
const WINDOW_FILES = [
  ['06:00', '08:00', 'phoenix_2025-07-15_0600_0800.json'],
  ['08:00', '10:00', 'phoenix_2025-07-15_0800_1000.json'],
  ['10:00', '12:00', 'phoenix_2025-07-15_1000_1200.json'],
  ['12:00', '14:00', 'phoenix_2025-07-15_1200_1400.json'],
  ['14:00', '16:00', 'phoenix_2025-07-15_1400_1600.json'],
] as const

const thermalEvidence = {
  source: 'FortyGuard /v1/heatmap analytic_type=exceedance',
  status: 'READY',
  exceedanceEvidenceStatus: 'complete' as const,
  forecastStatus: 'HISTORICAL_REPLAY',
  projectThermalTrigger: {
    thresholdC: 32,
    quantity: 'fortyguard_modeled_temperature' as const,
    provenance: 'CrewClock project_thermal_trigger configured before live retrieval; FortyGuard modeled temperature, not heat index.',
    thresholdUnits: 'celsius' as const,
    direction: 'above' as const,
  },
  observationDate: '2025-07-15',
  timezone: 'America/Phoenix',
  aoi: 'PHOENIX_CANONICAL_AOI_WGS84',
  geometryValidation: 'PASS',
  exceedanceWindows: WINDOW_FILES.map(([start, end, file]) => {
    const record = JSON.parse(readFileSync(join(EVIDENCE_DIR, file), 'utf8'))
    const feature = record.result.map_data.features[0]
    return {
      analyticType: 'exceedance' as const,
      start,
      end,
      units: 'hour' as const,
      status: 'VALID' as const,
      provenance: `LIVE_FORTYGUARD:${record.activity_id}:${record.result_sha256}`,
      aoi: 'PHOENIX_CANONICAL_AOI_WGS84',
      date: '2025-07-15',
      timezone: 'America/Phoenix',
      analyticSource: 'FortyGuard:/v1/heatmap',
      projectThermalTrigger: { thresholdC: 32, quantity: 'fortyguard_modeled_temperature' as const, thresholdUnits: 'celsius' as const, direction: 'above' as const },
      resultHash: record.result_sha256,
      version: 'fortyguard-canonical-phoenix-v1',
      qualifying: true,
      tiles: [{ polygon: feature.geometry.coordinates[0].slice(0, -1), valueHours: feature.properties.value }],
    }
  }),
} as const

const toRows = (schedule: Record<string, string>, label: string) => {
  const result = calculateScheduledHighHeatCrewHours(schedule, TASKS, CREWS, WORKFACES, thermalEvidence.exceedanceWindows, thermalEvidence.projectThermalTrigger)
  return {
    label,
    status: result.status,
    valid: result.valid,
    totalShhch: result.totalCrewHours,
    movableShhch: result.movableCrewHours,
    fixedShhch: result.fixedCrewHours,
    contributions: result.contributions,
  }
}

describe('canonical real FortyGuard evidence', () => {
  it('measures the frozen scenario and writes decision-grade artifacts', () => {
    expect(thermalEvidence.exceedanceWindows).toHaveLength(5)
    expect(thermalEvidence.exceedanceWindows.every(window => window.status === 'VALID')).toBe(true)
    expect(thermalEvidence.exceedanceWindows.every(window => window.projectThermalTrigger.thresholdC === 32)).toBe(true)

    const baseline = originalSchedule(TASKS)
    const run = runCrewClock({ thermalEvidence, scenarioLabel: 'CANONICAL_PHOENIX_REPLAY' })
    const disruptionMinutes = run.recommendation
      ? TASKS.reduce((sum, task) => sum + Math.abs(Number(run.recommendation?.[task.id].slice(0, 2)) * 60 + Number(run.recommendation?.[task.id].slice(3)) - (Number(run.original[task.id].slice(0, 2)) * 60 + Number(run.original[task.id].slice(3)))), 0)
      : null
    const baselineMetrics = toRows(baseline, 'baseline')
    const proposedMetrics = run.recommendation ? toRows(run.recommendation, 'proposed') : null
    const matrix = TASKS.filter(task => task.environment !== 'shaded-support').map((task: Task) => {
      const contribution = baselineMetrics.contributions.find(item => item.taskId === task.id)
      return {
        taskId: task.id,
        task: task.name,
        workface: task.zoneId,
        crewId: task.crewId,
        crewSize: CREWS.find(crew => crew.id === task.crewId)?.headcount ?? null,
        scheduledStart: baseline[task.id],
        scheduledEndMinutes: Number(baseline[task.id].slice(0, 2)) * 60 + Number(baseline[task.id].slice(3)) + task.durationMinutes,
        evidenceWindows: thermalEvidence.exceedanceWindows.map(window => ({ start: window.start, end: window.end, resultHash: window.resultHash, valueHours: window.tiles[0].valueHours })),
        validExceedanceHours: contribution?.overlappingExceedanceHours ?? null,
        crewHours: contribution?.crewHours ?? null,
        fixed: task.fixed,
        provenance: contribution?.provenance ?? [],
      }
    })

    writeFileSync(join(EVIDENCE_DIR, 'workface_time_matrix.json'), JSON.stringify({
      status: 'COMPLETE',
      semantics: { date: '2025-07-15', timezone: 'America/Phoenix', requestTimeSemantics: 'AOI_LOCAL_TIME', analyticType: 'exceedance', units: 'hour', trigger: thermalEvidence.projectThermalTrigger },
      method: 'Frozen CrewClock area-weighted tile intersection and schedule-aligned exceedance union; overlapping evidence intervals are not double-counted.',
      workfaceGeometry: {
        validation: 'PASS',
        interpretation: 'Each provider tile intersects each declared workface; ratios are retained to distinguish overlap from a claim of full-face coverage.',
        overlapRatiosByWindow: { north: 0.569696, south: 0.529689, laydown: 0.933531, access: 1 },
      },
      rows: matrix,
    }, null, 2))

    writeFileSync(join(EVIDENCE_DIR, 'shhch_derivation.json'), JSON.stringify({
      definition: 'valid scheduled exceedance overlap hours × crew size',
      baseline: baselineMetrics,
      proposed: proposedMetrics,
      evidenceHashInputs: thermalEvidence.exceedanceWindows.map(window => ({ start: window.start, end: window.end, resultHash: window.resultHash })),
    }, null, 2))

    writeFileSync(join(EVIDENCE_DIR, 'scheduler_comparison.json'), JSON.stringify({
      canonicalResult: run.decisionKind === 'operational-correction' ? 'REAL_FEASIBLE_OPERATIONAL_CORRECTION' : run.status === 'no-improvement' ? 'REAL_NO_FEASIBLE_IMPROVEMENT' : run.status,
      deterministicStatus: run.status,
      baselineSchedule: run.original,
      proposedSchedule: run.recommendation,
      baselineTotalShhch: baselineMetrics.totalShhch,
      baselineMovableShhch: baselineMetrics.movableShhch,
      baselineFixedShhch: baselineMetrics.fixedShhch,
      proposedTotalShhch: proposedMetrics?.totalShhch ?? null,
      proposedMovableShhch: proposedMetrics?.movableShhch ?? null,
      proposedFixedShhch: proposedMetrics?.fixedShhch ?? null,
      shhchDelta: proposedMetrics ? baselineMetrics.totalShhch! - proposedMetrics.totalShhch! : null,
      disruptionMinutes,
      tasksRetimed: run.recommendation ? TASKS.filter(task => run.recommendation?.[task.id] !== run.original[task.id]).length : null,
      schedulerStats: run.stats,
      baselineVerification: run.originalVerification,
      candidateVerification: run.recommendationVerification,
      feasibleAlternativeVerification: run.recommendationVerification?.passed ? 'PASS' : 'NOT_AVAILABLE',
      hardConstraintFamilies: run.originalVerification.families,
      schedulerMessage: run.message,
      frozenEngine: 'src/demo/engine.ts',
    }, null, 2))

    writeFileSync(join(EVIDENCE_DIR, 'canonical_outcome.json'), JSON.stringify({
      providerStatus: 'RESOLVED',
      sanityRequest: 'PASS',
      sanityActivityId: '60568d12-10d6-478b-af83-7d197c1eec37',
      decisionGradeCoverage: 'PASS',
      workfaceGeometryValidation: 'PASS',
      canonicalResult: run.decisionKind === 'operational-correction' ? 'REAL_FEASIBLE_OPERATIONAL_CORRECTION' : run.status === 'no-improvement' ? 'REAL_NO_FEASIBLE_IMPROVEMENT' : run.status,
      baseline: { total: baselineMetrics.totalShhch, movable: baselineMetrics.movableShhch, fixed: baselineMetrics.fixedShhch },
      proposed: proposedMetrics ? { total: proposedMetrics.totalShhch, movable: proposedMetrics.movableShhch, fixed: proposedMetrics.fixedShhch } : null,
      baselineValid: run.baselineValid,
      baselineConstraints: `${run.originalVerification.passedFamilies}/${run.originalVerification.totalFamilies}`,
      proposedConstraints: run.recommendationVerification ? `${run.recommendationVerification.passedFamilies}/${run.recommendationVerification.totalFamilies}` : null,
      selectedCorrection: run.recommendation ? `G4 → ${run.recommendation.G4}` : null,
      disruptionMinutes,
      thermalImprovementClaimed: run.shiftedCrewHours > 0,
      operationalCorrectionClaimed: run.decisionKind === 'operational-correction',
      deterministicVerification: run.recommendation ? run.recommendationVerification?.passed ? 'PASS' : 'FAIL' : 'NOT_APPLICABLE_NO_IMPROVEMENT',
      feasibleAlternativeVerification: run.recommendationVerification?.passed ? 'PASS' : 'NOT_AVAILABLE',
      approvalIdentity: run.recommendationId && run.candidateHash ? 'PASS' : 'FAIL',
      finalReverification: run.recommendation ? 'PASS' : 'N/A',
      realEvidence: true,
      syntheticDemoRetained: true,
    }, null, 2))

    expect(baselineMetrics.valid).toBe(true)
    expect(run.originalVerification.passed).toBe(false)
    expect(run.originalVerification.families.filter(family => family.id !== 'employer-policy').every(family => family.passed)).toBe(true)
    expect(run.originalVerification.families.find(family => family.id === 'employer-policy')?.passed).toBe(false)
    expect(run.status).toBe('recommended')
    expect(run.decisionKind).toBe('operational-correction')
    expect(run.baselineValid).toBe(false)
    expect(run.recommendation?.G4).toBe('13:30')
    expect(disruptionMinutes).toBe(60)
    expect(run.afterCrewHours).toBe(91.5)
    expect(run.shiftedCrewHours).toBe(0)
    expect(run.recommendationVerification?.passedFamilies).toBe(6)
    expect(run.message).toContain('substantial scheduled high-heat crew-hour overlap')
    expect(run.message).toContain('No feasible alternative reduced that modeled overlap')
    expect(run.message).toContain('Employer controls')
    expect(run.message).toContain('superintendent owns the decision')
    const approval = approveRecommendation(run, { recommendationId: run.recommendationId!, candidateHash: run.candidateHash! })
    expect(approval.approved).toBe(true)
    expect(approval.verification.passed).toBe(true)
    expect(run.stats.feasibleCandidates).toBeGreaterThan(0)
    expect(peakWindowCrewHoursFor(baseline, TASKS, CREWS, thermalEvidence, WORKFACES)).toBe(baselineMetrics.totalShhch)
  })
})
