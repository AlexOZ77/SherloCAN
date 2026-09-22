import csv
from app.capture.divergence import first_divergence

FIELDS=["sequence","timestamp","can_id","dlc","data","channel","is_extended"]
def write(path,rows):
    with path.open("w",newline="",encoding="utf-8") as h:
        w=csv.DictWriter(h,fieldnames=FIELDS);w.writeheader()
        for n,(t,cid) in enumerate(rows):w.writerow({"sequence":n,"timestamp":t,"can_id":cid,"dlc":1,"data":"00","channel":"x","is_extended":"false"})

def test_first_divergence_detects_new_ids_and_cluster(tmp_path):
    a=tmp_path/"a.csv";b=tmp_path/"b.csv"
    write(a,[(0.0,"0x100"),(.1,"0x100"),(.2,"0x100")])
    write(b,[(0.0,"0x100"),(.1,"0x100"),(.2,"0x100"),(.30,"0x200"),(.32,"0x300")])
    r=first_divergence(a,b)
    assert r["first_observed_change"]["kind"]=="NEW_ID"
    assert r["first_observed_change"]["can_id"]=="0x200"
    assert r["multi_id_events"][0]["count"]==2
    assert r["causality"]=="NOT_ESTABLISHED"
    assert r["ecu_ownership"]=="UNKNOWN"
