from fastapi import APIRouter, HTTPException

from app.core.config import get_settings
from app.schemas.requests import ScenarioRequest
from app.schemas.responses import (
    CurveResponse,
    DecisionResponse,
    FullReportResponse,
    MonteCarloResponse,
    SensitivityResponse,
    SummaryResponse,
)
from app.services.curve_service import generate_curve_by_mode, generate_growth_curve
from app.services.decision_service import build_decision
from app.services.feature_builder import scenario_to_classifier_row
from app.services.kinetic_service import generate_kinetic_curve
from app.services.model_registry import load_model_bundle
from app.services.monte_carlo_service import run_monte_carlo
from app.services.sensitivity_service import primary_risk_drivers, run_sensitivity_analysis
from app.services.summary_service import generate_summary

router = APIRouter(prefix="/predict", tags=["predict"])


def _classifier_probability(scenario: dict) -> float | None:
    try:
        model, _ = load_model_bundle("classifier")
        frame = scenario_to_classifier_row(scenario)
        return float(model.predict_proba(frame)[0][1])
    except FileNotFoundError:
        return None


@router.post("/curve", response_model=CurveResponse)
def predict_curve(request: ScenarioRequest) -> CurveResponse:
    try:
        return CurveResponse(**generate_curve_by_mode(request.model_dump(), request.curve_mode))
    except FileNotFoundError as exc:
        raise HTTPException(status_code=503, detail=f"Regression model artifact not found: {exc}") from exc


@router.post("/monte-carlo", response_model=MonteCarloResponse)
def predict_monte_carlo(request: ScenarioRequest) -> MonteCarloResponse:
    try:
        mode = "kinetic" if request.curve_mode == "kinetic" else "ml"
        return MonteCarloResponse(**run_monte_carlo(request.model_dump(), curve_mode=mode))
    except FileNotFoundError as exc:
        raise HTTPException(status_code=503, detail=f"Regression model artifact not found: {exc}") from exc


@router.post("/decision", response_model=DecisionResponse)
def predict_decision(request: ScenarioRequest) -> DecisionResponse:
    scenario = request.model_dump()
    monte_carlo = run_monte_carlo(scenario, curve_mode="ml")
    return DecisionResponse(**build_decision(request.target_shelf_life_days, monte_carlo, _classifier_probability(scenario)))


@router.post("/summary", response_model=SummaryResponse)
def predict_summary(request: ScenarioRequest) -> SummaryResponse:
    scenario = request.model_dump()
    monte_carlo = run_monte_carlo(scenario, curve_mode="ml")
    decision = build_decision(request.target_shelf_life_days, monte_carlo, _classifier_probability(scenario))
    sensitivity = run_sensitivity_analysis(scenario)
    summary = generate_summary(
        {
            "scenario": scenario,
            "curve": generate_growth_curve(scenario),
            "monte_carlo": monte_carlo,
            "decision": decision,
            "primary_risk_drivers": primary_risk_drivers(sensitivity),
        }
    )
    return SummaryResponse(**summary)


@router.post("/sensitivity", response_model=SensitivityResponse)
def predict_sensitivity(request: ScenarioRequest) -> SensitivityResponse:
    return SensitivityResponse(**run_sensitivity_analysis(request.model_dump()))


@router.post("/full-report", response_model=FullReportResponse)
def full_report(request: ScenarioRequest) -> FullReportResponse:
    scenario = request.model_dump()
    ml_curve = generate_growth_curve(scenario)
    kinetic_curve = generate_kinetic_curve(scenario)
    selected_curve = generate_curve_by_mode(scenario, request.curve_mode)
    monte_carlo = run_monte_carlo(scenario, curve_mode="ml")
    sensitivity = run_sensitivity_analysis(scenario)
    driver_names = primary_risk_drivers(sensitivity)
    decision = build_decision(request.target_shelf_life_days, monte_carlo, _classifier_probability(scenario))
    summary = generate_summary(
        {
            "scenario": scenario,
            "curve": selected_curve,
            "ml_curve": ml_curve,
            "kinetic_curve": kinetic_curve if request.curve_mode in ("kinetic", "both") else None,
            "monte_carlo": monte_carlo,
            "decision": decision,
            "primary_risk_drivers": driver_names,
        }
    )
    metadata = {
        "app_version": get_settings().app_version,
        "dataset_version": get_settings().dataset_version,
        "threshold_cfu_g": get_settings().threshold_cfu_g,
        "simulation_based": True,
        "curve_mode": request.curve_mode,
    }
    return FullReportResponse(
        scenario=scenario,
        curve=CurveResponse(**selected_curve),
        ml_curve=CurveResponse(**ml_curve),
        kinetic_curve=CurveResponse(**kinetic_curve),
        monte_carlo=MonteCarloResponse(**monte_carlo),
        decision=DecisionResponse(**decision),
        summary=summary["summary"],
        summary_provider=summary["summary_provider"],
        summary_fallback_used=summary["fallback_used"],
        sensitivity_analysis=SensitivityResponse(**sensitivity),
        primary_risk_drivers=driver_names,
        metadata=metadata,
    )
