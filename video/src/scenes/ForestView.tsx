import React from 'react';
import {AbsoluteFill, Img, staticFile, useCurrentFrame} from 'remotion';
import {C, T} from '../theme';
import {ramp, lerp, window} from '../lib/anim';
import {paraFrame, type SceneTiming, FPS} from '../lib/timing';
import {ChapterTag, Credit, Label, Stat} from '../components/Text';

// Canopy profile (schematic). Heights from Timberlake & Bayliss 2016: canopy trees 40–50 m.
const TREES = [
  [80, 44], [140, 38], [195, 48], [255, 30], [300, 42], [360, 50], [420, 35], [470, 46], [530, 28], [585, 41],
];
const GROUND = 360;
const PX_PER_M = 4.6;

export const ForestView: React.FC<{s: SceneTiming}> = ({s}) => {
  const f = useCurrentFrame();
  const p = (i: number, o = 0) => paraFrame(s, i, o);

  const push = ramp(f, 0, p(1) + 20); // slow push-in from satellite scale
  const sat = window(f, 0, p(1, 6), 18);
  const canopy = window(f, p(1, 5), p(2) + 10, 18);
  const timeline = window(f, p(2), p(3) + 8, 16);
  const people = window(f, p(3), p(4) + 8, 16);
  const coverage = ramp(f, p(4), 18);

  return (
    <AbsoluteFill style={{backgroundColor: C.navy}}>
      {/* Real satellite image */}
      <AbsoluteFill style={{opacity: sat}}>
        <div style={{position: 'absolute', inset: 0, overflow: 'hidden'}}>
          <Img
            src={staticFile('img/mabu_aster_2023.jpg')}
            style={{
              width: 854,
              position: 'absolute',
              top: lerp(-230, -280, push),
              left: 0,
              transform: `scale(${lerp(1, 1.35, push)})`,
              transformOrigin: '47% 52%',
            }}
          />
        </div>
        <AbsoluteFill style={{background: 'linear-gradient(90deg, rgba(11,20,38,0.75) 0%, rgba(11,20,38,0) 45%)'}} />
        <Label x={28} y={300} at={p(0, 3)} width={300} size={11} color={C.paper}>
          Satellite image of Mount Mabu, 4 Oct 2023 (ASTER). Not the 2005 Google Earth view.
        </Label>
        <div style={{position: 'absolute', right: 28, top: 70, width: 250, background: 'rgba(11,20,38,0.85)', padding: 10, opacity: ramp(f, p(1), 16)}}>
          <div style={{...T.kicker, color: C.cyan}}>From above you can see</div>
          <div style={{...T.label, color: C.paper, fontSize: 12.5, margin: '4px 0 8px'}}>extent · canopy texture · edges</div>
          <div style={{...T.kicker, color: C.amber}}>You cannot see</div>
          <div style={{...T.label, color: C.paper, fontSize: 12.5, marginTop: 4}}>species · understorey · forest floor</div>
        </div>
      </AbsoluteFill>

      {/* Canopy profile */}
      <AbsoluteFill style={{opacity: canopy}}>
        <svg width={854} height={480} style={{position: 'absolute'}}>
          <rect y={GROUND} width={854} height={40} fill="#2C2A22" />
          {TREES.map(([x, h], i) => {
            const top = GROUND - h * PX_PER_M * ramp(f, p(1, 5) + i * 3, 20);
            return (
              <g key={i}>
                <line x1={x} y1={GROUND} x2={x} y2={top + 14} stroke="#6B5A45" strokeWidth={3} />
                <ellipse cx={x} cy={top + 10} rx={26} ry={16} fill="#2E5B3E" />
              </g>
            );
          })}
          {[0, 10, 20, 30, 40, 50].map((m) => (
            <g key={m}>
              <line x1={624} x2={632} y1={GROUND - m * PX_PER_M} y2={GROUND - m * PX_PER_M} stroke={C.paperDim} />
              <text x={638} y={GROUND - m * PX_PER_M + 3.5} fill={C.paperDim} fontSize={9.5} fontFamily="Inter">
                {m} m
              </text>
            </g>
          ))}
          <line x1={0} x2={620} y1={GROUND - 45 * PX_PER_M} y2={GROUND - 45 * PX_PER_M} stroke={C.cyan} strokeDasharray="3 4" opacity={0.6} />
        </svg>
        <Label x={680} y={GROUND - 48 * PX_PER_M} at={p(1, 7)} width={160} size={11.5}>
          Canopy trees reach 40–50 m
        </Label>
        <Label x={680} y={GROUND - 22 * PX_PER_M} at={p(1, 8)} width={160} size={11.5} color={C.amber}>
          What lives below is invisible from orbit
        </Label>
        <Label x={28} y={70} at={p(1, 6)} size={10} color={C.amber}>
          SCHEMATIC PROFILE · heights to scale
        </Label>
      </AbsoluteFill>

      {/* Timeline + documented results */}
      <AbsoluteFill style={{opacity: timeline}}>
        <svg width={854} height={480} style={{position: 'absolute'}}>
          <line x1={60} x2={lerp(60, 794, ramp(f, p(2), 40))} y1={110} y2={110} stroke={C.paperFaint} strokeWidth={1.5} />
          {[[100, 0], [380, 3.5], [700, 20]].map(([x, o], i) => (
            <circle key={i} cx={x} cy={110} r={5} fill={i === 2 ? C.amber : C.cyan} opacity={ramp(f, p(2, o as number), 10)} />
          ))}
        </svg>
        <Label x={100} y={124} at={p(2)} align="center" size={11.5} width={160}>
          Dec 2005
          <br />
          <span style={{color: C.paperDim}}>first scientific visit</span>
        </Label>
        <Label x={380} y={124} at={p(2, 3.5)} align="center" size={11.5} width={240}>
          Oct 2008
          <br />
          <span style={{color: C.paperDim}}>Kew-led expedition with Mozambican, Malawian &amp; international partners</span>
        </Label>
        <Label x={700} y={124} at={p(2, 20)} align="center" size={11.5} width={190}>
          by 2016
          <br />
          <span style={{color: C.amber}}>13 new species recorded</span>
        </Label>
        <Stat x={60} y={200} at={p(2, 8)} value="≈ 69–79 km²" caption="of rainforest — estimates differ by method" size={26} width={300} />
        <div style={{position: 'absolute', left: 420, top: 196, width: 400}}>
          {[
            ['Atheris mabuensis', 'Mabu forest viper'],
            ['Rhampholeon maspictus', 'Mabu pygmy chameleon'],
            ['Rhinolophus mabuensis', 'a horseshoe bat'],
            ['Cymothoe sp. & others', 'new butterflies'],
          ].map(([sci, com], i) => (
            <div key={sci} style={{display: 'flex', gap: 10, borderTop: `1px solid ${C.paperFaint}`, padding: '4px 0', opacity: ramp(f, p(2, 14) + i * 22, 14)}}>
              <span style={{...T.label, fontSize: 12, color: C.paper, fontStyle: 'italic', width: 175}}>{sci}</span>
              <span style={{...T.label, fontSize: 12, color: C.paperDim}}>{com}</span>
            </div>
          ))}
        </div>
      </AbsoluteFill>

      {/* Who already knew the forest */}
      <AbsoluteFill style={{opacity: people}}>
        <Label x={60} y={80} at={p(3) + 4} width={700} size={22} weight={700}>
          New to biologists <span style={{color: C.amber}}>≠</span> new to people
        </Label>
        {[
          ['Local hunters', 'knew the forest’s animals and helped researchers record larger mammals'],
          ['Civil war', 'families reportedly moved into the forest and sheltered there'],
          ['Colonial era', 'tea estates were worked on the lower slopes'],
        ].map(([h, b], i) => (
          <div key={h} style={{position: 'absolute', left: 60 + i * 250, top: 150, width: 220, opacity: ramp(f, p(3, 3) + i * 40, 16)}}>
            <div style={{...T.kicker, color: C.cyan}}>{h}</div>
            <div style={{...T.label, color: C.paper, fontSize: 13, marginTop: 6}}>{b}</div>
          </div>
        ))}
      </AbsoluteFill>

      {/* Survey coverage (schematic) */}
      <AbsoluteFill style={{opacity: coverage}}>
        <svg width={854} height={480} style={{position: 'absolute'}}>
          <ellipse cx={427} cy={215} rx={190} ry={120} fill="#203A2C" />
          <path d="M427 95 A190 120 0 0 1 617 215 A190 120 0 0 1 427 335" fill="none" stroke={C.cyan} strokeWidth={3} />
          <path d="M427 335 A190 120 0 0 1 237 215 A190 120 0 0 1 427 95" fill="none" stroke={C.amber} strokeWidth={2} strokeDasharray="6 5" />
          <circle cx={427} cy={215} r={7} fill={C.cyan} />
        </svg>
        <Label x={440} y={200} at={p(4) + 6} size={11.5}>summit</Label>
        <Label x={630} y={180} at={p(4, 1.5)} width={200} size={12} color={C.cyan}>
          Eastern edge &amp; summit — where most surveys worked
        </Label>
        <Label x={225} y={180} at={p(4, 4.5)} width={200} size={12} color={C.amber} align="right">
          Drier western &amp; northern slopes — not visited by scientists as of 2016
        </Label>
        <Label x={826} y={70} at={p(4)} align="right" size={10} color={C.amber}>
          SCHEMATIC · not a survey map
        </Label>
      </AbsoluteFill>

      <ChapterTag n="04" word="Forest" place="Mount Mabu, Zambezia, Mozambique" />
      <Credit at={0} until={p(1, 6)}>Image: NASA/METI/AIST/Japan Space Systems, U.S./Japan ASTER Science Team (public domain)</Credit>
      <Credit at={p(1, 6)} until={p(5) + 999}>Sources: Bayliss et al. 2014, Oryx 48(2); Timberlake &amp; Bayliss 2016, Mabu management plan</Credit>
    </AbsoluteFill>
  );
};
