import React from 'react';
import {AbsoluteFill, useCurrentFrame} from 'remotion';
import {geoOrthographic} from 'd3-geo';
import {C} from '../theme';
import {ramp, lerp, win, easeOut, rnd} from '../lib/anim';
import {beats, type SceneTiming} from '../lib/timing';
import {SpaceBG, Camera} from '../components/Space';
import {BlackHole, Earth} from '../components/Bodies';
import {BigStat, Tag} from '../components/Type';
import {PhotoInsert, SunIcon, Flash} from '../components/Extras';

// 2017 EHT stations (lon, lat): SMA/JCMT Hawaii, SMT Arizona, LMT Mexico, ALMA/APEX Chile, IRAM 30m Spain, SPT South Pole.
const SITES: [number, number][] = [[-155.5, 19.8], [-109.9, 32.7], [-97.3, 19.0], [-67.8, -23.0], [-3.4, 37.1], [0, -89.9]];
// Planet orbit radii in AU (Mercury → Neptune).
const ORBITS = [0.39, 0.72, 1, 1.52, 5.2, 9.58, 19.2, 30.1];
const PLANET_COL = ['#BBB', '#E8C98A', '#5CA8FF', '#E0703A', '#E3B07A', '#E9D49A', '#9BE3EA', '#5C7CFF'];

