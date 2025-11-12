import fs from "fs";
import path from "path";

export default function handler(req, res) {
  const directoryPath = path.join(process.cwd(), "./public/sample_photos");
  try {
    const files = fs.readdirSync(directoryPath);
    res.status(200).json({ images: files });
  } catch (error) {
    res.status(500).json({ error: "Unable to read sample images" });
  }
}
