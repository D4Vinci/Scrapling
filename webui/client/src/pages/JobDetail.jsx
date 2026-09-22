import { useEffect, useRef, useState } from "react";
import { useParams } from "react-router-dom";
import { discardJob, getJob, getJobImages, jobLogsStreamUrl, listOutputFolders, saveJob } from "../api.js";
import FolderPicker from "../components/FolderPicker.jsx";
import StatusBadge from "../components/StatusBadge.jsx";

const ACTIVE_STATUSES = new Set(["pending", "running"]);

export default function JobDetail() {
  const { id } = useParams();
  const [job, setJob] = useState(null);
  const [error, setError] = useState(null);
  const [log, setLog] = useState("");
  const timerRef = useRef(null);
  const logRef = useRef(null);

  // Live log: an SSE connection per job. Reconnecting on id change (not on
  // every job-status poll) keeps this to exactly one stream per page visit.
  useEffect(() => {
    setLog("");
    const source = new EventSource(jobLogsStreamUrl(id));
    source.addEventListener("log", (e) => setLog((prev) => prev + JSON.parse(e.data)));
    source.addEventListener("done", () => source.close());
    source.onerror = () => source.close();
    return () => source.close();
  }, [id]);

  useEffect(() => {
    if (logRef.current) logRef.current.scrollTop = logRef.current.scrollHeight;
  }, [log]);

  useEffect(() => {
    let cancelled = false;

    async function poll() {
      try {
        const data = await getJob(id);
        if (cancelled) return;
        setJob(data);
        if (ACTIVE_STATUSES.has(data.status)) {
          timerRef.current = setTimeout(poll, 1500);
        }
      } catch (err) {
        if (!cancelled) setError(err.message);
      }
    }

    poll();
    return () => {
      cancelled = true;
      clearTimeout(timerRef.current);
    };
  }, [id]);

  if (error) return <p className="error">{error}</p>;
  if (!job) return <p>Loading…</p>;

  const running = ACTIVE_STATUSES.has(job.status);
  const unfiled = job.status === "success" && !job.folder;

  return (
    <div className="job-detail">
      <h1>Current job</h1>
      <p className="card">
        <StatusBadge status={job.status} /> · {job.fetcher_type} ·{" "}
        <a href={job.url} target="_blank" rel="noreferrer">
          {job.url}
        </a>
      </p>

      <details className="card" open={running}>
        <summary>
          Log {running && <span className="hint">— running, updating live</span>}
        </summary>
        <pre className="logs job-log" ref={logRef}>
          {log || "Waiting for output…"}
        </pre>
      </details>

      {job.status === "error" && <pre className="error">{job.error}</pre>}

      {job.status === "discarded" && <p className="hint">This job's output was discarded — nothing was saved.</p>}

      {job.status === "success" && (
        <>
          {job.output_format === "images" ? <ImageGallery jobId={job.id} /> : <ResultPreview job={job} />}
          {unfiled ? (
            <SavePanel jobId={job.id} onSaved={(updated) => setJob((prev) => ({ ...prev, ...updated }))} />
          ) : (
            <p className="card">
              <strong>Saved</strong> to folder: {job.folder || "(default)"}
            </p>
          )}
        </>
      )}
    </div>
  );
}

function ResultPreview({ job }) {
  return (
    <>
      <p>
        <a href={`/api/jobs/${job.id}/output?download=1`}>Download result</a>
      </p>
      {job.output_format === "html" ? (
        // sandbox with no "allow-scripts"/"allow-same-origin" tokens: the scraped
        // page's own <script> tags must never execute against our app's origin.
        <iframe title="result" src={`/api/jobs/${job.id}/output`} className="preview-frame" sandbox="" />
      ) : (
        <PreviewText jobId={job.id} />
      )}
    </>
  );
}

function PreviewText({ jobId }) {
  const [text, setText] = useState("Loading…");
  useEffect(() => {
    fetch(`/api/jobs/${jobId}/output`)
      .then((r) => r.text())
      .then(setText);
  }, [jobId]);
  return <pre className="preview-text">{text}</pre>;
}

// The decision point the New Job form used to force up front: now that the
// result is visible, decide where (or whether) to keep it.
function SavePanel({ jobId, onSaved }) {
  const [folder, setFolder] = useState("");
  const [folders, setFolders] = useState([]);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState(null);
  const [discarded, setDiscarded] = useState(false);

  useEffect(() => {
    listOutputFolders()
      .then(setFolders)
      .catch(() => {});
  }, []);

  async function handleSave() {
    setBusy(true);
    setError(null);
    try {
      const result = await saveJob(jobId, folder);
      onSaved(result);
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  }

  async function handleDiscard() {
    setBusy(true);
    setError(null);
    try {
      await discardJob(jobId);
      setDiscarded(true);
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  }

  if (discarded) return <p className="hint">Discarded — nothing was saved.</p>;

  return (
    <div className="card save-panel">
      <label className="field">
        <span>Save to folder</span>
        <FolderPicker value={folder} onChange={setFolder} folders={folders} />
        <small className="hint">Pick an existing folder or type a new name. Leave blank for the default output folder.</small>
      </label>
      {error && <p className="error">{error}</p>}
      <div className="save-panel-actions">
        <button type="button" onClick={handleSave} disabled={busy}>
          {busy ? "Working…" : "Save"}
        </button>
        <button type="button" className="secondary" onClick={handleDiscard} disabled={busy}>
          Discard
        </button>
      </div>
    </div>
  );
}

function ImageGallery({ jobId }) {
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    getJobImages(jobId)
      .then(setData)
      .catch((e) => setError(e.message));
  }, [jobId]);

  if (error) return <p className="error">{error}</p>;
  if (!data) return <p>Loading images…</p>;

  const failed = data.images.filter((img) => img.status === "error");

  return (
    <div>
      <p>
        Downloaded <strong>{data.ok}</strong> of {data.total} image{data.total === 1 ? "" : "s"} found on the page.
      </p>

      {data.total === 0 && <p className="hint">No images were found on this page (or inside the CSS selector, if set).</p>}

      {data.images.some((img) => img.status === "ok") && (
        <div className="image-grid">
          {data.images
            .filter((img) => img.status === "ok")
            .map((img) => (
              <a
                key={img.filename}
                href={`/api/jobs/${jobId}/images/${encodeURIComponent(img.filename)}?download=1`}
                className="image-card"
                title={img.url}
              >
                <img src={`/api/jobs/${jobId}/images/${encodeURIComponent(img.filename)}`} alt={img.filename} loading="lazy" />
                <span className="image-card-name">{img.filename}</span>
              </a>
            ))}
        </div>
      )}

      {failed.length > 0 && (
        <details>
          <summary>
            {failed.length} image{failed.length === 1 ? "" : "s"} failed to download
          </summary>
          <ul>
            {failed.map((img) => (
              <li key={img.url}>
                {img.url} — {img.error}
              </li>
            ))}
          </ul>
        </details>
      )}
    </div>
  );
}
