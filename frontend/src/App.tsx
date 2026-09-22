import {Activity,Car,FileSearch,Network,Radio,ShieldCheck,TimerReset,TriangleAlert,Wrench} from "lucide-react";

const nav=[["Overview",Activity],["Capture",Radio],["Network",Network],["Timeline",TimerReset],["Evidence",ShieldCheck],["Sherlock",FileSearch],["Crash",TriangleAlert]];
const ids=[["0x1A4","ACTIVE","10.1 ms"],["0x284","ACTIVE","20.0 ms"],["0x351","GAP","84.7 ms"],["0x5C5","ACTIVE","100 ms"]];

export default function App(){
 return <div className="shell">
  <aside><div className="brand"><div className="mark">S</div><div><b>SherloCAN</b><span>Automotive Network Investigator</span></div></div>
   <nav>{nav.map(([label,Icon]:any)=><button className={label==="Capture"?"active":""} key={label}><Icon size={18}/>{label}</button>)}</nav>
   <div className="safety"><ShieldCheck size={16}/><div><b>READ-ONLY</b><span>No CAN transmit</span></div></div>
  </aside>
  <main>
   <header><div><p className="eyebrow">CASE SC-0001 / LIVE CAPTURE</p><h1>Capture & Investigate</h1></div><div className="vehicle"><Car size={18}/><div><b>Nissan Qashqai J11</b><span>2014 · MR20DD · CVT · 4WD</span></div></div></header>
   <section className="statusbar"><Status label="SOURCE" value="File Replay" sub="OpenPort/J2534 next"/><Status label="STATE" value="CAPTURING" sub="00:03:42"/><Status label="TRAFFIC" value="1,284 fps" sub="42 active IDs"/><Status label="QUEUE" value="18 / 10,000" sub="0 dropped"/></section>
   <section className="workspace">
    <div className="left">
     <div className="panel capture"><PanelTitle icon={<Radio/>} title="Live Capture" meta="primary_can"/>
      <div className="wave"><div className="grid"/><div className="pulse p1"/><div className="pulse p2"/><div className="pulse p3"/><div className="event"><span>FAULT</span></div></div>
      <div className="controls"><button className="danger"><TriangleAlert size={16}/> MARK FAULT</button><button><Wrench size={16}/> WIGGLE</button><button>+ MARKER</button><span className="clock">T+ 00:03:42.817</span></div>
     </div>
     <div className="panel"><PanelTitle icon={<Activity/>} title="CAN ID Monitor" meta="baseline: IDLE"/>
      <table><thead><tr><th>CAN ID</th><th>STATE</th><th>PERIOD</th><th>LAST SEEN</th></tr></thead><tbody>{ids.map(x=><tr key={x[0]} className={x[1]==="GAP"?"warn":""}><td className="mono">{x[0]}</td><td><i className={x[1].toLowerCase()}/>{x[1]}</td><td>{x[2]}</td><td>now</td></tr>)}</tbody></table>
     </div>
    </div>
    <div className="right">
     <div className="panel"><PanelTitle icon={<FileSearch/>} title="Investigation" meta="event #E-017"/>
      <div className="finding"><span>FIRST OBSERVED CHANGE</span><b>CAN ID 0x351 developed a long gap</b><p>84.7 ms gap versus 20.1 ms baseline median. This is an observation, not a root-cause assignment.</p></div>
      <h3>Evidence</h3><Evidence state="support" text="Gap begins 31 ms after FAULT marker"/><Evidence state="neutral" text="No adapter data loss recorded"/><Evidence state="unknown" text="ECU ownership of 0x351 is UNKNOWN"/>
      <button className="primary">INVESTIGATE EVENT →</button>
     </div>
     <div className="panel"><PanelTitle icon={<Network/>} title="Network health" meta="evidence-aware"/>
      <div className="nodes"><Node name="ECM" state="unknown"/><b>—</b><Node name="ABS/ESP" state="unknown"/><b>—</b><Node name="4WD" state="unknown"/></div>
      <p className="hint">No ECU state inferred from unknown CAN IDs.</p>
     </div>
    </div>
   </section>
  </main>
 </div>
}
function Status({label,value,sub}:any){return <div className="stat"><span>{label}</span><b>{value}</b><small>{sub}</small></div>}
function PanelTitle({icon,title,meta}:any){return <div className="pt"><div>{icon}<b>{title}</b></div><span>{meta}</span></div>}
function Evidence({state,text}:any){return <div className={"evidence "+state}><i/> {text}</div>}
function Node({name}:any){return <div className="node"><span>?</span><b>{name}</b></div>}
