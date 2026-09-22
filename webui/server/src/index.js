import express from "express";
import path from "node:path";
import { fileURLToPath } from "node:url";
import jobsRouter from "./routes/jobs.js";
import optionsRouter from "./routes/options.js";
import mcpRouter from "./routes/mcp.js";
import previewRouter from "./routes/preview.js";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const app = express();

app.use(express.json());

app.use("/api/jobs", jobsRouter);
app.use("/api/options-schema", optionsRouter);
app.use("/api/mcp", mcpRouter);
app.use("/api/preview", previewRouter);

// Serve the built React app (run `npm run build` in ../client first).
// Express 5's router requires a named wildcard for catch-alls.
const clientDist = path.join(__dirname, "..", "..", "client", "dist");
app.use(express.static(clientDist));
app.get("/{*splat}", (req, res) => {
  res.sendFile(path.join(clientDist, "index.html"));
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`Scrapling web UI server listening on port ${PORT}`);
});
