import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'
import { approveRecommendation, runCrewClock, type RunOptions, type ThermalEvidence } from '../src/demo/engine'
import { EMPLOYER_POLICY, TASKS, CREWS, WORKFACES } from '../src/demo/scenario'
import { SYNTHETIC_POSITIVE_EVIDENCE, SYNTHETIC_POSITIVE_POLICY } from '../src/demo/runtime'

type Request = {
  action?: 'review' | 'approve'
  scenario?: 'synthetic-positive' | 'canonical-replay' | 'evidence-unavailable' | 'all-indoor'
  tasks?: typeof TASKS
  crews?: typeof CREWS
  recommendationId?: string
  candidateHash?: string
}

type CanonicalManifest = {
  analytic_type: string
  decision_grade_coverage: boolean
  geometry_validation: string
  historical_date: string
  phoenix_timezone: string
  provider_status: string
  result_hashes: Record<string, string>
  thermal_trigger: { threshold_c: number; quantity: string; threshold_units: string; direction: string; provenance: string }
  windows: Array<{ start: string; end: string; path: string; status: string; feature_count: number }>
}

const canonicalDirectory = resolve(process.cwd(), 'evidence', 'fortyguard-canonical-phoenix')
const canonicalManifest = JSON.parse(readFileSync(resolve(canonicalDirectory, 'request_manifest.json'), 'utf8')) as CanonicalManifest
if (canonicalManifest.provider_status !== 'RESOLVED' || !canonicalManifest.decision_grade_coverage || canonicalManifest.geometry_validation !== 'PASS' || canonicalManifest.analytic_type !== 'exceedance') {
  throw new Error('canonical_evidence_manifest_invalid')
}
for (const window of canonicalManifest.windows) {
  const artifactPath = resolve(canonicalDirectory, window.path)
  if (!artifactPath.startsWith(canonicalDirectory) || window.status !== 'COMPLETED' || window.feature_count < 1) throw new Error('canonical_evidence_window_invalid')
  const artifact = JSON.parse(readFileSync(artifactPath, 'utf8')) as { status?: string; local_window?: { start?: string; end?: string; timezone?: string }; request?: { analytic_type?: string } }
  if (artifact.status !== 'COMPLETED' || artifact.local_window?.start !== window.start || artifact.local_window?.end !== window.end || artifact.local_window?.timezone !== canonicalManifest.phoenix_timezone || artifact.request?.analytic_type !== 'exceedance') throw new Error('canonical_evidence_artifact_invalid')
}

const canonicalEvidence: ThermalEvidence = {
  source: 'Saved FortyGuard canonical evidence manifest',
  status: 'CANONICAL_FORTYGUARD',
  exceedanceEvidenceStatus: 'complete',
  forecastStatus: 'HISTORICAL_REPLAY',
  projectThermalTrigger: {
    thresholdC: canonicalManifest.thermal_trigger.threshold_c,
    quantity: canonicalManifest.thermal_trigger.quantity,
    provenance: 'evidence/fortyguard-canonical-phoenix/request_manifest.json',
    thresholdUnits: canonicalManifest.thermal_trigger.threshold_units,
    direction: canonicalManifest.thermal_trigger.direction,
  },
  classification: 'CANONICAL_FORTYGUARD',
  evidenceId: 'phoenix_canonical_2025_07_15',
  location: 'Phoenix, Arizona',
  observationDate: canonicalManifest.historical_date,
  timezone: canonicalManifest.phoenix_timezone,
  analyticType: canonicalManifest.analytic_type,
  geometry: 'Four bound polygon workfaces within the canonical AOI',
  coverage: '06:00–16:00 local in five contiguous two-hour windows',
  exceedanceWindows: canonicalManifest.windows.map(({ start, end }) => ({
    analyticType: 'exceedance' as const,
    start,
    end,
    units: 'hours',
    status: 'VALID' as const,
    provenance: 'LIVE_FORTYGUARD',
    aoi: 'phoenix-canonical-aoi',
    date: canonicalManifest.historical_date,
    timezone: canonicalManifest.phoenix_timezone,
    analyticSource: 'SAVED_CANONICAL_FORTYGUARD',
    projectThermalTrigger: { thresholdC: canonicalManifest.thermal_trigger.threshold_c, quantity: canonicalManifest.thermal_trigger.quantity, thresholdUnits: canonicalManifest.thermal_trigger.threshold_units, direction: canonicalManifest.thermal_trigger.direction },
    resultHash: canonicalManifest.result_hashes[start],
    version: 'canonical-manifest-v1',
    tiles: WORKFACES.map(face => ({ polygon: face.polygon, valueHours: 2 })),
  })),
}

const request = JSON.parse(readFileSync(0, 'utf8')) as Request
const scenario = request.scenario ?? 'evidence-unavailable'
const suppliedTasks = request.tasks ?? TASKS
const tasks = scenario === 'all-indoor'
  ? suppliedTasks.map(task => ({ ...task, environment: 'shaded-support' as const }))
  : suppliedTasks

const options: RunOptions = {
  tasks,
  crews: request.crews ?? CREWS,
  policy: EMPLOYER_POLICY,
  workfaces: WORKFACES,
  projectId: `production-${scenario}`,
}

if (scenario === 'synthetic-positive') {
  options.thermalEvidence = SYNTHETIC_POSITIVE_EVIDENCE
  options.scenarioLabel = 'SYNTHETIC TEST SCENARIO'
  options.policy = SYNTHETIC_POSITIVE_POLICY
} else if (scenario === 'canonical-replay') {
  options.thermalEvidence = canonicalEvidence
  options.scenarioLabel = 'CANONICAL_PHOENIX_REPLAY'
} else {
  options.evidenceState = 'missing'
  options.scenarioLabel = scenario === 'all-indoor' ? 'ALL_INDOOR' : 'USER_DEFINED_SHIFT'
}

const run = runCrewClock(options)
if (request.action === 'approve') {
  const decision = approveRecommendation(run, {
    recommendationId: request.recommendationId ?? '',
    candidateHash: request.candidateHash ?? '',
  })
  process.stdout.write(JSON.stringify({ run, decision }))
} else {
  process.stdout.write(JSON.stringify({ run }))
}
