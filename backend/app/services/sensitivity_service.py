from copy import deepcopy

from app.core.config import get_settings
from app.services.curve_service import generate_curve_by_mode
from app.services.decision_service import build_decision
from app.services.monte_carlo_service import run_monte_carlo
from app.utils.validation import clamp

NUMERIC_PERTURBATIONS = {
    "ph": 0.1,
    "aw": 0.01,
    "storage_temperature_c": 1.0,
    "initial_inoculum_log_cfu_g": 0.25,
    "salt_percent": 0.2,
    "sugar_percent": 0.25,
    "fat_percent": 0.5,
}

CATEGORICAL_PERTURBATIONS = {
    "preservative_flag": [True, False],
    "preservative_type": ["none", "nisin", "potassium_sorbate"],
    "packaging_type": ["tub", "vacuum", "MAP"],
    "oxygen_condition": ["aerobic", "reduced_oxygen", "anaerobic"],
}


def run_sensitivity_analysis(scenario: dict) -> dict:
    settings = get_settings()
    baseline_curve = generate_curve_by_mode(scenario, "ml")
    baseline_monte = run_monte_carlo(scenario, simulations=settings.sensitivity_simulations, curve_mode="ml")
    baseline_decision = build_decision(scenario["target_shelf_life_days"], baseline_monte)
    baseline = _snapshot(baseline_curve, baseline_decision)

    drivers = []
    for feature, delta in NUMERIC_PERTURBATIONS.items():
        for direction in (-1, 1):
            updated = deepcopy(scenario)
            updated[feature] = round(_bounded_numeric_value(feature, updated[feature] + (delta * direction)), 4)
            drivers.append(_compare_variant(feature, updated, baseline, scenario, settings.sensitivity_simulations))

    for feature, options in CATEGORICAL_PERTURBATIONS.items():
        for option in options:
            if option == scenario[feature]:
                continue
            updated = deepcopy(scenario)
            updated[feature] = option
            if feature == "preservative_flag" and option is False:
                updated["preservative_type"] = "none"
            drivers.append(_compare_variant(feature, updated, baseline, scenario, settings.sensitivity_simulations))

    ranked = sorted(drivers, key=lambda item: abs(item["impact_on_exceedance_probability"]), reverse=True)
    return {
        "baseline": baseline,
        "drivers": ranked[:8],
    }


def _compare_variant(feature: str, variant: dict, baseline: dict, original: dict, simulations: int) -> dict:
    curve = generate_curve_by_mode(variant, "ml")
    monte = run_monte_carlo(variant, simulations=simulations, curve_mode="ml")
    decision = build_decision(variant["target_shelf_life_days"], monte)
    snapshot = _snapshot(curve, decision)
    probability_delta = round(snapshot["threshold_exceedance_probability"] - baseline["threshold_exceedance_probability"], 4)
    final_log_delta = round(snapshot["predicted_final_log_cfu_g"] - baseline["predicted_final_log_cfu_g"], 4)
    shelf_life_delta = snapshot["recommended_max_shelf_life_days"] - baseline["recommended_max_shelf_life_days"]
    direction = _direction_label(feature, original[feature], variant[feature], probability_delta)
    return {
        "feature": feature,
        "variant_value": variant[feature],
        "impact_on_exceedance_probability": probability_delta,
        "impact_on_final_log_cfu_g": final_log_delta,
        "impact_on_recommended_shelf_life_days": shelf_life_delta,
        "direction": direction,
    }


def primary_risk_drivers(sensitivity_analysis: dict, limit: int = 3) -> list[str]:
    return [driver["feature"] for driver in sensitivity_analysis.get("drivers", [])[:limit]]


def _snapshot(curve: dict, decision: dict) -> dict:
    return {
        "predicted_final_log_cfu_g": curve["predicted_log_cfu_g"][-1],
        "threshold_exceedance_probability": decision["threshold_exceedance_probability"],
        "recommended_max_shelf_life_days": decision["recommended_max_shelf_life_days"],
    }


def _bounded_numeric_value(feature: str, value: float) -> float:
    bounds = {
        "ph": (3.0, 7.2),
        "aw": (0.85, 0.999),
        "storage_temperature_c": (-2.0, 30.0),
        "initial_inoculum_log_cfu_g": (0.0, 4.0),
        "salt_percent": (0.0, 10.0),
        "sugar_percent": (0.0, 20.0),
        "fat_percent": (0.0, 60.0),
    }
    lower, upper = bounds[feature]
    return clamp(value, lower, upper)


def _direction_label(feature: str, original_value, variant_value, probability_delta: float) -> str:
    if isinstance(original_value, (int, float)):
        changed = "increase" if variant_value > original_value else "decrease"
        risk_effect = "raises risk" if probability_delta > 0 else "lowers risk"
        return f"{changed} {risk_effect}"
    return "change raises risk" if probability_delta > 0 else "change lowers risk"
