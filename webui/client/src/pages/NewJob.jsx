import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { createJob, getOptionsSchema, listOutputFolders } from "../api.js";
import DynamicOptionsForm from "../components/DynamicOptionsForm.jsx";
import FolderPicker from "../components/FolderPicker.jsx";
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
  const fetcherMeta = schema.fetcherTypes[fetcherType];
  const outputMeta = schema.outputFormats.find((f) => f.value === outputFormat);

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

      <div className="card">
        <label className="field">
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
          {fetcherMeta?.hint && <small className="hint">{fetcherMeta.hint}</small>}
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
          <div className="select-wrap">
            <select value={outputFormat} onChange={(e) => setOutputFormat(e.target.value)}>
              {schema.outputFormats.map((f) => (
                <option key={f.value} value={f.value}>
                  {f.label}
                </option>
              ))}
            </select>
          </div>
          {outputMeta?.hint && <small className="hint">{outputMeta.hint}</small>}
        </label>

        <label className="field">
          <span>Save to folder</span>
          <FolderPicker value={folder} onChange={setFolder} folders={folders} />
          <small className="hint">
            Pick an existing folder from the list or type a new name to create one. Leave blank to save directly in the
            default output folder.
          </small>
        </label>
      </div>

      <details open className="card">
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
