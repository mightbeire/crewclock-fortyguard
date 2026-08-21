export type Polygon = Array<[number, number]>
export type ExceedanceTile = { polygon: Polygon; valueHours: number }
export type ProjectThermalTrigger = { thresholdC: number; quantity: 'fortyguard_modeled_temperature' | 'fortyguard_tcm_temperature'; provenance: string; thresholdUnits: 'celsius'; direction: 'above' }
export type ExceedanceWindow = {
  analyticType: 'exceedance'; start: string; end: string; units: 'hour' | 'hours'; status: 'VALID' | 'STALE' | 'INVALID' | 'NOT_DEMONSTRATED'; provenance: string
  aoi: string; date: string; timezone: string; analyticSource: string
  projectThermalTrigger: { thresholdC: number; quantity: ProjectThermalTrigger['quantity']; thresholdUnits: 'celsius'; direction: 'above' }
  resultHash: string; version: string; qualifying?: boolean; tiles: ExceedanceTile[]
}
export type ShhchTaskContribution = { taskId: string; workfaceId: string; overlappingExceedanceHours: number; crewHours: number; provenance: string[]; fixed: boolean }
export type ShhchResult = { status: 'SHHCH_READY' | 'EVIDENCE_UNAVAILABLE' | 'ERROR_SAFE'; valid: boolean; totalCrewHours: number | null; movableCrewHours: number | null; fixedCrewHours: number | null; contributions: ShhchTaskContribution[]; errors: string[]; provenance: string[] }

const polygonArea = (polygon: Polygon) => Math.abs(polygon.reduce((sum, point, index) => { const next = polygon[(index + 1) % polygon.length]; return sum + point[0] * next[1] - next[0] * point[1] }, 0) / 2)
const intersectionArea = (subject: Polygon, clipper: Polygon) => {
  if (subject.length < 3 || clipper.length < 3) return 0
  const signed = clipper.reduce((sum, point, index) => { const next = clipper[(index + 1) % clipper.length]; return sum + point[0] * next[1] - next[0] * point[1] }, 0)
  const sign = signed >= 0 ? 1 : -1; let result = subject
  for (let index = 0; index < clipper.length && result.length; index += 1) {
    const a = clipper[index]; const b = clipper[(index + 1) % clipper.length]
    const cross = (point: [number, number]) => (b[0] - a[0]) * (point[1] - a[1]) - (b[1] - a[1]) * (point[0] - a[0])
    const inside = (point: [number, number]) => sign * cross(point) >= -1e-9; const nextResult: Polygon = []
    result.forEach((current, currentIndex) => { const following = result[(currentIndex + 1) % result.length]; const ci = inside(current); const fi = inside(following); const intersection = () => { const c = cross(current); const f = cross(following); const ratio = c === f ? 0 : c / (c - f); return [current[0] + (following[0] - current[0]) * ratio, current[1] + (following[1] - current[1]) * ratio] as [number, number] }; if (ci && fi) nextResult.push(following); else if (ci && !fi) nextResult.push(intersection()); else if (!ci && fi) nextResult.push(intersection(), following) })
    result = nextResult
  }
  return result.length ? polygonArea(result) : 0
}
const weightedTileHours = (workface: Polygon, tiles: ExceedanceTile[]) => { const totalArea = tiles.reduce((sum, tile) => sum + intersectionArea(workface, tile.polygon), 0); if (totalArea <= 0) throw new Error('workface_does_not_overlap_exceedance_tiles'); return tiles.reduce((sum, tile) => sum + intersectionArea(workface, tile.polygon) * tile.valueHours, 0) / totalArea }
const minutes = (value: string) => { const [hour, minute] = value.split(':').map(Number); return hour * 60 + minute }

