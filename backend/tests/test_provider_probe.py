from app.capture.j2534.provider import probe_providers

def test_provider_probe_never_requires_optional_packages():
    providers=probe_providers()
    names={p.name for p in providers}
    assert "j2534-api" in names
    assert "python-can" in names
    assert "cantools" in names
    assert all(isinstance(p.installed,bool) for p in providers)
