from fastapi.testclient import TestClient

from app.main import app


def test_full_report_endpoint_includes_v2_fields(monkeypatch):
    from app.api import routes_predict

    monkeypatch.setattr(routes_predict, "_classifier_probability", lambda scenario: 0.42)
    monkeypatch.setattr(routes_predict, "generate_growth_curve", lambda scenario: {"days": [0, 7], "predicted_log_cfu_g": [1.0, 1.3]})
    monkeypatch.setattr(
        routes_predict,
        "generate_kinetic_curve",
        lambda scenario: {
            "days": [0, 7],
            "predicted_log_cfu_g": [1.0, 1.2],
            "model_name": "modified_gompertz",
            "mu_max": 0.04,
            "lag_time_days": 1.5,
            "nmax_log_cfu_g": 6.8,
        },
    )
    monkeypatch.setattr(routes_predict, "generate_curve_by_mode", lambda scenario, curve_mode: {"days": [0, 7], "predicted_log_cfu_g": [1.0, 1.3]})
    monkeypatch.setattr(
        routes_predict,
        "run_monte_carlo",
        lambda scenario, curve_mode="ml": {
            "days": [0, 7],
            "median_log_cfu_g": [1.0, 1.2],
            "p10_log_cfu_g": [0.9, 1.0],
            "p90_log_cfu_g": [1.1, 1.4],
            "threshold_exceedance_probability_by_day": [0.0, 0.12],
            "uncertainty_drivers": ["storage_temperature_c", "ph"],
            "simulations": 10,
            "curve_mode": "ml",
        },
    )
    monkeypatch.setattr(
        routes_predict,
        "run_sensitivity_analysis",
        lambda scenario: {
            "baseline": {
                "predicted_final_log_cfu_g": 1.3,
                "threshold_exceedance_probability": 0.12,
                "recommended_max_shelf_life_days": 14,
            },
            "drivers": [
                {
                    "feature": "storage_temperature_c",
                    "variant_value": 5.0,
                    "impact_on_exceedance_probability": 0.12,
                    "impact_on_final_log_cfu_g": 0.3,
                    "impact_on_recommended_shelf_life_days": -7,
                    "direction": "increase raises risk",
                }
            ],
        },
    )
    monkeypatch.setattr(routes_predict, "primary_risk_drivers", lambda analysis: ["storage_temperature_c"])
    monkeypatch.setattr(
        routes_predict,
        "generate_summary",
        lambda payload: {"summary": "Fallback summary.", "summary_provider": "fallback", "fallback_used": True},
    )

    client = TestClient(app)
    payload = {
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
        "curve_mode": "both",
    }
    response = client.post("/predict/full-report", json=payload)
    body = response.json()
    assert response.status_code == 200
    assert "kinetic_curve" in body
    assert "sensitivity_analysis" in body
    assert body["summary_provider"] == "fallback"
