import { Router } from "express";
import { randomUUID } from "node:crypto";
import path from "node:path";
import fs from "node:fs";
import { getJob, insertJob, listJobs } from "../db.js";
import { runJob } from "../services/scraplingRunner.js";
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
  const outputPath = path.join(outputDir, `${id}.${format.extension}`);
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
  runJob({ id, fetcherType, url, outputPath, options }).catch((err) => {
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
  if (!fs.existsSync(job.output_path)) {
    return res.status(410).json({ error: "Output file no longer exists" });
  }
  if (req.query.download === "1") {
    return res.download(job.output_path, path.basename(job.output_path));
  }
  res.type(path.extname(job.output_path).slice(1) === "html" ? "html" : "text/plain");
  res.sendFile(job.output_path);
});

export default router;
