import Icon from "./Icons";

export default function StatCard({ label, value, hint, icon, tone = "default" }) {
  return (
    <article className={`stat-card stat-${tone}`}>
      <div className="stat-top">
        <span className="stat-icon">
          <Icon name={icon} size={20} />
        </span>
        <span className="stat-label">{label}</span>
      </div>
      <strong className="stat-value">{value}</strong>
      {hint && <span className="stat-hint">{hint}</span>}
    </article>
  );
}
