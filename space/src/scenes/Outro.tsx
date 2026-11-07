import React from 'react';
import {AbsoluteFill, useCurrentFrame} from 'remotion';
import {C, DISPLAY, TEXT} from '../theme';
import {ramp, pop} from '../lib/anim';
import {beats, cueFrame, type SceneTiming} from '../lib/timing';
import {SpaceBG} from '../components/Space';
import {Mars, Jupiter, SaturnPole, Pulsar, BlackHole, Galaxy} from '../components/Bodies';
import {Cube3D} from '../components/Extras';

// Recap grid: each tile pops as its word is spoken, each one still moving.
const TILES = [
  {k: 'mountain', el: <Mars cx={60} cy={60} r={42} />},
  {k: 'storm', el: <Jupiter cx={60} cy={60} r={42} />},
  {k: 'hexagon', el: <SaturnPole cx={60} cy={60} r={44} />},
  {k: 'sugar', el: <Cube3D cx={60} cy={60} size={34} />},
  {k: 'flash', el: <Pulsar cx={60} cy={60} r={7} beamSpeed={10} />},
  {k: 'shadow', el: <BlackHole cx={60} cy={60} r={14} />},
  {k: 'speck', el: <Galaxy cx={60} cy={60} r={46} count={300} />},
];

export const Outro: React.FC<{s: SceneTiming}> = ({s}) => {
  const f = useCurrentFrame();
  const b = beats(s, {first: ['A mountain'], real: ['Every single one'], which: ['Which one surprised'], tell: ['Tell us'], more: ['And if you want more']});
  const c0 = cueFrame(s, 'A mountain');
  const per = Math.max(8, (b.real - c0) / 7.5);
  const gridOut = 1 - ramp(f, b.which - 4, 8);
  return (
    <AbsoluteFill style={{background: C.space}}>
      <SpaceBG seed={12} a="#FF8A3D" b="#5CE1FF" drift={[0.4, 0.06]} />
      <AbsoluteFill style={{opacity: gridOut}}>
        {TILES.map((t, i) => {
          const at = c0 + Math.round(i * per);
          const x = 40 + (i % 4) * 200 + (i >= 4 ? 100 : 0);
          const y = i < 4 ? 60 : 210;
          const sp = pop(f, at);
          return f < at ? null : (
            <div key={t.k} style={{position: 'absolute', left: x, top: y, width: 120, height: 120, transform: `scale(${sp})`, borderRadius: 12, overflow: 'hidden', background: 'rgba(255,255,255,0.04)', border: `1px solid ${C.faint}`}}>
              <div style={{position: 'absolute', left: 0, top: 0, width: 854, height: 480}}>{t.el}</div>
              <div style={{position: 'absolute', left: 0, right: 0, bottom: 4, textAlign: 'center', fontFamily: TEXT, fontWeight: 800, fontSize: 10, letterSpacing: 1.5, color: C.white, textTransform: 'uppercase', textShadow: '0 1px 4px #000'}}>{t.k}</div>
            </div>
          );
        })}
        <div style={{position: 'absolute', left: 0, right: 0, top: 350, textAlign: 'center', transform: `scale(${pop(f, b.real)})`, opacity: f > b.real ? 1 : 0, fontFamily: DISPLAY, fontWeight: 900, fontSize: 30, color: C.hot}}>EVERY SINGLE ONE IS REAL</div>
      </AbsoluteFill>
      <AbsoluteFill style={{opacity: ramp(f, b.which, 8), alignItems: 'center', justifyContent: 'center', flexDirection: 'column'}}>
        <div style={{transform: `scale(${pop(f, b.which)})`, fontFamily: DISPLAY, fontWeight: 900, fontSize: 44, color: C.white, textAlign: 'center', lineHeight: 1.05}}>
          WHICH ONE<br /><span style={{color: C.hot}}>SURPRISED YOU?</span>
        </div>
        <div style={{marginTop: 22, transform: `scale(${pop(f, b.tell)})`, opacity: f > b.tell ? 1 : 0, fontFamily: TEXT, fontWeight: 700, fontSize: 15, color: C.dim, letterSpacing: 2}}>TELL US IN THE COMMENTS</div>
        <div style={{marginTop: 26, transform: `scale(${pop(f, b.more + 20)})`, opacity: f > b.more + 20 ? 1 : 0, background: C.red, color: '#fff', fontFamily: TEXT, fontWeight: 800, fontSize: 16, letterSpacing: 1.5, padding: '10px 22px', borderRadius: 4}}>SUBSCRIBE FOR MORE</div>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};
