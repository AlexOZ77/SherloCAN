from app.capture.hypotheses import evaluate_hypotheses

def test_no_evidence_means_not_tested():
    r=evaluate_hypotheses({"signals":[]})
    assert all(x["status"]=="NOT_TESTED" for x in r["hypotheses"])

def test_repeatable_can_observation_supports_network_test_not_root_cause():
    r=evaluate_hypotheses({"signals":[{"can_id":"0x200","kind":"NEW_ID","reproduced_in_all_fault_trials":True,"fault_trials_observed":3,"fault_trials_total":3}]})
    by={x["id"]:x for x in r["hypotheses"]}
    assert by["H2"]["status"]=="SUPPORTED"
    assert by["H1"]["status"]=="INCONCLUSIVE"
    assert "not CONFIRMED" in r["rules"]
