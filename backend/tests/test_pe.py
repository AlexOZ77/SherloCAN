import struct
from app.capture.j2534.pe import dll_architecture, architecture_compatible

def make_pe(path,machine):
    data=bytearray(256)
    data[0:2]=b"MZ"
    data[0x3C:0x40]=struct.pack("<I",0x80)
    data[0x80:0x84]=b"PE\0\0"
    data[0x84:0x86]=struct.pack("<H",machine)
    path.write_bytes(data)

def test_pe_x86(tmp_path):
    p=tmp_path/"driver.dll"; make_pe(p,0x014C)
    assert dll_architecture(p)=="x86"

def test_pe_x64(tmp_path):
    p=tmp_path/"driver.dll"; make_pe(p,0x8664)
    assert dll_architecture(p)=="x64"

def test_unknown_is_not_claimed_compatible(tmp_path):
    p=tmp_path/"bad.dll"; p.write_bytes(b"not a pe")
    assert dll_architecture(p)=="UNKNOWN"
    assert architecture_compatible("UNKNOWN") is None
