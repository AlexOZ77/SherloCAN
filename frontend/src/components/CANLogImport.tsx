import {ChangeEvent,useRef,useState} from "react";
import {CheckCircle2,FileUp,LoaderCircle,PlayCircle,ShieldCheck,TriangleAlert} from "lucide-react";

export type ImportedCANLog={
 session_id:string;source_kind:string;original_name:string;source_format:string;
 source_path:string;normalized_path:string;sha256:string;size_bytes:number;
 frame_count:number;unique_can_ids:number;first_timestamp:number;last_timestamp:number;
 parsed:boolean;read_only:boolean;imported_at:string;interpretation:string;
};

export default function CANLogImport({onImported,onOpenAnalysis}:{onImported?:(r:ImportedCANLog)=>void;onOpenAnalysis?:(r:ImportedCANLog)=>void}){
 const input=useRef<HTMLInputElement|null>(null);
 const [busy,setBusy]=useState(false); const [error,setError]=useState(""); const [result,setResult]=useState<ImportedCANLog|null>(null);
 async function selected(e:ChangeEvent<HTMLInputElement>){
  const file=e.target.files?.[0]; if(!file)return;
  setBusy(true);setError("");setResult(null);
  try{
   const form=new FormData();form.append("file",file);
   const response=await fetch("/api/capture/import-log",{method:"POST",body:form});
   const body=await response.json().catch(()=>({detail:"Некорректный ответ backend"}));
   if(!response.ok)throw new Error(body.detail||("Import failed: HTTP "+response.status));
   setResult(body);onImported?.(body);
  }catch(e){setError(e instanceof Error?e.message:String(e))}
  finally{setBusy(false);e.target.value=""}
 }
 return <section className="panel canImport">
  <div className="pt"><div><FileUp/><b>Импорт CAN-лога</b></div><span>READ-ONLY · EVIDENCE COPY</span></div>
  <div className="canImportBody">
   <input ref={input} type="file" accept=".csv,.log,.txt,text/csv,text/plain" onChange={selected} hidden/>
   <div className="canImportIntro"><ShieldCheck/><div><b>Открыть сохранённый CAN-лог</b><p>CSV SherloCAN или candump LOG/TXT. Исходник сохраняется с SHA-256, кадры нормализуются в существующий CANFrame.</p></div></div>
   <button className="importButton" disabled={busy} onClick={()=>input.current?.click()}>{busy?<LoaderCircle className="spin"/>:<FileUp/>}{busy?" Импорт…":" Выбрать CAN-лог"}</button>
  </div>
  {error&&<div className="canImportError"><TriangleAlert/><div><b>Файл не импортирован</b><span>{error}</span></div></div>}
  {result&&<div className="canImportResult">
   <CheckCircle2/><div className="canImportSummary"><b>{result.original_name}</b><span>{result.source_format} · {result.frame_count.toLocaleString()} кадров · {result.unique_can_ids} CAN ID</span><code>SHA-256 {result.sha256}</code><small>{result.normalized_path}</small></div>
   <button onClick={()=>onOpenAnalysis?.(result)}><PlayCircle/> Анализировать</button>
  </div>}
 </section>
}
