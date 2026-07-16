/*
Author:  Chris Brennan
Company: Brennan Technologies, LLC
Email:   chris@brennantechnologies.com
Web:     https://www.brennantechnologies.com
*/

import type { EventRow } from "../types";

type TraceTableProps = {
	rows: EventRow[];
};

function formatDate(value: string): string {
	const date = new Date(value);
	return date.toLocaleString();
}

export function TraceTable({ rows }: TraceTableProps) {
	return (
		<section className="panel">
			<header>
				<h2>Recent Traces</h2>
				<span>Latest request-level events</span>
			</header>
			<div className="table-wrap">
				<table>
					<thead>
						<tr>
							<th>Time</th>
							<th>Request</th>
							<th>Model</th>
							<th>Status</th>
							<th>Latency</th>
							<th>Tokens</th>
							<th>Cost</th>
						</tr>
					</thead>
					<tbody>
						{rows.map((row) => (
							<tr key={row.id}>
								<td>{formatDate(row.timestamp)}</td>
								<td className="mono">{row.request_id}</td>
								<td>{row.model}</td>
								<td>
									<span className={`status status-${row.status === "success" ? "ok" : "error"}`}>
										{row.status}
									</span>
								</td>
								<td>{row.latency_ms} ms</td>
								<td>{row.total_tokens.toLocaleString()}</td>
								<td>${row.cost_usd.toFixed(4)}</td>
							</tr>
						))}
					</tbody>
				</table>
			</div>
		</section>
	);
}
