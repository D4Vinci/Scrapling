import { Router } from "express";
import { randomUUID } from "node:crypto";
import path from "node:path";
import fs from "node:fs";
import { getJob, insertJob, listJobs, updateJob } from "../db.js";
import { runImageJob, runJob } from "../services/scraplingRunner.js";
import { subscribe } from "../services/jobEvents.js";
import { deleteJobOutput, isValidFolderName, moveJobOutput, resolveOutputDir } from "../services/outputFolders.js";
import { FETCHER_TYPES, OUTPUT_FORMATS } from "../optionsSchema.js";

const router = Router();

// A job always runs into the default output folder first — where to actually
// file it away is a decision made on the Current Job page, after you've seen
// the result (see POST /:id/save below), not up front.
router.post("/", (req, res) => {
  const { fetcherType, url, outputFormat, options = {} } = req.body ?? {};

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

  const outputDir = resolveOutputDir("");
  const id = randomUUID();
  const isImages = format.kind === "images";
  const outputPath = isImages ? path.join(outputDir, id) : path.join(outputDir, `${id}.${format.extension}`);
  const createdAt = new Date().toISOString();

  insertJob({
    id,
    fetcher_type: fetcherType,
    url,
    output_format: outputFormat,
    folder: "",
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

const ACTIVE_STATUSES = new Set(["pending", "running"]);

// Server-Sent Events: sends whatever's already logged as a first burst, then
// streams new lines as the CLI produces them, and closes once the job's
// done. A client that connects to an already-finished job just gets the
// backlog immediately followed by a close — same code path either way.
router.get("/:id/logs/stream", (req, res) => {
  const job = getJob(req.params.id);
  if (!job) return res.status(404).json({ error: "Job not found" });

  res.set({
    "Content-Type": "text/event-stream",
    "Cache-Control": "no-cache",
    Connection: "keep-alive",
  });
  res.flushHeaders();

  if (job.logs) res.write(`event: log\ndata: ${JSON.stringify(job.logs)}\n\n`);

  if (!ACTIVE_STATUSES.has(job.status)) {
    res.write(`event: done\ndata: ${JSON.stringify(job.status)}\n\n`);
    return res.end();
  }

  const unsubscribe = subscribe(req.params.id, {
    onLog: (chunk) => res.write(`event: log\ndata: ${JSON.stringify(chunk)}\n\n`),
    onDone: (status) => {
      res.write(`event: done\ndata: ${JSON.stringify(status)}\n\n`);
      res.end();
    },
  });
  req.on("close", unsubscribe);
});

// Files a successful job's already-written output into the chosen folder —
// the folder picker lives on the Current Job page, not the New Job form, so
// this is the only place a job's storage location is decided.
router.post("/:id/save", (req, res) => {
  const job = getJob(req.params.id);
  if (!job) return res.status(404).json({ error: "Job not found" });
  if (job.status !== "success") return res.status(400).json({ error: "Only a successful job can be saved" });

  const folder = typeof req.body?.folder === "string" ? req.body.folder.trim() : "";
  if (folder && !isValidFolderName(folder)) {
    return res.status(400).json({ error: `Invalid folder name '${folder}' (letters, numbers, spaces, - and _ only)` });
  }

  try {
    const newPath = moveJobOutput(job.output_path, folder);
    updateJob(job.id, { folder, output_path: newPath });
    res.json({ folder, output_path: newPath });
  } catch (err) {
    res.status(500).json({ error: String(err.message || err) });
  }
});

// Deletes a job's output instead of filing it anywhere. The job stays in
// History (for the URL/log record) but its status flips to "discarded" and
// there's no file/folder backing it any more.
router.post("/:id/discard", (req, res) => {
  const job = getJob(req.params.id);
  if (!job) return res.status(404).json({ error: "Job not found" });
  if (job.status !== "success") return res.status(400).json({ error: "Only a successful job can be discarded" });

  if (job.output_path) deleteJobOutput(job.output_path);
  updateJob(job.id, { status: "discarded", output_path: null });
  res.json({ status: "discarded" });
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
