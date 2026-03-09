import math

import numpy as np


def gompertz_growth_curve(days: list[int], n0: float, nmax: float, mu_max: float, lag_time: float) -> list[float]:
    values = []
    if nmax <= n0:
        return [round(float(n0), 4) for _ in days]

    span = max(nmax - n0, 0.001)
    growth_term = (mu_max * math.e / span) if span else 0.0
    for day in days:
        exponent = -math.exp(growth_term * (lag_time - day) + 1.0)
        value = n0 + span * math.exp(exponent)
        values.append(round(float(min(max(value, n0), nmax)), 4))
    return values


def final_value(values: list[float]) -> float:
    return float(values[-1]) if values else 0.0


def monotonic_cap(values: list[float], cap: float) -> list[float]:
    if not values:
        return []
    bounded = np.minimum.accumulate(np.array(values[::-1], dtype=float))[::-1]
    bounded = np.minimum(bounded, cap)
    return [round(float(item), 4) for item in bounded]
