import { useEffect, useRef, useState } from "react";

// A combobox for picking an existing output folder or typing a new one.
// Replaces a bare `<input list>` datalist, whose "menu" is invisible/inert in
// enough browsers (no visible affordance, no click-to-open) that it read as
// broken. This renders its own dropdown so there's always something to click.
export default function FolderPicker({ value, onChange, folders }) {
  const [open, setOpen] = useState(false);
  const rootRef = useRef(null);

  useEffect(() => {
    function onClickOutside(e) {
      if (rootRef.current && !rootRef.current.contains(e.target)) setOpen(false);
    }
    document.addEventListener("mousedown", onClickOutside);
    return () => document.removeEventListener("mousedown", onClickOutside);
  }, []);

  const filtered = folders.filter((f) => f.toLowerCase().includes(value.trim().toLowerCase()));

  return (
    <div className="combobox" ref={rootRef}>
      <div className="combobox-row">
        <input
          type="text"
          role="combobox"
          aria-expanded={open}
          aria-haspopup="listbox"
          value={value}
          onChange={(e) => {
            onChange(e.target.value);
            setOpen(true);
          }}
          onFocus={() => setOpen(true)}
          onKeyDown={(e) => e.key === "Escape" && setOpen(false)}
          placeholder="(default output folder)"
        />
        <button
          type="button"
          className="combobox-toggle"
          aria-label={open ? "Hide folder list" : "Show existing folders"}
          onClick={() => setOpen((o) => !o)}
        >
          <ChevronIcon open={open} />
        </button>
      </div>

      {open && (
        <ul className="combobox-menu" role="listbox">
          <li role="option" aria-selected={value === ""}>
            <button type="button" onClick={() => { onChange(""); setOpen(false); }}>
              <em>(default output folder)</em>
            </button>
          </li>
          {filtered.map((f) => (
            <li key={f} role="option" aria-selected={f === value}>
              <button type="button" onClick={() => { onChange(f); setOpen(false); }}>
                {f}
              </button>
            </li>
          ))}
          {filtered.length === 0 && value.trim() && (
            <li className="combobox-hint">
              <em>"{value.trim()}" will be created as a new folder</em>
            </li>
          )}
          {folders.length === 0 && !value.trim() && (
            <li className="combobox-hint">
              <em>No folders yet — type a name to create one</em>
            </li>
          )}
        </ul>
      )}
    </div>
  );
}

function ChevronIcon({ open }) {
  return (
    <svg width="12" height="12" viewBox="0 0 12 12" style={{ transform: open ? "rotate(180deg)" : "none" }}>
      <path d="M2 4l4 4 4-4" stroke="currentColor" strokeWidth="1.6" fill="none" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  );
}
