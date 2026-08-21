import { useState } from 'react'
import { AlertTriangle, ArrowRight, Check, ChevronRight, ClipboardCheck, Clock3, Database, HardHat, LockKeyhole, Play, RotateCcw, ShieldCheck, Users, X } from 'lucide-react'
import { EMPLOYER_POLICY, THERMAL_EVIDENCE, type Task, timelinePosition, timelineWidth } from './demo/scenario'
import { type CrewClockRun, type Schedule } from './demo/engine'
import { approveRuntimeSession, createRuntimeSession, emptyRuntimeSession, recheckRuntimeSession, runtimeOptionsForMode, type RuntimeSession } from './demo/runtime'

type PlanView = 'original' | 'proposed'
type DrawerView = 'evidence' | 'audit' | null
type DecisionView = 'undecided' | 'current'
type StageKey = 'inspect' | 'select' | 'evidence' | 'alternatives' | 'verify'

const stageDefinitions: Array<{ key: StageKey; label: string; statuses: string[] }> = [
  { key: 'inspect', label: 'Shift inspected', statuses: ['SHIFT_INSPECTION_STARTED', 'SHIFT_INSPECTION_COMPLETED'] },
  { key: 'select', label: 'Flexible outdoor work identified', statuses: ['THERMAL_INVESTIGATION_REQUIRED'] },
  { key: 'evidence', label: 'Workface evidence checked', statuses: ['THERMAL_EVIDENCE_REQUESTED', 'THERMAL_EVIDENCE_READY', 'THERMAL_EVIDENCE_UNAVAILABLE'] },
  { key: 'alternatives', label: 'Alternatives tested', statuses: ['OPTIMIZATION_STARTED', 'CANDIDATES_GENERATED', 'NO_FEASIBLE_IMPROVEMENT'] },
  { key: 'verify', label: 'Constraints verified', statuses: ['VERIFICATION_STARTED', 'VERIFICATION_PASSED', 'VERIFICATION_FAILED'] },
]

function formatCrewHours(value: number | null) { return value === null ? '—' : `${value}h` }
const getRunOptions = () => runtimeOptionsForMode(new URLSearchParams(window.location.search).get('mode'))

function SourceTag({ children, tone = 'lime' }: { children: React.ReactNode; tone?: 'lime' | 'orange' | 'blue' | 'gray' }) {
  return <span className={`source-tag ${tone}`}>{children}</span>
}

function getStageState(stage: typeof stageDefinitions[number], events: RuntimeSession['events']) {
  const matching = events.filter(event => stage.statuses.includes(event.status))
  const terminalFailure = matching.some(event => ['THERMAL_EVIDENCE_UNAVAILABLE', 'NO_FEASIBLE_IMPROVEMENT', 'VERIFICATION_FAILED'].includes(event.status))
  return { matching, state: matching.length ? terminalFailure ? 'attention' : 'complete' as const : 'pending' as const }
}

function WorkflowRail({ events }: { events: RuntimeSession['events'] }) {
  return <section className="workflow-rail" aria-label="CrewClock review progress">
    <div className="section-kicker"><span>LIVE REVIEW</span><span>{events.length ? `${events.length} runtime events` : 'Ready when you are'}</span></div>
    <div className="workflow-list">
      {stageDefinitions.map(stage => {
        const { matching, state } = getStageState(stage, events)
        const latest = matching.at(-1)
        return <div key={stage.key} className={`workflow-step ${state}`}>
          <span className="workflow-mark">{state === 'complete' ? <Check size={13}/> : state === 'attention' ? <AlertTriangle size={12}/> : <i/>}</span>
          <div><strong>{stage.label}</strong><small>{latest?.summary ?? (stage.key === 'evidence' ? 'Decision-grade thermal evidence boundary' : 'Not started')}</small></div>
        </div>
      })}
    </div>
  </section>
}

