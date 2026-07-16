/*
Author:  Chris Brennan
Company: Brennan Technologies, LLC
Email:   chris@brennantechnologies.com
Web:     https://www.brennantechnologies.com
*/

import type { EventRow, SummaryMetrics, TimeseriesPoint } from "./types";

const API_BASE = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

async function request<T>(path: string): Promise<T> {
	const response = await fetch(`${API_BASE}${path}`);
	if (!response.ok) {
		const body = await response.text();
		throw new Error(`API ${response.status}: ${body}`);
	}
	return response.json() as Promise<T>;
}

export function getSummary(windowMinutes = 180): Promise<SummaryMetrics> {
	return request<SummaryMetrics>(`/api/metrics/summary?window_minutes=${windowMinutes}`);
}

export function getTimeseries(windowMinutes = 180, bucketSeconds = 600): Promise<TimeseriesPoint[]> {
	return request<TimeseriesPoint[]>(
		`/api/metrics/timeseries?window_minutes=${windowMinutes}&bucket_seconds=${bucketSeconds}`,
	);
}

export function getTraces(limit = 30, status?: string, model?: string): Promise<EventRow[]> {
	const params = new URLSearchParams({ limit: String(limit), offset: "0" });
	if (status) {
		params.append("status", status);
	}
	if (model) {
		params.append("model", model);
	}
	return request<EventRow[]>(`/api/traces?${params.toString()}`);
}

export function seedData(): Promise<{ inserted: number }> {
	return fetch(`${API_BASE}/api/seed`, { method: "POST" }).then(async (response) => {
		if (!response.ok) {
			throw new Error(`Seed failed with ${response.status}`);
		}
		return response.json() as Promise<{ inserted: number }>;
	});
}
