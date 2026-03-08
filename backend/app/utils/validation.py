from typing import Iterable


def ensure_required_columns(columns: Iterable[str], required_columns: list[str]) -> None:
    missing = sorted(set(required_columns) - set(columns))
    if missing:
        raise ValueError(f"Dataset is missing required columns: {', '.join(missing)}")


def clamp(value: float, lower: float, upper: float) -> float:
    return max(lower, min(value, upper))
