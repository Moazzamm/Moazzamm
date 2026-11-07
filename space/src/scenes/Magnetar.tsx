import React from 'react';
import {AbsoluteFill, useCurrentFrame} from 'remotion';
import {C, DISPLAY} from '../theme';
import {ramp, lerp, win, easeOut, shake, pop} from '../lib/anim';
import {beats, type SceneTiming} from '../lib/timing';
import {SpaceBG, Camera} from '../components/Space';
import {Earth, Galaxy} from '../components/Bodies';
import {BigStat, Tag} from '../components/Type';
import {PhotoInsert, Shockwave, Flash, SunIcon} from '../components/Extras';

// Procedural magnetar: blazing core with flowing dipole field lines.
const MagCore: React.FC<{cx: number; cy: number; r: number; k?: number}> = ({cx, cy, r, k = 1}) => {
  const f = useCurrentFrame();
  return (
    <>
      <svg width={854} height={480} style={{position: 'absolute', overflow: 'visible'}}>
        {Array.from({length: 7}).map((_, i) => {
          const s = (i + 1) * 0.55 * k;
          return [1, -1].map((dir) => (
            <path
              key={`${i}${dir}`}
              d={`M${cx} ${cy - r} C ${cx + dir * r * 3 * s} ${cy - r * 4 * s}, ${cx + dir * r * 3 * s} ${cy + r * 4 * s}, ${cx} ${cy + r}`}
              fill="none" stroke={i % 2 ? C.violet : C.cyan} strokeWidth={1.6} strokeDasharray="5 9" strokeDashoffset={-f * (2 + i * 0.4)} opacity={0.75 - i * 0.07}
            />
          ));
        })}
      </svg>
      <div style={{position: 'absolute', left: cx - r, top: cy - r, width: r * 2, height: r * 2, borderRadius: '50%', background: 'radial-gradient(circle at 40% 38%, #fff, #D9C8FF 45%, #8A6CFF 90%)', boxShadow: `0 0 ${r * 3}px #A88CFF`}} />
    </>
  );
};

