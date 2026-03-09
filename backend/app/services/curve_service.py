from typing import Any

import numpy as np

from app.core.config import get_settings
from app.services.feature_builder import scenario_to_regression_rows
from app.services.kinetic_service import generate_kinetic_curve
from app.services.model_registry import load_model_bundle


def build_day_grid(target_shelf_life_days: int, default_grid: list[int] | None = None) -> list[int]:
    settings = get_settings()
    grid = list(default_grid or settings.default_day_grid)
    target = int(max(target_shelf_life_days, 1))
    if target not in grid:
        grid.append(target)
    if target > max(grid):
        grid.extend(range(max(grid) + 7, target + 1, 7))
    return sorted(set(grid))


def generate_growth_curve(scenario: dict[str, Any]) -> dict[str, list[float] | list[int]]:
    days = build_day_grid(int(scenario["target_shelf_life_days"]))
    model, _ = load_model_bundle("regressor")
    features = scenario_to_regression_rows(scenario, days)
    predictions = _smooth_predictions(model.predict(features))
    return {
        "days": days,
        "predicted_log_cfu_g": [round(float(value), 4) for value in predictions],
    }


def generate_curve_by_mode(scenario: dict[str, Any], curve_mode: str | None = None) -> dict[str, Any]:
    mode = curve_mode or scenario.get("curve_mode") or get_settings().kinetic_curve_default_mode
    if mode == "kinetic":
        return generate_kinetic_curve(scenario)
    return generate_growth_curve(scenario)


def _smooth_predictions(predictions) -> np.ndarray:
    values = np.asarray(predictions, dtype=float)
    if len(values) < 3:
        return values
    smoothed = values.copy()
    for index in range(1, len(values) - 1):
        smoothed[index] = np.median(values[index - 1 : index + 2])
    return smoothed
