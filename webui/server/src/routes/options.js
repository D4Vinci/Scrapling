import { Router } from "express";
import { ALL_OPTIONS, FETCHER_TYPES, OUTPUT_FORMATS } from "../optionsSchema.js";

const router = Router();

router.get("/", (req, res) => {
  res.json({ fetcherTypes: FETCHER_TYPES, outputFormats: OUTPUT_FORMATS, options: ALL_OPTIONS });
});

export default router;
