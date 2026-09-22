import { useCallback, useEffect, useRef } from "react";

const HIGHLIGHT_OUTLINE = "2px solid #5b5ce0";

function cssEscape(s) {
  return window.CSS?.escape ? window.CSS.escape(s) : s.replace(/[^a-zA-Z0-9_-]/g, "\\$&");
}

function lastSegment(el) {
  const classes = [...el.classList].filter(Boolean).slice(0, 2);
  return el.tagName.toLowerCase() + (classes.length ? `.${classes.map(cssEscape).join(".")}` : "");
}

// Two selectors for whatever was clicked: a "general" one (just this
// element's tag+classes, matching every similar element on the page — the
// useful one for a gallery/list of repeated items) and a "precise" one (a
// full ancestor path with :nth-of-type, matching only this one element).
function selectorsFor(el, root) {
  const general = lastSegment(el);

  if (el.id) return { general, precise: `#${cssEscape(el.id)}` };

  const parts = [];
  let node = el;
  let depth = 0;
  while (node && node.nodeType === 1 && node !== root && depth < 4) {
    let part = node.tagName.toLowerCase();
    const classes = [...node.classList].filter(Boolean).slice(0, 2);
    if (classes.length) part += `.${classes.map(cssEscape).join(".")}`;
    const parent = node.parentElement;
    if (parent) {
      const siblings = [...parent.children].filter((s) => s.tagName === node.tagName);
      if (siblings.length > 1) part += `:nth-of-type(${siblings.indexOf(node) + 1})`;
    }
    parts.unshift(part);
    node = parent;
    depth += 1;
  }
  return { general, precise: parts.join(" > ") };
}

// Renders untrusted page HTML in a sandboxed iframe (allow-same-origin so the
// parent can walk/attach listeners to its DOM, but no allow-scripts token —
// so the scraped page's own <script> tags never execute) and turns hovering/
// clicking inside it into CSS selector suggestions, like a lightweight
// version of a browser devtools element picker.
export default function ElementPicker({ html, onPick }) {
  const iframeRef = useRef(null);
  const cleanupRef = useRef(() => {});

  const attach = useCallback(() => {
    cleanupRef.current();
    const doc = iframeRef.current?.contentDocument;
    if (!doc) return;

    let hovered = null;
    let prevOutline = "";

    function onMouseOver(e) {
      if (hovered) hovered.style.outline = prevOutline;
      hovered = e.target;
      prevOutline = hovered.style.outline;
      hovered.style.outline = HIGHLIGHT_OUTLINE;
    }
    function onMouseOut() {
      if (hovered) hovered.style.outline = prevOutline;
      hovered = null;
    }
    function onClick(e) {
      e.preventDefault();
      e.stopPropagation();
      const el = e.target;
      const { general, precise } = selectorsFor(el, doc.body);
      const generalCount = safeCount(doc, general);
      onPick({ general, precise, generalCount, tag: el.tagName.toLowerCase() });
    }

    doc.addEventListener("mouseover", onMouseOver);
    doc.addEventListener("mouseout", onMouseOut);
    doc.addEventListener("click", onClick, true);
    cleanupRef.current = () => {
      doc.removeEventListener("mouseover", onMouseOver);
      doc.removeEventListener("mouseout", onMouseOut);
      doc.removeEventListener("click", onClick, true);
    };
  }, [onPick]);

  useEffect(() => () => cleanupRef.current(), []);

  return (
    <iframe
      ref={iframeRef}
      title="Pick an element"
      srcDoc={html}
      sandbox="allow-same-origin"
      onLoad={attach}
      className="picker-frame"
    />
  );
}

function safeCount(doc, selector) {
  try {
    return doc.querySelectorAll(selector).length;
  } catch {
    return 0;
  }
}
