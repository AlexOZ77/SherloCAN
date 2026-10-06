from pathlib import Path

import pytest

from app.capture.can_log_import import CANLogImportError, import_can_log, parse_can_log
from app.capture.replay import FileReplayAdapter


def test_import_csv_normalizes_and_replays(tmp_path: Path):
    content = (
        b"timestamp,can_id,data,channel,is_extended\n"
        b"0.000,0x123,010203,primary_can,false\n"
        b"0.010,0x7DF,0201050000000000,primary_can,false\n"
    )
    result = import_can_log("vehicle.csv", content, tmp_path / "captures")
    assert result["parsed"] is True
    assert result["frame_count"] == 2
    assert result["unique_can_ids"] == 2
    assert result["read_only"] is True

    adapter = FileReplayAdapter()
    adapter.open(path=result["normalized_path"])
    frames = list(adapter.start())
    adapter.close()
    assert [f.can_id for f in frames] == [0x123, 0x7DF]
    assert frames[0].data == bytes.fromhex("010203")


def test_import_candump_text(tmp_path: Path):
    content = b"(0.100000) can0 123#010203\n(0.110000) can0 18DAF110#021001\n"
    result = import_can_log("capture.log", content, tmp_path / "captures")
    assert result["source_format"] == "CANDUMP_TEXT"
    assert result["frame_count"] == 2
    assert result["unique_can_ids"] == 2


@pytest.mark.parametrize("name,content,message", [
    ("bad.bin", b"abc", "unsupported CAN log extension"),
    ("empty.csv", b"", "CAN log is empty"),
    ("bad.csv", b"timestamp,can_id,data\n0.0,0x123,GG\n", "line 2"),
    ("bad.log", b"(0.1) can0 not-a-frame\n", "line 1"),
])
def test_invalid_import_is_rejected(name, content, message):
    with pytest.raises(CANLogImportError, match=message):
        parse_can_log(name, content)


def test_existing_replay_contract_remains_compatible(tmp_path: Path):
    source = tmp_path / "legacy.csv"
    source.write_text(
        "timestamp,can_id,data,channel,is_extended\n"
        "0.000,0x456,AABB,primary_can,false\n",
        encoding="utf-8",
    )
    adapter = FileReplayAdapter()
    adapter.open(path=source)
    frames = list(adapter.start())
    assert frames[0].can_id == 0x456
    assert adapter.get_capabilities() == {"read": True, "transmit": False, "replay": True}
