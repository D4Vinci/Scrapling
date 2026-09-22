function toggleInArray(array, item) {
  const set = new Set(array);
  if (set.has(item)) set.delete(item);
  else set.add(item);
  return [...set];
}

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
              placeholder={opt.placeholder ?? "one per line"}
              value={values[opt.name] ?? ""}
              onChange={(e) => onChange(opt.name, e.target.value)}
            />
          )}

          {opt.type === "multiselect" && (
            <div className="choice-row" role="group" aria-label={opt.label}>
              {opt.choices.map((choice) => {
                const selected = values[opt.name] ?? [];
                const checked = selected.includes(choice);
                return (
                  <label key={choice} className="choice-pill">
                    <input
                      type="checkbox"
                      checked={checked}
                      onChange={() => onChange(opt.name, toggleInArray(selected, choice))}
                    />
                    {choice}
                  </label>
                );
              })}
            </div>
          )}

          {opt.type === "string" && (
            <input
              type="text"
              placeholder={opt.placeholder}
              value={values[opt.name] ?? opt.default ?? ""}
              onChange={(e) => onChange(opt.name, e.target.value)}
            />
          )}

          {opt.hint && <small className="hint">{opt.hint}</small>}
        </label>
      ))}
    </div>
  );
}
