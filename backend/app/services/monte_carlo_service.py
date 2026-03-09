from typing import Any

import numpy as np

from app.core.config import get_settings
from app.services.curve_service import build_day_grid
from app.services.feature_builder import scenario_to_regression_rows
from app.services.kinetic_service import generate_kinetic_curve
from app.services.model_registry import load_model_bundle
from app.utils.validation import clamp

PERTURBATION_BOUNDS = {
    "ph": 0.08,
    "aw": 0.01,
    "storage_temperature_c": 0.7,
    "initial_inoculum_log_cfu_g": 0.25,
    "salt_percent": 0.15,
    "sugar_percent": 0.2,
    "fat_percent": 0.5,
}


def run_monte_carlo(scenario: dict[str, Any], simulations: int | None = None, curve_mode: str = "ml") -> dict[str, Any]:
    settings = get_settings()
    total = simulations or settings.default_simulations
    rng = np.random.default_rng(settings.monte_carlo_seed)
    model = None
    if curve_mode != "kinetic":
        model, _ = load_model_bundle("regressor")
    days = build_day_grid(int(scenario["target_shelf_life_days"]))

    curves = []
    sampled_inputs = []
    for _ in range(total):
        sampled = sample_scenario(scenario, rng)
        sampled_inputs.append(sampled)
        if curve_mode == "kinetic":
            curves.append(generate_kinetic_curve(sampled)["predicted_log_cfu_g"])
        else:
            frame = scenario_to_regression_rows(sampled, days)
            curves.append(model.predict(frame))

    curve_array = np.asarray(curves, dtype=float)
    probabilities = (curve_array >= settings.threshold_log_cfu_g).mean(axis=0)
    return {
        "days": days,
        "median_log_cfu_g": _round(np.median(curve_array, axis=0)),
        "p10_log_cfu_g": _round(np.percentile(curve_array, 10, axis=0)),
        "p90_log_cfu_g": _round(np.percentile(curve_array, 90, axis=0)),
        "threshold_exceedance_probability_by_day": _round(probabilities),
        "uncertainty_drivers": summarize_uncertainty_drivers(sampled_inputs),
        "simulations": total,
        "curve_mode": curve_mode,
    }


def sample_scenario(scenario: dict[str, Any], rng: np.random.Generator) -> dict[str, Any]:
    sampled = dict(scenario)
    sampled["ph"] = round(clamp(rng.normal(scenario["ph"], PERTURBATION_BOUNDS["ph"]), 3.0, 7.2), 4)
    sampled["aw"] = round(clamp(rng.normal(scenario["aw"], PERTURBATION_BOUNDS["aw"]), 0.85, 0.999), 4)
    sampled["storage_temperature_c"] = round(
        clamp(rng.normal(scenario["storage_temperature_c"], PERTURBATION_BOUNDS["storage_temperature_c"]), -2.0, 30.0), 4
    )
    sampled["initial_inoculum_log_cfu_g"] = round(
        clamp(rng.normal(scenario["initial_inoculum_log_cfu_g"], PERTURBATION_BOUNDS["initial_inoculum_log_cfu_g"]), 0.0, 4.0), 4
    )
    sampled["salt_percent"] = round(clamp(rng.normal(scenario["salt_percent"], PERTURBATION_BOUNDS["salt_percent"]), 0.0, 10.0), 4)
    sampled["sugar_percent"] = round(clamp(rng.normal(scenario["sugar_percent"], PERTURBATION_BOUNDS["sugar_percent"]), 0.0, 20.0), 4)
    sampled["fat_percent"] = round(clamp(rng.normal(scenario["fat_percent"], PERTURBATION_BOUNDS["fat_percent"]), 0.0, 60.0), 4)
    return sampled


def summarize_uncertainty_drivers(sampled_inputs: list[dict[str, Any]]) -> list[str]:
    if not sampled_inputs:
        return []
    spreads = {}
    for column in PERTURBATION_BOUNDS:
        spreads[column] = float(np.std([item[column] for item in sampled_inputs]))
    return [name for name, _ in sorted(spreads.items(), key=lambda item: item[1], reverse=True)[:3]]


def _round(values) -> list[float]:
    return [round(float(value), 4) for value in values]
