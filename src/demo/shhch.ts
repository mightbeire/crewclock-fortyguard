export type Polygon = Array<[number, number]>

export type ExceedanceTile = {
  polygon: Polygon
  valueHours: number
}

export type ExceedanceWindow = {
  analyticType: 'exceedance'
  start: string
  end: string
  units: 'hour' | 'hours'
  status: 'VALID' | 'STALE' | 'INVALID' | 'NOT_DEMONSTRATED'
  provenance: string
  tiles: ExceedanceTile[]
}

export type ProjectThermalTrigger = {
  thresholdC: number
  quantity: 'fortyguard_modeled_temperature' | 'fortyguard_tcm_temperature'
  provenance: string
}

export type ShhchTaskContribution = {
  taskId: string
  workfaceId: string
  overlappingExceedanceHours: number
  crewHours: number
  provenance: string[]
}

export type ShhchResult = {
  status: 'SHHCH_READY' | 'EVIDENCE_UNAVAILABLE' | 'ERROR_SAFE'
  valid: boolean
  totalCrewHours: number | null
  contributions: ShhchTaskContribution[]
  errors: string[]
  provenance: string[]
}

const polygonArea = (polygon: Polygon) => Math.abs(polygon.reduce((sum, point, index) => {
  const next = polygon[(index + 1) % polygon.length]
  return sum + point[0] * next[1] - next[0] * point[1]
}, 0) / 2)

const intersectionArea = (subject: Polygon, clipper: Polygon) => {
  if (subject.length < 3 || clipper.length < 3) return 0
  const signed = clipper.reduce((sum, point, index) => {
    const next = clipper[(index + 1) % clipper.length]
    return sum + point[0] * next[1] - next[0] * point[1]
  }, 0)
  const sign = signed >= 0 ? 1 : -1
  let result = subject
  for (let index = 0; index < clipper.length && result.length; index += 1) {
    const a = clipper[index]
    const b = clipper[(index + 1) % clipper.length]
    const cross = (point: [number, number]) => (b[0] - a[0]) * (point[1] - a[1]) - (b[1] - a[1]) * (point[0] - a[0])
    const inside = (point: [number, number]) => sign * cross(point) >= -1e-9
    const nextResult: Polygon = []
    result.forEach((current, currentIndex) => {
      const following = result[(currentIndex + 1) % result.length]
      const currentInside = inside(current)
      const followingInside = inside(following)
      const intersection = () => {
        const c = cross(current)
        const f = cross(following)
        const ratio = c === f ? 0 : c / (c - f)
        return [current[0] + (following[0] - current[0]) * ratio, current[1] + (following[1] - current[1]) * ratio] as [number, number]
      }
      if (currentInside && followingInside) nextResult.push(following)
      else if (currentInside && !followingInside) nextResult.push(intersection())
      else if (!currentInside && followingInside) nextResult.push(intersection(), following)
    })
    result = nextResult
  }
  return result.length ? polygonArea(result) : 0
}

const weightedTileHours = (workface: Polygon, tiles: ExceedanceTile[]) => {
  const totalArea = tiles.reduce((sum, tile) => sum + intersectionArea(workface, tile.polygon), 0)
  if (totalArea <= 0) throw new Error('workface_does_not_overlap_exceedance_tiles')
  return tiles.reduce((sum, tile) => sum + intersectionArea(workface, tile.polygon) * tile.valueHours, 0) / totalArea
}

const minutes = (value: string) => {
  const [hour, minute] = value.split(':').map(Number)
  return hour * 60 + minute
}

const overlapHours = (taskStart: number, taskEnd: number, windowStart: number, windowEnd: number) =>
  Math.max(0, Math.min(taskEnd, windowEnd) - Math.max(taskStart, windowStart)) / 60

export const calculateScheduledHighHeatCrewHours = (
  schedule: Record<string, string>,
  tasks: ReadonlyArray<{ id: string; durationMinutes: number; crewId: string; zoneId: string; environment: string; fixed: boolean }>,
  crews: ReadonlyArray<{ id: string; headcount: number }>,
  workfaces: ReadonlyArray<{ id: string; polygon: Polygon }>,
  windows: ReadonlyArray<ExceedanceWindow>,
  trigger: ProjectThermalTrigger,
): ShhchResult => {
  if (!Number.isFinite(trigger.thresholdC) || !trigger.provenance || (trigger.quantity as string).includes('heat_index')) {
    return { status: 'ERROR_SAFE', valid: false, totalCrewHours: null, contributions: [], errors: ['unsupported_project_thermal_trigger'], provenance: [] }
  }
  if (!windows.length) {
    return { status: 'EVIDENCE_UNAVAILABLE', valid: false, totalCrewHours: null, contributions: [], errors: ['schedule_aligned_exceedance_windows_required'], provenance: ['FORTYGUARD_EXCEEDANCE'] }
  }
  const faces = new Map(workfaces.map(face => [face.id, face]))
  const contributions: ShhchTaskContribution[] = []
  const errors: string[] = []
  let total = 0
  tasks.filter(task => task.environment !== 'shaded-support').forEach(task => {
    const face = faces.get(task.zoneId)
    const crew = crews.find(item => item.id === task.crewId)
    const start = schedule[task.id]
    if (!face) { errors.push(`missing_workface:${task.id}`); return }
    if (!crew || !start) { errors.push(`missing_task_schedule:${task.id}`); return }
    const taskStart = minutes(start)
    const taskEnd = taskStart + task.durationMinutes
    let exceedance = 0
    const provenance = new Set<string>()
    windows.forEach(window => {
      if (window.analyticType !== 'exceedance' || window.units !== 'hour' && window.units !== 'hours' || window.status !== 'VALID' || !window.provenance) {
        errors.push(`invalid_exceedance_window:${task.id}`); return
      }
      const windowStart = minutes(window.start)
      const windowEnd = minutes(window.end)
      const overlap = overlapHours(taskStart, taskEnd, windowStart, windowEnd)
      if (overlap <= 0) return
      try {
        exceedance += weightedTileHours(face.polygon, window.tiles) * (overlap / ((windowEnd - windowStart) / 60))
        provenance.add(window.provenance)
      } catch (error) { errors.push(`${task.id}:${error instanceof Error ? error.message : 'invalid_exceedance_geometry'}`) }
    })
    if (!provenance.size) errors.push(`uncovered_task_interval:${task.id}`)
    const crewHours = exceedance * crew.headcount
    total += crewHours
    contributions.push({ taskId: task.id, workfaceId: face.id, overlappingExceedanceHours: Number(exceedance.toFixed(6)), crewHours: Number(crewHours.toFixed(6)), provenance: [...provenance] })
  })
  if (errors.length) return { status: 'EVIDENCE_UNAVAILABLE', valid: false, totalCrewHours: null, contributions: [], errors, provenance: ['FORTYGUARD_EXCEEDANCE', trigger.provenance] }
  return { status: 'SHHCH_READY', valid: true, totalCrewHours: Number(total.toFixed(6)), contributions, errors: [], provenance: ['FORTYGUARD_EXCEEDANCE', trigger.provenance] }
}
