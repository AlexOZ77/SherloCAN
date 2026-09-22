from pathlib import Path
from app.capture.replay import FileReplayAdapter

def test_replay_reads_frames(tmp_path: Path):
    source = tmp_path / "sample.csv"
    source.write_text(
        "timestamp,can_id,data,channel,is_extended\n"
        "0.000,0x123,010203,primary_can,false\n"
        "0.010,0x456,AABB,primary_can,false\n",
        encoding="utf-8",
    )
    adapter = FileReplayAdapter()
    adapter.open(path=source)
    frames = list(adapter.start())
    assert len(frames) == 2
    assert frames[0].can_id == 0x123
    assert frames[0].data == bytes.fromhex("010203")
    assert adapter.get_capabilities()["transmit"] is False
