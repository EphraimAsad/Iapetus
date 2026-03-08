from fastapi import APIRouter, HTTPException

from app.core.config import get_settings
from app.schemas.requests import ScenarioRequest
from app.schemas.responses import CurveResponse, DecisionResponse, FullReportResponse, MonteCarloResponse, SummaryResponse
from app.services.curve_service import generate_growth_curve
from app.services.decision_service import build_decision
from app.services.feature_builder import scenario_to_classifier_row
from app.services.model_registry import load_model_bundle
from app.services.monte_carlo_service import run_monte_carlo
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
        return CurveResponse(**generate_growth_curve(request.model_dump()))
    except FileNotFoundError as exc:
        raise HTTPException(status_code=503, detail=f"Regression model artifact not found: {exc}") from exc


@router.post("/monte-carlo", response_model=MonteCarloResponse)
def predict_monte_carlo(request: ScenarioRequest) -> MonteCarloResponse:
    try:
        return MonteCarloResponse(**run_monte_carlo(request.model_dump()))
    except FileNotFoundError as exc:
        raise HTTPException(status_code=503, detail=f"Regression model artifact not found: {exc}") from exc


@router.post("/decision", response_model=DecisionResponse)
def predict_decision(request: ScenarioRequest) -> DecisionResponse:
    scenario = request.model_dump()
    monte_carlo = run_monte_carlo(scenario)
    return DecisionResponse(**build_decision(request.target_shelf_life_days, monte_carlo, _classifier_probability(scenario)))


@router.post("/summary", response_model=SummaryResponse)
def predict_summary(request: ScenarioRequest) -> SummaryResponse:
    scenario = request.model_dump()
    monte_carlo = run_monte_carlo(scenario)
    decision = build_decision(request.target_shelf_life_days, monte_carlo, _classifier_probability(scenario))
    return SummaryResponse(summary=generate_summary({"scenario": scenario, "monte_carlo": monte_carlo, "decision": decision}))


@router.post("/full-report", response_model=FullReportResponse)
def full_report(request: ScenarioRequest) -> FullReportResponse:
    scenario = request.model_dump()
    curve = generate_growth_curve(scenario)
    monte_carlo = run_monte_carlo(scenario)
    decision = build_decision(request.target_shelf_life_days, monte_carlo, _classifier_probability(scenario))
    metadata = {
        "app_version": get_settings().app_version,
        "dataset_version": get_settings().dataset_version,
        "threshold_cfu_g": get_settings().threshold_cfu_g,
        "simulation_based": True,
    }
    return FullReportResponse(
        scenario=scenario,
        curve=CurveResponse(**curve),
        monte_carlo=MonteCarloResponse(**monte_carlo),
        decision=DecisionResponse(**decision),
        summary=generate_summary({"scenario": scenario, "curve": curve, "monte_carlo": monte_carlo, "decision": decision}),
        metadata=metadata,
    )
