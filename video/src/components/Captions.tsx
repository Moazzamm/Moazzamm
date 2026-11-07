import React from 'react';
import {AbsoluteFill, useCurrentFrame} from 'remotion';
import {C, FONT} from '../theme';
import {FPS, type Cue} from '../lib/timing';
import {ramp} from '../lib/anim';

// Burned-in captions in a reserved band (y > 400). Diagrams never use this band.
export const Captions: React.FC<{cues: Cue[]}> = ({cues}) => {
  const frame = useCurrentFrame();
  const t = frame / FPS;
  const cue = cues.find((c) => t >= c.start && t < c.end + 0.15);
  if (!cue) return null;
  const f0 = Math.round(cue.start * FPS);
  const o = ramp(frame, f0, 5);
  return (
    <AbsoluteFill style={{justifyContent: 'flex-end', alignItems: 'center', paddingBottom: 14, pointerEvents: 'none'}}>
      <div
        style={{
          maxWidth: 700,
          background: 'rgba(8,14,27,0.78)',
          color: C.paper,
          fontFamily: FONT,
          fontSize: 17,
          fontWeight: 500,
          lineHeight: 1.32,
          padding: '6px 12px',
          borderRadius: 3,
          textAlign: 'center',
          opacity: o,
        }}
      >
        {cue.text}
      </div>
    </AbsoluteFill>
  );
};
