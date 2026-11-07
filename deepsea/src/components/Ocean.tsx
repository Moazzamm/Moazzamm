import React from 'react';
import {AbsoluteFill, useCurrentFrame} from 'remotion';
import {C, W, H, DISPLAY, TEXT} from '../theme';
import {rnd, ramp} from '../lib/anim';

// Water colour by depth (m): [depth, top, bottom]
const STOPS: [number, string, string][] = [
  [0, '#3DB4E6', '#0E6FA8'],
  [150, '#1478B3', '#0A4C80'],
  [400, '#0A3F70', '#062A4E'],
  [1000, '#041D38', '#021226'],
  [3000, '#020C1C', '#010712'],
  [11000, '#01050D', '#000206'],
];
const hex = (h: string) => [1, 3, 5].map((i) => parseInt(h.slice(i, i + 2), 16));
const mix = (a: string, b: string, t: number) => {
  const A = hex(a), B = hex(b);
  return `rgb(${A.map((v, i) => Math.round(v + (B[i] - v) * t)).join(',')})`;
};
const waterAt = (d: number) => {
  for (let i = 0; i < STOPS.length - 1; i++) {
    const [d0, t0, b0] = STOPS[i];
    const [d1, t1, b1] = STOPS[i + 1];
    if (d <= d1) {
      const t = Math.max(0, Math.min(1, (d - d0) / (d1 - d0)));
      return [mix(t0, t1, t), mix(b0, b1, t)];
    }
  }
  return [STOPS[STOPS.length - 1][1], STOPS[STOPS.length - 1][2]];
};

export const zoneOf = (d: number) =>
  d < 200 ? 'Sunlight zone' : d < 1000 ? 'Twilight zone' : d < 4000 ? 'Midnight zone' : d < 6000 ? 'Abyssal zone' : 'Hadal zone';

// The ocean itself: colour, light shafts, surface ripples, marine snow (moves up as we sink), bioluminescence.
export const Ocean: React.FC<{depth: number; speed: number}> = ({depth, speed}) => {
  const f = useCurrentFrame();
  const [top, bottom] = waterAt(depth);
  const sun = Math.max(0, 1 - depth / 260);
  const glowLife = Math.min(1, Math.max(0, (depth - 350) / 600));
  const surface = Math.max(0, 1 - depth / 25);
  // world scroll in px: 1 m ≈ 3 px near the surface; compressed deeper so particles keep moving
  const scroll = depth < 1000 ? depth * 3 : 3000 + (depth - 1000) * 0.9;
  const snow = [];
  for (let i = 0; i < 140; i++) {
    const layer = i % 3;
    const par = [0.35, 0.7, 1.15][layer];
    const x = (rnd(i) * (W + 80) + Math.sin(f / 70 + i) * 14) % (W + 80) - 40;
    const span = H + 60;
    const y = (((rnd(i + 31) * span - scroll * par - f * 0.25 * par) % span) + span) % span - 30;
    const r = [0.9, 1.4, 2.1][layer];
    const len = Math.min(16, 1 + speed * par * 0.9);
    snow.push(<line key={i} x1={x} y1={y} x2={x} y2={y + len} stroke="rgba(230,240,245,0.75)" strokeWidth={r} strokeLinecap="round" opacity={0.25 + 0.35 * layer / 2} />);
  }
  const sparks = [];
  if (glowLife > 0) {
    for (let i = 0; i < 46; i++) {
      const x = rnd(i + 900) * W;
      const span = H + 40;
      const y = (((rnd(i + 950) * span - scroll * 0.8) % span) + span) % span - 20;
      const blink = Math.max(0, Math.sin(f / (9 + rnd(i) * 20) + i * 3)) ** 6;
      const col = rnd(i + 3) > 0.5 ? C.cyan : '#8AB8FF';
      sparks.push(<circle key={i} cx={x} cy={y} r={1.5 + rnd(i + 7) * 2} fill={col} opacity={blink * glowLife} style={{filter: `drop-shadow(0 0 6px ${col})`}} />);
    }
  }
  return (
    <AbsoluteFill style={{background: `linear-gradient(${top}, ${bottom})`}}>
      {/* sunlight shafts */}
      {sun > 0 ? (
        <AbsoluteFill style={{opacity: sun * 0.55}}>
          {Array.from({length: 7}).map((_, i) => (
            <div
              key={i}
              style={{
                position: 'absolute', left: 80 + i * 170 + Math.sin(f / 50 + i) * 30, top: -120, width: 70 + rnd(i) * 70, height: 1000,
                background: 'linear-gradient(rgba(255,255,255,0.55), rgba(255,255,255,0))', transform: `rotate(${12 + Math.sin(f / 80 + i) * 3}deg)`,
                transformOrigin: '50% 0', filter: 'blur(14px)', opacity: 0.4 + 0.4 * Math.sin(f / 37 + i * 2),
              }}
            />
          ))}
        </AbsoluteFill>
      ) : null}
      {/* surface ripples */}
      {surface > 0 ? (
        <svg width={W} height={H} style={{position: 'absolute', opacity: surface}}>
          {Array.from({length: 4}).map((_, k) => (
            <path key={k} d={`M0 ${30 + k * 14} ${Array.from({length: 33}).map((_, i) => `L${i * 40} ${30 + k * 14 + Math.sin(i * 0.7 + f / 9 + k) * 6}`).join(' ')}`} stroke="rgba(255,255,255,0.5)" strokeWidth={2 - k * 0.4} fill="none" />
          ))}
        </svg>
      ) : null}
      <svg width={W} height={H} style={{position: 'absolute'}}>
        {snow}
        {sparks}
      </svg>
      <AbsoluteFill style={{background: 'radial-gradient(ellipse at 50% 45%, transparent 55%, rgba(0,0,0,0.55) 100%)'}} />
    </AbsoluteFill>
  );
};

