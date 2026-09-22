import { mkdirSync, readdirSync } from "node:fs";
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
