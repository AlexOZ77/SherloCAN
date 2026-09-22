import pytest
from app.capture.j2534.channel_test import run_channel_test

def test_channel_requires_explicit_positive_bitrate():
    with pytest.raises(ValueError): run_channel_test(0,"CAN",0)

def test_channel_blocks_active_iso15765_mode():
    with pytest.raises(ValueError): run_channel_test(0,"ISO15765",500000)
