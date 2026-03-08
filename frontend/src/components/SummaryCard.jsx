export function SummaryCard({ summary, uncertaintyDrivers }) {
  return (
    <div className="card">
      <h2>Summary</h2>
      <p>{summary}</p>
      <p className="drivers">Primary uncertainty drivers: {uncertaintyDrivers.join(", ")}</p>
    </div>
  );
}
