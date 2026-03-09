from app.services.sensitivity_service import primary_risk_drivers, run_sensitivity_analysis


SCENARIO = {
    "product_category": "deli_salad",
    "intended_use": "ready_to_eat",
    "pathogen": "Listeria monocytogenes",
    "ph": 5.0,
    "aw": 0.972,
    "salt_percent": 2.1,
    "sugar_percent": 3.2,
    "fat_percent": 7.1,
    "preservative_flag": False,
    "preservative_type": "none",
    "acidulant_type": "vinegar",
    "packaging_type": "tub",
    "oxygen_condition": "aerobic",
    "storage_temperature_c": 4.0,
    "inoculation_type": "low_inoculum",
    "initial_inoculum_log_cfu_g": 1.06,
    "target_shelf_life_days": 21,
}


def test_sensitivity_service_returns_ranked_drivers(monkeypatch):
    from app.services import sensitivity_service

    monkeypatch.setattr(
        sensitivity_service,
        "generate_curve_by_mode",
        lambda scenario, curve_mode: {"days": [0, 7], "predicted_log_cfu_g": [1.0, 1.0 + (scenario["storage_temperature_c"] / 10)]},
    )
    monkeypatch.setattr(
        sensitivity_service,
        "run_monte_carlo",
        lambda scenario, simulations=None, curve_mode="ml": {
            "days": [0, 7],
            "threshold_exceedance_probability_by_day": [0.0, scenario["storage_temperature_c"] / 100],
        },
    )
    monkeypatch.setattr(
        sensitivity_service,
        "build_decision",
        lambda target_days, monte_carlo, classifier_probability=None: {
            "threshold_exceedance_probability": monte_carlo["threshold_exceedance_probability_by_day"][-1],
            "recommended_max_shelf_life_days": max(0, 21 - int(monte_carlo["threshold_exceedance_probability_by_day"][-1] * 100)),
        },
    )
    analysis = run_sensitivity_analysis(SCENARIO)
    assert "baseline" in analysis
    assert len(analysis["drivers"]) > 0
    assert len(primary_risk_drivers(analysis)) == 3
