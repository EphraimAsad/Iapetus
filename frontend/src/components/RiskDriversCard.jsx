export function RiskDriversCard({ drivers }) {
  const maxImpact = Math.max(...drivers.map((driver) => Math.abs(driver.impact_on_exceedance_probability)), 0.001);

  return (
    <div className="card">
      <h2>Primary Risk Drivers</h2>
      <div className="driver-list">
        {drivers.map((driver) => {
          const width = `${(Math.abs(driver.impact_on_exceedance_probability) / maxImpact) * 100}%`;
          return (
            <div key={`${driver.feature}-${driver.variant_value}`} className="driver-item">
              <div className="driver-header">
                <strong>{driver.feature}</strong>
                <span>{driver.direction}</span>
              </div>
              <div className="driver-bar-track">
                <div className="driver-bar-fill" style={{ width }} />
              </div>
              <div className="driver-metrics">
                <span>Risk delta: {(driver.impact_on_exceedance_probability * 100).toFixed(1)}%</span>
                <span>Final log delta: {driver.impact_on_final_log_cfu_g.toFixed(2)}</span>
                <span>Shelf-life delta: {driver.impact_on_recommended_shelf_life_days} days</span>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
