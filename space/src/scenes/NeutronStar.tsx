import React from 'react';
import {AbsoluteFill, useCurrentFrame} from 'remotion';
import {C} from '../theme';
import {ramp, lerp, win, easeOut, shake, rnd} from '../lib/anim';
import {beats, type SceneTiming} from '../lib/timing';
import {SpaceBG, Camera} from '../components/Space';
import {Pulsar} from '../components/Bodies';
import {BigStat, Tag} from '../components/Type';
import {Cube3D, Shockwave, Flash} from '../components/Extras';

export const NeutronStar: React.FC<{s: SceneTiming}> = ({s}) => {
  const f = useCurrentFrame();
  const b = beats(s, {
    cube: ['A sugar cube you could'],
    dies: ['When a giant star dies'],
    around: ['Around one and a half'],
    densest: ['This is the densest'],
    piece: ['A piece the size'],
    mountain: ["That's as much as a mountain"],
    spin: ['And some neutron stars spin'],
  });
  const collapse = b.dies + 50;
  const sh = shake(f, collapse, 12, 24);
  const giantR = collapse > f ? 170 + 6 * Math.sin(f / 4) : lerp(170, 0, ramp(f, collapse - 12, 12));
  const cityIn = ramp(f, b.around + 50, 20);
  const tilt = ramp(f, b.piece + 20, 40, 0, 1, easeOut);

  return (
    <AbsoluteFill style={{background: C.space}}>
      <SpaceBG seed={4} a="#5CE1FF" b="#9B7BFF" drift={[0.3, 0.06]} />

      {/* sugar cube, spinning */}
      <AbsoluteFill style={{opacity: win(f, 40, b.dies + 4, 8)}}>
        <Cube3D cx={427} cy={225} size={90} />
        <Tag x={427} y={340} at={b.cube} align="center" size={16} color={C.cyan}>too heavy to lift</Tag>
      </AbsoluteFill>

      {/* dying giant collapses */}
      <AbsoluteFill style={{opacity: win(f, b.dies - 2, b.around + 52, 8)}}>
        <Camera x={sh.x} y={sh.y} zoom={1 + 0.15 * ramp(f, b.dies, 40)}>
          <div
            style={{
              position: 'absolute', left: 427 - giantR, top: 235 - giantR, width: giantR * 2, height: giantR * 2, borderRadius: '50%',
              background: 'radial-gradient(circle at 45% 42%, #FFD6A0, #FF7A2B 45%, #B22A12 80%, #5A0E06)',
              boxShadow: `0 0 ${giantR * 0.6}px rgba(255,90,40,0.8)`,
            }}
          />
          {f >= collapse ? <Pulsar cx={427} cy={235} r={10} beams={0} /> : null}
          <Shockwave cx={427} cy={235} at={collapse} maxR={700} dur={36} color="#BFE6FF" />
        </Camera>
        <Tag x={427} y={60} at={b.dies + 4} until={collapse} align="center" size={16} color={C.hot}>a giant star dies…</Tag>
        <BigStat x={427} y={300} at={b.around} value="1.5× THE SUN" label="crushed into a ball" size={40} color={C.cyan} />
      </AbsoluteFill>
      <Flash at={collapse} k={0.9} dur={10} />

      {/* city comparison */}
      <AbsoluteFill style={{opacity: win(f, b.around + 50, b.densest + 4, 8) * cityIn}}>
        <svg width={854} height={480} style={{position: 'absolute'}}>
          {Array.from({length: 22}).map((_, i) => (
            <line key={`h${i}`} x1={0} x2={854} y1={i * 24} y2={i * 24 + 6} stroke="rgba(255,200,120,0.18)" strokeWidth={2} />
          ))}
          {Array.from({length: 38}).map((_, i) => (
            <line key={`v${i}`} x1={i * 24} x2={i * 24 - 8} y1={0} y2={480} stroke="rgba(255,200,120,0.18)" strokeWidth={2} />
          ))}
          {Array.from({length: 160}).map((_, i) => (
            <circle key={i} cx={rnd(i) * 854} cy={rnd(i + 40) * 480} r={1.2} fill="#FFD9A0" opacity={0.4 + 0.6 * Math.abs(Math.sin(f / 9 + i))} />
          ))}
        </svg>
        <AbsoluteFill style={{transform: `scale(${lerp(0.4, 1, cityIn)})`}}>
          <Pulsar cx={427} cy={230} r={110} beams={0} />
        </AbsoluteFill>
        <BigStat x={427} y={330} at={b.around + 56} value="≈ 20 KM ACROSS" label="about the size of a city" size={32} />
      </AbsoluteFill>

      {/* densest + balance scale */}
      <AbsoluteFill style={{opacity: ramp(f, b.densest - 2, 8) * (1 - ramp(f, b.spin - 4, 8))}}>
        <BigStat x={427} y={40} at={b.densest} until={b.piece + 24} value="DENSEST MATTER" label="we can directly observe" size={40} color={C.cyan} />
        <svg width={854} height={480} style={{position: 'absolute'}}>
          <polygon points="417,420 437,420 427,250" fill="#556" />
          <g transform={`rotate(${-12 * tilt} 427 250)`}>
            <rect x={187} y={246} width={480} height={8} fill="#99A" />
            <line x1={247} y1={250} x2={247} y2={300} stroke="#99A" strokeWidth={2} />
            <line x1={607} y1={250} x2={607} y2={300} stroke="#99A" strokeWidth={2} />
            <rect x={197} y={300} width={100} height={6} fill="#99A" />
            <rect x={557} y={300} width={100} height={6} fill="#99A" />
            <path d="M562 300 L590 238 L604 256 L622 214 L652 300 Z" fill="#8C9AA8" opacity={ramp(f, b.mountain, 10)} />
            <path d="M612 232 L622 214 L632 236 Z" fill="#fff" opacity={ramp(f, b.mountain, 10)} />
          </g>
        </svg>
        {(() => {
          const th = (-12 * tilt * Math.PI) / 180;
          const px = 427 + -180 * Math.cos(th) - 50 * Math.sin(th);
          const py = 250 + -180 * Math.sin(th) + 50 * Math.cos(th);
          return <AbsoluteFill style={{opacity: ramp(f, b.piece, 10)}}><Cube3D cx={px} cy={py - 16} size={26} glow={0.8} /></AbsoluteFill>;
        })()}
        <BigStat x={200} y={110} at={b.piece + 26} count={[0, 1e9, (n) => `${(n / 1e9).toFixed(n < 1e9 ? 2 : 0)} BILLION`]} label="tonnes" size={30} color={C.hot} />
        <Tag x={640} y={150} at={b.mountain} align="center" size={16} color={C.hot}>≈ a mountain</Tag>
      </AbsoluteFill>

      {/* pulsar lighthouse */}
      <AbsoluteFill style={{opacity: ramp(f, b.spin - 2, 8)}}>
        <Camera zoom={1.1} rot={-8}>
          <Pulsar cx={427} cy={235} r={16} beamSpeed={14} />
        </Camera>
        <AbsoluteFill style={{background: '#CFE9FF', opacity: (f * 14) % 180 < 16 ? 0.15 * (1 - ((f * 14) % 180) / 16) : 0}} />
        <BigStat x={427} y={300} at={b.spin + 10} value="HUNDREDS" label="of spins every second" size={40} color={C.cyan} />
        <Tag x={427} y={60} at={b.spin + 40} align="center" size={16} color={C.white}>a cosmic lighthouse: a pulsar</Tag>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};
