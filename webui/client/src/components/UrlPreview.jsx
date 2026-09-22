import { useState } from "react";
import { renderPreview } from "../api.js";
import ElementPicker from "./ElementPicker.jsx";

const FETCHER_LABELS = {
  get: "GET",
  fetch: "Fetch (browser)",
  stealthy_fetch: "Stealthy fetch (anti-bot)",
};

// The "Fetch Page" step: a full JS-rendered fetch of the URL (a real headless
// browser, same as the "Fetch"/"Stealthy fetch" job fetchers would use), run
// once from an explicit button click since it's much slower than a plain
// GET — especially on a Pi. Once it comes back, this shows a suggestion for
// which fetcher the real job should use, and an element picker so clicking
// something in the rendered page fills in a CSS selector instead of having
// to guess one by hand.
export default function UrlPreview({ url, onUseSelector, onUseFetcher }) {
  const [state, setState] = useState("idle"); // idle | loading | success | error
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [picked, setPicked] = useState(null);

  async function handleFetch() {
    if (!url) {
      setError("Enter a URL first.");
      return;
    }
    setState("loading");
    setError(null);
    setResult(null);
    setPicked(null);
    try {
      const data = await renderPreview(url);
      if (!data.success) {
        setState("error");
        setError(data.error || "Fetch failed.");
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
        {state === "loading" ? "Fetching (JS-rendered, can take a while)…" : "Fetch Page"}
      </button>

      <div className="url-preview-details">
        <p className="hint">
          Loads the page in a real headless browser (JavaScript included) so you can see what it actually renders, get
          a suggested fetcher, and click an element to build a CSS selector — much slower than the job itself, so this
          only runs when you click the button.
        </p>

        {error && <p className="error">{error}</p>}

        {state === "success" && (
          <div className="preview-panel">
            <p>
              <strong>{result.signals?.title || "(no title)"}</strong> · {result.html.length.toLocaleString()} characters
              {result.truncated && " (truncated for preview)"}
            </p>

            {result.signals?.looksBlocked && (
              <p className="warning">Even the JS-rendered page looks blocked (a captcha/challenge page).</p>
            )}
            {result.signals?.looksEmpty && (
              <p className="warning">The rendered page still came back nearly empty — double check the URL.</p>
            )}

            {result.suggestion && (
              <p className="suggestion">
                Suggested fetcher: <strong>{FETCHER_LABELS[result.suggestion.fetcher] || result.suggestion.fetcher}</strong>
                <button type="button" className="link-button" onClick={() => onUseFetcher(result.suggestion.fetcher)}>
                  Use this fetcher
                </button>
                <br />
                <small className="hint">{result.suggestion.reason}</small>
              </p>
            )}

            <p className="hint">Click an element below to get a CSS selector for it.</p>
            <ElementPicker html={result.html} onPick={setPicked} />

            {picked && (
              <div className="picked-selector">
                <p>
                  Clicked a <code>{picked.tag}</code> — <code>{picked.general}</code>{" "}
                  {picked.generalCount > 1 ? `(${picked.generalCount} matches on the page)` : "(1 match)"}
                </p>
                <div className="picked-selector-actions">
                  {picked.generalCount > 1 && (
                    <button type="button" onClick={() => onUseSelector(picked.general)}>
                      Use selector for all {picked.generalCount} similar elements
                    </button>
                  )}
                  <button type="button" onClick={() => onUseSelector(picked.precise)} className="secondary">
                    Use selector for just this one element
                  </button>
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
