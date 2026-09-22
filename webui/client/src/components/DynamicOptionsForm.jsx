export default function DynamicOptionsForm({ options, values, onChange }) {
  return (
    <div className="options-grid">
      {options.map((opt) => (
        <label key={opt.name} className="field">
          <span>{opt.label}</span>
          {opt.type === "boolean" && (
            <input
              type="checkbox"
              checked={values[opt.name] ?? opt.default ?? false}
              onChange={(e) => onChange(opt.name, e.target.checked)}
            />
          )}
          {opt.type === "number" && (
            <input
              type="number"
              value={values[opt.name] ?? opt.default ?? ""}
              onChange={(e) => onChange(opt.name, e.target.value === "" ? "" : Number(e.target.value))}
            />
          )}
          {opt.type === "list" && (
            <textarea
              rows={2}
              placeholder="one per line"
              value={values[opt.name] ?? ""}
              onChange={(e) => onChange(opt.name, e.target.value)}
            />
          )}
          {opt.type === "string" && (
            <input type="text" value={values[opt.name] ?? opt.default ?? ""} onChange={(e) => onChange(opt.name, e.target.value)} />
          )}
        </label>
      ))}
    </div>
  );
}
