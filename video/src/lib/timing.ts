import timing from '../data/timing.json';

export type Cue = {start: number; end: number; text: string; para: number};
export type SceneTiming = {
  id: string;
  title: string;
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
