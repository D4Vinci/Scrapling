import { Router } from "express";
import { randomUUID } from "node:crypto";
import path from "node:path";
import fs from "node:fs";
import { getJob, insertJob, listJobs } from "../db.js";
import { runImageJob, runJob } from "../services/scraplingRunner.js";
import { resolveOutputDir } from "../services/outputFolders.js";
import { FETCHER_TYPES, OUTPUT_FORMATS } from "../optionsSchema.js";

const router = Router();

router.post("/", (req, res) => {
  const { fetcherType, url, outputFormat, folder = "", options = {} } = req.body ?? {};

  if (!FETCHER_TYPES[fetcherType]) {
    return res.status(400).json({ error: `Unknown fetcher type '${fetcherType}'` });
  }
  if (!url || typeof url !== "string") {
    return res.status(400).json({ error: "url is required" });
  }
  const format = OUTPUT_FORMATS.find((f) => f.value === outputFormat);
  if (!format) {
    return res.status(400).json({ error: `Unknown output format '${outputFormat}'` });
  }

  const trimmedFolder = typeof folder === "string" ? folder.trim() : "";
  let outputDir;
  try {
    outputDir = resolveOutputDir(trimmedFolder);
  } catch (err) {
    return res.status(400).json({ error: err.message });
  }

  const id = randomUUID();
  const isImages = format.kind === "images";
  const outputPath = isImages ? path.join(outputDir, id) : path.join(outputDir, `${id}.${format.extension}`);
  const createdAt = new Date().toISOString();

  insertJob({
    id,
    fetcher_type: fetcherType,
    url,
    output_format: outputFormat,
    folder: trimmedFolder,
    options_json: JSON.stringify(options),
    created_at: createdAt,
  });

  // Fire-and-forget: the client polls GET /api/jobs/:id instead of holding
  // this request open for however long a headless Chromium takes on a Pi.
  const runPromise = isImages
    ? runImageJob({ id, fetcherType, url, outputDir: outputPath, options })
    : runJob({ id, fetcherType, url, outputPath, options });
  runPromise.catch((err) => {
    console.error(`Unhandled error running job ${id}:`, err);
  });

  res.status(202).json({ id });
});

router.get("/", (req, res) => {
  const limit = Math.min(Number(req.query.limit) || 50, 200);
  const offset = Number(req.query.offset) || 0;
  const jobs = listJobs({ limit, offset }).map((job) => ({ ...job, options: JSON.parse(job.options_json) }));
  res.json(jobs);
});

router.get("/:id", (req, res) => {
  const job = getJob(req.params.id);
  if (!job) return res.status(404).json({ error: "Job not found" });
  res.json({ ...job, options: JSON.parse(job.options_json) });
});

router.get("/:id/output", (req, res) => {
  const job = getJob(req.params.id);
  if (!job || job.status !== "success" || !job.output_path) {
    return res.status(404).json({ error: "Output not available" });
  }
  if (job.output_format === "images") {
    return res.status(400).json({ error: "This job downloaded images — see GET /api/jobs/:id/images instead." });
  }
  if (!fs.existsSync(job.output_path)) {
    return res.status(410).json({ error: "Output file no longer exists" });
  }
  if (req.query.download === "1") {
    return res.download(job.output_path, path.basename(job.output_path));
  }
  res.type(path.extname(job.output_path).slice(1) === "html" ? "html" : "text/plain");
  res.sendFile(job.output_path);
});

router.get("/:id/images", (req, res) => {
  const job = getJob(req.params.id);
  if (!job || job.output_format !== "images" || !job.output_path) {
    return res.status(404).json({ error: "No image manifest for this job" });
  }
  const manifestPath = path.join(job.output_path, "manifest.json");
  if (!fs.existsSync(manifestPath)) {
    return res.status(job.status === "success" ? 410 : 404).json({ error: "Manifest not available yet" });
  }
  const manifest = JSON.parse(fs.readFileSync(manifestPath, "utf8"));
  res.json({
    total: manifest.length,
    ok: manifest.filter((m) => m.status === "ok").length,
    images: manifest,
  });
});

// `filename` is trusted only as a basename — resolved and re-checked against
// the job's own output directory so it can never escape via "../".
router.get("/:id/images/:filename", (req, res) => {
  const job = getJob(req.params.id);
  if (!job || job.output_format !== "images" || !job.output_path) {
    return res.status(404).json({ error: "Not found" });
  }
  const filePath = path.join(job.output_path, path.basename(req.params.filename));
  if (!filePath.startsWith(job.output_path + path.sep) || !fs.existsSync(filePath)) {
    return res.status(404).json({ error: "Not found" });
  }
  if (req.query.download === "1") {
    return res.download(filePath, path.basename(filePath));
  }
  res.sendFile(filePath);
});

export default router;