export const Magnetar: React.FC<{s: SceneTiming}> = ({s}) => {
  const f = useCurrentFrame();
  const b = beats(s, {
    takes: ['Number three takes'],
    this: ['This is a neutron star'],
    put: ['Put one a sixth'],
    dec: ['On December'],
    was: ['It was about fifty'],
    flash: ['And the flash still'],
    tenth: ['In just a tenth'],
  });
  const flareAt = b.dec + 40;
  const travel = ramp(f, b.flash, 50, 0, 1, (t) => t);
  const sh = shake(f, flareAt, 10, 22);
  const wipe = ramp(f, b.put + 70, 20);
  // Sun-years counter runs fast: 0 → 150,000 years
  const years = 150000 * ramp(f, b.tenth + 24, 60, 0, 1, (t) => t * t);

  return (
    <AbsoluteFill style={{background: C.space}}>
      <SpaceBG seed={9} a="#9B7BFF" b="#5CE1FF" drift={[0.35, 0.08]} neb={0.4} />

      {/* magnetar core */}
      <AbsoluteFill style={{opacity: win(f, 40, b.put + 2, 8)}}>
        <Camera zoom={lerp(0.9, 1.25, ramp(f, 40, 200, 0, 1, (t) => t))} rot={Math.sin(f / 50) * 4}>
          <MagCore cx={427} cy={230} r={18} />
        </Camera>
        <BigStat x={427} y={310} at={b.this + 70} value="STRONGEST MAGNETIC FIELD" label="known in the universe" size={30} color={C.violet} />
      </AbsoluteFill>
      <PhotoInsert src="img/magnetar_sgr1806_nasa.jpg" at={b.this} until={b.this + 66} credit="NASA/GSFC Conceptual Image Lab · public domain" stamp="ARTIST'S IMPRESSION" zoom={[1.05, 1.3]} />

      {/* Earth–Moon: magnetar at 1/6 of the way wipes credit cards */}
      <AbsoluteFill style={{opacity: win(f, b.put - 2, b.dec + 4, 8)}}>
        <Earth cx={120} cy={240} r={55} spin={1} />
        <div style={{position: 'absolute', left: 780 - 16, top: 240 - 16, width: 32, height: 32, borderRadius: '50%', background: 'radial-gradient(circle at 40% 40%, #eee, #888)'}} />
        <svg width={854} height={480} style={{position: 'absolute'}}>
          <line x1={175} x2={764} y1={240} y2={240} stroke={C.faint} strokeDasharray="4 6" />
          <line x1={175 + (589 / 6)} x2={175 + 589 / 6} y1={225} y2={255} stroke={C.hot} strokeWidth={2} opacity={ramp(f, b.put + 20, 8)} />
        </svg>
        <AbsoluteFill style={{opacity: ramp(f, b.put + 10, 10)}}>
          <MagCore cx={lerp(780, 175 + 589 / 6, ramp(f, b.put + 10, 30, 0, 1, easeOut))} cy={240} r={7} k={0.9} />
        </AbsoluteFill>
        <Tag x={273} y={270} at={b.put + 30} align="center" size={12} color={C.hot}>1/6 of the way to the Moon</Tag>
        {/* credit cards around Earth, strips wiped */}
        {[[60, 120], [170, 110], [60, 340], [170, 350]].map(([x, y], i) => (
          <div key={i} style={{position: 'absolute', left: x - 28, top: y - 17, width: 56, height: 34, borderRadius: 4, background: 'linear-gradient(135deg, #2E5BDB, #6A3CC8)', transform: `scale(${pop(f, b.put + 50 + i * 4)}) rotate(${(i - 1.5) * 8}deg)`, opacity: f > b.put + 50 ? 1 : 0}}>
            <div style={{position: 'absolute', left: 0, right: 0, top: 6, height: 7, background: wipe > 0.5 ? C.red : '#111'}} />
          </div>
        ))}
        <BigStat x={560} y={110} at={b.put + 72} value="WIPED" label="every credit card on Earth" size={42} color={C.red} />
      </AbsoluteFill>

      {/* the 2004 flare crossing the galaxy */}
      <AbsoluteFill style={{opacity: win(f, b.dec - 2, b.tenth + 4, 8)}}>
        <Camera x={sh.x} y={sh.y} zoom={lerp(1.15, 1, ramp(f, b.dec, 60, 0, 1, easeOut))}>
          <Galaxy cx={427} cy={240} r={230} tilt={0.5} />
          {/* magnetar on the far side; Earth (Sun) on this side */}
          <div style={{position: 'absolute', left: 560 - 6, top: 175 - 6, width: 12, height: 12, borderRadius: '50%', background: '#E9DDFF', boxShadow: '0 0 18px #B79CFF', opacity: ramp(f, b.dec + 10, 8)}} />
          <div style={{position: 'absolute', left: 300 - 5, top: 300 - 5, width: 10, height: 10, borderRadius: '50%', background: C.cyan, boxShadow: `0 0 12px ${C.cyan}`, opacity: ramp(f, b.dec + 16, 8)}} />
          <Shockwave cx={560} cy={175} at={flareAt} maxR={120} dur={20} color="#E9DDFF" />
          {/* flash travelling to Earth */}
          {f >= b.flash ? (
            <div style={{position: 'absolute', left: lerp(560, 300, travel) - 8, top: lerp(175, 300, travel) - 8, width: 16, height: 16, borderRadius: '50%', background: '#fff', boxShadow: '0 0 30px #fff, 0 0 60px #B79CFF', opacity: travel < 1 ? 1 : 0}} />
          ) : null}
          <svg width={854} height={480} style={{position: 'absolute'}}>
            <line x1={560} y1={175} x2={300} y2={300} stroke={C.hot} strokeDasharray="5 6" strokeWidth={1.5} opacity={ramp(f, b.was, 10)} />
          </svg>
        </Camera>
        <Tag x={572} y={150} at={b.dec + 14} size={12} color="#E9DDFF">SGR 1806-20</Tag>
        <Tag x={312} y={312} at={b.dec + 20} size={12} color={C.cyan}>Earth</Tag>
        <Tag x={14} y={380} at={b.dec + 20} size={9.5} color={C.dim}>Milky Way · illustration, positions approximate</Tag>
        <div style={{position: 'absolute', left: 427, top: 46, transform: `translateX(-50%) scale(${pop(f, b.dec)})`, opacity: f > b.dec ? 1 : 0, fontFamily: DISPLAY, fontWeight: 900, fontSize: 40, color: C.white, textShadow: '0 4px 18px #000'}}>27 DEC 2004</div>
        <BigStat x={720} y={300} at={b.was + 6} value="≈ 50,000" label="light-years away" size={34} color={C.hot} />
      </AbsoluteFill>
      <Flash at={flareAt} k={0.7} />
      {/* arrival at Earth: atmosphere lights up */}
      <AbsoluteFill style={{opacity: win(f, b.flash + 48, b.tenth + 4, 6)}}>
        <AbsoluteFill style={{background: C.space}} />
        <Earth cx={427} cy={250} r={150} spin={0.6} />
        <div style={{position: 'absolute', left: 427 - 168, top: 250 - 168, width: 336, height: 336, borderRadius: '50%', boxShadow: `0 0 ${40 + 30 * Math.sin(f / 2)}px 18px rgba(190,160,255,0.85)`, opacity: ramp(f, b.flash + 52, 6)}} />
        <Tag x={427} y={50} at={b.flash + 52} align="center" size={18} color="#E9DDFF">upper atmosphere lit up</Tag>
      </AbsoluteFill>
      <Flash at={b.flash + 48} k={0.8} />

      {/* 0.1 s vs 150,000 years */}
      <AbsoluteFill style={{opacity: ramp(f, b.tenth - 2, 8)}}>
        <AbsoluteFill style={{background: '#080A16'}} />
        <MagCore cx={200} cy={210} r={16} />
        <SunIcon cx={650} cy={210} r={48} />
        <BigStat x={200} y={300} at={b.tenth + 4} value="0.1 SECOND" label="magnetar flare" size={34} color="#D9C8FF" />
        <BigStat x={650} y={300} at={b.tenth + 24} value={`${Math.round(years).toLocaleString('en-US')} YEARS`} label="of sunlight" size={34} color={C.hot} />
        <Tag x={427} y={202} at={b.tenth + 40} align="center" size={30} color={C.white}>&gt;</Tag>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};
