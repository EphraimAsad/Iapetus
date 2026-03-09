from app.services.kinetic_service import estimate_nmax, generate_kinetic_curve


SCENARIO = {
    "product_category": "deli_salad",
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


def test_generate_kinetic_curve_is_bounded():
    curve = generate_kinetic_curve(SCENARIO)
    assert curve["predicted_log_cfu_g"][0] >= SCENARIO["initial_inoculum_log_cfu_g"]
    assert curve["predicted_log_cfu_g"][-1] <= curve["nmax_log_cfu_g"]
    assert len(curve["days"]) == len(curve["predicted_log_cfu_g"])


def test_estimate_nmax_reduces_for_harsher_conditions():
    baseline = estimate_nmax(SCENARIO)
    harsher = estimate_nmax({**SCENARIO, "ph": 4.5, "aw": 0.94, "preservative_flag": True})
    assert harsher < baseline
