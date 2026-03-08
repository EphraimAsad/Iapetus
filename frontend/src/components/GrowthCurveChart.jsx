import {
  Area,
  AreaChart,
  CartesianGrid,
  Line,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

export function GrowthCurveChart({ result }) {
  const rows = result.monte_carlo.days.map((day, index) => ({
    day,
    median: result.monte_carlo.median_log_cfu_g[index],
    p10: result.monte_carlo.p10_log_cfu_g[index],
    p90: result.monte_carlo.p90_log_cfu_g[index],
  }));

  return (
    <div className="card chart-card">
      <h2>Growth Curve</h2>
      <ResponsiveContainer width="100%" height={320}>
        <AreaChart data={rows}>
          <CartesianGrid strokeDasharray="3 3" stroke="#d8ddd4" />
          <XAxis dataKey="day" label={{ value: "Day", position: "insideBottom", offset: -5 }} />
          <YAxis label={{ value: "log CFU/g", angle: -90, position: "insideLeft" }} />
          <Tooltip />
          <Area type="monotone" dataKey="p90" stroke="none" fill="#f0c36b" fillOpacity={0.24} />
          <Area type="monotone" dataKey="p10" stroke="none" fill="#f7f3ea" fillOpacity={1} />
          <Line type="monotone" dataKey="median" stroke="#264653" strokeWidth={3} dot={{ r: 3 }} />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
}
