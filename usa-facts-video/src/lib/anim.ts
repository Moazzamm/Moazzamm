import { Easing, interpolate, spring } from "remotion";
import { FPS } from "./theme";

const clamp = { extrapolateLeft: "clamp", extrapolateRight: "clamp" } as const;
export const EASE = Easing.bezier(0.16, 1, 0.3, 1);
export const EASE_IN_OUT = Easing.bezier(0.65, 0, 0.35, 1);

/** 0→1 ease-out ramp starting at `start` lasting `dur` frames. */
export const ramp = (f: number, start: number, dur = 15, ease = EASE) =>
  interpolate(f, [start, start + dur], [0, 1], { ...clamp, easing: ease });

/** Fade in at `a`, fade out at `b`. */
export const window = (f: number, a: number, b: number, fade = 10) =>
  interpolate(f, [a, a + fade, b - fade, b], [0, 1, 1, 0], clamp);

export const pop = (f: number, start: number, damping = 12) =>
  spring({ frame: f - start, fps: FPS, config: { damping, stiffness: 170, mass: 0.8 } });

export const lerp = (f: number, input: number[], output: number[], ease = EASE_IN_OUT) =>
  interpolate(f, input, output, { ...clamp, easing: ease });
