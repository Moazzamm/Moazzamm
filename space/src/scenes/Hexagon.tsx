import React from 'react';
import {AbsoluteFill, useCurrentFrame} from 'remotion';
import {C} from '../theme';
import {ramp, lerp, win, easeOut} from '../lib/anim';
import {beats, type SceneTiming} from '../lib/timing';
import {SpaceBG, Camera} from '../components/Space';
import {SaturnPole, Earth} from '../components/Bodies';
import {BigStat, Tag} from '../components/Type';
import {Dim} from '../components/Extras';

export const Hexagon: React.FC<{s: SceneTiming}> = ({s}) => {
  const f = useCurrentFrame();
  const b = beats(s, {
    storm: ['A storm with straight'],
    nature: ['Nature almost never'],
    but: ["But at Saturn's north pole"],
    line: ['You could line up'],
    winds: ['Winds race around'],
    voyager: ['The Voyager probes'],
    decades: ['Decades later'],
    sci: ['Scientists think'],
  });
  const R = 200;
  const hexR = R * 0.55; // vertex radius → 30,000 km across vertex-to-vertex
  const kmPerPx = 30000 / (2 * hexR);
  const earthR = 12742 / kmPerPx / 2;
  const vortexZoom = ramp(f, b.winds + 60, 40, 0, 1);
  const poleOut = 1 - ramp(f, b.voyager - 4, 8);
  const roll = (k: number) => ramp(f, b.line + k * 10, 26, 0, 1, easeOut);

  return (
    <AbsoluteFill style={{background: C.space}}>
      <SpaceBG seed={6} a="#E3B566" b="#5CE1FF" drift={[0.15, 0.1]} neb={0.25} />

      <AbsoluteFill style={{opacity: poleOut}}>
        <Camera zoom={lerp(lerp(0.75, 1, ramp(f, 30, 120, 0, 1, easeOut)), 2.4, vortexZoom)} rot={f * 0.06}>
          <SaturnPole cx={427} cy={235} r={R} flow={f > b.winds ? 2.2 : 1} />
          {/* six-sided highlight trace */}
          <svg width={854} height={480} style={{position: 'absolute'}}>
            <polygon
              points={Array.from({length: 6}).map((_, k) => `${427 + Math.cos((k / 6) * Math.PI * 2) * hexR},${235 + Math.sin((k / 6) * Math.PI * 2) * hexR}`).join(' ')}
              fill="none" stroke="#fff" strokeWidth={3} pathLength={1} strokeDasharray="1" strokeDashoffset={1 - ramp(f, b.nature + 20, 40)}
              opacity={win(f, b.nature + 20, b.line, 10)}
            />
          </svg>
          {/* Earths rolling into the hexagon, to scale */}
          {[0, 1, 2].map((k) => {
            const t = roll(k);
            if (t <= 0) return null;
            const cx = 427 - hexR + earthR + k * 2 * earthR;
            return (
              <AbsoluteFill key={k} style={{opacity: win(f, b.line + k * 10, b.winds + 10, 8), clipPath: k === 2 ? `inset(0 ${854 - (427 + hexR)}px 0 0)` : undefined}}>
                <Earth cx={lerp(-100, cx, t)} cy={235} r={earthR} spin={2} />
              </AbsoluteFill>
            );
          })}
        </Camera>
        <Dim x1={427 - hexR * 0.75} x2={427 + hexR * 0.75} y={70} at={b.but + 25} label="≈ 30,000 KM ACROSS" />
        <BigStat x={720} y={330} at={b.line + 30} value="2+ EARTHS" size={30} color={C.cyan} />
        <BigStat x={130} y={320} at={b.winds} count={[0, 320, (n) => `${Math.round(n)}`]} label="km/h winds" size={52} color={C.hot} />
        <Tag x={427} y={120} at={b.winds + 70} align="center" size={15} color={C.hot}>a giant hurricane at the centre</Tag>
      </AbsoluteFill>

      {/* Discovery timeline with probes flying past */}
      <AbsoluteFill style={{opacity: win(f, b.voyager - 4, b.sci + 4, 8)}}>
        <svg width={854} height={480} style={{position: 'absolute'}}>
          <line x1={60} x2={794} y1={300} y2={300} stroke={C.faint} strokeWidth={2} />
          <circle cx={200} cy={300} r={8} fill={C.cyan} opacity={ramp(f, b.voyager, 6)} />
          <circle cx={640} cy={300} r={8} fill={C.hot} opacity={ramp(f, b.decades, 6)} />
          {/* probes */}
          {[{at: b.voyager, y: 170, c: C.cyan}, {at: b.decades, y: 210, c: C.hot}].map((p, i) => {
            const x = lerp(-80, 934, ramp(f, p.at, 70, 0, 1, (t) => t));
            return (
              <g key={i} transform={`translate(${x} ${p.y})`} opacity={f > p.at ? 1 : 0}>
                <rect x={-10} y={-6} width={20} height={12} fill="#ddd" />
                <circle cx={0} cy={-16} r={12} fill="none" stroke="#ddd" strokeWidth={3} />
                <line x1={10} y1={0} x2={34} y2={0} stroke="#aaa" strokeWidth={2} />
                <line x1={-80} y1={0} x2={-14} y2={0} stroke={p.c} strokeWidth={2} opacity={0.6} />
              </g>
            );
          })}
        </svg>
        <BigStat x={200} y={320} at={b.voyager + 6} value="1980–81" label="Voyagers spot it" size={36} color={C.cyan} />
        <BigStat x={640} y={320} at={b.decades + 6} value="2004+" label="Cassini: still there" size={36} color={C.hot} />
      </AbsoluteFill>

      {/* Leading explanation: fast and slow winds make a 6-crested wave */}
      <AbsoluteFill style={{opacity: ramp(f, b.sci - 2, 10)}}>
        <AbsoluteFill style={{background: '#070B18'}} />
        <svg width={854} height={480} style={{position: 'absolute'}}>
          {(() => {
            const a = 0.16 * ramp(f, b.sci + 20, 60);
            const pts: string[] = [];
            for (let k = 0; k <= 180; k++) {
              const th = (k / 180) * Math.PI * 2;
              const rr = 140 * (1 + a * Math.cos(6 * th + f * 0.02));
              pts.push(`${427 + Math.cos(th + f * 0.01) * rr},${235 + Math.sin(th + f * 0.01) * rr}`);
            }
            return <polygon points={pts.join(' ')} fill="rgba(92,225,255,0.06)" stroke={C.hot} strokeWidth={3} strokeDasharray="10 12" strokeDashoffset={-f * 3} />;
          })()}
          {/* inner fast / outer slow arrows */}
          {Array.from({length: 12}).map((_, k) => {
            const inner = k % 2 === 0;
            const rr = inner ? 95 : 190;
            const th = (k / 12) * Math.PI * 2 + f * (inner ? 0.03 : 0.008);
            const x = 427 + Math.cos(th) * rr, y = 235 + Math.sin(th) * rr;
            const d = th + Math.PI / 2;
            return (
              <g key={k} transform={`translate(${x} ${y}) rotate(${(d * 180) / Math.PI})`}>
                <path d="M-10 -5 L6 0 L-10 5" fill="none" stroke={inner ? C.hot : C.cyan} strokeWidth={2.5} />
              </g>
            );
          })}
        </svg>
        <Tag x={427} y={60} at={b.sci + 4} align="center" size={18}>Fast wind meets slower wind</Tag>
        <Tag x={427} y={88} at={b.sci + 40} align="center" size={13} color={C.hot}>→ the jet stream bends into a 6-crested wave</Tag>
        <Tag x={427} y={420} at={b.sci + 20} align="center" size={10} color={C.dim}>Leading explanation · illustration</Tag>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};
