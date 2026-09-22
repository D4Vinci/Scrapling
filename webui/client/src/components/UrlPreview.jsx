import { useMemo, useState } from "react";
import { previewUrl } from "../api.js";

const MAX_SNIPPETS = 5;
const SNIPPET_LENGTH = 200;

// Parsed via DOMParser, which never executes <script> tags in the resulting
// document — safe to query against even though the HTML came from an
// arbitrary, untrusted URL.
function findMatches(html, selector) {
  if (!html || !selector.trim()) return null;
  try {
    const doc = new DOMParser().parseFromString(html, "text/html");
    const elements = [...doc.querySelectorAll(selector)];
    return {
      count: elements.length,
      snippets: elements.slice(0, MAX_SNIPPETS).map((el) => {
        const text = el.outerHTML;
        return text.length > SNIPPET_LENGTH ? `${text.slice(0, SNIPPET_LENGTH)}…` : text;
      }),
    };
  } catch (err) {
    return { error: err.message };
  }
}

export default function UrlPreview({ url, onUseSelector }) {
  const [state, setState] = useState("idle"); // idle | loading | success | error
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [selector, setSelector] = useState("");

  const matches = useMemo(() => findMatches(result?.html, selector), [result, selector]);

  async function handleFetch() {
    if (!url) {
      setError("Enter a URL first.");
      return;
    }
    setState("loading");
    setError(null);
    setResult(null);
    try {
      const data = await previewUrl(url);
      if (!data.success) {
        setState("error");
        setError(data.error || "Preview fetch failed.");
        setResult(data); // keep signals even on failure (e.g. blocked-page detection)
        return;
      }
      setState("success");
      setResult(data);
    } catch (err) {
      setState("error");
      setError(err.message);
    }
  }

  return (
    // `display: contents` (see index.css) lets these children lay out as if
    // they were direct children of the .url-row flex container the caller
    // renders us in, so the button sits inline next to the URL input while
    // everything else below drops to its own full-width row.
    <div className="url-preview">
      <button type="button" onClick={handleFetch} disabled={state === "loading"}>
        {state === "loading" ? "Fetching…" : "Fetch"}
      </button>

      <div className="url-preview-details">
      <p className="hint">
        Quick plain-HTTP preview — no browser, no JS rendering. Use it to see what's on the page and try out a CSS
        selector before running the real job.
      </p>

      {error && <p className="error">{error}</p>}

      {result?.signals?.looksBlocked && (
        <p className="warning">
          This looks like it might be blocked (a captcha/challenge page). Try the "Fetch" or "Stealthy fetch" fetcher
          above instead of GET.
        </p>
      )}
      {result?.signals?.looksEmpty && (
        <p className="warning">
          The page came back almost empty — it may render its content with JavaScript. Try the "Fetch" or "Stealthy
          fetch" fetcher above instead of GET.
        </p>
      )}

      {state === "success" && (
        <div className="preview-panel">
          <p>
            <strong>{result.signals?.title || "(no title)"}</strong> · {result.html.length.toLocaleString()} characters
            {result.truncated && " (truncated for preview)"}
          </p>

          <label className="field">
            <span>Try a CSS selector against this page</span>
            <input
              type="text"
              placeholder=".product-title, article p"
              value={selector}
              onChange={(e) => setSelector(e.target.value)}
            />
          </label>

          {matches?.error && <p className="error">Invalid selector: {matches.error}</p>}

          {matches && !matches.error && (
            <div>
              <p>
                {matches.count} match{matches.count === 1 ? "" : "es"}
                {matches.count > 0 && (
                  <button type="button" className="link-button" onClick={() => onUseSelector(selector)}>
                    Use this selector
                  </button>
                )}
              </p>
              {matches.snippets.map((snippet, i) => (
                <pre key={i} className="preview-text snippet">
                  {snippet}
                </pre>
              ))}
            </div>
          )}
        </div>
      )}
      </div>
    </div>
  );
}
