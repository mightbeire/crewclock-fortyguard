import { useEffect, useMemo, useState } from 'react'
import {
  ArrowRight,
  Check,
  CirclePause,
  ClipboardCheck,
  Clock3,
  Database,
  HardHat,
  Layers3,
  LockKeyhole,
  MapPin,
  Play,
  RotateCcw,
  ShieldCheck,
  Sparkles,
  ThermometerSun,
  Users,
  X,
} from 'lucide-react'
import {
  AGENT_STEPS,
  CREWS,
  EMPLOYER_POLICY,
  HERO_METRIC,
  TASKS,
  THERMAL_EVIDENCE,
  Task,
  timelinePosition,
  timelineWidth,
} from './demo/scenario'

type PlanView = 'original' | 'proposed'
const PROPOSAL_STEP = 5
const VERIFY_STEP = 6

function ThermalProfile() {
  const values = THERMAL_EVIDENCE.apparentTemperatureC.slice(5, 17)
  const min = 27
  const max = 44
  const points = values.map((value, index) => `${index / (values.length - 1) * 100},${52 - (value - min) / (max - min) * 43}`).join(' ')
  return <section className="thermal-card">
    <div className="card-heading">
      <div><span className="kicker">CACHED-LIVE EVIDENCE</span><h3>Modeled thermal timing</h3></div>
      <div className="peak-tag"><ThermometerSun size={14}/><strong>42.5°C</strong><span>apparent · 13:00</span></div>
    </div>
    <div className="thermal-chart">
      <div className="peak-window"><span>11:00–15:00 INVESTIGATED WINDOW</span></div>
      <svg viewBox="0 0 100 58" preserveAspectRatio="none" aria-label="Cached hourly apparent temperature profile">
        <defs><linearGradient id="area" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stopColor="#ff844d" stopOpacity=".42"/><stop offset="1" stopColor="#ff844d" stopOpacity="0"/></linearGradient></defs>
        <polygon points={`0,56 ${points} 100,56`} fill="url(#area)"/>
        <polyline points={points} fill="none" stroke="#ff9d57" strokeWidth="1.4" vectorEffect="non-scaling-stroke"/>
      </svg>
      <div className="chart-axis"><span>05:00</span><span>08:00</span><span>11:00</span><span>14:00</span><span>16:00</span></div>
    </div>
    <p>Historical replay for 15 Jul 2025. Planning evidence only—onsite WBGT and the employer’s heat plan remain authoritative.</p>
  </section>
}

function SiteMap() {
  return <section className="site-card">
    <div className="card-heading"><div><span className="kicker">PHOENIX WORK PACKAGE</span><h3>Two workfaces, one laydown</h3></div><MapPin size={18}/></div>
    <div className="site-map">
      <svg viewBox="0 0 520 220" role="img" aria-label="Illustrative Phoenix construction work zones">
        <defs><radialGradient id="heatA"><stop stopColor="#ff7048" stopOpacity=".72"/><stop offset="1" stopColor="#ff7048" stopOpacity="0"/></radialGradient><pattern id="grid" width="22" height="22" patternUnits="userSpaceOnUse"><path d="M22 0H0V22" fill="none" stroke="#4d514b" strokeWidth=".5"/></pattern></defs>
        <rect width="520" height="220" fill="url(#grid)" opacity=".55"/>
        <circle cx="280" cy="110" r="150" fill="url(#heatA)"/>
        <path className="map-road" d="M-10 172 C105 132 188 146 275 101 S420 58 540 38"/>
        <path className="map-road thin" d="M94 -10 L152 230M400 -10 L342 230"/>
        <g className="map-zone north"><rect x="120" y="48" width="145" height="66" rx="5"/><text x="136" y="72">NORTH WORKFACE</text><text x="136" y="94">GROUNDWORKS</text></g>
        <g className="map-zone south"><rect x="290" y="105" width="150" height="68" rx="5"/><text x="306" y="130">SOUTH WORKFACE</text><text x="306" y="151">CONCRETE · SIGNAL</text></g>
        <g className="map-zone laydown"><rect x="50" y="144" width="112" height="49" rx="5"/><text x="64" y="165">LAYDOWN</text><text x="64" y="181">SHADE · SERVICE</text></g>
      </svg>
      <span className="map-boundary">Zone geometry is synthetic · thermal evidence is cached-live</span>
    </div>
  </section>
}

