import {useEffect,useState} from "react";
import {GitCompare,Save} from "lucide-react";
import type {AtomicCaptureResult} from "./LiveCaptureControl";

type Saved={session_id:string;role:string;note:string;evidence:any;trial?:number};
type Marker={kind:string;timestamp:number;note:string};
type Divergence={first_observed_change:{kind:string;can_id:string;at:number;detail:string}|null;events:{kind:string;can_id:string;at:number;detail:string}[];multi_id_events:{kind:string;at:number;count:number;can_ids:string[]}[];causality:string;ecu_ownership:string;alignment:{marker:string|null;normal_anchor:number;fault_anchor:number;window_before:number|null;window_after:number|null}};
type Comparison={a_session_id:string;b_session_id:string;a_data_loss:boolean;b_data_loss:boolean;ids:{can_id:string;normal_count:number;fault_count:number;delta:number;presence:string}[];interpretation:string};

export default function ExperimentAB({current}:{current:AtomicCaptureResult|null}){
 const [sessions,setSessions]=useState<Saved[]>([]),[comparison,setComparison]=useState<Comparison|null>(null),[divergence,setDivergence]=useState<Divergence|null>(null),[message,setMessage]=useState(""),[markerTime,setMarkerTime]=useState(""),[trial,setTrial]=useState("1");
 const refresh=()=>fetch("/api/capture/experiments").then(r=>r.json()).then(setSessions).catch(()=>setSessions([]));
 useEffect(refresh,[]);
 const save=async(role:"NORMAL_A"|"FAULT_B")=>{
  if(!current){setMessage("Сначала выполните аппаратный capture.");return}
  const q=new URLSearchParams({session_id:current.session_id,role,trial});
  const r=await fetch("/api/capture/experiments/save?"+q,{method:"POST"});
  if(!r.ok){setMessage("Сохранение сессии пока недоступно.");return} setMessage(role+" сохранена");refresh();
 };
 const a=sessions.filter(x=>x.role==="NORMAL_A").at(-1),b=sessions.filter(x=>x.role==="FAULT_B").at(-1);
 const markStart=async(session?:Saved)=>{const t=Number(markerTime);if(!session||!Number.isFinite(t)||t<0){setMessage("Выберите сессию и укажите timestamp START.");return}const q=new URLSearchParams({session_id:session.session_id,kind:"START",timestamp:String(t)});const r=await fetch("/api/capture/experiments/marker?"+q,{method:"POST"});setMessage(r.ok?"START marker сохранён":"Ошибка marker API")};
 const compare=async()=>{if(!a||!b)return;const q=new URLSearchParams({a_session_id:a.session_id,b_session_id:b.session_id,align_to:"START",window_before:"5",window_after:"15"});const [r,d]=await Promise.all([fetch("/api/capture/experiments/compare?"+q),fetch("/api/capture/experiments/divergence?"+q)]);if(r.ok)setComparison(await r.json());if(d.ok)setDivergence(await d.json())};
 return <section className="panel experimentAB">
  <div className="pt"><div><GitCompare/><b>Эксперимент P0603 · A/B</b></div><span>DESCRIPTIVE COMPARISON</span></div>
  <div className="abSlots"><Slot name="NORMAL A" session={a}/><Slot name="FAULT B" session={b}/></div>
  <div className="markerBar"><label>START timestamp<input value={markerTime} onChange={e=>setMarkerTime(e.target.value)} placeholder="seconds in RAW"/></label><button onClick={()=>markStart(a)} disabled={!a}>START → A</button><button onClick={()=>markStart(b)} disabled={!b}>START → B</button><span>A/B analysis: −5 s … +15 s from START</span></div><div className="trialBar"><label>Номер повтора<input value={trial} onChange={e=>setTrial(e.target.value)} inputMode="numeric"/></label><span>Сохраняйте последовательно A1/A2/A3 и B1/B2/B3.</span></div><div className="abActions"><button onClick={()=>save("NORMAL_A")} disabled={!current}><Save/>Текущий → NORMAL A</button><button onClick={()=>save("FAULT_B")} disabled={!current}><Save/>Текущий → FAULT B</button><button className="compare" onClick={compare} disabled={!a||!b}><GitCompare/>СРАВНИТЬ A/B</button></div>
  {message&&<p className="abMessage">{message}</p>}
  {divergence&&<div className="divergence"><span>FIRST OBSERVED CHANGE {divergence.alignment.marker?`· aligned to ${divergence.alignment.marker}`:""}</span>{divergence.first_observed_change?<><b>{divergence.first_observed_change.can_id} · {divergence.first_observed_change.kind} · {divergence.first_observed_change.at>=0?"+":""}{(divergence.first_observed_change.at*1000).toFixed(0)} ms</b><p>{divergence.first_observed_change.detail}</p></>:<b>NO DETERMINISTIC DIFFERENCE</b>}<div className="causalTags"><i>ECU {divergence.ecu_ownership}</i><i>CAUSALITY {divergence.causality}</i></div>{divergence.multi_id_events.map((x,i)=><div className="multiEvent" key={i}>MULTI-ID EVENT · {x.count} IDs · {x.can_ids.join(", ")}</div>)}</div>}{comparison&&<div className="abResult"><div className="abWarnings">{comparison.a_data_loss&&<b>NORMAL A: DATA LOSS</b>}{comparison.b_data_loss&&<b>FAULT B: DATA LOSS</b>}</div>
   <table><thead><tr><th>CAN ID</th><th>NORMAL</th><th>FAULT</th><th>Δ COUNT</th><th>PRESENCE</th></tr></thead><tbody>{comparison.ids.map(x=><tr key={x.can_id}><td className="mono">{x.can_id}</td><td>{x.normal_count}</td><td>{x.fault_count}</td><td>{x.delta}</td><td>{x.presence}</td></tr>)}</tbody></table>
   <p>{comparison.interpretation}</p></div>}
 </section>
}
function Slot({name,session}:{name:string;session?:Saved}){return <div><span>{name}{session?.trial?" · trial "+session.trial:""}</span><b>{session?session.session_id.slice(0,8):"NOT SAVED"}</b><small>{session?.evidence?.sha256?"RAW + SHA-256":"нет зарегистрированной сессии"}</small></div>}
