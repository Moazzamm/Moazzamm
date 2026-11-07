import {Easing, interpolate} from 'remotion';

// One easing curve for the whole film: smooth in, smooth out, no bounce.
export const ease = Easing.bezier(0.45, 0, 0.2, 1);

export const ramp = (frame: number, start: number, dur = 18, from = 0, to = 1) =>
  interpolate(frame, [start, start + dur], [from, to], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
    easing: ease,
  });

// Visible between start and end with soft edges.
export const window = (frame: number, start: number, end: number, fade = 12) =>
  Math.min(ramp(frame, start, fade), 1 - ramp(frame, end - fade, fade));

export const lerp = (a: number, b: number, t: number) => a + (b - a) * t;
