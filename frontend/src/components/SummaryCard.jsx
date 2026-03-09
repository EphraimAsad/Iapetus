export function SummaryCard({ summary, uncertaintyDrivers, summaryProvider, fallbackUsed }) {
  return (
    <div className="card">
      <h2>Summary</h2>
      <p>{summary}</p>
      <p className="summary-provider">
        Summary source: {summaryProvider}
        {fallbackUsed ? " (fallback active)" : ""}
      </p>
      <p className="drivers">Primary uncertainty drivers: {uncertaintyDrivers.join(", ")}</p>
    </div>
  );
}
