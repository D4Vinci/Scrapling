import path from "node:path";
import fs from "node:fs";
import { fileURLToPath } from "node:url";
import Database from "better-sqlite3";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const DATA_DIR = path.join(__dirname, "..", "data");
export const OUTPUTS_DIR = path.join(DATA_DIR, "outputs");

fs.mkdirSync(OUTPUTS_DIR, { recursive: true });

const db = new Database(path.join(DATA_DIR, "jobs.db"));
db.pragma("journal_mode = WAL");

db.exec(`
  CREATE TABLE IF NOT EXISTS jobs (
    id TEXT PRIMARY KEY,
    fetcher_type TEXT NOT NULL,
    url TEXT NOT NULL,
    output_format TEXT NOT NULL,
    options_json TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending',
    output_path TEXT,
    error TEXT,
    created_at TEXT NOT NULL,
    started_at TEXT,
    finished_at TEXT,
    duration_ms INTEGER
  )
`);

export function insertJob(job) {
  db.prepare(
    `INSERT INTO jobs (id, fetcher_type, url, output_format, options_json, status, created_at)
     VALUES (@id, @fetcher_type, @url, @output_format, @options_json, 'pending', @created_at)`,
  ).run(job);
}

export function updateJob(id, fields) {
  const setClause = Object.keys(fields)
    .map((column) => `${column} = @${column}`)
    .join(", ");
  db.prepare(`UPDATE jobs SET ${setClause} WHERE id = @id`).run({ ...fields, id });
}

export function getJob(id) {
  return db.prepare("SELECT * FROM jobs WHERE id = ?").get(id);
}

export function listJobs({ limit = 50, offset = 0 } = {}) {
  return db.prepare("SELECT * FROM jobs ORDER BY created_at DESC LIMIT ? OFFSET ?").all(limit, offset);
}

export default db;
