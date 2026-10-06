from pathlib import Path
import pytest
import app.capture.sd_prepare as sd


def test_non_windows_inspection_never_offers_automatic_format(monkeypatch,tmp_path):
    monkeypatch.setattr(sd.os,"name","posix")
    result=sd.inspect_target(tmp_path)
    assert result["supported"] is False
    assert result["safe_target"] is False
    assert "format" not in result or result.get("automatic_formatting") is not True


def test_windows_system_drive_is_blocked(monkeypatch):
    monkeypatch.setattr(sd.os,"name","nt")
    monkeypatch.setenv("SystemDrive","C:")
    result=sd.inspect_target(Path("C:/"))
    assert result["safe_target"] is False


def test_module_has_no_destructive_format_function():
    assert not hasattr(sd,"format_fat32")
