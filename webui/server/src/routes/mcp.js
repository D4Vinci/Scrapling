import { Router } from "express";
import * as mcpProcess from "../services/mcpProcess.js";

const router = Router();

router.get("/status", (req, res) => {
  res.json(mcpProcess.status());
});

router.post("/start", (req, res) => {
  try {
    res.status(201).json(mcpProcess.start(req.body ?? {}));
  } catch (err) {
    res.status(409).json({ error: err.message });
  }
});

router.post("/stop", (req, res) => {
  try {
    res.json(mcpProcess.stop());
  } catch (err) {
    res.status(409).json({ error: err.message });
  }
});

export default router;
