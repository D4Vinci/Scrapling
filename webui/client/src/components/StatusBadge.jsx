const COLOR_VARS = {
  pending: "var(--pending)",
  running: "var(--running)",
  success: "var(--success)",
  error: "var(--error)",
};

export default function StatusBadge({ status }) {
  return (
    <span className="status-badge" style={{ backgroundColor: COLOR_VARS[status] || "var(--pending)" }}>
      {status}
    </span>
  );
}
