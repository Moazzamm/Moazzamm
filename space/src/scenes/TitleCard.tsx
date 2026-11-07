import React from 'react';
import {AbsoluteFill, useCurrentFrame, useVideoConfig} from 'remotion';
import {C, DISPLAY} from '../theme';
import {ramp, pop} from '../lib/anim';
import {SpaceBG} from '../components/Space';

export const TitleCard: React.FC = () => {
  const f = useCurrentFrame();
  const {durationInFrames} = useVideoConfig();
  const out = 1 - ramp(f, durationInFrames - 8, 8);
  return (
    <AbsoluteFill style={{opacity: out}}>
      <SpaceBG seed={21} a="#FF8A3D" b="#7A4BFF" warp={0.5 - 0.4 * ramp(f, 0, 40)} />
      <AbsoluteFill style={{alignItems: 'center', justifyContent: 'center', textAlign: 'center', transform: `scale(${1 + f * 0.002})`}}>
        <div style={{fontFamily: DISPLAY, fontWeight: 900, fontSize: 30, color: C.white, letterSpacing: 1, transform: `scale(${pop(f, 2)})`}}>7 THINGS IN SPACE</div>
        <div style={{fontFamily: DISPLAY, fontWeight: 900, fontSize: 52, color: C.hot, letterSpacing: -1, lineHeight: 1, transform: `scale(${pop(f, 10)})`, textShadow: `0 0 30px ${C.orange}`}}>SO EXTREME</div>
        <div style={{fontFamily: DISPLAY, fontWeight: 900, fontSize: 30, color: C.white, letterSpacing: 1, transform: `scale(${pop(f, 18)})`}}>THEY SHOULDN&apos;T EXIST</div>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};
