# Iapetus

Iapetus is a synthetic-first predictive food microbiology MVP for shelf-life risk modelling and challenge-test style simulation focused on *Listeria monocytogenes*. In v2 it predicts ML and kinetic growth curves, quantifies uncertainty, estimates threshold exceedance risk, ranks local risk drivers, and generates a concise simulation-based summary through either local Ollama or a deterministic fallback.

## Synthetic-First Warning

This MVP is trained on a synthetic dataset and is intended for exploratory simulation only. It is not a regulatory-grade validated model and should not be used as a substitute for formal shelf-life validation or challenge testing.

## Progress

- 2026-03-08: Bootstrapped repo structure, copied the canonical dataset to `data/raw/`, and started backend/training implementation.
- 2026-03-08: Completed the FastAPI backend, training scripts, React frontend MVP, tests, and local run scaffolding.
- 2026-03-08: Generated the dataset inspection report, trained both CatBoost models, saved artifacts, produced a sample full-report payload, and verified the frontend production build.
- 2026-03-08: Updated `.gitignore` to cover CatBoost training output and Vite temporary cache directories.
- 2026-03-08: Rebuilt `.gitignore` with the full intended ruleset, including explicit frontend build/dependency directories and backend/report artifact ignores.
- 2026-03-09: Completed the v2 backend upgrade with Ollama-ready summaries, kinetic curve modelling, sensitivity analysis, richer API responses, and `curve_mode` support.
- 2026-03-09: Completed the v2 frontend, CI workflow, expanded automated tests, and refreshed sample outputs/documentation.
- 2026-03-09: Tuned v2 sensitivity-analysis runtime and revalidated the backend test suite with refreshed final sample payloads.

## New In V2

- GitHub Actions CI for backend tests and frontend builds
- Local sensitivity analysis and ranked primary risk drivers
- Heuristic kinetic growth curves with lag, growth, and plateau behavior
- Ratkowsky-style temperature response for kinetic growth rate
- Local Ollama summaries using `qwen3.5:4b` with deterministic fallback
- `curve_mode` support for ML, kinetic, or both curves

## What The MVP Does

- Accepts a food microbiology scenario for *Listeria monocytogenes*.
- Predicts a time-series ML growth curve and a bounded kinetic curve in log CFU/g.
- Runs Monte Carlo simulation to estimate p10/p50/p90 bands and threshold exceedance probabilities.
- Classifies risk, recommends a conservative maximum shelf life, and flags whether challenge testing is recommended.
- Ranks local risk drivers through one-at-a-time perturbation analysis.
- Returns either an Ollama-generated summary or a deterministic fallback summary.

## Repository Layout

```text
backend/   FastAPI app, services, schemas, tests, training scripts, artifacts
frontend/  Vite + React MVP UI with Recharts
data/raw/  Canonical synthetic v1 CSV
reports/   Dataset inspection report and generated sample payloads
scripts/   Convenience run scripts
.github/   GitHub Actions CI workflow
```

## Setup

### Backend

```bash
python -m pip install -r backend/requirements.txt
```

### Frontend

```bash
cd frontend
npm install
```

## Environment Variables

Backend v2 supports:

```bash
SUMMARY_PROVIDER=ollama
OLLAMA_ENABLED=true
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=qwen3.5:4b
OLLAMA_TIMEOUT_SECONDS=8
RATKOWSKY_B=0.02
RATKOWSKY_TMIN_C=-1.5
IAPETUS_CURVE_MODE=both
```

If `OLLAMA_ENABLED=false` or Ollama is unavailable, summaries automatically fall back to the deterministic template path.

## Train Models

Run these from the repo root:

```bash
PYTHONPATH=backend python backend/training/inspect_dataset.py
PYTHONPATH=backend python backend/training/train_regressor.py
PYTHONPATH=backend python backend/training/train_classifier.py
PYTHONPATH=backend python backend/training/evaluate_models.py
```

Generated outputs:

- `reports/dataset_inspection_report.json`
- `backend/artifacts/regressor.joblib`
- `backend/artifacts/regressor_metadata.json`
- `backend/artifacts/classifier.joblib`
- `backend/artifacts/classifier_metadata.json`

## Run The Backend

Direct command:

