from app.utils.validation import clamp


def ratkowsky_mu_max(temperature_c: float, b: float, t_min_c: float) -> float:
    if temperature_c <= t_min_c:
        return 0.0
    return max(0.0, (b * (temperature_c - t_min_c)) ** 2)


def scaled_temperature_factor(temperature_c: float, b: float, t_min_c: float) -> float:
    mu = ratkowsky_mu_max(temperature_c, b, t_min_c)
    return clamp(mu / 0.25 if mu > 0 else 0.0, 0.0, 2.0)
