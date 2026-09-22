import {useEffect,useState} from "react";
import {Cpu,RefreshCw,Usb} from "lucide-react";

type Device={name:string;vendor:string;dll_path:string;driver_found:boolean;dll_exists:boolean;dll_architecture:string;process_architecture:string;architecture_compatible:boolean|null;reusable_provider_installed:boolean;device_opened:boolean;channel_connected:boolean;capture_validated:boolean;next_action:string};

export default function OpenPortCard(){
 const [devices,setDevices]=useState<Device[]>([]); const [loading,setLoading]=useState(false); const [error,setError]=useState("");
 const test=()=>{setLoading(true);setError("");fetch("/api/capture/j2534/device-test").then(r=>{if(!r.ok)throw new Error("API "+r.status);return r.json()}).then(setDevices).catch(e=>setError(String(e))).finally(()=>setLoading(false))};
 useEffect(test,[]);
 return <div className="panel openport"><div className="pt"><div><Usb size={16}/><b>OpenPort / J2534</b></div><button className="mini" onClick={test} disabled={loading}><RefreshCw size={13}/>{loading?"TESTING":"DEVICE TEST"}</button></div>
  {error&&<div className="deviceEmpty">Device test error: {error}</div>}
  {!error&&!loading&&devices.length===0&&<div className="deviceEmpty">No registered J2534 provider detected on this computer.</div>}
  {devices.map((d,i)=><div className="device" key={d.dll_path+i}>
    <div className="deviceHead"><Cpu size={18}/><div><b>{d.name}</b><span>{d.vendor}</span></div><strong className={d.capture_validated?"ok":"pending"}>{d.capture_validated?"CAPTURE VALIDATED":"PREFLIGHT"}</strong></div>
    <div className="gates"><Gate n="DRIVER" ok={d.driver_found&&d.dll_exists}/><Gate n={"DLL "+d.dll_architecture} ok={d.architecture_compatible===true} unknown={d.architecture_compatible===null}/><Gate n="DEVICE OPEN" ok={d.device_opened}/><Gate n="CAN CHANNEL" ok={d.channel_connected}/></div>
    <p>{d.next_action}</p><code>{d.dll_path}</code>
  </div>)}
 </div>
}
function Gate({n,ok,unknown=false}:{n:string;ok:boolean;unknown?:boolean}){return <span className={unknown?"gate unknown":ok?"gate ok":"gate wait"}>{n}</span>}