function TaskBlock({ task, schedule, original, showMove }: { task: Task; schedule: Schedule; original: Schedule; showMove: boolean }) {
  const start = schedule[task.id]
  const moved = start !== original[task.id] && showMove
  return <div className={`task-block ${task.environment} ${task.fixed ? 'fixed' : ''} ${moved ? 'moved' : ''}`} style={{ left: `${timelinePosition(start)}%`, width: `${timelineWidth(task.durationMinutes)}%` }} title={`${task.id} · ${task.name} · ${start} · ${task.durationMinutes} minutes`}>
    {task.fixed && <LockKeyhole size={11}/>}<span><b>{task.id}</b> {task.name}</span><small>{start} · {task.zoneId}</small>
  </div>
}

function ScheduleBoard({ run, plan, revealed, verified, onPlan }: { run: CrewClockRun; plan: PlanView; revealed: boolean; verified: boolean; onPlan: (plan: PlanView) => void }) {
  const schedule = plan === 'proposed' && run.recommendation ? run.recommendation : run.original
  const changed = run.tasks.filter(task => run.recommendation && run.recommendation[task.id] !== run.original[task.id])
  const showProposed = plan === 'proposed' && revealed && Boolean(run.recommendation)
  return <section className={`schedule-panel ${showProposed ? 'proposed' : ''}`}>
    <div className="schedule-heading">
      <div><SourceTag tone={showProposed ? 'lime' : 'gray'}>{showProposed ? 'PROPOSED SHIFT' : 'CURRENT SHIFT'}</SourceTag><h2>One shift. Every commitment in view.</h2><p>06:00–16:00 · task timing, workface and crew assignments</p></div>
      <div className="plan-switch" role="group" aria-label="Compare current and proposed schedules"><button className={!showProposed ? 'active' : ''} onClick={() => onPlan('original')}>Current <b>{formatCrewHours(run.beforeCrewHours)}</b></button><button disabled={!revealed} className={showProposed ? 'active' : ''} onClick={() => onPlan('proposed')}>Proposed <b>{revealed ? formatCrewHours(run.afterCrewHours) : '—'}</b></button></div>
    </div>
    <div className="timeline-head"><span>06:00</span><span>08:00</span><span>10:00</span><span>12:00</span><span>14:00</span><span>16:00</span></div>
    <div className="schedule-grid">
      <div className="peak-band"><span>11:00–15:00 · CONFIGURED TRIGGER</span></div>
      {run.crews.map(crew => <div className="crew-row" key={crew.id}><div className="crew-label"><i style={{ background: crew.color }}/><span><strong>{crew.name}</strong><small>{crew.trade} · {crew.headcount} people</small></span></div><div className="crew-track">{run.tasks.filter(task => task.crewId === crew.id).map(task => <TaskBlock key={task.id} task={task} schedule={schedule} original={run.original} showMove={revealed}/>)}</div></div>)}
    </div>
    <div className="schedule-key"><span><i className="outdoor"/>Outdoor work</span><span><i className="support"/>Shaded / support</span><span><LockKeyhole size={12}/>Fixed commitment</span><span className={verified ? 'pass' : ''}><Check size={13}/>{verified ? `${run.recommendationVerification?.passedFamilies ?? 0}/${run.recommendationVerification?.totalFamilies ?? 0} hard checks pass` : `${run.tasks.length} tasks in source plan`}</span></div>
    <div className={`change-strip ${revealed ? 'visible' : ''}`}>
      <div><SourceTag tone={showProposed ? 'lime' : 'orange'}>{showProposed ? 'DECISION' : 'WATCHPOINT'}</SourceTag><strong>{revealed ? `${changed.length} task${changed.length === 1 ? '' : 's'} retimed` : 'Outdoor timing needs review'}</strong><small>{showProposed ? 'Fixed work stays fixed. Dependencies remain visible in sequence.' : run.thermalEvidence.exceedanceEvidenceStatus === 'complete' ? 'CrewClock will test flexible work against the configured trigger.' : 'No schedule change is issued without valid schedule-aligned evidence.'}</small></div>
      <div className="change-list">{revealed && changed.map(task => <span key={task.id}><b>{task.id}</b> {run.original[task.id]} <ArrowRight/> {run.recommendation?.[task.id]}</span>)}</div>
    </div>
  </section>
}

