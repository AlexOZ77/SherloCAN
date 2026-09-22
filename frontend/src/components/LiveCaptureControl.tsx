import {useState} from "react";
import {Play,Radio,ShieldCheck,TriangleAlert} from "lucide-react";
import type {CaptureEvidence} from "./CaptureEvidenceCard";

export type AtomicCaptureResult={
 session_id:string;device_opened:boolean;channel_connected:boolean;
 disconnected_cleanly:boolean;device_closed_cleanly:boolean;
 evidence:CaptureEvidence|null;error:string|null;transmit_performed:boolean;
};

export default function LiveCaptureControl({onComplete}:{onComplete:(r:AtomicCaptureResult)=>void}){
 const [provider,setProvider]=useState("0"); const [bitrate,setBitrate]=useState("");
 const [maxFrames,setMaxFrames]=useState("1000"); const [running,setRunning]=useState(false);
 const [error,setError]=useState("");
 const start=async()=>{
  const rate=Number(bitrate),limit=Number(maxFrames);
  if(!Number.isInteger(rate)||rate<=0){setError("Укажите подтверждённый bitrate (> 0). SherloCAN его не угадывает.");return}
  if(!Number.isInteger(limit)||limit<=0){setError("MAX FRAMES должен быть целым числом > 0.");return}
  setRunning(true);setError("");
  try{
   const q=new URLSearchParams({provider_index:provider,bitrate:String(rate),max_frames:String(limit)});
   const res=await fetch("/api/capture/j2534/atomic-capture?"+q,{method:"POST"});
   if(!res.ok)throw new Error("API "+res.status);
   const data:AtomicCaptureResult=await res.json(); onComplete(data);
   if(data.error)setError(data.error);
  }catch(e){setError(String(e))}finally{setRunning(false)}
 };
 return <section className="panel liveControl">
  <div className="pt"><div><Radio/><b>Live Capture</b></div><span>{running?"RUNNING":"READY FOR EXPLICIT INPUT"}</span></div>
  <div className="liveForm">
   <label>J2534 PROVIDER INDEX<input value={provider} onChange={e=>setProvider(e.target.value)} inputMode="numeric" disabled={running}/></label>
   <label>CONFIRMED BITRATE<input value={bitrate} onChange={e=>setBitrate(e.target.value)} inputMode="numeric" placeholder="UNKNOWN — enter verified value" disabled={running}/></label>
   <label>MAX FRAMES<input value={maxFrames} onChange={e=>setMaxFrames(e.target.value)} inputMode="numeric" disabled={running}/></label>
   <button className="startCapture" onClick={start} disabled={running||!bitrate}><Play/>{running?"CAPTURING…":"START CAPTURE"}</button>
  </div>
  <div className="captureNotice"><ShieldCheck/><span>Application read-only: Open → Connect → bounded Read → Disconnect → Close. No write-message path.</span></div>
  {error&&<div className="captureError"><TriangleAlert/>{error}</div>}
 </section>
}