```bash
PYTHONPATH=backend uvicorn app.main:app --app-dir backend --reload
```

Convenience script:

```bash
./scripts/run_backend.sh
```

Health check:

```bash
curl http://localhost:8000/health
```

## Run With Ollama

1. Install and run Ollama locally.
2. Pull the configured model:

```bash
ollama pull qwen3.5:4b
```

3. Start the backend with Ollama enabled:

```bash
SUMMARY_PROVIDER=ollama OLLAMA_ENABLED=true PYTHONPATH=backend uvicorn app.main:app --app-dir backend --reload
```

To force deterministic fallback:

```bash
SUMMARY_PROVIDER=ollama OLLAMA_ENABLED=false PYTHONPATH=backend uvicorn app.main:app --app-dir backend --reload
```

## Run The Frontend

```bash
cd frontend
npm run dev
```

Convenience script:

```bash
./scripts/run_frontend.sh
```

By default the frontend targets `http://localhost:8000`. Override with `VITE_API_BASE_URL` if needed.

## API Endpoints

- `POST /predict/curve`
- `POST /predict/monte-carlo`
- `POST /predict/decision`
- `POST /predict/summary`
- `POST /predict/sensitivity`
- `POST /predict/full-report`

## Example Scenario JSON

The generated sample input is saved at [`reports/sample_scenario.json`](/C:/Iapetus/reports/sample_scenario.json).

```json
{
  "product_category": "deli_salad",
  "intended_use": "ready_to_eat",
  "pathogen": "Listeria monocytogenes",
  "ph": 5.0,
  "aw": 0.972,
  "salt_percent": 2.1,
  "sugar_percent": 3.2,
  "fat_percent": 7.1,
  "preservative_flag": false,
  "preservative_type": "none",
  "acidulant_type": "vinegar",
  "packaging_type": "tub",
  "oxygen_condition": "aerobic",
  "storage_temperature_c": 4,
  "inoculation_type": "low_inoculum",
  "initial_inoculum_log_cfu_g": 1.06,
  "target_shelf_life_days": 21,
  "curve_mode": "both"
}
```

## Example Full-Report Response

The generated sample response is saved at [`reports/sample_full_report.json`](/C:/Iapetus/reports/sample_full_report.json).

```json
{
  "kinetic_curve": {
    "model_name": "modified_gompertz"
  },
  "decision": {
    "growth_risk_class": "moderate",
    "threshold_exceedance_probability": 0.054,
    "recommended_max_shelf_life_days": 14,
    "challenge_test_recommended": false,
    "confidence_label": "medium",
    "threshold_cfu_g": 100
  },
  "primary_risk_drivers": ["storage_temperature_c", "aw", "ph"],
  "summary_provider": "fallback",
  "summary": "For this deli_salad scenario stored at 4.0C, the simulation indicates a moderate risk profile with an estimated 5.4% probability of exceeding 100 CFU/g by day 21. The suggested maximum shelf life is 14 days. Challenge testing is not currently recommended. This is a simulation-based output, with primary risk drivers including storage_temperature_c, aw, ph; storage_temperature_c, fat_percent, initial_inoculum_log_cfu_g."
}
```

Additional generated payloads:

- [`reports/sample_full_report.json`](/C:/Iapetus/reports/sample_full_report.json)
- [`reports/sample_sensitivity.json`](/C:/Iapetus/reports/sample_sensitivity.json)

## Example Request

```bash
curl -X POST http://localhost:8000/predict/full-report \
  -H "Content-Type: application/json" \
  -d @reports/sample_scenario.json
```

## CI

The repo includes GitHub Actions CI at [`.github/workflows/ci.yml`](/C:/Iapetus/.github/workflows/ci.yml).

CI behavior:

- installs backend dependencies
- verifies backend imports
- runs dataset inspection
- runs backend pytest
- installs frontend dependencies with `npm ci`
- runs the frontend production build

CI does not retrain models and does not require a running Ollama instance.

## Real-Data Readiness

- Stable request schema retained even though the current dataset is single-organism and synthetic.
- Feature selection, validation, and artifact metadata are centralized in backend services.
- Dataset metadata tracks synthetic/source provenance and version.
- Summary generation supports optional local Ollama while remaining safe under fallback mode.
