import React from 'react';
import {AbsoluteFill, useCurrentFrame, useVideoConfig} from 'remotion';
import {C, T} from '../theme';
import {ramp} from '../lib/anim';

export const TitleCard: React.FC = () => {
  const f = useCurrentFrame();
  const {durationInFrames} = useVideoConfig();
  const out = 1 - ramp(f, durationInFrames - 14, 14);
  return (
    <AbsoluteFill style={{backgroundColor: C.navy, justifyContent: 'center', alignItems: 'center', opacity: out}}>
      <div style={{textAlign: 'center'}}>
        <div style={{...T.title, color: C.paper, opacity: ramp(f, 4, 16)}}>Earth Looks Fully Explored.</div>
        <div style={{...T.title, color: C.amber, marginTop: 6, opacity: ramp(f, 22, 16)}}>It Isn&apos;t.</div>
      </div>
    </AbsoluteFill>
  );
};
