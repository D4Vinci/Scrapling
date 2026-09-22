import { Router } from "express";
import { runPreview, runRenderedPreview } from "../services/previewFetch.js";

const router = Router();

router.post("/", async (req, res) => {
  const { url } = req.body ?? {};
  if (!url || typeof url !== "string") {
    return res.status(400).json({ error: "url is required" });
  }

  const result = await runPreview(url);
  res.json(result);
});

// The "Fetch Page" step on the New Job form: a full JS-rendered fetch (real
// browser), plus a suggestion for which fetcher the real job should use.
// Slow — only called from an explicit button click, never automatically.
router.post("/render", async (req, res) => {
  const { url } = req.body ?? {};
  if (!url || typeof url !== "string") {
    return res.status(400).json({ error: "url is required" });
  }

  const result = await runRenderedPreview(url);
  res.json(result);
});

export default router;
