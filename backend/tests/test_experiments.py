import csv
from app.capture.experiments import save_session,load_sessions,compare_sessions

def raw(path,ids):
    with path.open("w",newline="",encoding="utf-8") as h:
        w=csv.DictWriter(h,fieldnames=["can_id"]);w.writeheader()
        for i in ids:w.writerow({"can_id":i})

def session(sid,path):
    return {"session_id":sid,"started_at":"x","completed_at":"y","error":None,
            "evidence":{"raw_path":str(path),"capture_data_loss":False}}

def test_save_and_compare(tmp_path):
    a=tmp_path/"a.csv";b=tmp_path/"b.csv"
    raw(a,["0x100","0x100","0x200"]);raw(b,["0x100","0x300"])
    sa=save_session(tmp_path,session("A",a),"NORMAL_A","normal")
    sb=save_session(tmp_path,session("B",b),"FAULT_B","fault")
    assert len(load_sessions(tmp_path))==2
    result=compare_sessions(sa,sb)
    rows={x["can_id"]:x for x in result["ids"]}
    assert rows["0x100"]["delta"]==-1
    assert rows["0x200"]["presence"]=="NORMAL_ONLY"
    assert rows["0x300"]["presence"]=="FAULT_ONLY"
    assert "root cause" in result["interpretation"]
