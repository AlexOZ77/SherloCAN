import {useState} from "react";
import {Play,Radio,ShieldCheck,TriangleAlert,ClipboardCheck} from "lucide-react";
import type {CaptureEvidence} from "./CaptureEvidenceCard";

type Acceptance={status:"PASS"|"FAIL";checks:{id:string;passed:boolean;required:boolean}[];rule:string};
type Protocol={scenario:string;trial:number;ignition_state:string;engine_state:string;battery_voltage_v:number|null;bitrate:number;bitrate_source:string;provider_index:number;max_frames:number;timeout_ms:number;operator_note:string};

export type AtomicCaptureResult={
 session_id:string;device_opened:boolean;channel_connected:boolean;
 disconnected_cleanly:boolean;device_closed_cleanly:boolean;
 evidence:CaptureEvidence|null;error:string|null;transmit_performed:boolean;
 protocol?:Protocol;acceptance?:Acceptance;evidence_manifest?:Record<string,unknown>;
};

export default function LiveCaptureControl({onComplete,onRunning}:{onComplete:(r:AtomicCaptureResult)=>void;onRunning?:(v:boolean)=>void}){
 const [provider,setProvider]=useState("0"),[bitrate,setBitrate]=useState(""),[bitrateSource,setBitrateSource]=useState("");
 const [maxFrames,setMaxFrames]=useState("1000"),[timeoutMs,setTimeoutMs]=useState("100");
 const [scenario,setScenario]=useState("CONTROL"),[trial,setTrial]=useState("1"),[ignition,setIgnition]=useState("UNKNOWN"),[engine,setEngine]=useState("UNKNOWN");
 const [battery,setBattery]=useState(""),[note,setNote]=useState(""),[running,setRunning]=useState(false),[error,setError]=useState(""),[acceptance,setAcceptance]=useState<Acceptance|null>(null);

 const start=async()=>{
  const rate=Number(bitrate),limit=Number(maxFrames),timeout=Number(timeoutMs),trialNo=Number(trial),providerNo=Number(provider);
  const voltage=battery.trim()===""?null:Number(battery);
  if(!Number.isInteger(rate)||rate<=0){setError("Укажите подтверждённый bitrate (> 0). SherloCAN его не угадывает.");return}
  if(!bitrateSource.trim()){setError("Укажите источник подтверждения bitrate.");return}
  if(!Number.isInteger(limit)||limit<=0){setError("MAX FRAMES должен быть целым числом > 0.");return}
  if(!Number.isInteger(timeout)||timeout<=0){setError("TIMEOUT должен быть целым числом > 0.");return}
  if(!Number.isInteger(trialNo)||trialNo<1){setError("TRIAL должен быть целым числом >= 1.");return}
  if(!Number.isInteger(providerNo)||providerNo<0){setError("PROVIDER INDEX должен быть целым числом >= 0.");return}
  if(voltage!==null&&(!Number.isFinite(voltage)||voltage<=0)){setError("Напряжение АКБ должно быть > 0 либо оставьте поле пустым.");return}
  setRunning(true);onRunning?.(true);setError("");setAcceptance(null);
  try{
   const q=new URLSearchParams({
    provider_index:String(providerNo),bitrate:String(rate),bitrate_source:bitrateSource.trim(),
    max_frames:String(limit),timeout_ms:String(timeout),scenario,trial:String(trialNo),
    ignition_state:ignition,engine_state:engine,operator_note:note
   });
   if(voltage!==null)q.set("battery_voltage_v",String(voltage));
   const res=await fetch("/api/capture/j2534/atomic-capture?"+q,{method:"POST"});
   if(!res.ok){const body=await res.text();throw new Error("API "+res.status+" "+body)}
   const data:AtomicCaptureResult=await res.json();setAcceptance(data.acceptance??null);onComplete(data);
   if(data.error)setError(data.error);
  }catch(e){setError(String(e))}finally{setRunning(false);onRunning?.(false)}
 };

 return <section className="panel liveControl">
  <div className="pt"><div><Radio/><b>Live Capture · Experiment Protocol</b></div><span>{running?"RUNNING":"EXPLICIT INPUT REQUIRED"}</span></div>
  <div className="protocolForm">
   <label>SCENARIO<select value={scenario} onChange={e=>setScenario(e.target.value)} disabled={running}><option>CONTROL</option><option>NORMAL_A</option><option>FAULT_B</option><option>WIGGLE</option></select></label>
   <label>TRIAL<input value={trial} onChange={e=>setTrial(e.target.value)} inputMode="numeric" disabled={running}/></label>
   <label>IGNITION STATE<select value={ignition} onChange={e=>setIgnition(e.target.value)} disabled={running}><option>UNKNOWN</option><option>OFF</option><option>ON</option><option>START</option></select></label>
   <label>ENGINE STATE<select value={engine} onChange={e=>setEngine(e.target.value)} disabled={running}><option>UNKNOWN</option><option>STOPPED</option><option>CRANKING</option><option>RUNNING</option></select></label>
   <label>BATTERY V<input value={battery} onChange={e=>setBattery(e.target.value)} inputMode="decimal" placeholder="optional measured value" disabled={running}/></label>
   <label>J2534 PROVIDER INDEX<input value={provider} onChange={e=>setProvider(e.target.value)} inputMode="numeric" disabled={running}/></label>
   <label>CONFIRMED BITRATE<input value={bitrate} onChange={e=>setBitrate(e.target.value)} inputMode="numeric" placeholder="UNKNOWN — enter verified value" disabled={running}/></label>
   <label>BITRATE SOURCE<input value={bitrateSource} onChange={e=>setBitrateSource(e.target.value)} placeholder="ESM / verified source" disabled={running}/></label>
   <label>MAX FRAMES<input value={maxFrames} onChange={e=>setMaxFrames(e.target.value)} inputMode="numeric" disabled={running}/></label>
   <label>TIMEOUT MS<input value={timeoutMs} onChange={e=>setTimeoutMs(e.target.value)} inputMode="numeric" disabled={running}/></label>
   <label className="noteField">OPERATOR NOTE<input value={note} onChange={e=>setNote(e.target.value)} placeholder="conditions / observation" disabled={running}/></label>
   <button className="startCapture" onClick={start} disabled={running||!bitrate||!bitrateSource}><Play/>{running?"CAPTURING…":"START CAPTURE"}</button>
  </div>
  <div className="captureNotice"><ShieldCheck/><span>Application read-only: Open → Connect → bounded Read → Disconnect → Close. No write-message path.</span></div>
  {acceptance&&<div className={"acceptance "+(acceptance.status==="PASS"?"pass":"fail")}><ClipboardCheck/><div><b>CAPTURE ACCEPTANCE: {acceptance.status}</b><span>{acceptance.checks.map(x=>x.id+"="+(x.passed?"OK":"FAIL")).join(" · ")}</span><small>{acceptance.rule}</small></div></div>}
  {error&&<div className="captureError"><TriangleAlert/>{error}</div>}
 </section>
}
