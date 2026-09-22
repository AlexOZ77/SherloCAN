import {useEffect,useState} from "react";
import {Cpu,RefreshCw,Usb,Play} from "lucide-react";

type Device={name:string;vendor:string;dll_path:string;driver_found:boolean;dll_exists:boolean;dll_architecture:string;process_architecture:string;architecture_compatible:boolean|null;reusable_provider_installed:boolean;device_opened:boolean;channel_connected:boolean;capture_validated:boolean;next_action:string};
type OpenResult={device_opened:boolean;device_id:number|null;closed_cleanly:boolean;channel_connected:boolean;capture_validated:boolean;error:string|null};

export default function OpenPortCard(){
 const [devices,setDevices]=useState<Device[]>([]); const [loading,setLoading]=useState(false); const [opening,setOpening]=useState(false); const [error,setError]=useState(""); const [opened,setOpened]=useState<OpenResult|null>(null);
 const test=()=>{setLoading(true);setError("");setOpened(null);fetch("/api/capture/j2534/device-test").then(r=>{if(!r.ok)throw new Error("API "+r.status);return r.json()}).then(setDevices).catch(e=>setError(String(e))).finally(()=>setLoading(false))};
 const openTest=()=>{setOpening(true);setError("");fetch("/api/capture/j2534/open-test?provider_index=0",{method:"POST"}).then(r=>{if(!r.ok)throw new Error("API "+r.status);return r.json()}).then(setOpened).catch(e=>setError(String(e))).finally(()=>setOpening(false))};
 useEffect(test,[]);
 return <div className="panel openport"><div className="pt"><div><Usb size={16}/><b>OpenPort / J2534</b></div><button className="mini" onClick={test} disabled={loading||opening}><RefreshCw size={13}/>{loading?"TESTING":"DEVICE TEST"}</button></div>
  {error&&<div className="deviceEmpty">Hardware test error: {error}</div>}
  {!error&&!loading&&devices.length===0&&<div className="deviceEmpty">No registered J2534 provider detected on this computer.</div>}
  {devices.map((d,i)=><div className="device" key={d.dll_path+i}>
    <div className="deviceHead"><Cpu size={18}/><div><b>{d.name}</b><span>{d.vendor}</span></div><strong className={opened?.device_opened?"ok":"pending"}>{opened?.device_opened?"DEVICE OPEN VERIFIED":"PREFLIGHT"}</strong></div>
    <div className="gates"><Gate n="DRIVER" ok={d.driver_found&&d.dll_exists}/><Gate n={"DLL "+d.dll_architecture} ok={d.architecture_compatible===true} unknown={d.architecture_compatible===null}/><Gate n="DEVICE OPEN" ok={opened?.device_opened===true}/><Gate n="CAN CHANNEL" ok={false}/></div>
    {opened?.device_opened?<p>PassThruOpen succeeded; device {opened.closed_cleanly?"closed cleanly":"close status requires review"}. CAN channel was NOT opened.</p>:<p>{d.next_action}</p>}
    <code>{d.dll_path}</code>
    <div className="deviceActions"><button className="openTest" onClick={openTest} disabled={opening||d.architecture_compatible!==true}><Play size={13}/>{opening?"OPENING…":"VERIFY DEVICE OPEN"}</button><span>Explicit test · PassThruOpen → PassThruClose · no CAN channel</span></div>
  </div>)}
 </div>
}
function Gate({n,ok,unknown=false}:{n:string;ok:boolean;unknown?:boolean}){return <span className={unknown?"gate unknown":ok?"gate ok":"gate wait"}>{n}</span>}
