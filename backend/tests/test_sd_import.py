import hashlib
from app.capture.sd_import import inspect_sd_logs,import_sd_log

def test_import_preserves_source_and_hash(tmp_path):
    card=tmp_path/"card";card.mkdir();src=card/"LOG001.csv";src.write_bytes(b"time,id,data\n0,100,00\n")
    before=src.read_bytes();logs=inspect_sd_logs(card)
    assert len(logs)==1
    result=import_sd_log(src,tmp_path/"captures")
    assert src.read_bytes()==before
    assert result["sha256"]==hashlib.sha256(before).hexdigest()
    assert result["parsed"] is False