function DecisionRail({ session, onRun, onApprove, onRecheck, onAudit, onKeepCurrent }: { session: RuntimeSession; onRun: () => void; onApprove: () => void; onRecheck: () => void; onAudit: () => void; onKeepCurrent: () => void }) {
  const { run, events, approved } = session
  const revealed = run.status === 'recommended' && events.length > 0
  const failure = events.some(event => ['THERMAL_EVIDENCE_UNAVAILABLE', 'NO_FEASIBLE_IMPROVEMENT', 'VERIFICATION_FAILED', 'AI_ANALYSIS_UNAVAILABLE', 'FINAL_VERIFICATION_FAILED'].includes(event.status))
  const lastEvent = events.at(-1)
  const changed = run.tasks.filter(task => run.recommendation && run.recommendation[task.id] !== run.original[task.id])
  const validEvidence = run.thermalEvidence.exceedanceEvidenceStatus === 'complete'
  return <aside className="decision-rail">
    <div className="rail-heading"><div><SourceTag tone={approved ? 'lime' : failure ? 'orange' : revealed ? 'lime' : 'gray'}>{approved ? 'APPROVED · VERIFIED' : failure ? 'NO CHANGE ISSUED' : revealed ? 'DECISION READY' : 'NEXT ACTION'}</SourceTag><h2>{approved ? 'Plan is ready to carry forward.' : revealed ? 'A cooler sequence is ready for your call.' : failure ? 'The current plan stays intact.' : 'Review the upcoming shift.'}</h2></div><span className={`rail-light ${events.length ? 'active' : ''}`}/></div>
    {failure && <div className="rail-alert"><AlertTriangle size={16}/><div><strong>{run.status === 'missing-evidence' || run.status === 'stale-evidence' || run.status === 'tool-failure' ? 'Evidence unavailable' : 'Guardrail engaged'}</strong><p>{lastEvent?.summary ?? run.message}</p></div></div>}
    {!events.length && <div className="next-action"><div className="attention-number">{run.investigation.investigatedTaskIds.length}</div><div><strong>outdoor tasks to inspect</strong><p>{validEvidence ? 'CrewClock will test movable work against the configured 11:00–15:00 trigger.' : 'The source plan overlaps the configured trigger. A plan cannot be issued until valid FortyGuard evidence is available.'}</p></div></div>}
    {revealed && <div className="recommendation-summary"><div className="summary-label">WHAT CHANGED</div><strong>{changed.length} flexible tasks retimed</strong><p>{changed.map(task => `${task.id} ${run.original[task.id]} → ${run.recommendation?.[task.id]}`).join(' · ')}</p><div className="summary-label">WHY</div><p>{validEvidence ? 'Flexible work was moved away from the modeled 11:00–15:00 trigger where the deterministic scheduler found a feasible sequence.' : 'No recommendation was issued without valid evidence.'}</p></div>}
    {revealed && <div className="verification-box"><div className="summary-label">VERIFICATION</div><div className="check-list">{(run.recommendationVerification?.families ?? []).map(family => <span key={family.id} className={family.passed ? 'pass' : 'fail'}><Check size={13}/>{family.label}</span>)}</div><div className="rejected-line"><span>{run.stats.rejectedCandidates} alternatives rejected</span><button onClick={onAudit}>View runtime facts <ChevronRight size={13}/></button></div></div>}
    {approved && <div className="approved-note"><ShieldCheck size={17}/><div><strong>Human approval recorded.</strong><p>The exact verified recommendation passed final verification.</p></div></div>}
    {!events.length && <button id="run-plan" className="primary-action" onClick={onRun}><Play size={15} fill="currentColor"/>Review shift</button>}
    {failure && events.some(event => event.status === 'RECHECK_AVAILABLE') && <button id="recheck-evidence" className="secondary-action" onClick={onRecheck}>Recheck thermal evidence <ChevronRight size={14}/></button>}
    {revealed && !approved && <div className="decision-actions"><button id="approve-plan" className="primary-action" onClick={onApprove}><ShieldCheck size={15}/>Approve plan</button><button className="quiet-action" onClick={onKeepCurrent}>Keep current plan</button></div>}
    {events.length > 0 && <button className="audit-link" onClick={onAudit}><ClipboardCheck size={14}/>Open factual runtime trail <ChevronRight size={14}/></button>}
  </aside>
}

