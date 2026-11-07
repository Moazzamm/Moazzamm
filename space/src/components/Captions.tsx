import React from 'react';
import {AbsoluteFill, useCurrentFrame} from 'remotion';
import {C, DISPLAY} from '../theme';
import {FPS, type Cue} from '../lib/timing';
import {pop} from '../lib/anim';

// Kinetic captions: words pop in roughly as they are spoken (character-proportional within each
// sentence cue). Numbers and scene keywords are highlighted.
export const KineticCaptions: React.FC<{cues: Cue[]; keywords?: string[]}> = ({cues, keywords = []}) => {
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
    <AbsoluteFill style={{justifyContent: 'flex-end', alignItems: 'center', paddingBottom: 22, pointerEvents: 'none'}}>
      <div style={{maxWidth: 780, textAlign: 'center', lineHeight: 1.18}}>
        {words.map((w, i) => {
          const at = cue.start + (acc / total) * dur * 0.92;
          acc += w.length + 1;
          const start = Math.round(at * FPS);
          const sp = pop(f, start);
          const clean = w.replace(/[^\w'’-]/g, '').toLowerCase();
          const hot = /\d/.test(w) || kw.some((k) => clean === k || clean.startsWith(k));
          return (
            <span
              key={i}
              style={{
                display: 'inline-block',
                margin: '0 4px',
                fontFamily: DISPLAY,
                fontWeight: 800,
                fontSize: hot ? 27 : 24,
                letterSpacing: -0.3,
                color: hot ? C.hot : C.white,
                opacity: f >= start ? 1 : 0.0,
                transform: `translateY(${(1 - Math.min(sp, 1)) * 8}px) scale(${0.7 + 0.3 * sp})`,
                textShadow: '0 2px 4px rgba(0,0,0,0.95)',
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
