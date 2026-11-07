import React from 'react';
import {AbsoluteFill, Img, OffthreadVideo, staticFile, useCurrentFrame} from 'remotion';
import {C, DISPLAY, TEXT} from '../theme';
import {FPS, type Cue} from '../lib/timing';
import {pop, ramp, lerp} from '../lib/anim';

// Kinetic captions: words appear as spoken; numbers and keywords glow cyan.
export const Captions: React.FC<{cues: Cue[]; keywords?: string[]}> = ({cues, keywords = []}) => {
  const f = useCurrentFrame();
  const t = f / FPS;
  const cue = cues.find((c) => t >= c.start && t < c.end + 0.1);
  if (!cue) return null;
  const words = cue.text.split(' ');
  const total = cue.text.length;
  const dur = cue.end - cue.start;
  let acc = 0;
  const kw = keywords.map((k) => k.toLowerCase());
  return (
    <AbsoluteFill style={{justifyContent: 'flex-end', alignItems: 'center', paddingBottom: 34, pointerEvents: 'none'}}>
      <div style={{maxWidth: 1040, textAlign: 'center', lineHeight: 1.2}}>
        {words.map((w, i) => {
          const start = Math.round((cue.start + (acc / total) * dur * 0.92) * FPS);
          acc += w.length + 1;
          const sp = pop(f, start);
          const clean = w.replace(/[^\w'’-]/g, '').toLowerCase();
          const hot = /\d/.test(w) || kw.some((k) => clean === k || clean.startsWith(k));
          return (
            <span
              key={i}
              style={{
                display: 'inline-block', margin: '0 5px', fontFamily: DISPLAY, fontWeight: 800, fontSize: hot ? 36 : 32, letterSpacing: -0.3,
                color: hot ? C.cyan : C.white, opacity: f >= start ? 1 : 0, transform: `translateY(${(1 - Math.min(sp, 1)) * 10}px) scale(${0.75 + 0.25 * sp})`,
                textShadow: hot ? '0 0 18px rgba(92,242,224,0.55), 0 2px 4px rgba(0,0,0,0.95)' : '0 2px 5px rgba(0,0,0,0.95)',
              }}
            >
              {w}
            </span>
          );
        })}
      </div>
    </AbsoluteFill>
  );
};

export const BigStat: React.FC<{x: number; y: number; at: number; until?: number; value?: string; count?: [number, number, (n: number) => string, number?]; label?: string; color?: string; size?: number; align?: 'left' | 'center' | 'right'}> = ({
  x, y, at, until, value, count, label, color = C.white, size = 72, align = 'center',
}) => {
  const f = useCurrentFrame();
  if (f < at) return null;
  const sp = pop(f, at);
  const out = until ? 1 - ramp(f, until - 10, 10) : 1;
  const v = count ? count[2](count[0] + (count[1] - count[0]) * ramp(f, at, count[3] ?? 40)) : value;
  const tx = align === 'center' ? '-50%' : align === 'right' ? '-100%' : '0';
  return (
    <div style={{position: 'absolute', left: x, top: y, transform: `translate(${tx}, 0) scale(${Math.min(sp, 1.08)})`, transformOrigin: align === 'left' ? '0 50%' : align === 'right' ? '100% 50%' : '50% 50%', opacity: out, textAlign: align}}>
      <div style={{fontFamily: DISPLAY, fontWeight: 800, fontSize: size, color, letterSpacing: -2, lineHeight: 1, textShadow: '0 6px 30px rgba(0,0,0,0.65)'}}>{v}</div>
      {label ? <div style={{fontFamily: TEXT, fontWeight: 600, fontSize: 16, color: C.dim, marginTop: 6, letterSpacing: 2.4, textTransform: 'uppercase'}}>{label}</div> : null}
    </div>
  );
};

export const Tag: React.FC<{x: number; y: number; at: number; until?: number; children: React.ReactNode; color?: string; size?: number; align?: 'left' | 'center' | 'right'; weight?: number}> = ({
  x, y, at, until, children, color = C.white, size = 18, align = 'left', weight = 700,
}) => {
  const f = useCurrentFrame();
  if (f < at || (until && f > until)) return null;
  const o = Math.min(ramp(f, at, 10), until ? 1 - ramp(f, until - 10, 10) : 1);
  const tx = align === 'center' ? '-50%' : align === 'right' ? '-100%' : '0';
  return (
    <div style={{position: 'absolute', left: x, top: y, transform: `translate(${tx}, ${(1 - o) * 8}px)`, opacity: o, fontFamily: TEXT, fontWeight: weight, fontSize: size, color, letterSpacing: 1.6, textTransform: 'uppercase', whiteSpace: 'nowrap', textShadow: '0 2px 10px rgba(0,0,0,0.9)'}}>
      {children}
    </div>
  );
};

// Real footage / photo insert with a cinematic frame, slow push and credit.
export const RealInsert: React.FC<{src: string; video?: boolean; at: number; until: number; credit: string; x?: number; y?: number; w?: number; h?: number; zoom?: [number, number]; origin?: string; startFrom?: number}> = ({
  src, video, at, until, credit, x = 0, y = 0, w = 1280, h = 720, zoom = [1.04, 1.16], origin = '50% 50%', startFrom = 0,
}) => {
  const f = useCurrentFrame();
  if (f < at || f > until) return null;
  const o = Math.min(ramp(f, at, 10), 1 - ramp(f, until - 10, 10));
  const z = lerp(zoom[0], zoom[1], (f - at) / Math.max(1, until - at));
  const framed = x !== 0 || y !== 0 || w !== 1280;
  return (
    <div style={{position: 'absolute', left: x, top: y, width: w, height: h, overflow: 'hidden', opacity: o, borderRadius: framed ? 6 : 0, boxShadow: framed ? '0 20px 60px rgba(0,0,0,0.7)' : undefined, border: framed ? '1px solid rgba(255,255,255,0.25)' : undefined}}>
      <div style={{width: '100%', height: '100%', transform: `scale(${z})`, transformOrigin: origin}}>
        {video ? (
          <OffthreadVideo src={staticFile(src)} startFrom={startFrom} muted style={{width: '100%', height: '100%', objectFit: 'cover'}} />
        ) : (
          <Img src={staticFile(src)} style={{width: '100%', height: '100%', objectFit: 'cover'}} />
        )}
      </div>
      <div style={{position: 'absolute', left: 14, top: 14, fontFamily: TEXT, fontWeight: 800, fontSize: 13, letterSpacing: 2.5, color: '#00151A', background: C.cyan, padding: '4px 9px'}}>{video ? 'REAL FOOTAGE' : 'REAL PHOTO'}</div>
      <div style={{position: 'absolute', right: 10, bottom: 8, fontFamily: TEXT, fontSize: 12, color: 'rgba(255,255,255,0.85)', textShadow: '0 1px 3px #000'}}>{credit}</div>
    </div>
  );
};

// Horizontal scale bar with label.
export const ScaleBar: React.FC<{x1: number; x2: number; y: number; at: number; label: string; color?: string}> = ({x1, x2, y, at, label, color = C.cyan}) => {
  const f = useCurrentFrame();
  if (f < at) return null;
  const t = ramp(f, at, 16);
  const xm = (x1 + x2) / 2, hw = ((x2 - x1) / 2) * t;
  return (
    <>
      <svg width={1280} height={720} style={{position: 'absolute', left: 0, top: 0}}>
        <line x1={xm - hw} x2={xm + hw} y1={y} y2={y} stroke={color} strokeWidth={2.5} />
        <line x1={xm - hw} x2={xm - hw} y1={y - 10} y2={y + 10} stroke={color} strokeWidth={2.5} />
        <line x1={xm + hw} x2={xm + hw} y1={y - 10} y2={y + 10} stroke={color} strokeWidth={2.5} />
      </svg>
      <div style={{position: 'absolute', left: xm, top: y - 38, transform: 'translateX(-50%)', opacity: t, fontFamily: TEXT, fontWeight: 800, fontSize: 20, letterSpacing: 2, color, whiteSpace: 'nowrap', textShadow: '0 2px 10px #000'}}>{label}</div>
    </>
  );
};

export const Panel: React.FC<{x: number; y: number; w: number; h: number; at: number; until?: number; children: React.ReactNode}> = ({x, y, w, h, at, until, children}) => {
  const f = useCurrentFrame();
  if (f < at || (until && f > until)) return null;
  const o = Math.min(ramp(f, at, 12), until ? 1 - ramp(f, until - 10, 10) : 1);
  return (
    <div style={{position: 'absolute', left: x, top: y, width: w, height: h, opacity: o, transform: `translateY(${(1 - o) * 14}px)`, background: 'rgba(4,20,34,0.72)', border: '1px solid rgba(92,242,224,0.3)', borderRadius: 10, backdropFilter: 'blur(2px)'}}>
      {children}
    </div>
  );
};
