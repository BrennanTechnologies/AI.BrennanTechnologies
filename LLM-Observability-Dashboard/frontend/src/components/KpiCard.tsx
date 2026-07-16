/*
Author:  Chris Brennan
Company: Brennan Technologies, LLC
Email:   chris@brennantechnologies.com
Web:     https://www.brennantechnologies.com
*/

type KpiCardProps = {
	label: string;
	value: string;
	tone?: "neutral" | "good" | "warn";
};

export function KpiCard({ label, value, tone = "neutral" }: KpiCardProps) {
	return (
		<article className={`kpi kpi-${tone}`}>
			<p>{label}</p>
			<h3>{value}</h3>
		</article>
	);
}
