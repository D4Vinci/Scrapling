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
        <label key={opt.name} className={`field${opt.type === "boolean" ? " field-toggle" : ""}`}>
          {opt.type === "boolean" ? (
            <span className="toggle-row">
              <span className="toggle-switch">
                <input
                  type="checkbox"
                  checked={values[opt.name] ?? opt.default ?? false}
                  onChange={(e) => onChange(opt.name, e.target.checked)}
                />
                <span className="toggle-track" aria-hidden="true" />
              </span>
              <span>{opt.label}</span>
            </span>
          ) : (
            <span>{opt.label}</span>
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
                  <label key={choice} className={`choice-pill${checked ? " is-selected" : ""}`}>
                    <input
                      type="checkbox"
                      checked={checked}
                      onChange={() => onChange(opt.name, toggleInArray(selected, choice))}
                    />
                    <CheckIcon />
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

function CheckIcon() {
  return (
    <svg className="choice-pill-check" width="10" height="10" viewBox="0 0 10 10" aria-hidden="true">
      <path d="M1.5 5l2.5 2.5L8.5 2" stroke="currentColor" strokeWidth="1.6" fill="none" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  );
}