function TaskBlock({ task, plan }: { task: Task; plan: PlanView }) {
  const start = plan === 'original' ? task.originalStart : task.proposedStart
  const changed = task.originalStart !== task.proposedStart
  return <div
    className={`task ${task.environment} ${task.fixed ? 'fixed' : ''} ${changed ? 'changed' : ''}`}
    style={{ left: `${timelinePosition(start)}%`, width: `${timelineWidth(task.durationMinutes)}%` }}
    title={`${task.id} · ${task.name} · ${start} · ${task.durationMinutes} min`}
  >
    {task.fixed && <LockKeyhole size={10}/>}<span>{task.name}</span><small>{start}</small>
  </div>
}

function ScheduleBoard({ plan, verified, onPlanChange }: { plan: PlanView; verified: boolean; onPlanChange: (plan: PlanView) => void }) {
  return <section className={`schedule-card plan-${plan}`}>
    <div className="schedule-head">
      <div><span className="kicker">TOMORROW · TUESDAY 15 JUL</span><h2>{plan === 'original' ? 'Original field plan' : 'CrewClock proposal'}</h2></div>
      <div className="plan-toggle" role="group" aria-label="Schedule comparison">
        <button className={plan === 'original' ? 'active' : ''} onClick={() => onPlanChange('original')}>Before <b>22h</b></button>
        <button className={plan === 'proposed' ? 'active' : ''} onClick={() => onPlanChange('proposed')}>Proposed <b>6h</b></button>
      </div>
    </div>
    <div className="timeline-header"><span>05:30</span><span>08:00</span><span>11:00</span><span>13:00</span><span>15:00</span></div>
    <div className="schedule-grid">
      <div className="high-window-band"><span>MODELED PEAK WINDOW</span></div>
      {CREWS.map(crew => <div className="crew-row" key={crew.id}>
        <div className="crew-label"><i style={{ background: crew.color }}/><span><strong>{crew.name}</strong><small>{crew.trade} · {crew.headcount}</small></span></div>
        <div className="crew-track">
          {TASKS.filter(task => task.crewId === crew.id).map(task => <TaskBlock key={task.id} task={task} plan={plan}/>)}
        </div>
      </div>)}
    </div>
    <div className="schedule-legend">
      <span><i className="heavy"/> Outdoor moderate/heavy</span><span><i className="support"/> Shaded/support</span><span><LockKeyhole size={11}/> Fixed commitment</span><span className={verified ? 'verified' : ''}><Check size={12}/> 14/14 tasks retained</span>
    </div>
  </section>
}

function AgentPanel({ step, running, approved, onStart, onApprove }: { step: number; running: boolean; approved: boolean; onStart: () => void; onApprove: () => void }) {
  const proposed = step >= PROPOSAL_STEP
  const verified = step === VERIFY_STEP
  const progress = Math.max(0, (step + 1) / AGENT_STEPS.length * 100)
  return <aside className="agent-card">
    <div className="agent-head"><div><span className="kicker">AGENT RUN · CC-0715</span><h2>{running ? 'CrewClock is working' : verified ? 'Plan verified' : proposed ? 'Decision required' : 'Ready to investigate'}</h2></div><span className={`agent-orb ${running ? 'active' : ''}`}><Layers3 size={18}/></span></div>
    <div className="agent-progress"><i style={{ width: `${progress}%` }}/></div>
    <ol>{AGENT_STEPS.map((item, index) => <li key={item.label} className={index < step ? 'done' : index === step ? 'current' : ''}>
      <span className="step-icon">{index < step ? <Check/> : index === step && running ? <span className="spinner"/> : String(index + 1).padStart(2, '0')}</span>
      <div><strong>{item.label}</strong><small>{index <= step ? item.detail : item.tool}</small></div>
    </li>)}</ol>
    {!proposed && <button className="primary run-button" onClick={onStart}><Play size={15} fill="currentColor"/>{step < 0 ? 'Run tomorrow’s plan' : 'Replay investigation'}</button>}
    {proposed && !verified && <div className="approval-callout"><ShieldCheck/><div><strong>Feasible plan ready</strong><small>Superintendent retains decision authority.</small></div><button onClick={onApprove} disabled={approved}>{approved ? <><Check/> Approved</> : <><CirclePause/> Approve plan</>}</button></div>}
    {verified && <div className="verified-callout"><Check/><div><strong>Approved result recomputed</strong><small>No external schedule was changed.</small></div></div>}
  </aside>
}

