/*
Author:  Chris Brennan
Company: Brennan Technologies, LLC
Email:   chris@brennantechnologies.com
Web:     https://www.brennantechnologies.com
*/

import { useEffect, useMemo, useState } from "react";

import { getSummary, getTimeseries, getTraces, seedData } from "./api";
import { KpiCard } from "./components/KpiCard";
import { LatencyChart } from "./components/LatencyChart";
import { TraceTable } from "./components/TraceTable";
import type { EventRow, SummaryMetrics, TimeseriesPoint } from "./types";

const EMPTY_SUMMARY: SummaryMetrics = {
	total_requests: 0,
	success_rate_pct: 0,
	error_rate_pct: 0,
	p50_latency_ms: 0,
	p95_latency_ms: 0,
	total_tokens: 0,
	total_cost_usd: 0,
};

export default function App() {
	const [summary, setSummary] = useState<SummaryMetrics>(EMPTY_SUMMARY);
	const [timeseries, setTimeseries] = useState<TimeseriesPoint[]>([]);
	const [traces, setTraces] = useState<EventRow[]>([]);
	const [statusFilter, setStatusFilter] = useState("");
	const [modelFilter, setModelFilter] = useState("");
	const [loading, setLoading] = useState(true);
	const [errorMessage, setErrorMessage] = useState("");

	const models = useMemo(
		() => Array.from(new Set(traces.map((trace) => trace.model))).sort(),
		[traces],
	);

	async function refreshData() {
		try {
			setErrorMessage("");
			const [summaryData, timeseriesData, tracesData] = await Promise.all([
				getSummary(180),
				getTimeseries(180, 600),
				getTraces(30, statusFilter || undefined, modelFilter || undefined),
			]);
			setSummary(summaryData);
			setTimeseries(timeseriesData);
			setTraces(tracesData);
		} catch (error) {
			setErrorMessage(error instanceof Error ? error.message : "Unknown error");
		} finally {
			setLoading(false);
		}
	}

	async function handleSeed() {
		setLoading(true);
		await seedData();
		await refreshData();
	}

	useEffect(() => {
		void refreshData();
		const interval = setInterval(() => void refreshData(), 15000);
		return () => clearInterval(interval);
	}, [statusFilter, modelFilter]);

	return (
		<main>
			<div className="bg-grid" aria-hidden />
			<div className="bg-glow bg-glow-1" aria-hidden />
			<div className="bg-glow bg-glow-2" aria-hidden />

			<header className="hero">
				<div>
					<p className="eyebrow">LLM Operations Center</p>
					<h1>Observability Dashboard</h1>
					<p>Track reliability, latency, and cost in real time across all your AI workloads.</p>
				</div>
				<div className="hero-actions">
					<button onClick={() => void refreshData()} disabled={loading}>
						Refresh
					</button>
					<button onClick={() => void handleSeed()} className="secondary" disabled={loading}>
						Seed Demo Data
					</button>
				</div>
			</header>

			{errorMessage ? <div className="error">{errorMessage}</div> : null}

			<section className="kpi-grid">
				<KpiCard label="Requests" value={summary.total_requests.toLocaleString()} />
				<KpiCard label="P95 Latency" value={`${summary.p95_latency_ms} ms`} tone="warn" />
				<KpiCard label="Error Rate" value={`${summary.error_rate_pct}%`} tone="warn" />
				<KpiCard label="Tokens" value={summary.total_tokens.toLocaleString()} />
				<KpiCard label="Cost" value={`$${summary.total_cost_usd.toFixed(4)}`} />
			</section>

			<section className="controls panel">
				<header>
					<h2>Filters</h2>
				</header>
				<div className="filter-row">
					<label>
						Status
						<select value={statusFilter} onChange={(e) => setStatusFilter(e.target.value)}>
							<option value="">All</option>
							<option value="success">Success</option>
							<option value="error">Error</option>
						</select>
					</label>
					<label>
						Model
						<select value={modelFilter} onChange={(e) => setModelFilter(e.target.value)}>
							<option value="">All</option>
							{models.map((m) => (
								<option key={m} value={m}>
									{m}
								</option>
							))}
						</select>
					</label>
				</div>
			</section>

			<LatencyChart data={timeseries} />
			<TraceTable rows={traces} />
		</main>
	);
}