function FixtureControls({ tasks, onToggleFixed }: { tasks: Task[]; onToggleFixed: (id: string) => void }) {
  return <section className="inspector-block fixture-block"><div className="block-header"><div><SourceTag tone="gray">SAMPLE PROJECT INPUT</SourceTag><h3>Fixture controls</h3></div><span>rerun to apply</span></div><p>Lightly edit the demo input, then close this panel and review the shift again. Operational math remains unchanged.</p><div className="fixture-list">{tasks.filter(task => task.environment !== 'shaded-support').map(task => <label key={task.id}><input type="checkbox" checked={task.fixed} onChange={() => onToggleFixed(task.id)}/><span><b>{task.id}</b> {task.name}</span><small>{task.fixed ? 'fixed' : 'movable'}</small></label>)}</div></section>
}

function Inspector({ view, session, tasks, onClose, onToggleFixed }: { view: DrawerView; session: RuntimeSession; tasks: Task[]; onClose: () => void; onToggleFixed: (id: string) => void }) {
  const { run } = session
  const audit = session.events
  const synthetic = run.thermalEvidence.exceedanceEvidenceStatus === 'complete' && run.thermalEvidence.status === 'SYNTHETIC_TEST_SCENARIO'
  return <><div className={`drawer-backdrop ${view ? 'open' : ''}`} onClick={onClose}/><aside className={`inspector ${view ? 'open' : ''}`} aria-hidden={!view}>
    <div className="inspector-head"><div><SourceTag tone={view === 'audit' ? 'gray' : 'lime'}>{view === 'audit' ? 'RUNTIME EVENTS ONLY' : 'EVIDENCE INSPECTOR'}</SourceTag><h2>{view === 'audit' ? 'Factual runtime trail' : 'Why this plan?'}</h2><p>{view === 'audit' ? 'High-level stages emitted by the application. No chain-of-thought is shown.' : 'Technical depth for judges and reviewers; operator decisions stay on the main scene.'}</p></div><button className="plain-icon" onClick={onClose} aria-label="Close inspector"><X/></button></div>
    {view === 'audit' ? <div className="audit-list">{audit.length ? audit.map(event => <article key={event.event_id}><time>{event.timestamp.slice(11, 19)}</time><div><strong>{event.summary}</strong><SourceTag tone={event.source === 'DETERMINISTIC_VERIFIER' ? 'orange' : event.source === 'MOCK_EVIDENCE_PROVIDER' ? 'blue' : 'gray'}>{event.status}</SourceTag></div></article>) : <div className="empty-inspector">Run the shift review to populate the runtime trail.</div>}</div> : <>
      <section className="inspector-block"><SourceTag tone={synthetic ? 'blue' : 'orange'}>{synthetic ? 'SYNTHETIC TEST EVIDENCE' : 'EVIDENCE UNAVAILABLE'}</SourceTag><dl><dt>FortyGuard status</dt><dd>{run.thermalEvidence.status}</dd><dt>AOI</dt><dd>{THERMAL_EVIDENCE.location}</dd><dt>Observation</dt><dd>{THERMAL_EVIDENCE.observationDate} · {THERMAL_EVIDENCE.timezone}</dd><dt>Thermal trigger</dt><dd>{THERMAL_EVIDENCE.projectThermalTrigger.thresholdC}°C modeled temperature · above</dd><dt>Covered intervals</dt><dd>{synthetic ? run.thermalEvidence.exceedanceWindows.map(window => `${window.start}–${window.end}`).join(' · ') : 'Not demonstrated'}</dd><dt>Provenance</dt><dd>{synthetic ? 'Mock evidence provider · synthetic scenario only' : 'No schedule-aligned exceedance windows currently cached'}</dd></dl></section>
      <section className="inspector-block"><SourceTag tone="orange">DERIVED FROM RUN</SourceTag><dl><dt>Workfaces checked</dt><dd>{run.investigation.workfaceIds.join(' · ') || '—'}</dd><dt>Movable outdoor tasks</dt><dd>{run.investigation.investigatedTaskIds.join(', ') || '—'}</dd><dt>Current overlap</dt><dd>{formatCrewHours(run.beforeCrewHours)}</dd><dt>Proposed overlap</dt><dd>{formatCrewHours(run.afterCrewHours)}</dd><dt>Candidates tested</dt><dd>{run.stats.candidatesConsidered}</dd><dt>Rejected alternatives</dt><dd>{run.stats.rejectedCandidates} · reasons only when emitted</dd></dl></section>
      <section className="inspector-block"><SourceTag tone="blue">DETERMINISTIC VERIFIER</SourceTag>{run.recommendationVerification ? <div className="evidence-checks">{run.recommendationVerification.families.map(family => <div key={family.id}><span className={family.passed ? 'pass-dot' : 'fail-dot'}/><strong>{family.label}</strong><small>{family.checks} checks · {family.detail}</small></div>)}</div> : <p>Verification has not produced a recommendation for this run.</p>}</section>
      <section className="inspector-block"><SourceTag tone="blue">EMPLOYER POLICY</SourceTag><strong>{EMPLOYER_POLICY.name}</strong><p>Version {EMPLOYER_POLICY.breakRules[0].version}. {EMPLOYER_POLICY.authorityBoundary}</p><ul>{EMPLOYER_POLICY.planningRules.slice(0, 4).map(rule => <li key={rule}>{rule}</li>)}</ul></section>
      <FixtureControls tasks={tasks} onToggleFixed={onToggleFixed}/>
      <div className="authority-note"><ShieldCheck/><p><strong>Human authority preserved.</strong> CrewClock never self-approves. Current onsite conditions and professional judgment remain with the supervisor.</p></div>
      <div className="cache-paths"><Database/><div><strong>Sanitized local cache · no network calls</strong>{THERMAL_EVIDENCE.cachePaths.map(path => <small key={path}>{path}</small>)}</div></div>
    </>}
  </aside></>
}

