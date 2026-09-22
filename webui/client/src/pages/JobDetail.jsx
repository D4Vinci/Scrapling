import { useEffect, useRef, useState } from "react";
import { useParams } from "react-router-dom";
import { getJob } from "../api.js";
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
      <p>
        <StatusBadge status={job.status} /> · {job.fetcher_type} ·{" "}
        <a href={job.url} target="_blank" rel="noreferrer">
          {job.url}
        </a>
      </p>

      {ACTIVE_STATUSES.has(job.status) && <p>Running… this page updates automatically.</p>}

      {job.status === "error" && <pre className="error">{job.error}</pre>}

      {job.status === "success" && (
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
