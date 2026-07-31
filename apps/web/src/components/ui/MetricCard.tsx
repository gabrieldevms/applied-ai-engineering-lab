type MetricCardProps = {
  label: string;
  value: string | number;
  description?: string;
};

export function MetricCard({ label, value, description }: MetricCardProps) {
  return (
    <article className="metric-card">
      <span>{label}</span>
      <strong>{value}</strong>
      {description ? <small>{description}</small> : null}
    </article>
  );
}
