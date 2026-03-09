export function DecisionCard({ decision }) {
  return (
    <div className="card">
      <h2>Decision</h2>
      <div className="metric-grid">
        <div>
          <span className="metric-label">Risk Class</span>
          <strong>{decision.growth_risk_class}</strong>
        </div>
        <div>
          <span className="metric-label">Threshold Probability</span>
          <strong>{(decision.threshold_exceedance_probability * 100).toFixed(1)}%</strong>
        </div>
        <div>
          <span className="metric-label">Recommended Max Shelf Life</span>
          <strong>{decision.recommended_max_shelf_life_days} days</strong>
        </div>
        <div>
          <span className="metric-label">Challenge Test</span>
          <strong>{decision.challenge_test_recommended ? "Recommended" : "Not currently recommended"}</strong>
        </div>
        <div>
          <span className="metric-label">Confidence</span>
          <strong>{decision.confidence_label}</strong>
        </div>
        {decision.study_level_classifier_probability !== null && decision.study_level_classifier_probability !== undefined && (
          <div>
            <span className="metric-label">Study-Level Probability</span>
            <strong>{(decision.study_level_classifier_probability * 100).toFixed(1)}%</strong>
          </div>
        )}
      </div>
      <p className="disclaimer">{decision.simulation_basis}</p>
    </div>
  );
}
