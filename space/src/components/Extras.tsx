import React from 'react';
import {Img, staticFile, useCurrentFrame} from 'remotion';
import {C, TEXT} from '../theme';
import {ramp, lerp, rnd} from '../lib/anim';

// Real image insert: slides in, keeps moving (push + drift), carries a "REAL IMAGE" stamp + credit.
export const PhotoInsert: React.FC<{src: string; at: number; until: number; credit: string; stamp?: string; x?: number; y?: number; w?: number; h?: number; fit?: 'cover' | 'contain'; zoom?: [number, number]; origin?: string}> = ({
  src, at, until, credit, stamp = 'REAL IMAGE', x = 0, y = 0, w = 854, h = 480, fit = 'cover', zoom = [1.05, 1.25], origin = '50% 50%',
}) => {
  const f = useCurrentFrame();
  if (f < at || f > until) return null;
  const o = Math.min(ramp(f, at, 8), 1 - ramp(f, until - 8, 8));
  const z = lerp(zoom[0], zoom[1], ramp(f, at, until - at, 0, 1, (t) => t));
  return (
    <div style={{position: 'absolute', left: x, top: y, width: w, height: h, overflow: 'hidden', opacity: o, borderRadius: x || y ? 4 : 0, boxShadow: x || y ? '0 10px 40px rgba(0,0,0,0.7)' : undefined}}>
      <Img src={staticFile(src)} style={{width: '100%', height: '100%', objectFit: fit, transform: `scale(${z})`, transformOrigin: origin, background: '#000'}} />
      {stamp ? <div style={{position: 'absolute', right: 10, top: 10, fontFamily: TEXT, fontWeight: 800, fontSize: 11, letterSpacing: 2, color: '#000', background: C.hot, padding: '3px 7px'}}>{stamp}</div> : null}
      <div style={{position: 'absolute', right: 8, bottom: 6, fontFamily: TEXT, fontSize: 9.5, color: 'rgba(255,255,255,0.85)', textShadow: '0 1px 3px #000'}}>{credit}</div>
    </div>
  );
};

// A glowing 3D sugar cube (CSS 3D), spinning.
export const Cube3D: React.FC<{cx: number; cy: number; size: number; glow?: number}> = ({cx, cy, size, glow = 1}) => {
  const f = useCurrentFrame();
  const s = size;
  const face = (t: string, shade: number) => (
    <div
      style={{
        position: 'absolute', width: s, height: s, transform: t,
        background: `linear-gradient(135deg, rgba(255,255,255,${0.95 * shade}), rgba(220,230,255,${0.75 * shade}))`,
        border: '1px solid rgba(160,200,255,0.9)', boxShadow: `inset 0 0 ${s * 0.3}px rgba(140,190,255,0.6)`,
      }}
    />
  );
  return (
    <div style={{position: 'absolute', left: cx - s / 2, top: cy - s / 2, width: s, height: s, perspective: s * 5}}>
      <div style={{position: 'absolute', inset: -s * 0.8, borderRadius: '50%', background: `radial-gradient(circle, rgba(140,200,255,${0.55 * glow}), transparent 65%)`}} />
      <div style={{position: 'absolute', width: s, height: s, transformStyle: 'preserve-3d', transform: `rotateX(${-22 + 8 * Math.sin(f / 30)}deg) rotateY(${f * 2}deg)`}}>
        {face(`translateZ(${s / 2}px)`, 1)}
        {face(`rotateY(180deg) translateZ(${s / 2}px)`, 0.7)}
        {face(`rotateY(90deg) translateZ(${s / 2}px)`, 0.85)}
        {face(`rotateY(-90deg) translateZ(${s / 2}px)`, 0.8)}
        {face(`rotateX(90deg) translateZ(${s / 2}px)`, 1)}
        {face(`rotateX(-90deg) translateZ(${s / 2}px)`, 0.6)}
      </div>
    </div>
  );
};

export const SunIcon: React.FC<{cx: number; cy: number; r: number; o?: number}> = ({cx, cy, r, o = 1}) => (
  <div style={{position: 'absolute', left: cx - r, top: cy - r, width: r * 2, height: r * 2, borderRadius: '50%', opacity: o, background: 'radial-gradient(circle at 40% 40%, #FFF6D0, #FFC15C 45%, #FF7A2B 90%)', boxShadow: `0 0 ${r * 1.5}px rgba(255,170,60,0.8)`}} />
);