export default function App() {
  const initialOptions = getRunOptions()
  const [session, setSession] = useState<RuntimeSession>(() => emptyRuntimeSession(initialOptions))
  const [plan, setPlan] = useState<PlanView>('original')
  const [drawer, setDrawer] = useState<DrawerView>(null)
  const [decision, setDecision] = useState<DecisionView>('undecided')
  const [fixtureTasks, setFixtureTasks] = useState<Task[] | undefined>(() => initialOptions.tasks)
  const run = session.run
  const configuredTasks = fixtureTasks ?? run.tasks
  const revealed = run.status === 'recommended' && session.events.length > 0
  const verified = session.approved
  const investigating = session.events.some(event => event.status === 'THERMAL_INVESTIGATION_REQUIRED' || event.status === 'THERMAL_EVIDENCE_REQUESTED') && !session.events.some(event => ['RUN_COMPLETED', 'AWAITING_APPROVAL', 'APPROVED'].includes(event.status))
  const validEvidence = run.thermalEvidence.exceedanceEvidenceStatus === 'complete'
  const runWithFixture = () => ({ ...initialOptions, tasks: configuredTasks })
  const start = () => { setSession(createRuntimeSession(runWithFixture())); setPlan('proposed'); setDecision('undecided') }
  const approve = () => { setSession(approveRuntimeSession(session)); setPlan('proposed') }
  const recheck = () => { setSession(recheckRuntimeSession(session)); setPlan('original'); setDecision('undecided') }
  const reset = () => { setFixtureTasks(initialOptions.tasks); setSession(emptyRuntimeSession(initialOptions)); setPlan('original'); setDecision('undecided'); setDrawer(null) }
  const toggleFixed = (id: string) => setFixtureTasks(configuredTasks.map(task => task.id === id ? { ...task, fixed: !task.fixed } : task))
  const totalPeople = run.crews.reduce((sum, crew) => sum + crew.headcount, 0)
  const attentionText = validEvidence ? 'Movable outdoor work overlaps the configured 11:00–15:00 trigger. CrewClock can test a safer sequence.' : 'Outdoor work overlaps the configured 11:00–15:00 trigger. Decision-grade FortyGuard evidence is not currently available.'
  return <main className="app-shell" data-state={verified ? 'verified' : revealed ? 'proposed' : investigating ? 'investigating' : 'initial'}>
    <header className="topbar"><div className="brand"><span className="brand-mark"><Clock3 size={16}/></span><span>CREWCLOCK<small>FIELD PLANNING</small></span></div><div className="top-context"><span className="live-dot"/>PHOENIX INDUSTRIAL PROJECT <em>·</em> SAMPLE PROJECT</div><div className="top-actions"><button onClick={() => setDrawer('evidence')}><Database size={14}/>Evidence</button><button onClick={() => setDrawer('audit')}><ClipboardCheck size={14}/>Audit</button><button className="reset-control" onClick={reset}><RotateCcw size={13}/>Reset sample project</button></div></header>
    <section className="shift-context"><div className="context-primary"><SourceTag tone="gray">UPCOMING SHIFT</SourceTag><h1>Phoenix Industrial Project</h1><p>Wed · Jul 16 <span>·</span> 06:00–16:00 <span>·</span> Phoenix, AZ</p></div><div className="context-project"><span>WORK PACKAGE</span><strong>ADOT SR-202 signal package</strong><small>Traffic systems · PHX-SIG-04</small></div><div className="context-metric"><HardHat/><strong>{run.tasks.length}</strong><span>tasks</span></div><div className="context-metric"><Users/><strong>{run.crews.length}</strong><span>crews · {totalPeople} people</span></div><div className={`context-status ${validEvidence ? 'evidence-ready' : ''} ${verified ? 'verified' : ''}`}><span>{verified ? 'APPROVED · VERIFIED' : validEvidence ? 'SYNTHETIC TEST SCENARIO' : 'EVIDENCE UNAVAILABLE'}</span><strong>{verified ? `${run.shiftedCrewHours}h reduced` : validEvidence ? 'Review can produce a plan' : 'No plan issued'}</strong></div></section>
    <section className="scene-intro"><div><span className="eyebrow">SHIFT WATCHPOINT <i/> THERMAL / OPERATIONAL</span><h2>{run.investigation.investigatedTaskIds.length} outdoor tasks need attention</h2><p>{attentionText}</p></div><div className="intro-legend"><span><i className="orange-dot"/>attention</span><span><i className="lime-dot"/>CrewClock action</span><span><LockKeyhole size={12}/>fixed</span></div></section>
    <section className="mission-layout"><div className="mission-main"><WorkflowRail events={session.events}/><ScheduleBoard run={run} plan={plan} revealed={revealed || verified} verified={verified} onPlan={setPlan}/></div><DecisionRail session={session} onRun={start} onApprove={approve} onRecheck={recheck} onAudit={() => setDrawer('audit')} onKeepCurrent={() => { setPlan('original'); setDecision('current') }}/></section>
    {decision === 'current' && <div className="current-plan-note"><Check size={14}/>Current plan selected. No schedule change was issued.</div>}
    <footer className="bottomline"><span><ShieldCheck size={12}/>Planning support ≠ compliance or safety certification</span><span>{session.runId} · runtime event contract</span><span>FortyGuard: {validEvidence ? 'synthetic test scenario only' : 'exceedance windows not demonstrated'} · result: {verified ? 'approved' : run.status === 'recommended' ? 'awaiting approval' : 'fail-closed'}</span></footer>
    <Inspector view={drawer} session={session} tasks={configuredTasks} onClose={() => setDrawer(null)} onToggleFixed={toggleFixed}/>
  </main>
}
