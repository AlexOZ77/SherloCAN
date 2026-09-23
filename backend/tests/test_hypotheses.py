from app.capture.hypotheses import evaluate_hypotheses

def test_no_evidence_means_not_tested():
    r=evaluate_hypotheses({"signals":[]})
    assert all(x["status"]=="NOT_TESTED" for x in r["hypotheses"])

def test_repeatable_can_observation_is_inconclusive_not_support():
    r=evaluate_hypotheses({"signals":[{"can_id":"0x200","kind":"NEW_ID","reproduced_in_all_fault_trials":True,"fault_trials_observed":3,"fault_trials_total":3}]})
    by={x["id"]:x for x in r["hypotheses"]}
    assert by["H2"]["status"]=="INCONCLUSIVE"
    assert by["H2"]["unknown"]

def test_direct_evidence_can_support_or_contradict():
    r=evaluate_hypotheses({"signals":[]},[
      {"hypothesis_id":"H1","verdict":"SUPPORTS","description":"Measured shutdown behavior matched the test criterion."},
      {"hypothesis_id":"H2","verdict":"CONTRADICTS","description":"Controlled connector test produced no correlated network disruption."},
    ])
    by={x["id"]:x for x in r["hypotheses"]}
    assert by["H1"]["status"]=="SUPPORTED"
    assert by["H2"]["status"]=="CONTRADICTED"
    assert "No automatic CONFIRMED" in r["rules"]
