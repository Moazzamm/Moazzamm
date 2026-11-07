import {Easing, interpolate, spring} from 'remotion';

export const ease = Easing.bezier(0.45, 0, 0.2, 1);
export const easeOut = Easing.bezier(0.16, 1, 0.3, 1);

export const ramp = (f: number, start: number, dur = 18, from = 0, to = 1, e = ease) =>
  interpolate(f, [start, start + Math.max(1, dur)], [from, to], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: e});

export const win = (f: number, a: number, b: number, fade = 10) => Math.min(ramp(f, a, fade), 1 - ramp(f, b - fade, fade));
export const lerp = (a: number, b: number, t: number) => a + (b - a) * t;

// Punchy pop with a small overshoot (this channel style allows it; used for type and icons only).
export const pop = (f: number, start: number, fps = 30) =>
  spring({frame: f - start, fps, config: {damping: 11, stiffness: 170, mass: 0.6}});

export const rnd = (i: number) => {
  const x = Math.sin(i * 127.1 + 311.7) * 43758.5453;
  return x - Math.floor(x);
};

// Decaying camera shake from an impact at `start`.
export const shake = (f: number, start: number, amp = 6, dur = 18) => {
  const t = f - start;
  if (t < 0 || t > dur) return {x: 0, y: 0};
  const k = 1 - t / dur;
  return {x: Math.sin(t * 2.7) * amp * k, y: Math.cos(t * 3.3) * amp * k * 0.7};
};

export const fmt = (n: number) => Math.round(n).toLocaleString('en-US');
