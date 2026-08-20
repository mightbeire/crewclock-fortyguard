import { useEffect, useMemo, useState } from 'react'
import { ArrowRight, Check, ChevronRight, CirclePause, Database, Layers3, Play, ShieldCheck, Sparkles, ThermometerSun, X } from 'lucide-react'
import { DEMO_IDS, DemoId, DemoScenario, MEASURED_EVIDENCE, PROPOSAL_STEP, SCENARIOS, VERIFY_STEP } from './demo/scenario'

const cells = Array.from({ length: 56 }, (_, index) => {
  const row = Math.floor(index / 8), col = index % 8
  return { x: 40 + col * 78 + (row % 2) * 39, y: 40 + row * 68, heat: Math.max(0, Math.min(1, .25 + .48 * Math.sin(index * .74) + col * .055)), id: index }
})
const routeStops = [{x:92,y:415},{x:178,y:340},{x:275,y:372},{x:372,y:285},{x:452,y:365},{x:535,y:260},{x:605,y:170}]
const crowd = Array.from({length: 80}, (_,i) => ({x:82+(i%20)*24,y:405+Math.floor(i/20)*13+(i%3)*3,id:i}))

function HeatCells({ subdued = false }: { subdued?: boolean }) {
  return <>{cells.map(c => <polygon key={c.id} points={`${c.x},${c.y-28} ${c.x+25},${c.y-14} ${c.x+25},${c.y+14} ${c.x},${c.y+28} ${c.x-25},${c.y+14} ${c.x-25},${c.y-14}`} fill={`rgba(${Math.round(240+c.heat*15)},${Math.round(167-c.heat*105)},${Math.round(65-c.heat*40)},${subdued ? .08+c.heat*.2 : .14+c.heat*.45})`} />)}</>
}

function DeliveryMap({ proposed, verified }: { proposed: boolean; verified: boolean }) {
  const before = 'M92 415 L178 340 L275 372 L372 285 L452 365 L535 260 L605 170'
  const after = 'M92 415 L178 340 L452 365 L372 285 L275 372 L535 260 L605 170'
  return <g>
    <path className="street" d="M-30 410 C120 340 160 225 300 250 S520 420 730 240M120 -20 C180 100 190 310 80 580M480 -30 C420 120 470 290 620 560"/>
    <path className={`route before-route ${verified ? 'retired' : ''}`} d={before}/>
    {(proposed || verified) && <path className={`route after-route ${verified ? 'committed' : ''}`} d={after}/>}
    {routeStops.map((p,i)=><g className={`stop ${[2,4,5].includes(i)?'flexible':''}`} key={i} transform={`translate(${p.x} ${p.y})`}><circle r="14"/><text y="4">{i+1}</text></g>)}
    {proposed && !verified && <text className="map-callout" x="348" y="225">PROPOSED SEQUENCE</text>}
  </g>
}

function RaceMap({ proposed, verified }: { proposed: boolean; verified: boolean }) {
  const before='M72 430 C130 370 172 320 242 327 L365 327 L454 245 L600 190'
  const after='M72 430 C130 370 172 320 242 327 L320 268 L430 268 L454 245 L600 190'
  return <g>
    <path className="street race-street" d="M25 450 L640 105M10 315 L650 315M160 40 L160 520M450 20 L450 520"/>
    <path className={`route race-route before-route ${verified?'retired':''}`} d={before}/>
    {(proposed||verified)&&<path className={`route after-route ${verified?'committed':''}`} d={after}/>}
    {crowd.map((p,i)=><circle key={p.id} className={`runner ${verified?'spread':''}`} cx={p.x+(verified&&i%4===0?70:0)} cy={p.y-(verified&&i%4===0?82:0)} r="2.3"/>)}
    <g className="aid"><circle cx="244" cy="327" r="9"/><text x="259" y="331">AID 02</text></g>
    <text className="map-callout" x="85" y="475">4 WAVES · EACH DOT = 30 RUNNERS</text>
  </g>
}

function CampusMap({ proposed, verified }: { proposed: boolean; verified: boolean }) {
  return <g className="campus">
    <rect className="campus-path" x="52" y="70" width="570" height="390" rx="12"/>
    <g className="zone court"><rect x="78" y="105" width="205" height="145" rx="6"/><path d="M180 105V250M78 177H283"/><text x="96" y="132">ASPHALT COURT · 40.2°C</text></g>
    <g className="zone field"><rect x="325" y="105" width="265" height="145" rx="40"/><path d="M457 105V250M325 177H590"/><text x="349" y="132">FIELD · 37.1°C</text></g>
    <g className="zone shade"><path d="M78 294H590V430H78Z"/><circle cx="120" cy="338" r="28"/><circle cx="190" cy="385" r="32"/><circle cx="535" cy="350" r="34"/><text x="96" y="320">GREEN / SHADE · 33.5°C</text></g>
    <g className={`activity activity-a ${verified?'moved':''}`} transform={verified?'translate(330 350)':'translate(128 182)'}><rect x="-45" y="-19" width="90" height="38" rx="4"/><text textAnchor="middle" y="4">GRADE 4 · 90</text></g>
    <g className={`activity activity-b ${verified?'moved':''}`} transform={verified?'translate(180 182)':'translate(420 350)'}><rect x="-42" y="-19" width="84" height="38" rx="4"/><text textAnchor="middle" y="4">ART CLUB · 30</text></g>
    {proposed&&!verified&&<path className="swap-line" d="M180 205 C250 280 330 280 420 350M420 328 C350 260 265 260 180 182"/>}
  </g>
}

