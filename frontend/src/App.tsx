import {useEffect,useState} from "react";
import {Activity,Car,FileSearch,Network,Radio,ShieldCheck,TimerReset,TriangleAlert,Wrench,BatteryCharging,Gauge,Play,Download} from "lucide-react";
import OpenPortCard from "./components/OpenPortCard";

type Demo={synthetic:boolean;vehicle_label:string;source:string;safety:string;baseline:Record<string,{count:number;median_period_ms:number|null;typical_dlc:number}>;anomalies:{kind:string;can_id:string;timestamp:number;detail:string;ecu_owner:string}[];interpretation:string};
const nav=[["Overview",Activity],["Capture",Radio],["Network",Network],["Timeline",TimerReset],["Evidence",ShieldCheck],["Sherlock",FileSearch],["Crash",TriangleAlert]];

export default function App(){
 const [demo,setDemo]=useState<Demo|null>(null); const [error,setError]=useState("");
 useEffect(()=>{fetch("/api/capture/demo-analysis").then(r=>{if(!r.ok)throw new Error("API "+r.status);return r.json()}).then(setDemo).catch(e=>setError(String(e)))},[]);
 const anomaly=demo?.anomalies[0]; const rows=demo?Object.entries(demo.baseline):[];
 return <div className="shell">
  <aside><div className="brand"><div className="mark">S</div><div><b>SherloCAN</b><span>Automotive Network Investigator</span></div></div>
   <nav>{nav.map(([label,Icon]:any)=><button className={label==="Capture"?"active":""} key={label}><Icon size={18}/>{label}</button>)}</nav>
   <div className="safety"><ShieldCheck size={16}/><div><b>{demo?.safety||"READ-ONLY"}</b><span>No CAN transmit</span></div></div>
  </aside>
  <main><header><div><p className="eyebrow">FIRST RUNNABLE SLICE / SYNTHETIC DATA</p><h1>Capture & Investigate</h1></div><div className="vehicle"><Car size={18}/><div><b>Nissan Qashqai J11</b><span>synthetic fixture · no ECU mapping inferred</span></div></div></header>
   <section className="commandHero"><div><p className="eyebrow">СЕССИЯ / ЛОКАЛЬНЫЙ РЕЖИМ</p><h1>Диагностика <strong>OpenPort.</strong></h1><p>Проверьте соединение адаптера и готовность CAN-шины перед чтением ECU.</p></div><div className="commandActions"><button><Download size={16}/> Экспорт отчёта</button><button className="cyan"><Play size={16}/> Запустить проверку</button></div></section><section className="kpis"><div><span>ОБЩИЙ СТАТУС</span><b>PRE-FLIGHT</b><small>аппаратные ворота проверяются</small></div><div><span>НАПРЯЖЕНИЕ</span><b><BatteryCharging size={18}/> UNKNOWN</b><small>нет подтверждённого измерения</small></div><div><span>ЗАДЕРЖКА CAN</span><b><Gauge size={18}/> UNKNOWN</b><small>CAN-канал ещё не открыт</small></div></section><section className="statusbar"><Status label="SOURCE" value={demo?.source||"Connecting…"} sub="OpenPort/J2534 gated"/><Status label="DATA" value={demo?"LOADED":"WAITING"} sub="synthetic fixture"/><Status label="BASELINE IDS" value={String(rows.length)} sub="measured from NORMAL"/><Status label="ANOMALIES" value={String(demo?.anomalies.length??0)} sub={error||"deterministic analysis"}/></section>
   <OpenPortCard/><section className="workspace"><div className="left">
    <div className="panel capture"><PanelTitle icon={<Radio/>} title="Replay Analysis" meta="NORMAL → FAULT"/><div className="wave"><div className="grid"/><div className="pulse p1"/><div className="pulse p2"/><div className="pulse p3"/>{anomaly&&<div className="event"><span>LONG GAP</span></div>}</div><div className="controls"><button className="danger"><TriangleAlert size={16}/> MARK FAULT</button><button><Wrench size={16}/> WIGGLE</button><button>+ MARKER</button><span className="clock">{demo?"API CONNECTED":"CONNECTING"}</span></div></div>
    <div className="panel"><PanelTitle icon={<Activity/>} title="Measured Baseline" meta="synthetic NORMAL"/><table><thead><tr><th>CAN ID</th><th>STATE</th><th>MEDIAN PERIOD</th><th>DLC</th></tr></thead><tbody>{rows.map(([id,x])=><tr key={id} className={anomaly?.can_id===id?"warn":""}><td className="mono">{id}</td><td><i/>MEASURED</td><td>{x.median_period_ms??"—"} ms</td><td>{x.typical_dlc}</td></tr>)}</tbody></table></div>
   </div><div className="right">
    <div className="panel"><PanelTitle icon={<FileSearch/>} title="Investigation" meta="backend result"/>{anomaly?<><div className="finding"><span>FIRST OBSERVED CHANGE</span><b>{anomaly.can_id} · {anomaly.kind}</b><p>{anomaly.detail}. {demo?.interpretation}</p></div><h3>Evidence</h3><Evidence state="support" text="Anomaly reproduced from FAULT fixture"/><Evidence state="neutral" text="Baseline calculated from NORMAL fixture"/><Evidence state="unknown" text={"ECU ownership: "+anomaly.ecu_owner}/></>:<div className="finding"><b>{error||"Loading analysis…"}</b></div>}<button className="primary">INVESTIGATE EVENT →</button></div>
    <div className="panel"><PanelTitle icon={<Network/>} title="Network health" meta="evidence-aware"/><div className="nodes"><Node name="ECM"/><b>—</b><Node name="ABS/ESP"/><b>—</b><Node name="4WD"/></div><p className="hint">Unknown CAN IDs are not assigned to these ECUs.</p></div>
   </div></section>
  </main></div>
}
function Status({label,value,sub}:any){return <div className="stat"><span>{label}</span><b>{value}</b><small>{sub}</small></div>}
function PanelTitle({icon,title,meta}:any){return <div className="pt"><div>{icon}<b>{title}</b></div><span>{meta}</span></div>}
function Evidence({state,text}:any){return <div className={"evidence "+state}><i/> {text}</div>}
function Node({name}:any){return <div className="node"><span>?</span><b>{name}</b></div>}
