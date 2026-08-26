import type { CrewClockRun } from './engine'

export type TerminalNoChangeCopy = {
  heading: string
  detail: string
}

export const terminalNoChangeCopy = (
  run: Pick<CrewClockRun, 'baselineValid' | 'beforeCrewHours' | 'message'>,
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

  if (run.beforeCrewHours !== null && run.beforeCrewHours > 0) {
    return {
      heading: 'No feasible thermal improvement found.',
      detail: 'The valid current shift remains the operational plan.',
    }
  }

  return {
    heading: 'Thermal investigation was unnecessary.',
    detail: 'No relevant movable outdoor work was found. The current plan remains.',
  }
}