// Expanding shockwave ring.
export const Shockwave: React.FC<{cx: number; cy: number; at: number; maxR?: number; dur?: number; color?: string}> = ({cx, cy, at, maxR = 600, dur = 30, color = '#FFFFFF'}) => {
  const f = useCurrentFrame();
  const t = (f - at) / dur;
  if (t < 0 || t > 1) return null;
  const r = maxR * (1 - Math.pow(1 - t, 3));
  return <div style={{position: 'absolute', left: cx - r, top: cy - r, width: r * 2, height: r * 2, borderRadius: '50%', border: `${3 + 6 * (1 - t)}px solid ${color}`, opacity: 1 - t, boxShadow: `0 0 30px ${color}`}} />;
};

// Full-frame white flash.
export const Flash: React.FC<{at: number; dur?: number; k?: number}> = ({at, dur = 8, k = 0.9}) => {
  const f = useCurrentFrame();
  const t = f - at;
  if (t < 0 || t > dur) return null;
  return <div style={{position: 'absolute', inset: 0, background: '#fff', opacity: k * (1 - t / dur)}} />;
};

// Dimension line with label.
export const Dim: React.FC<{x1: number; x2: number; y: number; at: number; label: string; color?: string}> = ({x1, x2, y, at, label, color = C.hot}) => {
  const f = useCurrentFrame();
  if (f < at) return null;
  const t = ramp(f, at, 14);
  const xm = (x1 + x2) / 2;
  const hw = ((x2 - x1) / 2) * t;
  return (
    <>
      <svg width={854} height={480} style={{position: 'absolute', left: 0, top: 0, overflow: 'visible'}}>
        <line x1={xm - hw} x2={xm + hw} y1={y} y2={y} stroke={color} strokeWidth={2} />
        <line x1={xm - hw} x2={xm - hw} y1={y - 8} y2={y + 8} stroke={color} strokeWidth={2} />
        <line x1={xm + hw} x2={xm + hw} y1={y - 8} y2={y + 8} stroke={color} strokeWidth={2} />
      </svg>
      <div style={{position: 'absolute', left: xm, top: y - 30, transform: 'translateX(-50%)', opacity: t, fontFamily: TEXT, fontWeight: 800, fontSize: 15, letterSpacing: 1.5, color, whiteSpace: 'nowrap', textShadow: '0 2px 8px #000'}}>{label}</div>
    </>
  );
};

// Light-travel streak used for "ancient light".
export const LightStreak: React.FC<{y: number; at: number; dur?: number}> = ({y, at, dur = 40}) => {
  const f = useCurrentFrame();
  const t = (f - at) / dur;
  if (t < 0 || t > 1.3) return null;
  const x = lerp(-80, 934, Math.min(t, 1));
  return <div style={{position: 'absolute', left: x - 260, top: y - 2, width: 260, height: 4, borderRadius: 2, background: `linear-gradient(90deg, transparent, ${C.cyan}, #fff)`, boxShadow: `0 0 16px ${C.cyan}`, opacity: t > 1 ? 1 - (t - 1) / 0.3 : 1}} />;
};

export const Particles: React.FC<{cx: number; cy: number; n?: number; at: number; converge?: boolean; color?: string; spread?: number}> = ({cx, cy, n = 120, at, converge = false, color = '#FFE6B8', spread = 260}) => {
  const f = useCurrentFrame();
  if (f < at) return null;
  const t = ramp(f, at, 45);
  return (
    <svg width={854} height={480} style={{position: 'absolute', left: 0, top: 0}}>
      {Array.from({length: n}).map((_, i) => {
        const a = rnd(i) * Math.PI * 2 + f * 0.01;
        const d = spread * (0.2 + rnd(i + 3) * 0.8) * (converge ? 1 - t * 0.92 : t);
        return <circle key={i} cx={cx + Math.cos(a) * d} cy={cy + Math.sin(a) * d * 0.7} r={0.8 + rnd(i + 5) * 1.4} fill={color} opacity={0.4 + 0.6 * rnd(i + 9)} />;
      })}
    </svg>
  );
};
