import hashlib
import struct
from pathlib import Path

import pytest

from app.capture.fnirsi_import import FNIRSIImportError, import_fnirsi_bmp, inspect_bmp


def _bmp(width=4, height=3):
    row = ((width * 3 + 3) // 4) * 4
    pixels = bytes(row * height)
    size = 54 + len(pixels)
    h = bytearray(54)
    h[:2] = b"BM"
    struct.pack_into("<I", h, 2, size)
    struct.pack_into("<I", h, 10, 54)
    struct.pack_into("<I", h, 14, 40)
    struct.pack_into("<i", h, 18, width)
    struct.pack_into("<i", h, 22, height)
    struct.pack_into("<H", h, 26, 1)
    struct.pack_into("<H", h, 28, 24)
    struct.pack_into("<I", h, 34, len(pixels))
    return bytes(h) + pixels


def test_fnirsi_bmp_import_preserves_evidence(tmp_path: Path):
    content = _bmp()
    result = import_fnirsi_bmp("PIC001.bmp", content, tmp_path, can_session_id="import-can")
    assert result["source_kind"] == "FNIRSI_2C53T_RENDERED_WAVEFORM"
    assert result["raw_adc_samples"] is False
    assert result["sync_status"] == "MANUAL_REQUIRED"
    assert result["sha256"] == hashlib.sha256(content).hexdigest()
    assert Path(result["source_path"]).read_bytes() == content
    assert result["bmp"]["width_px"] == 4
    assert result["bmp"]["height_px"] == 3


@pytest.mark.parametrize("name,content", [
    ("wave.png", b"BM" + bytes(100)),
    ("wave.bmp", b""),
    ("wave.bmp", b"not a bitmap"),
    ("wave.bmp", b"BM" + bytes(52)),
])
def test_invalid_fnirsi_artifacts_are_rejected(name, content):
    with pytest.raises(FNIRSIImportError):
        inspect_bmp(name, content)
