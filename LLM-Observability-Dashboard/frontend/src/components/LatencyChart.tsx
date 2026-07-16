/*
Author:  Chris Brennan
Company: Brennan Technologies, LLC
Email:   chris@brennantechnologies.com
Web:     https://www.brennantechnologies.com
*/

import {
	CartesianGrid,
	Line,
	LineChart,
	ResponsiveContainer,
	Tooltip,
	XAxis,
	YAxis,
} from "recharts";

import type { TimeseriesPoint } from "../types";

type LatencyChartProps = {
	data: TimeseriesPoint[];
};

function shortTimestamp(iso: string): string {
	const d = new Date(iso);
	return `${String(d.getHours()).padStart(2, "0")}:${String(d.getMinutes()).padStart(2, "0")}`;
}

export function LatencyChart({ data }: LatencyChartProps) {
	return (
		<section className="panel chart-panel">
			<header>
				<h2>Latency and Errors</h2>
				<span>Time bucket trends</span>
			</header>
			<div className="chart-wrap">
				<ResponsiveContainer width="100%" height={320}>
					<LineChart data={data} margin={{ top: 16, right: 20, left: -8, bottom: 8 }}>
						<CartesianGrid strokeDasharray="4 4" stroke="rgba(255,255,255,0.12)" />
						<XAxis
							dataKey="bucket_start"
							tickFormatter={shortTimestamp}
							tick={{ fill: "#f5f7ff", fontSize: 12 }}
						/>
						<YAxis yAxisId="left" tick={{ fill: "#f5f7ff", fontSize: 12 }} />
						<YAxis yAxisId="right" orientation="right" tick={{ fill: "#f5f7ff", fontSize: 12 }} />
						<Tooltip
							contentStyle={{
								background: "#0b0f1f",
								border: "1px solid rgba(255,255,255,0.2)",
								borderRadius: "8px",
							}}
						/>
						<Line
							yAxisId="left"
							type="monotone"
							dataKey="avg_latency_ms"
							stroke="#58e1ff"
							strokeWidth={3}
							dot={false}
							name="Avg latency (ms)"
						/>
						<Line
							yAxisId="right"
							type="monotone"
							dataKey="error_rate_pct"
							stroke="#ff9f43"
							strokeWidth={3}
							dot={false}
							name="Error rate (%)"
						/>
					</LineChart>
				</ResponsiveContainer>
			</div>
		</section>
	);
}
