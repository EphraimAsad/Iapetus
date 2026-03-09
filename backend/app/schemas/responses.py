from typing import Any

from pydantic import BaseModel


class CurveResponse(BaseModel):
    days: list[int]
    predicted_log_cfu_g: list[float]
    model_name: str | None = None
    mu_max: float | None = None
    lag_time_days: float | None = None
    nmax_log_cfu_g: float | None = None


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
    summary_provider: str
    fallback_used: bool


class SensitivityDriverResponse(BaseModel):
    feature: str
    variant_value: str | float | bool
    impact_on_exceedance_probability: float
    impact_on_final_log_cfu_g: float
    impact_on_recommended_shelf_life_days: int
    direction: str


class SensitivityResponse(BaseModel):
    baseline: dict[str, Any]
    drivers: list[SensitivityDriverResponse]


class FullReportResponse(BaseModel):
    scenario: dict[str, Any]
    curve: CurveResponse
    ml_curve: CurveResponse | None = None
    kinetic_curve: CurveResponse | None = None
    monte_carlo: MonteCarloResponse
    decision: DecisionResponse
    summary: str
    summary_provider: str
    summary_fallback_used: bool
    sensitivity_analysis: SensitivityResponse
    primary_risk_drivers: list[str]
    metadata: dict[str, Any]
