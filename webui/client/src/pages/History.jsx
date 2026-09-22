import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { listJobs } from "../api.js";
import StatusBadge from "../components/StatusBadge.jsx";

export default function History() {
  const [jobs, setJobs] = useState([]);
  const [error, setError] = useState(null);

  useEffect(() => {
    listJobs({ limit: 100 })
      .then(setJobs)
      .catch((e) => setError(e.message));
  }, []);

  if (error) return <p className="error">{error}</p>;

  return (
    <div>
      <h1>Job history</h1>
      <table className="history-table">
        <thead>
          <tr>
            <th>Created</th>
            <th>Fetcher</th>
            <th>URL</th>
            <th>Folder</th>
            <th>Status</th>
          </tr>
        </thead>
        <tbody>
          {jobs.map((job) => (
            <tr key={job.id}>
              <td>{new Date(job.created_at).toLocaleString()}</td>
              <td>{job.fetcher_type}</td>
              <td className="url-cell">{job.url}</td>
              <td>{job.folder || "(default)"}</td>
              <td>
                <Link to={`/jobs/${job.id}`}>
                  <StatusBadge status={job.status} />
                </Link>
              </td>
            </tr>
          ))}
          {jobs.length === 0 && (
            <tr>
              <td colSpan={5}>No jobs yet.</td>
            </tr>
          )}
        </tbody>
      </table>
    </div>
  );
}
