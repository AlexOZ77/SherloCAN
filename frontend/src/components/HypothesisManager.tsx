import {useEffect,useState} from "react";
import {FlaskConical,RefreshCw} from "lucide-react";
type H={id:string;title:string;status:"SUPPORTED"|"CONTRADICTED"|"INCONCLUSIVE"|"NOT_TESTED";evidence_for:string[];evidence_against:string[];unknown:string[];next_test:string};
export default function HypothesisManager(){
 const [rows,setRows]=useState<H[]>([]),[rule,setRule]=useState("");
 const load=()=>fetch("/api/capture/experiments/hypotheses").then(r=>r.json()).then(x=>{setRows(x.hypotheses);setRule(x.rules)});
 useEffect(()=>{void load()},[]);
 return <section className="panel hypothesisPanel">
  <div className="pt"><div><FlaskConical/><b>Hypothesis Manager</b></div><button className="iconRefresh" onClick={load}><RefreshCw/></button></div>
  <div className="hypGrid">{rows.map(h=><article key={h.id}><header><b>{h.id}</b><span>{h.status}</span></header><h3>{h.title}</h3>
   <small>EVIDENCE FOR</small>{h.evidence_for.length?h.evidence_for.map((e,i)=><p key={"f"+i}>{e}</p>):<p>Нет прямых evidence.</p>}
   <small>EVIDENCE AGAINST</small>{h.evidence_against.length?h.evidence_against.map((e,i)=><p key={"a"+i}>{e}</p>):<p>Нет прямых evidence.</p>}
   <small>UNKNOWN / LIMITATIONS</small>{h.unknown.length?h.unknown.map((e,i)=><p key={"u"+i}>{e}</p>):<p>Нет дополнительных ограничений.</p>}
   <small>NEXT DISCRIMINATING TEST</small><p>{h.next_test}</p>
  </article>)}</div><div className="hypRule">{rule}</div>
 </section>
}
