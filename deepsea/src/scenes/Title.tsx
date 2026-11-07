import React from 'react';
import {AbsoluteFill, useCurrentFrame, useVideoConfig} from 'remotion';
import {C, DISPLAY, TEXT} from '../theme';
import {ramp, pop} from '../lib/anim';

export const Title: React.FC = () => {
  const f = useCurrentFrame();
  const {durationInFrames} = useVideoConfig();
  const out = 1 - ramp(f, durationInFrames - 12, 12);
  return (
    <AbsoluteFill style={{alignItems: 'center', justifyContent: 'center', opacity: out}}>
      <div style={{fontFamily: TEXT, fontWeight: 700, letterSpacing: 8, color: C.cyan, fontSize: 18, opacity: ramp(f, 4, 14)}}>A DIVE TO THE BOTTOM OF THE OCEAN</div>
      <div style={{width: 360 * ramp(f, 8, 30), height: 1, background: C.cyan, margin: '18px 0'}} />
      <div style={{fontFamily: DISPLAY, fontWeight: 800, fontSize: 84, color: C.white, lineHeight: 1, textAlign: 'center', transform: `scale(${pop(f, 10)})`, textShadow: '0 8px 40px rgba(0,0,0,0.5)'}}>
        WHY THE DEEP SEA<br />IS FULL OF <span style={{color: C.cyan}}>GIANTS</span>
      </div>
    </AbsoluteFill>
  );
};
