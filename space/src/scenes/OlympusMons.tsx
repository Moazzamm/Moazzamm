import React from 'react';
import {AbsoluteFill, useCurrentFrame} from 'remotion';
import {geoMercator, geoPath} from 'd3-geo';
import {feature} from 'topojson-client';
import usTopo from 'us-atlas/states-10m.json';
import type {FeatureCollection, Feature} from 'geojson';
import {C} from '../theme';
import {ramp, lerp, pop, win, easeOut, fmt} from '../lib/anim';
import {beats, type SceneTiming} from '../lib/timing';
import {SpaceBG, Camera} from '../components/Space';
import {Mars} from '../components/Bodies';
import {BigStat, Tag} from '../components/Type';
import {PhotoInsert, Dim} from '../components/Extras';

// eslint-disable-next-line @typescript-eslint/no-explicit-any
const STATES = feature(usTopo as any, (usTopo as any).objects.states) as unknown as FeatureCollection;
const ARIZONA = STATES.features.find((g) => (g.properties as {name?: string})?.name === 'Arizona') as Feature;

// Same scale for Olympus Mons and Arizona: 0.42 px per km.
const PX_PER_KM = 0.42;
const R_EARTH = 6371;

export const OlympusMons: React.FC<{s: SceneTiming}> = ({s}) => {
  const f = useCurrentFrame();
  const b = beats(s, {
    mars: ['On Mars'],
    rises: ['It rises about'],
    everest: ["That's nearly three"],
    tall: ["And it's not just tall"],
    base: ['Its base is about'],
    how: ['How did it get so big'],
    plates: ['Mars has no moving'],
    so: ['So the volcano sat'],
  });

  // Profile chart scale: 10 px per km (vertical). Horizontal is compressed and labelled as such.
  const GROUND = 360;
  const VK = 10;
  const rise = ramp(f, b.rises, 40, 0, 1, easeOut);
  const ruler = 25 * rise;

  // Arizona projected at the same px/km as the volcano disc.
  const lat = 34.2;
  const proj = geoMercator().center([-111.7, lat]).translate([427, 215]).scale(PX_PER_KM * R_EARTH * Math.cos((lat * Math.PI) / 180));
  const azPath = geoPath(proj)(ARIZONA) ?? '';
  const draw = ramp(f, b.base + 40, 40);

  // Hot-spot explainer timing
  const hs = f - b.plates;

  return (
    <AbsoluteFill style={{background: C.space}}>
      <SpaceBG seed={7} a="#FF6A2B" b="#7A4BFF" drift={[0.3, 0.04]} neb={0.3} />

      {/* Mars, rotating, camera drifting in */}
      <AbsoluteFill style={{opacity: win(f, 30, b.rises + 6, 10)}}>
        <Camera zoom={lerp(0.9, 1.35, ramp(f, 30, b.rises - 30, 0, 1, (t) => t))}>
          <Mars cx={427} cy={235} r={165} highlight={0.5 + 0.5 * Math.sin(f / 6)} />
        </Camera>
        <Tag x={560} y={130} at={b.mars + 10} until={b.rises} color={C.hot} size={14}>← Olympus Mons</Tag>
      </AbsoluteFill>

      {/* Profile chart: volcano rises, Everests stack beside it */}
      <AbsoluteFill style={{opacity: win(f, b.rises - 2, b.base + 4, 8)}}>
        <svg width={854} height={480} style={{position: 'absolute'}}>
          <defs>
            <linearGradient id="om" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0" stopColor="#E9925C" />
              <stop offset="1" stopColor="#6E2A14" />
            </linearGradient>
          </defs>
          {/* broad shield with cliff edges */}
          <path
            d={`M40 ${GROUND} L70 ${GROUND - 60 * rise} Q 240 ${GROUND - 250 * rise} 330 ${GROUND - 250 * rise} Q 420 ${GROUND - 250 * rise} 590 ${GROUND - 60 * rise} L620 ${GROUND} Z`}
            fill="url(#om)"
          />
          <line x1={20} x2={834} y1={GROUND} y2={GROUND} stroke={C.dim} />
          {/* ruler */}
          {[0, 5, 10, 15, 20, 25].map((k) => (
            <g key={k} opacity={ramp(f, b.rises + k, 6)}>
              <line x1={820} x2={830} y1={GROUND - k * VK} y2={GROUND - k * VK} stroke={C.dim} />
              <text x={815} y={GROUND - k * VK + 4} fill={C.dim} fontSize={11} textAnchor="end" fontFamily="Inter">{k} km</text>
            </g>
          ))}
          {/* Everests, 8.85 km each */}
          {[0, 1, 2].map((k) => {
            const p = pop(f, b.everest + k * 9);
            if (f < b.everest + k * 9) return null;
            const h = 8.85 * VK;
            const base = GROUND - k * h;
            return (
              <g key={k} transform={`translate(720 ${base}) scale(${Math.min(p, 1.15)}) translate(-720 ${-base})`}>
                <path d={`M680 ${base} L720 ${base - h} L760 ${base} Z`} fill="#DDE6EE" stroke="#8FA3B5" />
                <path d={`M708 ${base - h * 0.7} L720 ${base - h} L732 ${base - h * 0.7} L724 ${base - h * 0.62} L716 ${base - h * 0.66} Z`} fill="#fff" />
              </g>
            );
          })}
        </svg>
        <BigStat x={330} y={70} at={b.rises + 8} count={[0, 25, (n) => `${n.toFixed(0)} KM`]} size={46} color={C.hot} label="above the surrounding plains" />
        <Tag x={720} y={GROUND + 10} at={b.everest} align="center" size={12}>Everest × 3</Tag>
        <Tag x={40} y={GROUND + 12} at={b.rises + 20} size={10} color={C.dim}>Heights to scale · width compressed</Tag>
        <Tag x={720} y={GROUND - ruler * VK - 26} at={b.rises + 4} until={b.everest} align="center" size={12} color={C.dim}>{ruler.toFixed(1)} km</Tag>
      </AbsoluteFill>

      {/* Footprint: real Viking mosaic disc vs Arizona, same scale */}
      <AbsoluteFill style={{opacity: win(f, b.base - 2, b.how + 4, 8)}}>
        <AbsoluteFill style={{transform: `rotate(${f * 0.05}deg) scale(${lerp(0.85, 1, ramp(f, b.base, 20, 0, 1, easeOut))})`}}>
          <div style={{position: 'absolute', left: 427 - 300 * PX_PER_KM, top: 215 - 300 * PX_PER_KM, width: 600 * PX_PER_KM, height: 600 * PX_PER_KM, borderRadius: '50%', overflow: 'hidden', boxShadow: '0 0 40px rgba(255,120,60,0.5)'}}>
            <PhotoInsert src="img/olympus_mons_viking.jpg" at={b.base - 2} until={b.how + 4} credit="" stamp="" zoom={[1.15, 1.3]} />
          </div>
        </AbsoluteFill>
        <svg width={854} height={480} style={{position: 'absolute'}}>
          <path d={azPath} fill={`rgba(92,225,255,${0.16 * draw})`} stroke={C.cyan} strokeWidth={3.5} pathLength={1} strokeDasharray="1" strokeDashoffset={1 - draw} />
        </svg>
        <Dim x1={427 - 300 * PX_PER_KM} x2={427 + 300 * PX_PER_KM} y={360} at={b.base + 10} label="≈ 600 KM WIDE" />
        <Tag x={560} y={90} at={b.base + 45} color={C.cyan} size={15}>Arizona · same scale</Tag>
        <Tag x={840} y={14} at={b.base} size={9.5} color={C.dim} align="right">Real image: NASA/Viking 1 mosaic (public domain) · Arizona outline: US Census via us-atlas</Tag>
      </AbsoluteFill>

      {/* Cliffs (on the profile) appear with "edges drop away" — shown as a zoomed edge */}
      <AbsoluteFill style={{opacity: win(f, b.base + Math.round(4.6 * 30), b.how + 4, 8)}}>
        <AbsoluteFill style={{background: 'linear-gradient(#1A0F14, #3A1A10)'}} />
        <svg width={854} height={480} style={{position: 'absolute'}}>
          <defs><linearGradient id="cl" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stopColor="#D9824C" /><stop offset="1" stopColor="#5A2010" /></linearGradient></defs>
          <path d="M0 150 Q 200 140 372 146 L388 168 L380 210 L398 260 L392 320 L410 362 L854 366 L854 480 L0 480 Z" fill="url(#cl)" />
          <path d="M372 146 L388 168 L380 210 L398 260 L392 320 L410 362" fill="none" stroke={C.hot} strokeWidth={4} pathLength={1} strokeDasharray="1" strokeDashoffset={1 - ramp(f, b.base + 145, 24)} />
          <g opacity={ramp(f, b.base + 160, 10)}><line x1={470} x2={470} y1={146} y2={364} stroke={C.white} strokeWidth={2} /><line x1={460} x2={480} y1={146} y2={146} stroke={C.white} strokeWidth={2} /><line x1={460} x2={480} y1={364} y2={364} stroke={C.white} strokeWidth={2} /></g>
        </svg>
        <BigStat x={560} y={180} at={b.base + 150} value="6 KM" label="cliffs at its edges" size={56} color={C.hot} />
      </AbsoluteFill>

      {/* Hot-spot explainer: Earth plate moves (chain), Mars plate fixed (one giant) */}
      <AbsoluteFill style={{opacity: ramp(f, b.how - 2, 10)}}>
        <AbsoluteFill style={{background: '#0B0F1E'}} />
        {[0, 1].map((side) => {
          const ox = side * 427;
          const plateShift = side === 0 ? Math.max(0, hs) * 0.9 : 0;
          const grow = side === 1 ? ramp(f, b.plates, 200) : 0;
          return (
            <svg key={side} width={427} height={480} style={{position: 'absolute', left: ox}}>
              <rect x={0} y={300} width={427} height={180} fill="#3A1A10" />
              <circle cx={213} cy={470} r={40 + 6 * Math.sin(f / 5)} fill="#FF6A2B" opacity={0.75} />
              {/* lava blobs rising */}
              {[0, 1, 2].map((k) => {
                const t = (((f + k * 20) % 60) / 60);
                return <circle key={k} cx={213} cy={460 - t * 160} r={6} fill="#FFB547" opacity={1 - t} />;
              })}
              <g transform={`translate(${-plateShift % 427} 0)`}>
                <rect x={-427} y={270} width={1281} height={32} fill="#6B4A3A" />
                {side === 0
                  ? [0, 1, 2, 3, 4, 5].map((k) => (
                      <path key={k} d={`M${213 + k * 90 - 28} 272 L${213 + k * 90} ${236 - (k === 0 ? 10 : 0)} L${213 + k * 90 + 28} 272 Z`} fill="#8C5A40" opacity={k * 90 < plateShift + 40 ? 1 : 0} />
                    ))
                  : <path d={`M${213 - 60 - grow * 90} 272 Q 213 ${272 - 30 - grow * 150} ${213 + 60 + grow * 90} 272 Z`} fill="#B55A30" />}
              </g>
            </svg>
          );
        })}
        <div style={{position: 'absolute', left: 426, top: 60, width: 2, height: 420, background: C.faint}} />
        <Tag x={213} y={70} at={b.plates} align="center" size={16} color={C.cyan}>Earth: plate moves</Tag>
        <Tag x={213} y={94} at={b.plates + 20} align="center" size={11} color={C.dim}>a chain of smaller volcanoes (like Hawaii)</Tag>
        <Tag x={640} y={70} at={b.plates + 10} align="center" size={16} color={C.hot}>Mars: plate stays put</Tag>
        <Tag x={640} y={94} at={b.so} align="center" size={11} color={C.dim}>one volcano keeps growing</Tag>
        <Tag x={213} y={440} at={b.plates + 4} align="center" size={10} color={C.dim}>hot spot</Tag>
        <Tag x={640} y={440} at={b.plates + 4} align="center" size={10} color={C.dim}>hot spot</Tag>
      </AbsoluteFill>
      {fmt(0) ? null : null}
    </AbsoluteFill>
  );
};
