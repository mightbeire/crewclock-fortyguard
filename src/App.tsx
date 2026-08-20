import { useEffect, useMemo, useState } from 'react'
import { ArrowRight, Check, ChevronRight, CirclePause, Database, Layers3, Play, ShieldCheck, Sparkles, ThermometerSun, X } from 'lucide-react'
import { DEMO_SCENARIO } from './demo/scenario'

const cells = Array.from({ length: 56 }, (_, index) => {
  const row = Math.floor(index / 8), col = index % 8
  const x = 40 + col * 78 + (row % 2) * 39, y = 40 + row * 68
  const heat = Math.max(0, Math.min(1, .25 + .48 * Math.sin(index * .74) + col * .055))
  return { x, y, heat, id: index }
})

function ThermalMap({ after }: { after: boolean }) {
  return <div className="map" aria-label="Stylized FortyGuard-compatible thermal grid">
    <svg viewBox="0 0 680 540" role="img">
      <defs><filter id="glow"><feGaussianBlur stdDeviation="10" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter></defs>
      <path className="road" d="M-30 410 C120 340 160 225 300 250 S520 420 730 240" />
      <path className="road fine" d="M120 -20 C180 100 190 310 80 580M480 -30 C420 120 470 290 620 560" />
      {cells.map(c => <polygon key={c.id} points={`${c.x},${c.y-28} ${c.x+25},${c.y-14} ${c.x+25},${c.y+14} ${c.x},${c.y+28} ${c.x-25},${c.y+14} ${c.x-25},${c.y-14}`} fill={`rgba(${Math.round(240+c.heat*15)},${Math.round(167-c.heat*105)},${Math.round(65-c.heat*40)},${after ? .1 + c.heat*.23 : .16 + c.heat*.58})`} />)}
      <circle cx={after ? 174 : 514} cy={after ? 170 : 348} r="10" className="pulse" filter="url(#glow)" />
    </svg>
    <div className="map-label"><span>PHX · 33.45° N</span><span>100 m analysis grid</span></div>
    <div className="legend"><span>thermal intensity</span><i /></div>
  </div>
}

