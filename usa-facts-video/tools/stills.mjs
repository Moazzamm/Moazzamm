// Renders sample frames of each scene for visual QA: node tools/stills.mjs [sceneId ...]
import { bundle } from "@remotion/bundler";
import { renderStill, selectComposition, openBrowser } from "@remotion/renderer";
import path from "node:path";
import fs from "node:fs";

const OUT = process.env.OUT ?? "/tmp/claude-0/frames";
const N = Number(process.env.N ?? 8);
fs.mkdirSync(OUT, { recursive: true });
const serveUrl = await bundle({ entryPoint: path.resolve("src/index.ts") });
const browser = await openBrowser("chrome", {
  browserExecutable: "/opt/pw-browsers/chromium-1243/chrome-linux64/chrome",
  chromiumOptions: { gl: "swangle" },
});
const ids = process.argv.slice(2);
for (const id of ids) {
  const compId = id.startsWith("Thumb") || id === "USAFacts" ? id : `Scene-${id}`;
  const comp = await selectComposition({ serveUrl, id: compId, puppeteerInstance: browser });
  const frames = process.env.FRAMES ? process.env.FRAMES.split(",").map(Number) : Array.from({ length: N }, (_, i) => Math.round(((i + 0.5) * comp.durationInFrames) / N));
  for (const fr of frames) {
    await renderStill({
      serveUrl, composition: comp, frame: fr, output: `${OUT}/${id}_${String(fr).padStart(5, "0")}.jpg`,
      scale: compId.startsWith("Thumb") ? 1 : 0.5, puppeteerInstance: browser, imageFormat: "jpeg",
      chromiumOptions: { gl: "swangle" },
    });
  }
  console.log("done", id, frames.join(","));
}
await browser.close({ silent: true });
