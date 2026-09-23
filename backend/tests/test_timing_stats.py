from app.capture.timing_stats import timing_summary

def test_timing_summary_reports_spread():
    x=timing_summary([0,.01,.02,.031,.04])
    assert x["sample_count"]==5
    assert x["median_period"] is not None
    assert x["mad_period"] is not None
    assert x["iqr_period"] is not None
