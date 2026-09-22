import { Router } from "express";
import { listOutputFolders } from "../services/outputFolders.js";

const router = Router();

router.get("/", (req, res) => {
  res.json(listOutputFolders());
});

export default router;
