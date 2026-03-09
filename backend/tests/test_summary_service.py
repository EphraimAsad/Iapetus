from app.services.summary_prompt_builder import build_summary_prompt
from app.services.summary_service import generate_summary


PAYLOAD = {
    "scenario": {
        "product_category": "deli_salad",
        "pathogen": "Listeria monocytogenes",
        "ph": 5.0,
        "aw": 0.972,
        "storage_temperature_c": 4.0,
        "initial_inoculum_log_cfu_g": 1.06,
        "target_shelf_life_days": 21,
    },
    "curve": {"predicted_log_cfu_g": [1.0, 1.5]},
    "monte_carlo": {"uncertainty_drivers": ["storage_temperature_c", "ph"]},
    "decision": {
        "threshold_exceedance_probability": 0.054,
        "growth_risk_class": "moderate",
        "recommended_max_shelf_life_days": 14,
        "challenge_test_recommended": False,
    },
    "primary_risk_drivers": ["storage_temperature_c", "aw", "ph"],
}


def test_prompt_builder_contains_required_sections():
    prompt = build_summary_prompt({"product_category": "deli_salad", "primary_risk_drivers": ["ph"]})
    assert "System instruction:" in prompt
    assert "Structured data:" in prompt
    assert "Do not invent numbers." in prompt


def test_generate_summary_falls_back_when_ollama_disabled(monkeypatch):
    monkeypatch.setenv("OLLAMA_ENABLED", "false")
    monkeypatch.setenv("SUMMARY_PROVIDER", "ollama")
    from app.core.config import get_settings

    get_settings.cache_clear()
    result = generate_summary(PAYLOAD)
    assert result["summary_provider"] == "fallback"
    assert result["fallback_used"] is True
    assert "simulation-based" in result["summary"]
    get_settings.cache_clear()
