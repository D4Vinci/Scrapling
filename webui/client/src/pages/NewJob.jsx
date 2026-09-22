import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { createJob, getOptionsSchema } from "../api.js";
import DynamicOptionsForm from "../components/DynamicOptionsForm.jsx";
import UrlPreview from "../components/UrlPreview.jsx";

const URL_HINT = "The page to fetch and extract from.";
const FETCHER_HINT_SUFFIX =
  " Not sure which to use? Click \"Fetch Page\" below to analyze the page first — it'll suggest one.";

export default function NewJob() {
  const [schema, setSchema] = useState(null);
  const [fetcherType, setFetcherType] = useState("get");
  const [url, setUrl] = useState("");
  const [outputFormat, setOutputFormat] = useState("html");
  const [values, setValues] = useState({});
  const [error, setError] = useState(null);
  const [submitting, setSubmitting] = useState(false);
  const [activeHint, setActiveHint] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    getOptionsSchema()
      .then((s) => {
        setSchema(s);
        if (!s.outputFormats.some((f) => f.value === outputFormat)) setOutputFormat(s.outputFormats[0]?.value);
      })
      .catch((e) => setError(e.message));
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  if (error && !schema) return <p className="error">{error}</p>;
  if (!schema) return <p>Loading options…</p>;

  const options = schema.options[fetcherType] || [];
  const fetcherMeta = schema.fetcherTypes[fetcherType];
  const outputMeta = schema.outputFormats.find((f) => f.value === outputFormat);

  function hint(title, text) {
    return {
      onMouseEnter: () => setActiveHint({ title, hint: text }),
      onMouseLeave: () => setActiveHint(null),
    };
  }

  function handleFetcherChange(next) {
    setFetcherType(next);
    setValues({});
  }

  function handleOptionChange(name, value) {
    setValues((prev) => ({ ...prev, [name]: value }));
  }

  async function handleSubmit(e) {
    e.preventDefault();
    setError(null);
    setSubmitting(true);
    try {
      const cleanedOptions = {};
      for (const opt of options) {
        const raw = values[opt.name];
        if (raw === undefined || raw === "") continue;
        if (opt.type === "multiselect" && (!Array.isArray(raw) || raw.length === 0)) continue;
        cleanedOptions[opt.name] = opt.type === "list" ? raw.split("\n").filter(Boolean) : raw;
      }
      const job = await createJob({ fetcherType, url, outputFormat, options: cleanedOptions });
      navigate(`/jobs/${job.id}`);
    } catch (err) {
      setError(err.message);
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="job-layout">
      <form
        onSubmit={handleSubmit}
        className="new-job-form"
        onKeyDown={(e) => {
          // Enter shouldn't fire "Run job" from an arbitrary field — only the
          // button itself should trigger a submit, since a stray Enter while
          // filling in a header/cookie value is easy to hit by accident.
          if (e.key === "Enter" && e.target.tagName !== "TEXTAREA") e.preventDefault();
        }}
      >
        <h1>New extract job</h1>

        <div className="card">
          <label className="field" {...hint("Fetcher", `${fetcherMeta?.hint ?? ""}${FETCHER_HINT_SUFFIX}`)}>
            <span>Fetcher</span>
            <div className="select-wrap">
              <select value={fetcherType} onChange={(e) => handleFetcherChange(e.target.value)}>
                {Object.entries(schema.fetcherTypes).map(([key, meta]) => (
                  <option key={key} value={key}>
                    {meta.label}
                  </option>
                ))}
              </select>
            </div>
          </label>

          <label className="field" {...hint("URL", URL_HINT)}>
            <span>URL</span>
            <div className="url-row">
              <input type="url" required value={url} onChange={(e) => setUrl(e.target.value)} placeholder="https://example.com" />
              <UrlPreview
                url={url}
                onUseSelector={(selector) => handleOptionChange("css_selector", selector)}
                onUseFetcher={handleFetcherChange}
              />
            </div>
          </label>

          <label className="field" {...hint("Extract", outputMeta?.hint)}>
            <span>Extract</span>
            <div className="select-wrap">
              <select value={outputFormat} onChange={(e) => setOutputFormat(e.target.value)}>
                {schema.outputFormats.map((f) => (
                  <option key={f.value} value={f.value}>
                    {f.label}
                  </option>
                ))}
              </select>
            </div>
          </label>
        </div>

        <details open className="card">
          <summary>Options</summary>
          <DynamicOptionsForm options={options} values={values} onChange={handleOptionChange} onHint={setActiveHint} />
        </details>

        {error && <p className="error">{error}</p>}

        <button type="submit" disabled={submitting}>
          {submitting ? "Starting…" : "Run job"}
        </button>
      </form>

      <aside className="hint-panel">
        {activeHint ? (
          <>
            <h2 className="hint-panel-title">{activeHint.title}</h2>
            <p>{activeHint.hint || "No extra detail for this one — the label says it all."}</p>
          </>
        ) : (
          <p className="hint-panel-placeholder">Hover a field to see what it does and what values it accepts.</p>
        )}
      </aside>
    </div>
  );
}
