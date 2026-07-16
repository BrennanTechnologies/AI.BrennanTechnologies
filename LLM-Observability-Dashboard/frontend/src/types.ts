/*
Author:  Chris Brennan
Company: Brennan Technologies, LLC
Email:   chris@brennantechnologies.com
Web:     https://www.brennantechnologies.com
*/

export type EventRow = {
	id: number;
	timestamp: string;
	request_id: string;
	model: string;
	provider: string;
	status: string;
	latency_ms: number;
	prompt_tokens: number;
	completion_tokens: number;
	total_tokens: number;
	cost_usd: number;
	input?: string;
	output?: string;
	metadata?: Record<string, unknown>;
};

export type SummaryMetrics = {
	total_requests: number;
	success_rate_pct: number;
	error_rate_pct: number;
	p50_latency_ms: number;
	p95_latency_ms: number;
	total_tokens: number;
	total_cost_usd: number;
};

export type TimeseriesPoint = {
	bucket_start: string;
	avg_latency_ms: number;
	error_rate_pct: number;
	requests: number;
};
