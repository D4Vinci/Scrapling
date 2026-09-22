import { useEffect, useRef, useState } from "react";
import { useParams } from "react-router-dom";
import { getJob, getJobImages } from "../api.js";
import StatusBadge from "../components/StatusBadge.jsx";

const ACTIVE_STATUSES = new Set(["pending", "running"]);

export default function JobDetail() {
  const { id } = useParams();
  const [job, setJob] = useState(null);
  const [error, setError] = useState(null);
  const timerRef = useRef(null);

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

  return (
    <div className="job-detail">
      <h1>Job</h1>
      <p className="card">
        <StatusBadge status={job.status} /> · {job.fetcher_type} · folder: {job.folder || "(default)"} ·{" "}
        <a href={job.url} target="_blank" rel="noreferrer">
          {job.url}
        </a>
      </p>

      {ACTIVE_STATUSES.has(job.status) && <p>Running… this page updates automatically.</p>}

      {job.status === "error" && <pre className="error">{job.error}</pre>}

      {job.status === "success" && job.output_format === "images" && <ImageGallery jobId={job.id} />}

      {job.status === "success" && job.output_format !== "images" && (
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
      )}
    </div>
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
