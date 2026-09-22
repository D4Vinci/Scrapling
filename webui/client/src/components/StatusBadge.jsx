const COLORS = {
  pending: "#888",
  running: "#0077cc",
  success: "#2e7d32",
  error: "#c62828",
};

export default function StatusBadge({ status }) {
  return (
    <span className="status-badge" style={{ backgroundColor: COLORS[status] || "#888" }}>
      {status}
    </span>
  );
}
