import { mkdirSync, readdirSync, renameSync, rmSync } from "node:fs";
import path from "node:path";
import { OUTPUTS_DIR } from "../db.js";

// Single path segment only — no slashes or ".." — so a folder name can never
// resolve outside OUTPUTS_DIR.
const FOLDER_NAME_RE = /^[A-Za-z0-9 _-]{1,100}$/;

export function isValidFolderName(name) {
  return FOLDER_NAME_RE.test(name);
}

export function listOutputFolders() {
  return readdirSync(OUTPUTS_DIR, { withFileTypes: true })
    .filter((entry) => entry.isDirectory())
    .map((entry) => entry.name)
    .sort();
}

// Empty/blank folder means "save directly in the default output folder".
export function resolveOutputDir(folder) {
  if (!folder) return OUTPUTS_DIR;
  if (!isValidFolderName(folder)) {
    throw new Error(`Invalid folder name '${folder}' (letters, numbers, spaces, - and _ only)`);
  }
  const dir = path.join(OUTPUTS_DIR, folder);
  mkdirSync(dir, { recursive: true });
  return dir;
}

// Moves a job's already-written output (a single file for html/txt, or a
// whole directory for the images format) from wherever it landed at run
// time into the folder the user picked on the Current Job page. Used by the
// "Save" action, which only happens after the job succeeds — the run itself
// always writes to the default output folder first (see runJob/runImageJob).
export function moveJobOutput(currentPath, folder) {
  const targetDir = resolveOutputDir(folder);
  const newPath = path.join(targetDir, path.basename(currentPath));
  if (newPath !== currentPath) renameSync(currentPath, newPath);
  return newPath;
}

// Used by the "Discard" action to delete a job's output without keeping it
// around in any folder.
export function deleteJobOutput(outputPath) {
  rmSync(outputPath, { recursive: true, force: true });
}