export const calculateScheduledHighHeatCrewHours = (schedule: Record<string, string>, tasks: ReadonlyArray<{ id: string; durationMinutes: number; crewId: string; zoneId: string; environment: string; fixed: boolean }>, crews: ReadonlyArray<{ id: string; headcount: number }>, workfaces: ReadonlyArray<{ id: string; polygon: Polygon }>, windows: ReadonlyArray<ExceedanceWindow>, trigger: ProjectThermalTrigger): ShhchResult => {
  if (!Number.isFinite(trigger.thresholdC) || !trigger.provenance || trigger.thresholdUnits !== 'celsius' || trigger.direction !== 'above' || (trigger.quantity as string).includes('heat_index')) return { status: 'ERROR_SAFE', valid: false, totalCrewHours: null, movableCrewHours: null, fixedCrewHours: null, contributions: [], errors: ['unsupported_project_thermal_trigger'], provenance: [] }
  if (!windows.length) return { status: 'EVIDENCE_UNAVAILABLE', valid: false, totalCrewHours: null, movableCrewHours: null, fixedCrewHours: null, contributions: [], errors: ['schedule_aligned_exceedance_windows_required'], provenance: ['FORTYGUARD_EXCEEDANCE'] }
  const faces = new Map(workfaces.map(face => [face.id, face])); const errors: string[] = []; const contributions: ShhchTaskContribution[] = []; let total = 0; let movable = 0; let fixed = 0
  tasks.filter(task => task.environment !== 'shaded-support').forEach(task => {
    const face = faces.get(task.zoneId); const crew = crews.find(item => item.id === task.crewId); const start = schedule[task.id]
    if (!face) { errors.push(`missing_workface:${task.id}`); return }; if (!crew || !start) { errors.push(`missing_task_schedule:${task.id}`); return }
    const taskStart = minutes(start); const taskEnd = taskStart + task.durationMinutes; const boundaries = new Set([taskStart, taskEnd])
    windows.forEach(window => { boundaries.add(Math.max(taskStart, minutes(window.start))); boundaries.add(Math.min(taskEnd, minutes(window.end))) })
    const points = [...boundaries].filter(point => point >= taskStart && point <= taskEnd).sort((a, b) => a - b)
    const provenance = new Set<string>(); let exceedance = 0; let invalidWindow = false
    windows.forEach(window => { if (window.analyticType !== 'exceedance' || !['hour', 'hours'].includes(window.units) || window.status !== 'VALID' || !window.provenance || !window.aoi || !window.date || !window.timezone || !window.analyticSource || !window.resultHash || !window.version || window.projectThermalTrigger.thresholdC !== trigger.thresholdC || window.projectThermalTrigger.quantity !== trigger.quantity || window.projectThermalTrigger.thresholdUnits !== trigger.thresholdUnits || window.projectThermalTrigger.direction !== trigger.direction) invalidWindow = true })
    if (invalidWindow) { errors.push(`invalid_exceedance_window:${task.id}`); return }
    if (points.slice(0, -1).some((left, index) => points[index + 1] > left && !windows.some(window => minutes(window.start) <= left && points[index + 1] <= minutes(window.end)))) { errors.push(`uncovered_task_interval:${task.id}`); return }
    points.slice(0, -1).forEach((left, index) => { const right = points[index + 1]; const covering = windows.filter(window => minutes(window.start) <= left && right <= minutes(window.end)); if (!covering.length) return; const rates = covering.map(window => ({ rate: window.qualifying === false ? 0 : Math.max(0, Math.min(1, weightedTileHours(face.polygon, window.tiles) / ((minutes(window.end) - minutes(window.start)) / 60))), provenance: window.provenance })); const selected = rates.reduce((best, item) => item.rate > best.rate ? item : best, { rate: 0, provenance: '' }); exceedance += (right - left) / 60 * selected.rate; rates.forEach(item => provenance.add(item.provenance)) })
    const crewHours = Number((exceedance * crew.headcount).toFixed(6)); total += crewHours; if (task.fixed) fixed += crewHours; else movable += crewHours; contributions.push({ taskId: task.id, workfaceId: face.id, overlappingExceedanceHours: Number(exceedance.toFixed(6)), crewHours, provenance: [...provenance], fixed: task.fixed })
  })
  if (errors.length) return { status: 'EVIDENCE_UNAVAILABLE', valid: false, totalCrewHours: null, movableCrewHours: null, fixedCrewHours: null, contributions: [], errors, provenance: ['FORTYGUARD_EXCEEDANCE', trigger.provenance] }
  return { status: 'SHHCH_READY', valid: true, totalCrewHours: Number(total.toFixed(6)), movableCrewHours: Number(movable.toFixed(6)), fixedCrewHours: Number(fixed.toFixed(6)), contributions, errors: [], provenance: ['FORTYGUARD_EXCEEDANCE', trigger.provenance] }
}