// Right-side depth gauge with moving ticks and live readout.
export const DepthMeter: React.FC<{depth: number; opacity?: number}> = ({depth, opacity = 1}) => {
  const PX_PER_100 = 26; // tick spacing per 100 m (gauge is not to scale with the scene)
  const cy = 360;
  const ticks = [];
  const start = Math.floor((depth - 1400) / 100) * 100;
  for (let m = Math.max(0, start); m < depth + 1400; m += 100) {
    const y = cy + ((m - depth) / 100) * PX_PER_100;
    if (y < 90 || y > 630) continue;
    const major = m % 1000 === 0;
    const o = 1 - Math.min(1, Math.abs(y - cy) / 280);
    ticks.push(
      <g key={m} opacity={o}>
        <line x1={1222} x2={major ? 1252 : 1240} y1={y} y2={y} stroke={C.white} strokeWidth={major ? 2 : 1} />
        {major ? <text x={1214} y={y + 4} fill={C.white} fontSize={12} textAnchor="end" fontFamily="Inter">{(m / 1000).toFixed(0)} km</text> : null}
      </g>,
    );
  }
  return (
    <AbsoluteFill style={{opacity, pointerEvents: 'none'}}>
      <svg width={W} height={H} style={{position: 'absolute'}}>
        <line x1={1252} x2={1252} y1={90} y2={630} stroke={C.faint} strokeWidth={2} />
        {ticks}
        <path d={`M1258 ${cy} l10 -7 v14 z`} fill={C.cyan} />
      </svg>
      <div style={{position: 'absolute', right: 70, top: cy - 30, textAlign: 'right'}}>
        <div style={{fontFamily: DISPLAY, fontWeight: 800, fontSize: 30, color: C.white, letterSpacing: -0.5, textShadow: '0 2px 10px rgba(0,0,0,0.6)'}}>
          {Math.round(depth).toLocaleString('en-US')} m
        </div>
        <div style={{fontFamily: TEXT, fontWeight: 700, fontSize: 11, color: C.cyan, letterSpacing: 2.5, textTransform: 'uppercase'}}>{zoneOf(depth)}</div>
      </div>
    </AbsoluteFill>
  );
};

// Elegant zone title: tracking-in letters and a thin line.
export const ZoneTitle: React.FC<{at: number; title: string; sub: string; dur?: number}> = ({at, title, sub, dur = 90}) => {
  const f = useCurrentFrame();
  if (f < at || f > at + dur) return null;
  const t = f - at;
  const o = Math.min(ramp(t, 0, 14), 1 - ramp(t, dur - 16, 16));
  return (
    <AbsoluteFill style={{alignItems: 'center', justifyContent: 'center', opacity: o, pointerEvents: 'none'}}>
      <div style={{fontFamily: TEXT, fontWeight: 700, fontSize: 14, letterSpacing: 6, color: C.cyan, textTransform: 'uppercase'}}>{sub}</div>
      <div style={{width: 280 * ramp(t, 4, 24), height: 1, background: C.cyan, margin: '12px 0'}} />
      <div style={{fontFamily: DISPLAY, fontWeight: 300, fontSize: 64, letterSpacing: 4 + 10 * (1 - ramp(t, 0, 40)), color: C.white, textTransform: 'uppercase', textShadow: '0 4px 30px rgba(0,0,0,0.6)'}}>{title}</div>
    </AbsoluteFill>
  );
};
