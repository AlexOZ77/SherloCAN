import pytest
from app.capture.experiment_protocol import ExperimentProtocol

def test_protocol_requires_explicit_bitrate_source():
    p=ExperimentProtocol("NORMAL_A",1,"ON","RUNNING",12.4,500000,"service-manual",0,1000,100)
    assert p.to_dict()["scenario"]=="NORMAL_A"

def test_protocol_rejects_unknown_bitrate_source():
    with pytest.raises(ValueError):
        ExperimentProtocol("NORMAL_A",1,"ON","RUNNING",12.4,500000,"",0,1000,100).validate()
