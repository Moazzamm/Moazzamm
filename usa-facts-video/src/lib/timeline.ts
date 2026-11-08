import vo from "../data/vo.json";
import { FPS } from "./theme";

export type Word = { w: string; s: number; e: number };
export type SceneId =
  | "intro" | "f10" | "f9" | "f8" | "f7" | "f6" | "myth"
  | "f5" | "f4" | "f3" | "f2" | "f1" | "outro";

export const ORDER: SceneId[] = [
  "intro", "f10", "f9", "f8", "f7", "f6", "myth", "f5", "f4", "f3", "f2", "f1", "outro",
];

/** Frames of silence before the voice starts in each scene. */
export const HEAD = 14;
/** Frames of breathing room after the voice ends. */
export const TAIL = 16;
/** Overlap of the transition between two scenes. */
export const TRANSITION = 12;
/** Extra end-screen time appended to the outro. */
export const END_SCREEN = 7 * FPS;

const data = vo as unknown as Record<SceneId, { dur: number; words: Word[] }>;

export const words = (id: SceneId): Word[] => data[id].words;

export const sceneFrames = (id: SceneId): number =>
  HEAD + Math.ceil(data[id].dur * FPS) + TAIL + (id === "outro" ? END_SCREEN : 0);

export const totalFrames = (): number =>
  ORDER.reduce((a, id) => a + sceneFrames(id), 0) - TRANSITION * (ORDER.length - 1);

/** Global start frame of each scene (accounting for transition overlaps). */
export const sceneStart = (id: SceneId): number => {
  let f = 0;
  for (const s of ORDER) {
    if (s === id) return f;
    f += sceneFrames(s) - TRANSITION;
  }
  return f;
};

const norm = (s: string) => s.toLowerCase().replace(/[^a-z0-9]/g, "");

/**
 * Frame (relative to the scene start, including HEAD) at which the narrator
 * starts saying `phrase`. `nth` picks a later occurrence. Throws if missing so
 * that a script change never silently desyncs a visual beat.
 */
export const cue = (id: SceneId, phrase: string, nth = 0, edge: "s" | "e" = "s"): number => {
  const ws = words(id);
  const target = phrase.split(/\s+/).map(norm).filter(Boolean);
  let hit = -1;
  let count = 0;
  for (let i = 0; i <= ws.length - target.length; i++) {
    if (target.every((t, k) => norm(ws[i + k].w).startsWith(t))) {
      if (count === nth) {
        hit = i;
        break;
      }
      count++;
    }
  }
  if (hit < 0) throw new Error(`cue not found: ${id} "${phrase}"`);
  const w = edge === "s" ? ws[hit] : ws[hit + target.length - 1];
  return HEAD + Math.round((edge === "s" ? w.s : w.e) * FPS);
};

export const voEnd = (id: SceneId) => HEAD + Math.ceil(data[id].dur * FPS);
