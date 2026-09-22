import { Router } from "express";
import { runPreview } from "../services/previewFetch.js";

const router = Router();

router.post("/", async (req, res) => {
  const { url } = req.body ?? {};
  if (!url || typeof url !== "string") {
    return res.status(400).json({ error: "url is required" });
  }

  const result = await runPreview(url);
  res.json(result);
});

export default router;
