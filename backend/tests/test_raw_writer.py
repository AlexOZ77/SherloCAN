import csv
from app.capture.base import CANFrame
from app.capture.raw_writer import RawCaptureWriter

def test_raw_writer_and_hash(tmp_path):
    path = tmp_path / "capture.csv"
    writer = RawCaptureWriter(path, flush_every=1)
    writer.open()
    writer.write(CANFrame(1.25, 0x123, bytes.fromhex("AABB")))
    digest = writer.close()
    assert len(digest) == 64
    assert writer.frame_count == 1
    with path.open(encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    assert rows[0]["can_id"] == "0x123"
    assert rows[0]["data"] == "AABB"
