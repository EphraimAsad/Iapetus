# Iapetus

Iapetus is a synthetic-first predictive food microbiology MVP for shelf-life risk modelling and challenge-test style simulation focused on *Listeria monocytogenes*. It predicts a growth curve, quantifies uncertainty, estimates threshold exceedance risk, recommends a maximum shelf life, and generates a concise simulation-based summary.

## Synthetic-First Warning

This MVP is trained on a synthetic dataset and is intended for exploratory simulation only. It is not a regulatory-grade validated model and should not be used as a substitute for formal shelf-life validation or challenge testing.

## Progress

- 2026-03-08: Bootstrapped repo structure, copied the canonical dataset to `data/raw/`, and started backend/training implementation.
- 2026-03-08: Completed the FastAPI backend, training scripts, React frontend MVP, tests, and local run scaffolding.
- 2026-03-08: Generated the dataset inspection report, trained both CatBoost models, saved artifacts, produced a sample full-report payload, and verified the frontend production build.
- 2026-03-08: Updated `.gitignore` to cover CatBoost training output and Vite temporary cache directories.
- 2026-03-08: Rebuilt `.gitignore` with the full intended ruleset, including explicit frontend build/dependency directories and backend/report artifact ignores.

## What The MVP Does

- Accepts a food microbiology scenario for *Listeria monocytogenes*.
- Predicts a time-series growth curve in log CFU/g.
- Runs Monte Carlo simulation to estimate p10/p50/p90 bands and threshold exceedance probabilities.
- Classifies risk, recommends a conservative maximum shelf life, and flags whether challenge testing is recommended.
- Returns a deterministic plain-English summary designed to be replaceable later with a local LLM integration.

## Repository Layout

```text
backend/   FastAPI app, services, schemas, tests, training scripts, artifacts
frontend/  Vite + React MVP UI with Recharts
data/raw/  Canonical synthetic v1 CSV
reports/   Dataset inspection report and generated sample payloads
scripts/   Convenience run scripts
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
  "target_shelf_life_days": 21
}
```

## Example Full-Report Response

The generated sample response is saved at [`reports/sample_full_report.json`](/C:/Iapetus/reports/sample_full_report.json).

```json
{
  "decision": {
    "growth_risk_class": "moderate",
    "threshold_exceedance_probability": 0.054,
    "recommended_max_shelf_life_days": 14,
    "challenge_test_recommended": false,
    "confidence_label": "medium",
    "threshold_cfu_g": 100
  },
  "summary": "For this deli_salad scenario stored at 4.0C, the simulation indicates a moderate risk profile with an estimated 5.4% probability of exceeding 100 CFU/g by day 21. The suggested maximum shelf life is 14 days. Challenge testing is not currently recommended, and the output remains simulation-based with material uncertainty."
}
```

## Example Request

```bash
curl -X POST http://localhost:8000/predict/full-report \
  -H "Content-Type: application/json" \
  -d @reports/sample_scenario.json
```

## Real-Data Readiness

- Stable request schema retained even though the current dataset is single-organism and synthetic.
- Feature selection, validation, and artifact metadata are centralized in backend services.
- Dataset metadata tracks synthetic/source provenance and version.
- Summary generation includes an integration hook for future local Ollama/Qwen support.
