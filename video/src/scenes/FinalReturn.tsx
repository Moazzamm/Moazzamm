import React from 'react';
import {AbsoluteFill, useCurrentFrame} from 'remotion';
import {C, T} from '../theme';
import {ramp, window} from '../lib/anim';
import {paraFrame, type SceneTiming} from '../lib/timing';
import {FlatMap} from './MapReveal';
import {Credit, Label} from '../components/Text';

// Each kind of knowledge gets its own mark, used consistently.
const LAYERS: {label: string; sub: string; mark: 'stipple' | 'swath' | 'track' | 'dot' | 'line' | 'edge' | 'warm'}[] = [
  {label: 'Estimated', sub: 'seafloor shape from satellites', mark: 'stipple'},
  {label: 'Measured', sub: 'swaths of sonar', mark: 'swath'},
  {label: 'Seen', sub: 'narrow camera tracks', mark: 'track'},
  {label: 'Sampled', sub: 'a 60 cm borehole', mark: 'dot'},
  {label: 'Surveyed', sub: 'passages measured by hand', mark: 'line'},
  {label: 'Walked', sub: 'forest edges, by scientists', mark: 'edge'},
  {label: 'Known locally', sub: 'by the people who live there', mark: 'warm'},
];

const Mark: React.FC<{m: (typeof LAYERS)[number]['mark']}> = ({m}) => (
  <svg width={26} height={14}>
    {m === 'stipple' && [3, 9, 15, 21].map((x) => [3, 9].map((y) => <circle key={`${x}${y}`} cx={x} cy={y + 1} r={1} fill={C.cyan} />))}
    {m === 'swath' && <rect x={1} y={3} width={24} height={8} fill={C.cyan} opacity={0.6} />}
    {m === 'track' && <line x1={1} y1={7} x2={25} y2={7} stroke={C.paper} strokeWidth={1} />}
    {m === 'dot' && <circle cx={13} cy={7} r={3.5} fill={C.amber} />}
    {m === 'line' && <polyline points="1,10 8,5 15,8 25,3" stroke={C.amber} strokeWidth={2} fill="none" />}
    {m === 'edge' && <path d="M1 11 Q13 0 25 11" stroke={C.cyan} strokeWidth={2} fill="none" />}
    {m === 'warm' && <rect x={1} y={2} width={24} height={10} fill="none" stroke="#E9C9A0" strokeWidth={1.5} />}
  </svg>
);

export const FinalReturn: React.FC<{s: SceneTiming}> = ({s}) => {
  const f = useCurrentFrame();
  const p = (i: number, o = 0) => paraFrame(s, i, o);
  const layersStart = p(1, 2.2);
  const step = (p(2) - layersStart) / (LAYERS.length + 0.5);
  const close = ramp(f, p(2) - 6, 24);
  const fadeOut = ramp(f, s.durationInFrames - 45, 40);

  return (
    <AbsoluteFill style={{backgroundColor: C.navy}}>
      <AbsoluteFill style={{opacity: (1 - close * 0.85) * (1 - fadeOut)}}>
        <AbsoluteFill style={{transform: `translateX(${-150 * ramp(f, p(1), 30)}px) scale(${1 - 0.15 * ramp(f, p(1), 30)})`}}>
          <FlatMap opacity={1} frame={f} markersAt={[4, 8, 12, 16]} />
        </AbsoluteFill>
      </AbsoluteFill>

      <div style={{position: 'absolute', left: 590, top: 70, width: 240, opacity: window(f, p(1), p(2) + 8, 14)}}>
        <div style={{...T.kicker, color: C.cyan, marginBottom: 10}}>The same map, read in layers</div>
        {LAYERS.map((l, i) => (
          <div key={l.label} style={{display: 'flex', gap: 10, alignItems: 'center', marginBottom: 9, opacity: ramp(f, layersStart + i * step, 12)}}>
            <Mark m={l.mark} />
            <div>
              <div style={{...T.label, fontSize: 12.5, color: C.paper}}>{l.label}</div>
              <div style={{...T.small, fontSize: 10, color: C.paperDim}}>{l.sub}</div>
            </div>
          </div>
        ))}
      </div>

      <AbsoluteFill style={{opacity: 1 - fadeOut}}>
        <Label x={427} y={150} at={p(2, 4.5)} align="center" size={26} weight={700} width={700}>
          Earth isn&apos;t unexplored.
        </Label>
        <Label x={427} y={190} at={p(2, 6)} align="center" size={26} weight={700} width={700}>
          It is <span style={{color: C.amber}}>unevenly</span> observed.
        </Label>
      </AbsoluteFill>
      <Credit at={p(2, 9)}>Sources and licences: see description · Narration in this cut is a synthetic scratch voice</Credit>
    </AbsoluteFill>
  );
};
