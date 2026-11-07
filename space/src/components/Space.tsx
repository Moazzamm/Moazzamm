import React from 'react';
import {AbsoluteFill, useCurrentFrame} from 'remotion';
import {C, W, H} from '../theme';
import {rnd} from '../lib/anim';

// Three-layer parallax starfield. `drift` is camera velocity in px/frame for the nearest layer,
// `warp` (0–1) stretches stars into streaks radiating from the centre (used for transitions).
export const Starfield: React.FC<{seed?: number; drift?: [number, number]; warp?: number; count?: number; opacity?: number}> = ({
  seed = 1, drift = [0.25, 0.05], warp = 0, count = 150, opacity = 1,
}) => {
  const f = useCurrentFrame();
  const stars = [];
  for (let i = 0; i < count; i++) {
    const layer = i % 3; // 0 far, 2 near
    const depth = [0.25, 0.55, 1][layer];
    const span = W + 200;
    const x0 = rnd(i * 3 + seed) * span;
    const y0 = rnd(i * 7 + seed * 2) * (H + 200);
    const x = ((x0 - f * drift[0] * depth) % span + span) % span - 100;
    const y = ((y0 - f * drift[1] * depth) % (H + 200) + (H + 200)) % (H + 200) - 100;
    const r = [0.5, 0.8, 1.25][layer] * (0.7 + rnd(i + 9) * 0.6);
    const tw = 0.55 + 0.45 * Math.sin(f * (0.05 + rnd(i) * 0.12) + i);
    if (warp > 0.01) {
      const dx = x - W / 2, dy = y - H / 2;
      const len = warp * depth * 0.35;
      stars.push(<line key={i} x1={x} y1={y} x2={x + dx * len} y2={y + dy * len} stroke="#fff" strokeWidth={r} opacity={0.5 + 0.5 * warp} strokeLinecap="round" />);
    } else {
      const col = rnd(i + 4) > 0.86 ? (rnd(i + 5) > 0.5 ? '#FFD9A8' : '#B9DCFF') : '#FFFFFF';
      stars.push(<circle key={i} cx={x} cy={y} r={r} fill={col} opacity={tw * [0.45, 0.7, 1][layer]} />);
    }
  }
  return (
    <AbsoluteFill style={{opacity}}>
      <svg width={W} height={H}>{stars}</svg>
    </AbsoluteFill>
  );
};

// Slow-drifting nebula glow; colours per scene.
export const Nebula: React.FC<{a?: string; b?: string; intensity?: number}> = ({a = C.violet, b = C.cyan, intensity = 0.35}) => {
  const f = useCurrentFrame();
  const x1 = 30 + 8 * Math.sin(f / 140), y1 = 35 + 6 * Math.cos(f / 170);
  const x2 = 72 + 7 * Math.cos(f / 160), y2 = 68 + 5 * Math.sin(f / 120);
  return (
    <AbsoluteFill
      style={{
        opacity: intensity,
        background: `radial-gradient(ellipse 45% 38% at ${x1}% ${y1}%, ${a}66, transparent 70%), radial-gradient(ellipse 40% 45% at ${x2}% ${y2}%, ${b}55, transparent 70%)`,
      }}
    />
  );
};

export const SpaceBG: React.FC<{seed?: number; a?: string; b?: string; drift?: [number, number]; warp?: number; neb?: number}> = ({seed, a, b, drift, warp, neb}) => (
  <AbsoluteFill style={{background: `radial-gradient(ellipse at 50% 40%, ${C.deep} 0%, ${C.space} 75%)`}}>
    <Nebula a={a} b={b} intensity={neb ?? 0.35} />
    <Starfield seed={seed} drift={drift} warp={warp} />
  </AbsoluteFill>
);

// Wrapper that adds a continuous slow push-in plus optional shake offsets.
export const Camera: React.FC<{zoom?: number; x?: number; y?: number; rot?: number; children: React.ReactNode}> = ({zoom = 1, x = 0, y = 0, rot = 0, children}) => (
  <AbsoluteFill style={{transform: `translate(${x}px, ${y}px) scale(${zoom}) rotate(${rot}deg)`, transformOrigin: '50% 50%'}}>{children}</AbsoluteFill>
);
