import React from 'react';
import {useCurrentFrame} from 'remotion';
import {C, DISPLAY, TEXT} from '../theme';
import {pop, ramp} from '../lib/anim';

// Big kinetic stat: pops in, optionally counts up.
export const BigStat: React.FC<{x: number; y: number; at: number; until?: number; value?: string; count?: [number, number, (n: number) => string]; label?: string; color?: string; size?: number; align?: 'left' | 'center' | 'right'}> = ({
  x, y, at, until, value, count, label, color = C.white, size = 54, align = 'center',
}) => {
  const f = useCurrentFrame();
  const sp = pop(f, at);
  const out = until ? 1 - ramp(f, until - 8, 8) : 1;
  if (f < at) return null;
  const v = count ? count[2](count[0] + (count[1] - count[0]) * ramp(f, at, 30)) : value;
  const tx = align === 'center' ? '-50%' : align === 'right' ? '-100%' : '0';
  return (
    <div style={{position: 'absolute', left: x, top: y, transform: `translate(${tx}, 0) scale(${sp})`, transformOrigin: align === 'left' ? '0 50%' : '50% 50%', opacity: out, textAlign: align}}>
      <div style={{fontFamily: DISPLAY, fontWeight: 900, fontSize: size, color, letterSpacing: -1.5, lineHeight: 1, textShadow: '0 4px 18px rgba(0,0,0,0.7)'}}>{v}</div>
      {label ? <div style={{fontFamily: TEXT, fontWeight: 600, fontSize: 13, color: C.dim, marginTop: 4, textTransform: 'uppercase', letterSpacing: 1.6}}>{label}</div> : null}
    </div>
  );
};

export const Tag: React.FC<{x: number; y: number; at: number; until?: number; children: React.ReactNode; color?: string; size?: number; align?: 'left' | 'center' | 'right'}> = ({x, y, at, until, children, color = C.white, size = 13, align = 'left'}) => {
  const f = useCurrentFrame();
  if (f < at) return null;
  const o = Math.min(ramp(f, at, 8), until ? 1 - ramp(f, until - 8, 8) : 1);
  const tx = align === 'center' ? '-50%' : align === 'right' ? '-100%' : '0';
  return (
    <div style={{position: 'absolute', left: x, top: y, transform: `translate(${tx}, ${(1 - o) * 6}px)`, opacity: o, fontFamily: TEXT, fontWeight: 700, fontSize: size, color, letterSpacing: 1.2, textTransform: 'uppercase', whiteSpace: 'nowrap', textShadow: '0 2px 8px rgba(0,0,0,0.9)'}}>
      {children}
    </div>
  );
};

// Small credit line for real imagery.
export const Credit: React.FC<{at: number; until?: number; children: React.ReactNode}> = ({at, until, children}) => {
  const f = useCurrentFrame();
  if (f < at || (until && f > until)) return null;
  return (
    <div style={{position: 'absolute', right: 14, top: 12, fontFamily: TEXT, fontSize: 10, color: C.dim, background: 'rgba(0,0,0,0.45)', padding: '2px 6px', borderRadius: 2}}>{children}</div>
  );
};
