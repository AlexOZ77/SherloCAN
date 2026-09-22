import {FileCheck2,ShieldAlert,ShieldCheck} from "lucide-react";

export type CaptureEvidence={
 frames_observed:number;frames_accepted:number;frames_dropped:number;unique_ids:number;
 capture_data_loss:boolean;raw_path:string;sha256:string;bitrate?:number;
};

export default function CaptureEvidenceCard({result}:{result:CaptureEvidence|null}){
 return <section className="panel evidenceCard">
  <div className="pt"><div><FileCheck2/><b>Capture Evidence</b></div><span>MEASURED ONLY</span></div>
  {!result?<div className="captureEmpty">Live capture ещё не выполнялся. Измерения отсутствуют.</div>:
  <>
   <div className="captureMetrics">
    <Metric label="OBSERVED" value={result.frames_observed}/>
    <Metric label="ACCEPTED" value={result.frames_accepted}/>
    <Metric label="DROPPED" value={result.frames_dropped} warn={result.frames_dropped>0}/>
    <Metric label="UNIQUE IDS" value={result.unique_ids}/>
   </div>
   <div className={result.capture_data_loss?"lossBanner bad":"lossBanner good"}>
    {result.capture_data_loss?<ShieldAlert/>:<ShieldCheck/>}
    <div><b>{result.capture_data_loss?"CAPTURE DATA LOSS":"NO QUEUE LOSS OBSERVED"}</b>
    <span>{result.capture_data_loss?"RAW evidence is incomplete for this capture.":"No FrameQueue drops were reported by this capture."}</span></div>
   </div>
   <div className="evidenceFile"><span>RAW</span><code>{result.raw_path}</code><span>SHA-256</span><code>{result.sha256}</code></div>
  </>}
 </section>
}
function Metric({label,value,warn=false}:{label:string;value:number;warn?:boolean}){return <div className={warn?"metric warn":"metric"}><span>{label}</span><b>{value.toLocaleString()}</b></div>}
