import {useEffect,useState} from "react";
import {GitCompare,Save} from "lucide-react";
import type {AtomicCaptureResult} from "./LiveCaptureControl";

type Saved={session_id:string;role:string;note:string;evidence:any};
type Comparison={a_session_id:string;b_session_id:string;a_data_loss:boolean;b_data_loss:boolean;ids:{can_id:string;normal_count:number;fault_count:number;delta:number;presence:string}[];interpretation:string};

export default function ExperimentAB({current}:{current:AtomicCaptureResult|null}){
 const [sessions,setSessions]=useState<Saved[]>([]),[comparison,setComparison]=useState<Comparison|null>(null),[message,setMessage]=useState("");
 const refresh=()=>fetch("/api/capture/experiments").then(r=>r.json()).then(setSessions).catch(()=>setSessions([]));
 useEffect(refresh,[]);
 const save=async(role:"NORMAL_A"|"FAULT_B")=>{
  if(!current){setMessage("Сначала выполните аппаратный capture.");return}
  const q=new URLSearchParams({session_id:current.session_id,role});
  const r=await fetch("/api/capture/experiments/save?"+q,{method:"POST"});
  if(!r.ok){setMessage("Сохранение сессии пока недоступно.");return} setMessage(role+" сохранена");refresh();
 };
 const a=sessions.filter(x=>x.role==="NORMAL_A").at(-1),b=sessions.filter(x=>x.role==="FAULT_B").at(-1);
 const compare=async()=>{if(!a||!b)return;const q=new URLSearchParams({a_session_id:a.session_id,b_session_id:b.session_id});const r=await fetch("/api/capture/experiments/compare?"+q);if(r.ok)setComparison(await r.json())};
 return <section className="panel experimentAB">
  <div className="pt"><div><GitCompare/><b>Эксперимент P0603 · A/B</b></div><span>DESCRIPTIVE COMPARISON</span></div>
  <div className="abSlots"><Slot name="NORMAL A" session={a}/><Slot name="FAULT B" session={b}/></div>
  <div className="abActions"><button onClick={()=>save("NORMAL_A")} disabled={!current}><Save/>Текущий → NORMAL A</button><button onClick={()=>save("FAULT_B")} disabled={!current}><Save/>Текущий → FAULT B</button><button className="compare" onClick={compare} disabled={!a||!b}><GitCompare/>СРАВНИТЬ A/B</button></div>
  {message&&<p className="abMessage">{message}</p>}
  {comparison&&<div className="abResult"><div className="abWarnings">{comparison.a_data_loss&&<b>NORMAL A: DATA LOSS</b>}{comparison.b_data_loss&&<b>FAULT B: DATA LOSS</b>}</div>
   <table><thead><tr><th>CAN ID</th><th>NORMAL</th><th>FAULT</th><th>Δ COUNT</th><th>PRESENCE</th></tr></thead><tbody>{comparison.ids.map(x=><tr key={x.can_id}><td className="mono">{x.can_id}</td><td>{x.normal_count}</td><td>{x.fault_count}</td><td>{x.delta}</td><td>{x.presence}</td></tr>)}</tbody></table>
   <p>{comparison.interpretation}</p></div>}
 </section>
}
function Slot({name,session}:{name:string;session?:Saved}){return <div><span>{name}</span><b>{session?session.session_id.slice(0,8):"NOT SAVED"}</b><small>{session?.evidence?.sha256?"RAW + SHA-256":"нет зарегистрированной сессии"}</small></div>}