export const M87: React.FC<{s: SceneTiming}> = ({s}) => {
  const f = useCurrentFrame();
  const b = beats(s, {
    first: ['The first black hole'],
    in2019: ['In 2019'],
    shadow: ['The shadow of the black hole'],
    far: ["It's fifty-five million"],
    horizon: ['Its event horizon'],
    drop: ['Drop it into'],
  });
  const tiltOsc = 0.24 + 0.06 * Math.sin(f / 60);
  // Event horizon ≈ 40 billion km ≈ 267 AU across. Solar-system zoom-out: Neptune orbit first 300 px wide.
  const out = ramp(f, b.drop + 30, 60, 0, 1, easeOut);
  const pxPerAU = lerp(300 / (2 * 30.1), 380 / 267, out);
  const proj = geoOrthographic().rotate([-f * 0.6 + 120, -10]).scale(150).translate([427, 240]).clipAngle(90);

  return (
    <AbsoluteFill style={{background: C.space}}>
      <SpaceBG seed={2} a="#FF8A3D" b="#7A4BFF" drift={[0.2, 0.05]} neb={0.3} />

      {/* procedural black hole, slowly orbiting camera */}
      <AbsoluteFill style={{opacity: win(f, 30, b.in2019 + 4, 8)}}>
        <Camera zoom={lerp(0.8, 1.2, ramp(f, 30, 150, 0, 1, (t) => t))}>
          <BlackHole cx={427} cy={230} r={46} tilt={tiltOsc} />
        </Camera>
        <Tag x={427} y={360} at={b.first + 6} align="center" size={18} color={C.hot}>the first ever photographed</Tag>
      </AbsoluteFill>

      {/* Earth-sized telescope network */}
      <AbsoluteFill style={{opacity: win(f, b.in2019 - 2, b.shadow + 4, 8)}}>
        <Earth cx={427} cy={240} r={150} spin={0.6} />
        <svg width={854} height={480} style={{position: 'absolute'}}>
          {SITES.map((p, i) => {
            const xy = proj(p);
            const visible = (() => {
              const r = proj.rotate();
              const lon = ((p[0] + r[0] + 540) % 360) - 180;
              return Math.cos((lon * Math.PI) / 180) * Math.cos((p[1] * Math.PI) / 180) > -0.05;
            })();
            if (!xy || !visible) return null;
            return (
              <g key={i} opacity={ramp(f, b.in2019 + 10 + i * 5, 6)}>
                <circle cx={xy[0]} cy={xy[1]} r={5} fill={C.hot} />
                <circle cx={xy[0]} cy={xy[1]} r={10 + 4 * Math.sin(f / 4 + i)} fill="none" stroke={C.hot} opacity={0.6} />
              </g>
            );
          })}
        </svg>
        <Tag x={427} y={50} at={b.in2019 + 20} align="center" size={17}>radio dishes linked into one Earth-sized telescope</Tag>
        <Tag x={427} y={410} at={b.in2019 + 40} align="center" size={12} color={C.dim}>2017 observing stations (positions approximate)</Tag>
      </AbsoluteFill>

      {/* the real image */}
      <PhotoInsert src="img/m87_eht.jpg" at={b.shadow} until={b.horizon + 2} credit="EHT Collaboration · CC BY 4.0" stamp="REAL IMAGE · EHT" fit="cover" zoom={[1.0, 1.35]} />
      <AbsoluteFill style={{opacity: win(f, b.far, b.horizon + 2, 6)}}>
        <BigStat x={170} y={360} at={b.far} count={[0, 55, (n) => `${Math.round(n)} MILLION`]} label="light-years away" size={30} color={C.white} />
        <BigStat x={650} y={360} at={b.far + 60} count={[0, 6.5, (n) => `${n.toFixed(1)} BILLION`]} label="times the Sun's mass" size={30} color={C.hot} />
        {Array.from({length: 60}).map((_, i) => {
          const t = ramp(f, b.far + 60 + i * 0.6, 14, 0, 1, easeOut);
          return t > 0 ? <SunIcon key={i} cx={lerp(650, rnd(i) * 854, t)} cy={lerp(330, rnd(i + 7) * 300, t)} r={4 + rnd(i + 2) * 5} o={0.85 * (1 - ramp(f, b.horizon - 10, 10))} /> : null;
        })}
      </AbsoluteFill>

      {/* solar system swallowed by the event horizon */}
      <AbsoluteFill style={{opacity: ramp(f, b.horizon - 2, 8)}}>
        <AbsoluteFill style={{background: C.space}} />
        <svg width={854} height={480} style={{position: 'absolute'}}>
          {ORBITS.map((au, i) => {
            const rr = au * pxPerAU;
            const ang = f * (0.05 / Math.sqrt(au)) + i;
            return (
              <g key={i} opacity={ramp(f, b.drop + i * 3, 8)}>
                <circle cx={427} cy={235} r={rr} fill="none" stroke="rgba(255,255,255,0.25)" />
                <circle cx={427 + Math.cos(ang) * rr} cy={235 + Math.sin(ang) * rr} r={Math.max(1.4, 3.2 - out * 1.5)} fill={PLANET_COL[i]} />
              </g>
            );
          })}
        </svg>
        <SunIcon cx={427} cy={235} r={Math.max(2, 7 - out * 5)} o={ramp(f, b.drop, 8)} />
        <AbsoluteFill style={{opacity: win(f, b.horizon - 2, b.drop + 6, 8)}}>
          <BlackHole cx={427} cy={235} r={lerp(40, 70, ramp(f, b.horizon, b.drop - b.horizon))} tilt={tiltOsc} />
        </AbsoluteFill>
        {/* event horizon outline, true scale: ≈ 40 billion km ≈ 267 AU */}
        <div
          style={{
            position: 'absolute', left: 427 - (267 / 2) * pxPerAU, top: 235 - (267 / 2) * pxPerAU, width: 267 * pxPerAU, height: 267 * pxPerAU, borderRadius: '50%',
            border: `3px solid ${C.hot}`, boxShadow: `0 0 30px ${C.orange}, inset 0 0 60px rgba(0,0,0,0.9)`, background: `rgba(0,0,0,${0.55 * out})`,
            opacity: f < b.drop ? ramp(f, b.horizon + 6, 10) : 1,
          }}
        />
        <BigStat x={427} y={30} at={b.horizon + 10} value="≈ 40 BILLION KM" label="event horizon diameter" size={34} color={C.hot} />
        <Tag x={427} y={430} at={b.drop + 70} align="center" size={15}>Every planet's orbit fits inside, with room to spare</Tag>
        <Tag x={840} y={14} at={b.drop} size={9.5} color={C.dim} align="right">Orbits and event horizon drawn to the same scale</Tag>
      </AbsoluteFill>
      <Flash at={b.shadow} k={0.5} />
    </AbsoluteFill>
  );
};
