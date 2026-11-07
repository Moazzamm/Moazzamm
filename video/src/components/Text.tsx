import React from 'react';
import {useCurrentFrame} from 'remotion';
import {C, T} from '../theme';
import {ramp} from '../lib/anim';

type Pos = {x: number; y: number};

// Chapter marker, top-left: "01 · WATER — Clarion-Clipperton Zone"
export const ChapterTag: React.FC<{n: string; word: string; place: string; at?: number}> = ({n, word, place, at = 4}) => {
  const f = useCurrentFrame();
  const o = ramp(f, at, 20);
  return (
    <div style={{position: 'absolute', left: 28, top: 22, opacity: o, transform: `translateY(${(1 - o) * 6}px)`}}>
      <div style={{...T.kicker, color: C.cyan}}>{n} · {word}</div>
      <div style={{...T.label, color: C.paper, fontSize: 15, marginTop: 4}}>{place}</div>
    </div>
  );
};

// Source credit, bottom-right above the caption band.
export const Credit: React.FC<{children: React.ReactNode; at: number; until?: number; left?: boolean}> = ({children, at, until, left}) => {
  const f = useCurrentFrame();
  const o = until ? Math.min(ramp(f, at, 12), 1 - ramp(f, until - 12, 12)) : ramp(f, at, 12);
  return (
    <div
      style={{
        position: 'absolute',
        [left ? 'left' : 'right']: 28,
        top: 382,
        ...T.small,
        fontSize: 9.5,
        color: C.paperDim,
        opacity: o,
        maxWidth: 520,
        textAlign: left ? 'left' : 'right',
      }}
    >
      {children}
    </div>
  );
};

// A label that fades/slides in at a given frame. Amber = uncertainty or key measurement.
export const Label: React.FC<
  Pos & {at: number; until?: number; children: React.ReactNode; color?: string; size?: number; weight?: number; width?: number; align?: 'left' | 'right' | 'center'; bg?: boolean}
> = ({x, y, at, until, children, color = C.paper, size = 13, weight = 500, width, align = 'left', bg}) => {
  const f = useCurrentFrame();
  const o = until ? Math.min(ramp(f, at, 14), 1 - ramp(f, until - 12, 12)) : ramp(f, at, 14);
  const tx = align === 'right' ? '-100%' : align === 'center' ? '-50%' : '0';
  return (
    <div
      style={{
        position: 'absolute',
        left: x,
        top: y,
        width,
        transform: `translate(${tx}, ${(1 - o) * 5}px)`,
        opacity: o,
        ...T.label,
        fontSize: size,
        fontWeight: weight,
        color,
        textAlign: align,
        whiteSpace: width ? 'normal' : 'nowrap',
        ...(bg ? {background: 'rgba(11,20,38,0.82)', padding: '2px 6px', borderRadius: 2} : {}),
      }}
    >
      {children}
    </div>
  );
};

export const Stat: React.FC<Pos & {at: number; until?: number; value: string; caption: React.ReactNode; color?: string; size?: number; width?: number}> = ({
  x, y, at, until, value, caption, color = C.paper, size = 40, width = 260,
}) => {
  const f = useCurrentFrame();
  const o = until ? Math.min(ramp(f, at, 16), 1 - ramp(f, until - 12, 12)) : ramp(f, at, 16);
  return (
    <div style={{position: 'absolute', left: x, top: y, width, opacity: o, transform: `translateY(${(1 - o) * 6}px)`}}>
      <div style={{...T.stat, fontSize: size, color}}>{value}</div>
      <div style={{...T.label, fontSize: 12, color: C.paperDim, marginTop: 2}}>{caption}</div>
    </div>
  );
};

// Small legend chip for evidence layers.
export const Chip: React.FC<{color: string; dashed?: boolean; label: string; sub?: string}> = ({color, dashed, label, sub}) => (
  <div style={{display: 'flex', alignItems: 'center', gap: 8, marginBottom: 7}}>
    <div style={{width: 18, height: 0, borderTop: `2.5px ${dashed ? 'dashed' : 'solid'} ${color}`}} />
    <div>
      <div style={{...T.label, fontSize: 12.5, color: C.paper}}>{label}</div>
      {sub ? <div style={{...T.small, fontSize: 10, color: C.paperDim}}>{sub}</div> : null}
    </div>
  </div>
);
