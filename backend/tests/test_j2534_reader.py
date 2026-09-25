import pytest
from app.capture.j2534.reader import normalize_raw_can

class Message:
    def __init__(self, data, rx_status=0, timestamp_us=0):
        self._data = bytes(data)
        self.RxStatus = rx_status
        self.Timestamp = timestamp_us
    def get_data(self):
        return self._data

def test_normalizes_four_byte_can_id_prefix():
    frame = normalize_raw_can(Message([0, 0, 1, 0x23, 0xAA, 0xBB]), timestamp=1.25)
    assert frame.can_id == 0x123
    assert frame.data == b"\xAA\xBB"
    assert frame.timestamp == 1.25
    assert frame.is_extended is False

def test_uses_rxstatus_for_29bit_identifier():
    frame = normalize_raw_can(Message([0x18, 0xFE, 0xF1, 0, 1, 2], rx_status=0x100), timestamp=2.0)
    assert frame.can_id == 0x18FEF100
    assert frame.data == b"\x01\x02"
    assert frame.is_extended is True

def test_uses_device_timestamp_microseconds_when_available():
    frame = normalize_raw_can(Message([0,0,1,0x23,0xAA], timestamp_us=1250000))
    assert frame.timestamp == 1.25

def test_rejects_truncated_identifier():
    with pytest.raises(ValueError):
        normalize_raw_can(Message([0, 1, 2]), timestamp=3.0)

class LegacyMessage:
    def __init__(self, data):
        self._data=data
    def get_data_bytes(self):
        return self._data

def test_legacy_data_accessor_remains_supported():
    frame=normalize_raw_can(LegacyMessage([0,0,1,0x23,0x11]),timestamp=1.0)
    assert frame.can_id==0x123 and frame.data==b"\x11"
