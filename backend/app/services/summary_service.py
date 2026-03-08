from app.core.config import get_settings


def generate_summary(payload: dict) -> str:
    scenario = payload["scenario"]
    decision = payload["decision"]
    probability_pct = round(decision["threshold_exceedance_probability"] * 100, 1)
    recommendation = "recommended" if decision["challenge_test_recommended"] else "not currently recommended"
    return (
        f"For this {scenario['product_category']} scenario stored at {scenario['storage_temperature_c']}C, "
        f"the simulation indicates a {decision['growth_risk_class']} risk profile with an estimated {probability_pct}% "
        f"probability of exceeding 100 CFU/g by day {scenario['target_shelf_life_days']}. The suggested maximum shelf "
        f"life is {decision['recommended_max_shelf_life_days']} days. Challenge testing is {recommendation}, and the "
        f"output remains simulation-based with material uncertainty."
    )


def maybe_generate_with_ollama(prompt: str) -> str:
    if not get_settings().ollama_enabled:
        raise RuntimeError("Ollama integration is disabled in this MVP.")
    raise NotImplementedError("Future Ollama/Qwen integration hook is not implemented yet.")
