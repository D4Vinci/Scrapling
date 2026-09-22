import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { createJob, getOptionsSchema, listOutputFolders } from "../api.js";
import DynamicOptionsForm from "../components/DynamicOptionsForm.jsx";
import UrlPreview from "../components/UrlPreview.jsx";

export default function NewJob() {
  const [schema, setSchema] = useState(null);
  const [fetcherType, setFetcherType] = useState("get");
  const [url, setUrl] = useState("");
  const [outputFormat, setOutputFormat] = useState("md");
  const [folder, setFolder] = useState("");
  const [folders, setFolders] = useState([]);
  const [values, setValues] = useState({});
  const [error, setError] = useState(null);
  const [submitting, setSubmitting] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    getOptionsSchema()
      .then(setSchema)
      .catch((e) => setError(e.message));
    listOutputFolders()
      .then(setFolders)
      .catch(() => {}); // non-critical: the folder field just falls back to free text
  }, []);

  if (error && !schema) return <p className="error">{error}</p>;
  if (!schema) return <p>Loading options…</p>;

  const options = schema.options[fetcherType] || [];

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
      const job = await createJob({ fetcherType, url, outputFormat, folder, options: cleanedOptions });
      navigate(`/jobs/${job.id}`);
    } catch (err) {
      setError(err.message);
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <form onSubmit={handleSubmit} className="new-job-form">
      <h1>New extract job</h1>

      <label className="field">
        <span>Fetcher</span>
        <select value={fetcherType} onChange={(e) => handleFetcherChange(e.target.value)}>
          {Object.entries(schema.fetcherTypes).map(([key, meta]) => (
            <option key={key} value={key}>
              {meta.label}
            </option>
          ))}
        </select>
      </label>

      <label className="field">
        <span>URL</span>
        <div className="url-row">
          <input type="url" required value={url} onChange={(e) => setUrl(e.target.value)} placeholder="https://example.com" />
          <UrlPreview url={url} onUseSelector={(selector) => handleOptionChange("css_selector", selector)} />
        </div>
      </label>

      <label className="field">
        <span>Output format</span>
        <select value={outputFormat} onChange={(e) => setOutputFormat(e.target.value)}>
          {schema.outputFormats.map((f) => (
            <option key={f.value} value={f.value}>
              {f.label}
            </option>
          ))}
        </select>
      </label>

      <label className="field">
        <span>Save to folder</span>
        <input
          list="output-folders"
          value={folder}
          onChange={(e) => setFolder(e.target.value)}
          placeholder="(default output folder)"
        />
        <datalist id="output-folders">
          {folders.map((f) => (
            <option key={f} value={f} />
          ))}
        </datalist>
        <small className="hint">
          Pick an existing folder from the list or type a new name to create one. Leave blank to save directly in the
          default output folder.
        </small>
      </label>

      <details open>
        <summary>Options</summary>
        <DynamicOptionsForm options={options} values={values} onChange={handleOptionChange} />
      </details>

      {error && <p className="error">{error}</p>}

      <button type="submit" disabled={submitting}>
        {submitting ? "Starting…" : "Run job"}
      </button>
    </form>
  );
}
