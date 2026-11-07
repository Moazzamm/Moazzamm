import React from 'react';
import {AbsoluteFill, useCurrentFrame} from 'remotion';
import {C, DISPLAY} from '../theme';
import {ramp, lerp, pop, shake, win, easeOut} from '../lib/anim';
import {beats, type SceneTiming} from '../lib/timing';
import {SpaceBG, Camera} from '../components/Space';
import {Jupiter, Earth, Pulsar, BlackHole, Galaxy, Mars} from '../components/Bodies';
import {BigStat, Tag} from '../components/Type';
import {Flash, LightStreak} from '../components/Extras';

export const Intro: React.FC<{s: SceneTiming}> = ({s}) => {
  const f = useCurrentFrame();
  const b = beats(s, {
    storm: ["There's a storm"],
    raging: ['It has been raging'],
    five: ["And it's only number five"],
    because: ['Because out there'],
    mountain: ['From a mountain'],
    seven: ['These are seven'],
  });

  // Phase A: Jupiter, camera pushing toward the Great Red Spot; Earth flies in to show scale.
  const aOut = 1 - ramp(f, b.because - 4, 8);
  const push = ramp(f, 0, b.five, 0, 1, (t) => t);
  const earthIn = ramp(f, b.storm + 30, 34, 0, 1, easeOut);
  const jr = 150;
  const jcx = 470, jcy = 235;
  const gx = jcx + jr * 0.32, gy = jcy + jr * 0.3;
  const sh = shake(f, b.five, 9, 20);

  // Phase B: fly-through montage of what's coming.
  const fly = (start: number) => {
    const t = (f - start) / 26;
    return {o: t < 0 || t > 1 ? 0 : Math.sin(t * Math.PI), z: lerp(0.3, 2.8, Math.max(0, Math.min(1, t)))};
  };
  const m1 = fly(b.because + 2), m2 = fly(b.because + 22), m3 = fly(b.because + 42);

  return (
    <AbsoluteFill style={{background: C.space}}>
      <SpaceBG seed={3} a="#7A4BFF" b="#FF8A3D" drift={[0.4, 0.05]} warp={win(f, b.because - 6, b.mountain + 4, 8) * 0.9} />

      <AbsoluteFill style={{opacity: aOut}}>
        <Camera zoom={1 + push * 0.45} x={-push * 70 + sh.x} y={-push * 50 + sh.y}>
          <Jupiter cx={jcx} cy={jcy} r={jr} />
          <AbsoluteFill style={{opacity: earthIn}}>
            <Earth cx={lerp(-80, gx, earthIn)} cy={lerp(120, gy, earthIn)} r={jr * 0.36 / 1.3} spin={1.2} />
          </AbsoluteFill>
        </Camera>
        <Tag x={60} y={70} at={b.storm + 40} until={b.five} color={C.hot} size={15}>Earth fits inside this storm</Tag>
        <BigStat x={190} y={300} at={b.raging} until={b.five} value="1800s →" label="raging since at least" size={44} />
      </AbsoluteFill>

      {/* "only number five" slam */}
      <AbsoluteFill style={{opacity: win(f, b.five, b.because + 2, 6)}}>
        <AbsoluteFill style={{background: 'rgba(4,6,14,0.55)'}} />
        <BigStat x={427} y={140} at={b.five} value="#5" color={C.hot} size={150} label="...and it's only number five" />
      </AbsoluteFill>

      {/* fly-through teasers */}
      <AbsoluteFill style={{opacity: m1.o, transform: `scale(${m1.z})`}}>
        <Pulsar cx={427} cy={230} r={14} beamSpeed={9} />
      </AbsoluteFill>
      <AbsoluteFill style={{opacity: m2.o, transform: `scale(${m2.z})`}}>
        <BlackHole cx={427} cy={230} r={34} />
      </AbsoluteFill>
      <AbsoluteFill style={{opacity: m3.o, transform: `scale(${m3.z})`}}>
        <Galaxy cx={427} cy={230} r={120} count={500} />
      </AbsoluteFill>
      <Tag x={427} y={70} at={b.because + 4} until={b.mountain} align="center" size={20} color={C.white}>
        Too big · too dense · too violent
      </Tag>

      {/* mountain vs ancient light */}
      <AbsoluteFill style={{opacity: win(f, b.mountain, b.seven + 2, 8)}}>
        <AbsoluteFill style={{transform: `translateX(${(1 - ramp(f, b.mountain, 14, 0, 1, easeOut)) * -300}px)`}}>
          <Mars cx={200} cy={230} r={110} highlight={1} />
        </AbsoluteFill>
        <BigStat x={200} y={360} at={b.mountain + 6} value="3× EVEREST" size={30} color={C.hot} />
        <LightStreak y={200} at={b.mountain + 40} dur={36} />
        <LightStreak y={250} at={b.mountain + 48} dur={30} />
        <BigStat x={620} y={140} at={b.mountain + 46} value="13.5 BILLION" label="years of travelling light" size={40} color={C.cyan} />
      </AbsoluteFill>

      {/* seven */}
      <AbsoluteFill style={{opacity: ramp(f, b.seven, 6), alignItems: 'center', justifyContent: 'center'}}>
        <div style={{transform: `scale(${pop(f, b.seven)})`, textAlign: 'center'}}>
          <div style={{fontFamily: DISPLAY, fontWeight: 900, fontSize: 170, color: C.white, lineHeight: 0.9, textShadow: `0 0 50px ${C.orange}`}}>7</div>
          <div style={{fontFamily: DISPLAY, fontWeight: 800, fontSize: 22, color: C.hot, letterSpacing: 3, textTransform: 'uppercase', marginTop: 8}}>of the most extreme things in the universe</div>
        </div>
      </AbsoluteFill>
      <Flash at={b.five} k={0.6} />
      <Flash at={b.seven} k={0.5} />
    </AbsoluteFill>
  );
};
