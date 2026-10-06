import {Activity,AlertTriangle,BarChart3} from "lucide-react";
import type {ImportedCANLog} from "./CANLogImport";

export type ImportedLogAnalysis={
 session_id:string;frame_count:number;unique_can_ids:number;duration_s:number;
 ids:{can_id:string;count:number;median_period_ms:number|null;observed_rate_hz:number|null;typical_dlc:number;ecu_owner:string}[];
 timeline:{bucket_width_s:number;counts:number[]};
 anomalies:{kind:string;can_id:string;timestamp:number;gap_ms:number;ratio:number;detail:string;ecu_owner:string}[];
 interpretation:string;
};

export default function ImportedLogAnalysisPanel({source,analysis,loading,error}:{source:ImportedCANLog|null;analysis:ImportedLogAnalysis|null;loading:boolean;error:string}){
 if(!source)return null;
 const max=analysis?Math.max(1,...analysis.timeline.counts):1;
 return <section className="panel importedAnalysis">
  <div className="pt"><div><BarChart3/><b>Анализ импортированного лога</b></div><span>{loading?"ANALYZING":analysis?"MEASURED":"WAITING"}</span></div>
  {loading&&<div className="analysisEmpty">Расчёт периодов, частот и временных разрывов…</div>}
  {error&&<div className="analysisError"><AlertTriangle/> {error}</div>}
  {analysis&&<><div className="analysisKpis"><div><span>FRAMES</span><b>{analysis.frame_count.toLocaleString()}</b></div><div><span>CAN IDs</span><b>{analysis.unique_can_ids}</b></div><div><span>DURATION</span><b>{analysis.duration_s.toFixed(3)} s</b></div><div><span>LONG GAPS</span><b>{analysis.anomalies.length}</b></div></div>
   <div className="timelineBars" title={"bucket "+analysis.timeline.bucket_width_s.toFixed(6)+" s"}>{analysis.timeline.counts.map((v,i)=><i key={i} style={{height:(6+34*v/max)+"px"}}/>)}</div>
   <table><thead><tr><th>CAN ID</th><th>FRAMES</th><th>MEDIAN PERIOD</th><th>RATE</th><th>DLC</th><th>OWNER</th></tr></thead><tbody>{analysis.ids.map(x=><tr key={x.can_id}><td className="mono">{x.can_id}</td><td>{x.count}</td><td>{x.median_period_ms==null?"—":x.median_period_ms+" ms"}</td><td>{x.observed_rate_hz==null?"—":x.observed_rate_hz+" Hz"}</td><td>{x.typical_dlc}</td><td>UNKNOWN</td></tr>)}</tbody></table>
   <div className="anomalyList"><h3><Activity/> Наблюдаемые временные отклонения</h3>{analysis.anomalies.length===0?<p>Разрывы ≥3× медианного периода не обнаружены.</p>:analysis.anomalies.slice(0,50).map((a,i)=><div key={i}><b>{a.can_id} · {a.kind}</b><span>{a.detail} · t={a.timestamp.toFixed(6)}</span></div>)}{analysis.anomalies.length>50&&<p>Показаны первые 50 из {analysis.anomalies.length} событий.</p>}</div>
   <div className="analysisRule"><AlertTriangle/> {analysis.interpretation}</div></>}
 </section>
}
