import {Activity,Check,Clock3,Radio,ShieldCheck,XCircle} from "lucide-react";
import type {AtomicCaptureResult} from "./LiveCaptureControl";

export default function CaptureRunStatus({running,result}:{running:boolean;result:AtomicCaptureResult|null}){
 const traffic=(result?.evidence?.frames_observed??0)>0;
 const stages=[
  ["Открытие устройства",result?.device_opened],
  ["Подключение к CAN",result?.channel_connected],
  ["Чтение данных",result?traffic:undefined],
  ["Отключение от CAN",result?.disconnected_cleanly],
  ["Закрытие устройства",result?.device_closed_cleanly],
 ] as const;
 return <section className="panel runStatus">
  <div className="pt"><div><Activity/><b>Состояние захвата</b></div><span className={running?"runBadge active":"runBadge"}>{running?"RUNNING":result?"COMPLETED":"NOT STARTED"}</span></div>
  <div className="stageList">{stages.map(([name,state],i)=><div className="runStage" key={name}>
   <i className={state===true?"ok":state===false?"bad":running&&i===2?"active":""}>{state===true?<Check/>:state===false?<XCircle/>:running&&i===2?<Radio/>:<Clock3/>}</i>
   <span><b>{i+1}. {name}</b><small>{state===true?"Подтверждено":state===false?"Требует проверки":running&&i===2?"Выполняется…":"Ожидание"}</small></span>
  </div>)}</div>
  <div className="runSafety"><ShieldCheck/> Передача CAN-сообщений приложением не выполняется.</div>
 </section>
}
