# Codex Worklog

## 2026-03-08

### Step 1

- Created the root project structure for backend, frontend, data, reports, scripts, and notebooks.
- Copied `synthetic_food_micro_challenge_train_100k.csv` into `data/raw/` as the canonical v1 dataset.
- Inspected the dataset schema to lock the practical feature and target design before implementation.

### Step 2

- Started implementing the backend application modules, training scripts, and core documentation scaffolding.
- Completed the backend core, services, schemas, API routes, model registry, dataset inspection script, training scripts, and initial tests.

### Step 3

- Built the Vite/React frontend MVP with a scenario form, chart, decision card, summary card, and loading state.
- Added run scripts, notebook scaffolding, package manifests, and supporting project files.

### Step 4

- Executed the dataset inspection script and saved `reports/dataset_inspection_report.json`.
- Installed `catboost`, trained the regression and classification models, and saved artifacts plus metadata in `backend/artifacts/`.
- Generated sample request and full-report JSON payloads under `reports/`.

### Step 5

- Verified the backend import path, pytest suite, model metadata evaluation, and full-report API flow.
- Installed frontend dependencies and completed a successful production `vite build`.
- Noted one frontend build warning about chunk size from Recharts/Vite bundling; the build still completed successfully.

### Step 6

- Updated `.gitignore` to include `catboost_info/` and `frontend/.vite-temp/` so generated training and frontend cache output stay untracked.

### Step 7

- Recreated `.gitignore` with the full ignore set after confirming the file had become empty.
- Included Python caches, frontend dependency/build directories, CatBoost training output, backend model artifacts, processed data, and generated report files.

## 2026-03-09

### Step 8

- Upgraded the backend to v2 with configurable summary provider settings, Ollama client scaffolding, structured summary prompt building, and deterministic fallback summary behavior.
- Added kinetic growth modelling, Ratkowsky temperature response helpers, plateau/Nmax estimation, sensitivity analysis, `curve_mode` support, and richer full-report plus `/predict/sensitivity` API outputs.

### Step 9

- Updated the React frontend for v2 with curve-mode selection, ML/kinetic overlay rendering, primary risk-driver display, and summary-provider visibility.

### Step 10

- Added GitHub Actions CI, expanded lightweight backend tests for v2 services and API shape, regenerated v2 sample outputs, and refreshed README documentation for Ollama, CI, and the new feature set.

### Step 11

- Tuned sensitivity-analysis runtime by lowering its internal Monte Carlo simulation count from the main risk-analysis default.
- Re-ran the v2 backend test suite successfully and regenerated the final v2 sample full-report and sensitivity payloads.
