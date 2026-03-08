from typing import Any


def build_decision(target_shelf_life_days: int, monte_carlo_output: dict[str, Any], classifier_probability: float | None = None) -> dict[str, Any]:
    days = monte_carlo_output["days"]
    probabilities = monte_carlo_output["threshold_exceedance_probability_by_day"]
    probability_at_target = _probability_at_day(target_shelf_life_days, days, probabilities)
    spread = estimate_uncertainty_width(monte_carlo_output)

    if probability_at_target < 0.05:
        risk_class = "low"
    elif probability_at_target < 0.20:
        risk_class = "moderate"
    else:
        risk_class = "high"

    decision = {
        "growth_risk_class": risk_class,
        "threshold_exceedance_probability": round(float(probability_at_target), 4),
        "recommended_max_shelf_life_days": int(latest_safe_day(days, probabilities, 0.05)),
        "challenge_test_recommended": bool(probability_at_target >= 0.10 or (0.05 <= probability_at_target < 0.15 and spread >= 0.75)),
        "confidence_label": "low" if spread >= 1.0 else "medium" if spread >= 0.5 else "high",
        "threshold_cfu_g": 100,
        "simulation_basis": "Synthetic-trained simulation output; not a regulatory-grade validated decision.",
    }
    if classifier_probability is not None:
        decision["study_level_classifier_probability"] = round(float(classifier_probability), 4)
    return decision


def latest_safe_day(days: list[int], probabilities: list[float], safe_probability: float) -> int:
    safe_days = [day for day, probability in zip(days, probabilities) if probability < safe_probability]
    return safe_days[-1] if safe_days else 0


def estimate_uncertainty_width(monte_carlo_output: dict[str, Any]) -> float:
    widths = [upper - lower for lower, upper in zip(monte_carlo_output["p10_log_cfu_g"], monte_carlo_output["p90_log_cfu_g"])]
    return float(max(widths)) if widths else 0.0


def _probability_at_day(target_day: int, days: list[int], probabilities: list[float]) -> float:
    if target_day in days:
        return float(probabilities[days.index(target_day)])
    for day, probability in zip(days, probabilities):
        if day > target_day:
            return float(probability)
    return float(probabilities[-1])
