from app.core.config import get_settings
from app.utils.kinetics import gompertz_growth_curve
from app.utils.temperature_models import ratkowsky_mu_max, scaled_temperature_factor


PRODUCT_BASE_NMAX = {
    "deli_salad": 7.1,
    "dairy_dip": 7.4,
    "acidified_sauce": 5.9,
    "rte_meat": 8.0,
    "plant_based_spread": 6.7,
    "smoked_seafood": 7.2,
    "cooked_poultry": 7.8,
    "mayo_dressing": 6.0,
    "hummus_dip": 6.5,
    "soft_cheese": 7.3,
}


def estimate_mu_max(scenario: dict) -> float:
    settings = get_settings()
    base = ratkowsky_mu_max(scenario["storage_temperature_c"], settings.ratkowsky_b, settings.ratkowsky_tmin_c)
    aw_factor = max(0.0, (scenario["aw"] - 0.92) / 0.08)
    ph_factor = max(0.0, (scenario["ph"] - 4.4) / 1.8)
    preservative_factor = 0.72 if scenario["preservative_flag"] else 1.0
    return round(base * aw_factor * ph_factor * preservative_factor, 4)


def estimate_lag_time(scenario: dict) -> float:
    temp_factor = scaled_temperature_factor(
        scenario["storage_temperature_c"], get_settings().ratkowsky_b, get_settings().ratkowsky_tmin_c
    )
    lag = 5.5 - (temp_factor * 2.3)
    if scenario["preservative_flag"]:
        lag += 1.2
    lag += max(0.0, 5.1 - scenario["ph"]) * 1.0
    lag += max(0.0, 0.97 - scenario["aw"]) * 30.0
    return round(max(0.25, lag), 4)


def estimate_nmax(scenario: dict) -> float:
    nmax = PRODUCT_BASE_NMAX.get(scenario["product_category"], 7.0)
    nmax -= max(0.0, 5.0 - scenario["ph"]) * 0.55
    nmax -= max(0.0, 0.96 - scenario["aw"]) * 20.0
    nmax -= min(scenario["salt_percent"], 4.0) * 0.08
    nmax -= min(scenario["sugar_percent"], 8.0) * 0.04
    if scenario["preservative_flag"]:
        nmax -= 0.45
    if scenario["oxygen_condition"] == "anaerobic":
        nmax -= 0.2
    elif scenario["oxygen_condition"] == "reduced_oxygen":
        nmax -= 0.1
    return round(max(scenario["initial_inoculum_log_cfu_g"] + 0.2, nmax), 4)


def generate_kinetic_curve(scenario: dict) -> dict:
    days = build_day_grid(int(scenario["target_shelf_life_days"]))
    mu_max = estimate_mu_max(scenario)
    lag_time = estimate_lag_time(scenario)
    nmax = estimate_nmax(scenario)
    values = gompertz_growth_curve(days, scenario["initial_inoculum_log_cfu_g"], nmax, mu_max, lag_time)
    return {
        "days": days,
        "predicted_log_cfu_g": values,
        "model_name": "modified_gompertz",
        "mu_max": mu_max,
        "lag_time_days": lag_time,
        "nmax_log_cfu_g": nmax,
    }


def build_day_grid(target_shelf_life_days: int) -> list[int]:
    settings = get_settings()
    grid = list(settings.default_day_grid)
    target = int(max(target_shelf_life_days, 1))
    if target not in grid:
        grid.append(target)
    if target > max(grid):
        grid.extend(range(max(grid) + 7, target + 1, 7))
    return sorted(set(grid))