export default function App() {
  const [step, setStep] = useState(-1)
  const [running, setRunning] = useState(false)
  const [approved, setApproved] = useState(false)
  const [evidenceOpen, setEvidenceOpen] = useState(false)
  const finished = step === DEMO_SCENARIO.steps.length - 1
  useEffect(() => {
    if (!running || finished) return
    const timer = setTimeout(() => setStep(s => {
      if (s >= DEMO_SCENARIO.steps.length - 2) setRunning(false)
      return s + 1
    }), 920)
    return () => clearTimeout(timer)
  }, [running, step, finished])
  const progress = useMemo(() => Math.max(0, ((step + 1) / DEMO_SCENARIO.steps.length) * 100), [step])
  const start = () => { setApproved(false); setStep(0); setRunning(true) }
  return <main>
    <header><div className="brand"><span className="mark">40</span><span>FORTYGUARD <small>AGENT STAGE</small></span></div><div className="status"><span className="dot"/> CACHED DEMO · NO API CREDITS</div><button className="icon-button" onClick={() => setEvidenceOpen(true)} aria-label="Open evidence"><Database size={17}/></button></header>
    <section className="hero">
      <div className="eyebrow"><Sparkles size={14}/> REUSABLE OPERATIONS SHELL <span>SCENARIO 01</span></div>
      <h1>Move the work.<br/><em>Beat the heat.</em></h1>
      <p className="lede">An agent turns hyperlocal thermal evidence into a safer-looking, constraint-checked operating plan—then proves the difference.</p>
      <div className="hero-actions"><button className="primary" onClick={start}><Play size={16} fill="currentColor"/>{step < 0 ? 'Run agent demo' : 'Replay sequence'}</button><button className="secondary" onClick={() => setEvidenceOpen(true)}>Inspect evidence <ArrowRight size={15}/></button></div>
      <div className="reading"><ThermometerSun/><div><strong>{DEMO_SCENARIO.measured.maxTemperatureC.toFixed(1)}°</strong><span>cached max °C</span></div><div className="mini-rule"/><div><strong>15.6°</strong><span>site-to-site delta</span></div></div>
    </section>
    <section className="stage">
      <ThermalMap after={finished}/>
      <aside className="agent-panel">
        <div className="panel-head"><div><span className="kicker">AUTONOMOUS RUN</span><h2>{running ? 'Agent is working' : finished ? 'Recommendation ready' : 'Standing by'}</h2></div><span className={`orb ${running ? 'active' : ''}`}><Layers3 size={18}/></span></div>
        <div className="progress"><i style={{width:`${progress}%`}}/></div>
        <ol>{DEMO_SCENARIO.steps.map((s, i) => <li className={i < step ? 'done' : i === step ? 'current' : ''} key={s.label}><span className="step-icon">{i < step ? <Check/> : i === step && running ? <span className="spinner"/> : <span>{String(i+1).padStart(2,'0')}</span>}</span><div><strong>{s.label}</strong><small>{i <= step ? s.detail : s.tool}</small></div></li>)}</ol>
      </aside>
      <div className="metric"><span>{finished ? '−44%' : '—'}</span><div><strong>peak-window exposure</strong><small>scenario-derived · verified after planning</small></div></div>
    </section>
    <section className="comparison">
      <div className="section-title"><span>01 / TRANSFORMATION</span><h2>One plan. Two outcomes.</h2></div>
      <div className="compare-grid">
        <article><span className="flag before">BEFORE</span><h3>168 minutes</h3><p>Flexible work overlaps the hottest modeled window. The map is evidence, but nobody turns it into a plan.</p><div className="timeline hot"><i/><i/><i/><i/><i/></div></article>
        <div className="swap"><ChevronRight/></div>
        <article className={finished ? 'revealed' : ''}><span className="flag after">AFTER</span><h3>{finished ? '94 minutes' : 'Run agent'}</h3><p>Three movable tasks shift earlier while crew, deadline and approval constraints stay intact.</p><div className="timeline cool"><i/><i/><i/><i/><i/></div></article>
      </div>
      <div className="approval"><div><ShieldCheck/><span><strong>Human control stays in the loop</strong><small>Recommendation only · no external action executed</small></span></div><button disabled={!finished || approved} onClick={() => setApproved(true)}>{approved ? <><Check/> Approved</> : <><CirclePause/> Approve recommendation</>}</button></div>
    </section>
    <footer><span>FORTYGUARD HACKATHON ’26</span><span>Measured evidence ≠ derived scenario</span><span>btn operations</span></footer>
    <div className={`drawer-backdrop ${evidenceOpen ? 'open' : ''}`} onClick={() => setEvidenceOpen(false)}/>
    <aside className={`drawer ${evidenceOpen ? 'open' : ''}`}><div className="drawer-head"><div><span className="kicker">AUDITABLE EVIDENCE</span><h2>What is real?</h2></div><button className="icon-button" onClick={() => setEvidenceOpen(false)}><X/></button></div>
      <div className="evidence-block"><span>MEASURED · CACHED-LIVE</span><dl><dt>Max temperature</dt><dd>40.1505 °C</dd><dt>Average</dt><dd>37.0796 °C</dd><dt>Observation date</dt><dd>2025-07-15</dd><dt>Source</dt><dd>/v1/heatmap</dd><dt>Status</dt><dd><b>CACHED</b></dd></dl></div>
      <div className="evidence-block"><span>DERIVED · DEMO SCENARIO</span><dl><dt>Before</dt><dd>168 min</dd><dt>After</dt><dd>94 min</dd><dt>Avoided</dt><dd>74 min / 44%</dd></dl></div>
      <div className="evidence-block"><span>ASSUMPTIONS</span><ul>{DEMO_SCENARIO.assumptions.map(a => <li key={a}>{a}</li>)}</ul></div>
      <div className="provenance"><Database/><div><strong>Sanitized cache</strong><small>{DEMO_SCENARIO.measured.cachePath}</small></div></div>
    </aside>
  </main>
}
