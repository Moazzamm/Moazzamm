import React from 'react';
import {AbsoluteFill, useCurrentFrame} from 'remotion';
import {C, DISPLAY, TEXT} from '../theme';
import {ramp, pop, easeOut} from '../lib/anim';
import {Starfield} from './Space';

// Countdown sting: warp-speed streaks, flash, giant number slams in, name wipes on;
// then the number shrinks to a persistent badge in the top-left corner.
export const STING_FRAMES = 63;

export const Sting: React.FC<{num: number; name: string; total: number}> = ({num, name, total}) => {
  const f = useCurrentFrame();
  const warp = f < STING_FRAMES ? Math.min(ramp(f, 0, 10), 1 - ramp(f, 40, 16)) : 0;
  const slam = pop(f, 8);
  const flash = Math.max(0, 1 - Math.abs(f - 9) / 6);
  const toBadge = ramp(f, 46, 16, 0, 1, easeOut);
  const fullBg = 1 - ramp(f, 48, 14);
  const nameIn = ramp(f, 18, 12);
  const badgeOut = 1 - ramp(f, total - 10, 10);
  return (
    <AbsoluteFill style={{pointerEvents: 'none'}}>
      <AbsoluteFill style={{background: C.space, opacity: fullBg}}>
        <Starfield seed={num * 11} warp={warp} drift={[0, 0]} />
        <AbsoluteFill style={{background: `radial-gradient(circle at 50% 45%, ${C.orange}55, transparent 55%)`, opacity: 0.6 * warp}} />
      </AbsoluteFill>
      <div
        style={{
          position: 'absolute',
          left: 427 + (60 - 427) * toBadge,
          top: 200 + (38 - 200) * toBadge,
          transform: `translate(-50%, -50%) scale(${(f < 46 ? 3.2 - 2.2 * Math.min(slam, 1.1) : 1) * (1 - 0.72 * toBadge)})`,
          opacity: badgeOut,
        }}
      >
        <div style={{fontFamily: DISPLAY, fontWeight: 900, fontSize: 150, lineHeight: 1, color: C.white, letterSpacing: -6, textShadow: `0 0 40px ${C.orange}AA, 0 6px 0 ${C.orange}`}}>
          <span style={{fontSize: 80, verticalAlign: 'top', color: C.orange}}>#</span>
          {num}
        </div>
      </div>
      {/* Big name under the number (sting only) */}
      <div
        style={{
          position: 'absolute', left: 427, top: 300, transform: 'translateX(-50%)',
          clipPath: `inset(0 ${100 - nameIn * 100}% 0 0)`, opacity: 1 - ramp(f, 42, 8),
          fontFamily: DISPLAY, fontWeight: 900, fontSize: 40, letterSpacing: -0.5, textTransform: 'uppercase',
          color: C.white, whiteSpace: 'nowrap', textShadow: '0 3px 12px rgba(0,0,0,0.8)',
        }}
      >
        {name}
      </div>
      {/* Persistent badge label next to the shrunken number */}
      <div
        style={{
          position: 'absolute', left: 92, top: 29, opacity: Math.min(ramp(f, 56, 10), badgeOut),
          transform: `translateX(${(1 - ramp(f, 56, 10)) * -10}px)`,
          fontFamily: TEXT, fontWeight: 700, fontSize: 14, letterSpacing: 2, textTransform: 'uppercase',
          color: C.white, whiteSpace: 'nowrap', textShadow: '0 2px 8px rgba(0,0,0,0.9)',
        }}
      >
        {name}
      </div>
      <AbsoluteFill style={{background: '#fff', opacity: flash * 0.85}} />
    </AbsoluteFill>
  );
};
