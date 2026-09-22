import csv
from app.capture.markers import add_marker,marker_time
from app.capture.divergence import first_divergence
FIELDS=["sequence","timestamp","can_id","dlc","data","channel","is_extended"]
def write(path,rows):
    with path.open("w",newline="",encoding="utf-8") as h:
        w=csv.DictWriter(h,fieldnames=FIELDS);w.writeheader()
        for n,(t,cid) in enumerate(rows):w.writerow({"sequence":n,"timestamp":t,"can_id":cid,"dlc":1,"data":"00","channel":"x","is_extended":"false"})

def test_modelled_start_aligned_flow(tmp_path):
    a=tmp_path/"a.csv";b=tmp_path/"b.csv"
    write(a,[(9.9,"0x100"),(10.0,"0x100"),(10.1,"0x100"),(10.2,"0x100")])
    write(b,[(19.9,"0x100"),(20.0,"0x100"),(20.1,"0x100"),(20.2,"0x100"),(20.42,"0x200"),(20.44,"0x300")])
    add_marker(tmp_path,"A","START",10.0,"modelled normal start")
    add_marker(tmp_path,"B","START",20.0,"modelled fault start")
    r=first_divergence(a,b,a_anchor=marker_time(tmp_path,"A","START"),b_anchor=marker_time(tmp_path,"B","START"),window_before=1,window_after=2,anchor_kind="START")
    assert r["alignment"]["marker"]=="START"
    assert abs(r["first_observed_change"]["at"]-.42)<1e-6
    assert r["first_observed_change"]["can_id"]=="0x200"
    assert r["multi_id_events"][0]["count"]==2
    assert r["causality"]=="NOT_ESTABLISHED"