function OperationalMap({ scenario, proposed, verified }: { scenario: DemoScenario; proposed: boolean; verified: boolean }) {
  return <div className={`map map-${scenario.mapKind}`} aria-label={`${scenario.name} thermal operational map`}>
    <svg viewBox="0 0 680 540" role="img"><defs><filter id="glow"><feGaussianBlur stdDeviation="10" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter></defs><HeatCells subdued={scenario.mapKind==='campus'}/>{scenario.mapKind==='delivery'?<DeliveryMap proposed={proposed} verified={verified}/>:scenario.mapKind==='race'?<RaceMap proposed={proposed} verified={verified}/>:<CampusMap proposed={proposed} verified={verified}/>}</svg>
    <div className="map-label"><span>{scenario.locationLabel}</span><span>{MEASURED_EVIDENCE.grid}</span></div>
    <div className="legend"><span>FortyGuard thermal evidence</span><i /></div>
    <div className="map-object-label">{scenario.objectLabel}</div>
  </div>
}

function format(value:number){return new Intl.NumberFormat('en-US').format(value)}

export default function App() {
  const initial = new URLSearchParams(window.location.search).get('demo') as DemoId | null
  const [demoId,setDemoId]=useState<DemoId>(initial&&DEMO_IDS.includes(initial)?initial:'shiftshield')
  const [step,setStep]=useState(-1), [running,setRunning]=useState(false), [approved,setApproved]=useState(false), [evidenceOpen,setEvidenceOpen]=useState(false)
  const scenario=SCENARIOS[demoId], proposed=step>=PROPOSAL_STEP, verified=step===VERIFY_STEP
  useEffect(()=>{if(!running||step>=PROPOSAL_STEP)return;const timer=setTimeout(()=>setStep(s=>{if(s>=PROPOSAL_STEP-1)setRunning(false);return s+1}),1150);return()=>clearTimeout(timer)},[running,step])
  const progress=useMemo(()=>Math.max(0,((step+1)/scenario.steps.length)*100),[step,scenario.steps.length])
  const reset=(id:DemoId)=>{setDemoId(id);setStep(-1);setRunning(false);setApproved(false);setEvidenceOpen(false);window.history.replaceState({},'',`?demo=${id}`)}
  const start=()=>{setStep(0);setRunning(true);setApproved(false)}
  const approve=()=>{setApproved(true);setRunning(true);setTimeout(()=>{setStep(VERIFY_STEP);setRunning(false)},850)}
  return <main data-demo={demoId} data-state={verified?'verified':proposed?'proposed':step>=0?'investigating':'opening'}>
    <header><div className="brand"><span className="mark">40</span><span>FORTYGUARD <small>FINALIST SHOWDOWN</small></span></div><nav className="demo-tabs" aria-label="Finalist demos">{DEMO_IDS.map(id=><button key={id} className={id===demoId?'active':''} onClick={()=>reset(id)}><span>{SCENARIOS[id].number}</span>{SCENARIOS[id].name}</button>)}</nav><div className="status"><span className="dot"/> CACHED · ZERO CREDITS</div><button className="icon-button" onClick={()=>setEvidenceOpen(true)} aria-label="Open evidence"><Database size={17}/></button></header>
    <section className="hero">
      <div className="eyebrow"><Sparkles size={14}/> {scenario.name.toUpperCase()} <span>~75 SEC STAGE PATH</span></div>
      <h1>{scenario.hero[0]}<br/><em>{scenario.hero[1]}</em></h1><p className="audience">FOR {scenario.audience.toUpperCase()}</p><p className="lede">{scenario.lede}</p>
      <div className="hero-actions"><button className="primary" onClick={start}><Play size={16} fill="currentColor"/>{step<0?'Run micro-demo':'Replay sequence'}</button><button className="secondary" onClick={()=>setEvidenceOpen(true)}>Inspect evidence <ArrowRight size={15}/></button></div>
      <div className="reading"><ThermometerSun/><div><strong>{MEASURED_EVIDENCE.maxTemperatureC.toFixed(1)}°</strong><span>cached max °C</span></div><div className="mini-rule"/><div><strong>{scenario.scale.value}</strong><span>{scenario.scale.label}</span></div></div>
    </section>
    <section className="stage">
      <OperationalMap scenario={scenario} proposed={proposed} verified={verified}/>
      <aside className="agent-panel"><div className="panel-head"><div><span className="kicker">AGENT RUN · {scenario.number}</span><h2>{running?'Agent is working':verified?'Result verified':proposed?'Approval required':'Standing by'}</h2></div><span className={`orb ${running?'active':''}`}><Layers3 size={18}/></span></div><div className="progress"><i style={{width:`${progress}%`}}/></div>
        <ol>{scenario.steps.map((s,i)=><li className={i<step?'done':i===step?'current':''} key={s.label}><span className="step-icon">{i<step?<Check/>:i===step&&running?<span className="spinner"/>:<span>{String(i+1).padStart(2,'0')}</span>}</span><div><strong>{s.label}</strong><small>{i<=step?s.detail:s.tool}</small></div></li>)}</ol>
      </aside>
      <div className="metric"><span>{verified?scenario.derived.headline:'—'}</span><div><strong>{scenario.derived.label}</strong><small>scenario-derived · cached FortyGuard evidence</small></div></div>
    </section>
    <section className="constraint-strip"><span>CONSTRAINTS PRESERVED</span>{scenario.constraints.map(c=><div key={c}><Check/> {c}</div>)}</section>
    <section className="comparison"><div className="section-title"><span>{scenario.number} / TRANSFORMATION</span><h2>Same obligations. Better allocation.</h2></div><div className="compare-grid">
      <article><span className="flag before">BEFORE</span><h3>{format(scenario.derived.before)}</h3><small>{scenario.derived.unit}</small><p>{scenario.context}</p><div className="timeline hot"><i/><i/><i/><i/><i/></div></article><div className="swap"><ChevronRight/></div>
      <article className={verified?'revealed':''}><span className="flag after">AFTER</span><h3>{verified?format(scenario.derived.after):proposed?'Pending approval':'Run agent'}</h3><small>{scenario.derived.unit}</small><p>{proposed?`Recommendation preserves ${scenario.constraints.slice(0,3).join(', ').toLowerCase()}.`:'The verified comparison appears only after evidence, constraints and human approval.'}</p><div className="timeline cool"><i/><i/><i/><i/><i/></div></article></div>
      <div className="approval"><div><ShieldCheck/><span><strong>{proposed&&!verified?'Recommendation ready for a human':verified?'Approved and independently recomputed':'Human control stays in the loop'}</strong><small>No external action is executed by this demo</small></span></div><button disabled={!proposed||approved} onClick={approve}>{approved?<><Check/> Approved</>:<><CirclePause/> Approve recommendation</>}</button></div>
    </section>
    <footer><span>FORTYGUARD HACKATHON ’26</span><span>Measured evidence ≠ deterministic scenario</span><span>FINAL MVP SELECTED · NO</span></footer>
    <div className={`drawer-backdrop ${evidenceOpen?'open':''}`} onClick={()=>setEvidenceOpen(false)}/><aside className={`drawer ${evidenceOpen?'open':''}`}><div className="drawer-head"><div><span className="kicker">AUDITABLE EVIDENCE</span><h2>What is real?</h2></div><button className="icon-button" onClick={()=>setEvidenceOpen(false)} aria-label="Close evidence"><X/></button></div>
      <div className="evidence-block"><span>REAL FORTYGUARD · CACHED-LIVE</span><dl><dt>Maximum</dt><dd>{MEASURED_EVIDENCE.maxTemperatureC} °C</dd><dt>Average</dt><dd>{MEASURED_EVIDENCE.averageTemperatureC} °C</dd><dt>Observation date</dt><dd>{MEASURED_EVIDENCE.date}</dd><dt>Endpoint</dt><dd>/v1/heatmap</dd><dt>Status</dt><dd><b>CACHED</b></dd></dl></div>
      <div className="evidence-block"><span>DERIVED · DETERMINISTIC</span><dl><dt>Before</dt><dd>{format(scenario.derived.before)}</dd><dt>After</dt><dd>{format(scenario.derived.after)}</dd><dt>Shifted</dt><dd>{format(scenario.derived.shifted)} / {scenario.derived.percent}%</dd></dl></div>
      <div className="evidence-block"><span>PUBLIC DATA BOUNDARY</span><p>{scenario.publicData}</p></div><div className="evidence-block"><span>SYNTHETIC OPERATIONAL CONSTRAINTS</span><ul>{scenario.assumptions.map(a=><li key={a}>{a}</li>)}</ul></div>
      <div className="provenance"><Database/><div><strong>Sanitized cached response</strong><small>{MEASURED_EVIDENCE.cachePath}</small></div></div></aside>
  </main>
}
