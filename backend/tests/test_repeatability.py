import csv
from app.capture.experiments import save_session
from app.capture.markers import add_marker
from app.capture.repeatability import repeatability
FIELDS=["sequence","timestamp","can_id","dlc","data","channel","is_extended"]
def raw(p,start,fault=False):
    rows=[(start-.1,"0x100"),(start,"0x100"),(start+.1,"0x100"),(start+.2,"0x100")]
    if fault: rows += [(start+.42,"0x200"),(start+.44,"0x300")]
    with p.open("w",newline="",encoding="utf-8") as h:
        w=csv.DictWriter(h,fieldnames=FIELDS);w.writeheader()
        for n,(t,c) in enumerate(rows):w.writerow({"sequence":n,"timestamp":t,"can_id":c,"dlc":1,"data":"00","channel":"x","is_extended":"false"})
def s(sid,p):return {"session_id":sid,"evidence":{"raw_path":str(p),"capture_data_loss":False},"error":None}
def test_repeatability_six_modelled_trials(tmp_path):
    sessions=[]
    for role,prefix,fault in [("NORMAL_A","A",False),("FAULT_B","B",True)]:
        for trial in range(1,4):
            path=tmp_path/f"{prefix}{trial}.csv";start=trial*10+(100 if fault else 0);raw(path,start,fault)
            sessions.append(save_session(tmp_path,s(prefix+str(trial),path),role,trial=trial))
            add_marker(tmp_path,prefix+str(trial),"START",start)
    r=repeatability(tmp_path,sessions)
    assert r["normal_trials"]==3 and r["fault_trials"]==3
    sig={(x["can_id"],x["kind"]):x for x in r["signals"]}
    assert sig[("0x200","NEW_ID")]["reproduced_in_all_fault_trials"] is True
    assert sig[("0x300","NEW_ID")]["fault_trials_observed"]==3
    assert r["interpretation"].startswith("Repeatability")

def test_repeatability_blocks_data_loss(tmp_path):
    sessions=[]
    for role,prefix,fault in [("NORMAL_A","A",False),("FAULT_B","B",True)]:
        for trial in range(1,3):
            path=tmp_path/f"{prefix}{trial}.csv";start=trial*10+(100 if fault else 0);raw(path,start,fault)
            item=s(prefix+str(trial),path)
            if role=="FAULT_B" and trial==2: item["evidence"]["capture_data_loss"]=True
            sessions.append(save_session(tmp_path,item,role,trial=trial))
            add_marker(tmp_path,prefix+str(trial),"START",start)
    r=repeatability(tmp_path,sessions)
    assert r["status"]=="BLOCKED_DATA_LOSS"
    assert "B2" in r["sessions"]
