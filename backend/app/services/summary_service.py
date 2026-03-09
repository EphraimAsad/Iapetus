from app.core.config import get_settings
from app.services.ollama_client import OllamaUnavailableError, generate_text
from app.services.summary_prompt_builder import build_summary_prompt


def generate_summary(payload: dict) -> dict[str, str | bool]:
    settings = get_settings()
    summary_input = build_summary_input(payload)
    if settings.summary_provider == "ollama" and settings.ollama_enabled:
        try:
            prompt = build_summary_prompt(summary_input)
            return {
                "summary": generate_text(prompt),
                "summary_provider": "ollama",
                "fallback_used": False,
            }
        except OllamaUnavailableError:
            pass
    return {
        "summary": deterministic_summary(summary_input),
        "summary_provider": "fallback",
        "fallback_used": True,
    }


def build_summary_input(payload: dict) -> dict:
    scenario = payload["scenario"]
    decision = payload["decision"]
    primary_risk_drivers = payload.get("primary_risk_drivers", [])
    curve = payload.get("curve") or payload.get("ml_curve") or {}
    predicted_final = curve.get("predicted_log_cfu_g", [None])[-1]
    uncertainty_drivers = payload.get("monte_carlo", {}).get("uncertainty_drivers", [])
    return {
        "product_category": scenario["product_category"],
        "pathogen": scenario["pathogen"],
        "ph": scenario["ph"],
        "aw": scenario["aw"],
        "storage_temperature_c": scenario["storage_temperature_c"],
        "initial_inoculum_log_cfu_g": scenario["initial_inoculum_log_cfu_g"],
        "target_shelf_life_days": scenario["target_shelf_life_days"],
        "predicted_final_log_cfu_g": predicted_final,
        "threshold_exceedance_probability": decision["threshold_exceedance_probability"],
        "growth_risk_class": decision["growth_risk_class"],
        "recommended_max_shelf_life_days": decision["recommended_max_shelf_life_days"],
        "challenge_test_recommended": decision["challenge_test_recommended"],
        "primary_risk_drivers": primary_risk_drivers,
        "uncertainty_note": ", ".join(uncertainty_drivers[:3]),
        "kinetic_curve_used": payload.get("kinetic_curve") is not None,
    }


def deterministic_summary(summary_input: dict) -> str:
    probability_pct = round(summary_input["threshold_exceedance_probability"] * 100, 1)
    recommendation = "recommended" if summary_input["challenge_test_recommended"] else "not currently recommended"
    drivers = ", ".join(summary_input["primary_risk_drivers"][:3]) or "temperature and formulation factors"
    uncertainty_note = summary_input["uncertainty_note"] or "the scenario remains uncertainty-sensitive"
    return (
        f"For this {summary_input['product_category']} scenario stored at {summary_input['storage_temperature_c']}C, "
        f"the simulation indicates a {summary_input['growth_risk_class']} risk profile with an estimated {probability_pct}% "
        f"probability of exceeding 100 CFU/g by day {summary_input['target_shelf_life_days']}. "
        f"The suggested maximum shelf life is {summary_input['recommended_max_shelf_life_days']} days, and challenge testing is "
        f"{recommendation}. This is a simulation-based output, with primary risk drivers including {drivers}; "
        f"{uncertainty_note}."
    )
