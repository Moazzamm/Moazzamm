import timing from '../data/timing.json';

export type Cue = {start: number; end: number; text: string; para: number};
export type SceneTiming = {
  id: string;
  title: string;
  num?: number | null;
  vo: string;
  voDur: number;
  leadIn: number;
  durationInFrames: number;
  paras: {start: number; end: number}[];
  cues: Cue[];
};

export const FPS: number = timing.fps;
export const TIMING = timing as unknown as {
  fps: number;
  titleCardFrames: number;
  totalFrames: number;
  scenes: SceneTiming[];
};

export const sceneById = (id: string) => TIMING.scenes.find((s) => s.id === id)!;

// Frame at which paragraph i starts (plus an optional offset in seconds).
export const paraFrame = (s: SceneTiming, i: number, offsetSec = 0) =>
  Math.round((s.paras[Math.min(i, s.paras.length - 1)].start + offsetSec) * FPS);

// Frame at which the sentence containing `text` starts. Keys a visual to the exact spoken
// words, so reveals stay in sync even if the narration is re-recorded at a different pace.
export const cueFrame = (s: SceneTiming, text: string, offsetSec = 0) => {
  const c = s.cues.find((q) => q.text.includes(text));
  if (!c) throw new Error(`cueFrame: no cue containing "${text}" in scene ${s.id}`);
  return Math.round((c.start + offsetSec) * FPS);
};

// All key moments for a scene, resolved by the words that trigger them.
export const beats = (s: SceneTiming, map: Record<string, [string, number?]>) => {
  const out: Record<string, number> = {};
  for (const [k, [text, off]] of Object.entries(map)) out[k] = cueFrame(s, text, off ?? 0);
  return out;
};
