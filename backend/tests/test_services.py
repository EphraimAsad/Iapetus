from app.services.decision_service import build_decision, latest_safe_day


def test_latest_safe_day_returns_last_safe_day():
    assert latest_safe_day([0, 7, 14], [0.0, 0.03, 0.2], 0.05) == 7


def test_build_decision_classifies_high_risk():
    monte_carlo = {
        "days": [0, 7, 14],
        "threshold_exceedance_probability_by_day": [0.0, 0.15, 0.35],
        "p10_log_cfu_g": [1.0, 1.2, 1.5],
        "p90_log_cfu_g": [1.2, 2.0, 2.8],
    }
    decision = build_decision(14, monte_carlo, 0.62)
    assert decision["growth_risk_class"] == "high"
    assert decision["challenge_test_recommended"] is True
    assert decision["study_level_classifier_probability"] == 0.62
