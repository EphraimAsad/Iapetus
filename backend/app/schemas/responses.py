from typing import Any

from pydantic import BaseModel


class CurveResponse(BaseModel):
    days: list[int]
    predicted_log_cfu_g: list[float]


class MonteCarloResponse(BaseModel):
    days: list[int]
    median_log_cfu_g: list[float]
    p10_log_cfu_g: list[float]
    p90_log_cfu_g: list[float]
    threshold_exceedance_probability_by_day: list[float]
    uncertainty_drivers: list[str]
    simulations: int


class DecisionResponse(BaseModel):
    growth_risk_class: str
    threshold_exceedance_probability: float
    recommended_max_shelf_life_days: int
    challenge_test_recommended: bool
    confidence_label: str
    threshold_cfu_g: int
    simulation_basis: str
    study_level_classifier_probability: float | None = None


class SummaryResponse(BaseModel):
    summary: str


class FullReportResponse(BaseModel):
    scenario: dict[str, Any]
    curve: CurveResponse
    monte_carlo: MonteCarloResponse
    decision: DecisionResponse
    summary: str
    metadata: dict[str, Any]