export default function App() {
  const [step, setStep] = useState(-1)
  const [running, setRunning] = useState(false)
  const [approved, setApproved] = useState(false)
  const [planView, setPlanView] = useState<PlanView>('original')
  const [evidenceOpen, setEvidenceOpen] = useState(false)
  const proposed = step >= PROPOSAL_STEP
  const verified = step === VERIFY_STEP

  useEffect(() => {
    if (!running || step >= PROPOSAL_STEP) return
    const timer = window.setTimeout(() => {
      const nextStep = step + 1
      setStep(nextStep)
      if (nextStep === PROPOSAL_STEP) {
        setRunning(false)
        setPlanView('proposed')
      }
    }, 950)
    return () => window.clearTimeout(timer)
  }, [running, step])

  const status = useMemo(() => verified ? 'VERIFIED' : proposed ? 'AWAITING APPROVAL' : running ? 'INVESTIGATING' : 'READY', [verified, proposed, running])
  const start = () => { setStep(0); setRunning(true); setApproved(false); setPlanView('original') }
  const approve = () => { setApproved(true); window.setTimeout(() => { setStep(VERIFY_STEP); setPlanView('proposed') }, 700) }
  const reset = () => { setStep(-1); setRunning(false); setApproved(false); setPlanView('original') }

  return <main data-state={verified ? 'verified' : proposed ? 'proposed' : running ? 'investigating' : 'opening'}>
    <header className="topbar">
      <div className="brand"><span className="mark"><Clock3 size={17}/></span><span>CREWCLOCK<small>FIELD PLANNING</small></span></div>
      <nav><button className="active">Tomorrow plan</button><button onClick={() => setEvidenceOpen(true)}>Evidence</button><button onClick={() => setEvidenceOpen(true)}>Decision log</button></nav>
      <div className="cache-status"><span className="dot"/> CACHED · ZERO CREDITS</div>
      <button className="icon-button" onClick={() => setEvidenceOpen(true)} aria-label="Open evidence"><Database size={16}/></button>
    </header>

    <section className="mission-head">
      <div className="mission-copy">
        <span className="eyebrow"><Sparkles size={13}/> MISSION CONTROL FOR TOMORROW’S CONSTRUCTION DAY</span>
        <h1>Keep the day moving.<br/><em>Move the heat.</em></h1>
        <p>Turn tomorrow’s jobs, crews, deadlines, and company heat rules into one workable plan—before the shift starts.</p>
      </div>
      <div className="run-summary">
        <div className="run-id"><span>PHX SIGNAL PACKAGE</span><strong>{status}</strong><small>Historical thermal replay · superintendent review</small></div>
        <div className="headline-metric"><strong>{verified ? HERO_METRIC.moved : '—'}</strong><span>crew-hours moved out of the<br/>highest modeled heat window</span></div>
      </div>
    </section>

    <section className="stat-strip">
      <div><HardHat/><span><strong>14</strong><small>tomorrow tasks</small></span></div>
      <div><Users/><span><strong>3 / 15</strong><small>crews / workers</small></span></div>
      <div><Clock3/><span><strong>11–15</strong><small>investigated window</small></span></div>
      <div><ClipboardCheck/><span><strong>{verified ? '6/6' : '—'}</strong><small>constraint groups pass</small></span></div>
      <div><ThermometerSun/><span><strong>42.5°</strong><small>cached apparent peak °C</small></span></div>
    </section>

    <section className="cockpit">
      <div className="left-rail">
        <ScheduleBoard plan={planView} verified={verified} onPlanChange={setPlanView}/>
        <div className="evidence-row"><ThermalProfile/><SiteMap/></div>
      </div>
      <AgentPanel step={step} running={running} approved={approved} onStart={start} onApprove={approve}/>
    </section>

    <section className={`result-band ${verified ? 'revealed' : ''}`}>
      <div><span className="kicker">VERIFIED TRANSFORMATION</span><h2>Same obligations. Better-timed work.</h2></div>
      <div className="result-numbers"><article><span>BEFORE</span><strong>22</strong><small>modeled peak-window crew-hours</small></article><ArrowRight/><article><span>PROPOSED</span><strong>{proposed ? '6' : '—'}</strong><small>modelled peak-window crew-hours</small></article><article className="hero-result"><span>SHIFTED</span><strong>{verified ? '16' : '—'}</strong><small>derived planning proxy · not a safety outcome</small></article></div>
      <div className="constraint-row"><span>CONSTRAINTS PRESERVED</span>{['14/14 tasks', '3/3 crew qualifications', '11/11 dependencies', '5/5 fixed commitments', '14/14 deadlines', 'policy control passes'].map(item => <div key={item}><Check/> {item}</div>)}</div>
    </section>

    <footer><span>CREWCLOCK · FORTYGUARD HACKATHON ’26</span><span>Planning support ≠ safety certification</span><button onClick={reset}><RotateCcw size={12}/> Reset stage</button></footer>

    <div className={`drawer-backdrop ${evidenceOpen ? 'open' : ''}`} onClick={() => setEvidenceOpen(false)}/>
    <aside className={`drawer ${evidenceOpen ? 'open' : ''}`}>
      <div className="drawer-head"><div><span className="kicker">AUDITABLE INPUTS</span><h2>What is real?</h2></div><button className="icon-button" onClick={() => setEvidenceOpen(false)} aria-label="Close evidence"><X/></button></div>
      <div className="evidence-block real"><span>REAL · CACHED-LIVE FORTYGUARD</span><dl><dt>Location</dt><dd>{THERMAL_EVIDENCE.location}</dd><dt>Date</dt><dd>{THERMAL_EVIDENCE.observationDate}</dd><dt>Maximum TCM</dt><dd>{THERMAL_EVIDENCE.maxTemperatureC} °C</dd><dt>Apparent peak</dt><dd>42.5 °C at 13:00</dd><dt>Time analysis</dt><dd>{THERMAL_EVIDENCE.timeOfMeasureCells} cells · {THERMAL_EVIDENCE.grid}</dd></dl></div>
      <div className="evidence-block derived"><span>DERIVED · DETERMINISTIC</span><dl><dt>Eligible workload</dt><dd>Flexible outdoor moderate/heavy tasks</dd><dt>Original overlap</dt><dd>{HERO_METRIC.before} crew-hours</dd><dt>Proposed overlap</dt><dd>{HERO_METRIC.after} crew-hours</dd><dt>Shifted</dt><dd>{HERO_METRIC.moved} crew-hours</dd></dl></div>
      <div className="evidence-block synthetic"><span>SYNTHETIC · DEMO OPERATIONS</span><p>The 14-task work package, three crews, workface geometry, qualifications, dependencies, deadlines, fixed commitments, and employer policy are realistic scenario data—not a customer record.</p></div>
      <div className="evidence-block policy"><span>EMPLOYER POLICY · NOT FORTYGUARD</span><strong>{EMPLOYER_POLICY.name}</strong><ul>{EMPLOYER_POLICY.planningRules.map(rule => <li key={rule}>{rule}</li>)}</ul></div>
      <div className="authority"><ShieldCheck/><div><strong>Onsite authority remains in control</strong><p>{EMPLOYER_POLICY.authorityBoundary} CrewClock must stop and escalate when required evidence is missing, stale, or conflicting.</p></div></div>
      <div className="provenance"><Database/><div><strong>Sanitized cache only</strong>{THERMAL_EVIDENCE.cachePaths.map(path => <small key={path}>{path}</small>)}</div></div>
    </aside>
  </main>
}
