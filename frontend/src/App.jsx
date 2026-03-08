import { useState } from "react";

import { fetchFullReport } from "./api";
import { DecisionCard } from "./components/DecisionCard";
import { GrowthCurveChart } from "./components/GrowthCurveChart";
import { LoadingSpinner } from "./components/LoadingSpinner";
import { ScenarioForm } from "./components/ScenarioForm";
import { SummaryCard } from "./components/SummaryCard";
import "./styles/app.css";

const defaultForm = {
  product_category: "deli_salad",
  intended_use: "ready_to_eat",
  pathogen: "Listeria monocytogenes",
  ph: 5.0,
  aw: 0.972,
  salt_percent: 2.1,
  sugar_percent: 3.2,
  fat_percent: 7.1,
  preservative_flag: false,
  preservative_type: "none",
  acidulant_type: "vinegar",
  packaging_type: "tub",
  oxygen_condition: "aerobic",
  storage_temperature_c: 4,
  inoculation_type: "low_inoculum",
  initial_inoculum_log_cfu_g: 1.06,
  target_shelf_life_days: 21,
};

const numberFields = new Set([
  "ph",
  "aw",
  "salt_percent",
  "sugar_percent",
  "fat_percent",
  "storage_temperature_c",
  "initial_inoculum_log_cfu_g",
  "target_shelf_life_days",
]);

export default function App() {
  const [formData, setFormData] = useState(defaultForm);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  function handleChange(event) {
    const { name, value } = event.target;
    let nextValue = value;
    if (name === "preservative_flag") {
      nextValue = value === "true";
    } else if (numberFields.has(name)) {
      nextValue = value === "" ? "" : Number(value);
    }
    setFormData((current) => ({ ...current, [name]: nextValue }));
  }

  async function handleSubmit(event) {
    event.preventDefault();
    setLoading(true);
    setError("");
    try {
      const payload = {
        ...formData,
        target_shelf_life_days: Number(formData.target_shelf_life_days),
      };
      const response = await fetchFullReport(payload);
      setResult(response);
    } catch (submitError) {
      setError(submitError.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="app-shell">
      <header className="hero">
        <div>
          <p className="eyebrow">Iapetus</p>
          <h1>Shelf-Life Risk Engine</h1>
          <p className="hero-copy">
            Synthetic-first predictive microbiology for challenge-test style shelf-life simulation.
          </p>
        </div>
      </header>

      <main className="layout">
        <section className="panel">
          <div className="card">
            <h2>Scenario Input</h2>
            <ScenarioForm formData={formData} onChange={handleChange} onSubmit={handleSubmit} loading={loading} />
          </div>
        </section>
        <section className="panel results-panel">
          {loading && <LoadingSpinner />}
          {error && <div className="card error-card">{error}</div>}
          {!loading && !error && result && (
            <>
              <GrowthCurveChart result={result} />
              <DecisionCard decision={result.decision} />
              <SummaryCard summary={result.summary} uncertaintyDrivers={result.monte_carlo.uncertainty_drivers} />
            </>
          )}
          {!loading && !result && (
            <div className="card empty-state">
              Run a scenario to see the predicted growth curve, uncertainty band, and shelf-life recommendation.
            </div>
          )}
        </section>
      </main>
    </div>
  );
}
