// Renders preview stills at given global frames (QA only).
import {bundle} from '@remotion/bundler';
import {renderStill, selectComposition} from '@remotion/renderer';
import path from 'node:path';
import fs from 'node:fs';

const frames = process.argv.slice(2).map(Number);
const browserExecutable = process.env.REMOTION_BROWSER;
const serveUrl = await bundle({entryPoint: path.resolve('src/index.ts')});
const comp = await selectComposition({serveUrl, id: 'Documentary', browserExecutable});
fs.mkdirSync('out/stills', {recursive: true});
for (const frame of frames) {
  await renderStill({composition: comp, serveUrl, frame, output: `out/stills/f${String(frame).padStart(5, '0')}.png`, browserExecutable});
  console.log('rendered', frame);
}
