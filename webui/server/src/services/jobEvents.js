import { EventEmitter } from "node:events";

// One emitter per running job, so an SSE client that connects mid-run can
// still get the backlog (from the DB's `logs` column) before subscribing to
// what's still to come. Entries are cleaned up once the job finishes and
// every listener has disconnected, so this never grows unbounded.
const emitters = new Map();

function getEmitter(jobId) {
  let emitter = emitters.get(jobId);
  if (!emitter) {
    emitter = new EventEmitter();
    emitter.setMaxListeners(20);
    emitters.set(jobId, emitter);
  }
  return emitter;
}

export function emitLog(jobId, chunk) {
  getEmitter(jobId).emit("log", chunk);
}

export function emitDone(jobId, status) {
  const emitter = emitters.get(jobId);
  if (!emitter) return;
  emitter.emit("done", status);
  // Give already-attached listeners a tick to receive the "done" event
  // before the emitter (and their subscriptions to it) is torn down.
  setTimeout(() => emitters.delete(jobId), 1000);
}

export function subscribe(jobId, { onLog, onDone }) {
  const emitter = getEmitter(jobId);
  emitter.on("log", onLog);
  emitter.on("done", onDone);
  return () => {
    emitter.off("log", onLog);
    emitter.off("done", onDone);
  };
}
