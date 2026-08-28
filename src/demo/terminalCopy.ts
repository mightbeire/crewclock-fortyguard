import type { CrewClockRun, ThermalEvidence } from './engine'

export type TerminalNoChangeCopy = {
  heading: string
  detail: string
}

const minutes = (value: string) => {
  const [hour, minute] = value.split(':').map(Number)
  return hour * 60 + minute
}

const fullWindowHours = (start: string, end: string) => Math.max(0, (minutes(end) - minutes(start)) / 60)

const windowAppliesToWorkface = (
  window: ThermalEvidence['exceedanceWindows'][number],
  workfaceId: string,
) => {
  const explicitlyScoped = Boolean(window.workface_id) || Boolean(window.workfaceIds?.length)
  if (!explicitlyScoped) return true
  return window.workface_id === workfaceId || Boolean(window.workfaceIds?.includes(workfaceId))
}

const workfaceIsFullyAboveTrigger = (
  windows: ThermalEvidence['exceedanceWindows'],
  workfaceId: string,
  shiftStart: string,
  shiftEnd: string,
) => {
  const start = minutes(shiftStart)
  const end = minutes(shiftEnd)
  if (!Number.isFinite(start) || !Number.isFinite(end) || end <= start) return false

  const relevant = windows
    .filter(window => window.status === 'VALID' && windowAppliesToWorkface(window, workfaceId))
    .filter(window => minutes(window.end) > start && minutes(window.start) < end)

  if (!relevant.length) return false

  const epsilon = 1e-6
  const everyMeasuredWindowIsFullyAboveTrigger = relevant.every(window => {
    const durationHours = fullWindowHours(window.start, window.end)
    return window.qualifying !== false &&
      durationHours > 0 &&
      window.tiles.length > 0 &&
      window.tiles.every(tile => Number.isFinite(tile.valueHours) && tile.valueHours >= durationHours - epsilon)
  })
  if (!everyMeasuredWindowIsFullyAboveTrigger) return false

  const intervals = relevant
    .map(window => [Math.max(start, minutes(window.start)), Math.min(end, minutes(window.end))] as const)
    .filter(([left, right]) => right > left)
    .sort((left, right) => left[0] - right[0])

  if (!intervals.length || intervals[0][0] > start) return false
  let coveredUntil = intervals[0][1]
  for (const [left, right] of intervals.slice(1)) {
    if (left > coveredUntil) return false
    coveredUntil = Math.max(coveredUntil, right)
  }
  return coveredUntil >= end
}

export const fullShiftModeledHighHeat = (
  run: Pick<CrewClockRun, 'status' | 'baselineValid' | 'beforeCrewHours' | 'thermalEvidence' | 'investigation' | 'shiftStart' | 'shiftEnd'>,
) => {
  if (run.status !== 'no-improvement' || !run.baselineValid || run.beforeCrewHours === null || run.beforeCrewHours <= 0) return false
  if (run.thermalEvidence.exceedanceEvidenceStatus !== 'complete') return false
  if (!run.investigation.workfaceIds.length) return false

  return run.investigation.workfaceIds.every(workfaceId =>
    workfaceIsFullyAboveTrigger(run.thermalEvidence.exceedanceWindows, workfaceId, run.shiftStart, run.shiftEnd),
  )
}

export const terminalNoChangeCopy = (
  run: Pick<CrewClockRun, 'status' | 'baselineValid' | 'beforeCrewHours' | 'message' | 'thermalEvidence' | 'investigation' | 'shiftStart' | 'shiftEnd'>,
): TerminalNoChangeCopy => {
  if (!run.baselineValid) {
    return {
      heading: 'A hard operational constraint requires attention.',
      detail: run.message,
    }
  }

  if (run.beforeCrewHours === 0) {
    return {
      heading: 'No thermal schedule change needed.',
      detail: 'The valid current shift has 0 scheduled high-heat crew-hours.',
    }
  }

  if (fullShiftModeledHighHeat(run)) {
    return {
      heading: 'The full measured shift remains above the configured trigger.',
      detail: `FortyGuard evidence shows the configured ${run.thermalEvidence.projectThermalTrigger.thresholdC} °C modeled-temperature trigger across the full measured shift window for the investigated workfaces. Retiming within this shift cannot reduce SHHCH. CrewClock does not make a safety determination. Use the employer heat plan to decide whether to delay, modify, or keep the work.`,
    }
  }

  if (run.beforeCrewHours !== null && run.beforeCrewHours > 0) {
    return {
      heading: 'No lower-SHHCH schedule was found within this shift.',
      detail: 'The current shift remains unchanged. CrewClock is not claiming that the schedule is globally optimal.',
    }
  }

  return {
    heading: 'Thermal investigation was unnecessary.',
    detail: 'No relevant movable outdoor work was found. The current plan remains.',
  }
}
