import React from 'react';
import {AbsoluteFill, useCurrentFrame} from 'remotion';
import {C, TEXT} from '../theme';
import {ramp, lerp, win, easeOut} from '../lib/anim';
import {beats, type SceneTiming} from '../lib/timing';
import {SpaceBG} from '../components/Space';
import {BigStat, Tag} from '../components/Type';
import {PhotoInsert, Particles, SunIcon} from '../components/Extras';

// Universe age 13.8 billion years mapped to x 60 → 794.
const X0 = 60, X1 = 794, AGE = 13.8;
const xOf = (gyr: number) => X0 + (gyr / AGE) * (X1 - X0);

export const MostDistant: React.FC<{s: SceneTiming}> = ({s}) => {
  const f = useCurrentFrame();
  const b = beats(s, {
    most: ['The most distant galaxy'],
    called: ["It's called"],
    light: ['That light has been'],
    left: ['It left this galaxy'],
    two: ["That's about two percent"],
    so: ["So you're not seeing"],
    baby: ["You're seeing it as a baby"],
    bright: ["And it's surprisingly bright"],
  });
  const photon = ramp(f, b.light + 10, 80, 0, 1, (t) => t);
  const yearsGone = 13.5 * photon;

  return (
    <AbsoluteFill style={{background: C.space}}>
      <SpaceBG seed={1} a="#5CE1FF" b="#9B7BFF" drift={[0, 0]} warp={win(f, 30, b.called, 10) * 0.8} />

      {/* diving into a real Webb deep field */}
      <PhotoInsert
        src="img/webb_first_deep_field.jpg" at={b.called} until={b.light + 4}
        credit="Webb's First Deep Field (SMACS 0723) · NASA, ESA, CSA, STScI · public domain — not MoM-z14" stamp="JWST · REAL IMAGE" zoom={[1.0, 2.6]} origin="58% 42%"
      />
      <Tag x={427} y={60} at={b.called + 30} until={b.light} align="center" size={22} color={C.cyan}>MoM-z14</Tag>

      {/* light-travel timeline */}
      <AbsoluteFill style={{opacity: win(f, b.light - 2, b.so + 4, 8)}}>
        <svg width={854} height={480} style={{position: 'absolute'}}>
          <defs>
            <linearGradient id="tl" x1="0" x2="1">
              <stop offset="0" stopColor="#FFFFFF" />
              <stop offset="0.1" stopColor={C.violet} />
              <stop offset="1" stopColor={C.cyan} />
            </linearGradient>
          </defs>
          <rect x={X0} y={236} width={(X1 - X0) * ramp(f, b.light, 20)} height={8} rx={4} fill="url(#tl)" opacity={0.5} />
          {/* photon with trail from the galaxy (0.28 Gyr) to today */}
          {f > b.light + 10 ? (
            <>
              <rect x={xOf(0.28)} y={238} width={(xOf(13.8) - xOf(0.28)) * photon} height={4} fill={C.cyan} />
              <circle cx={xOf(0.28) + (xOf(13.8) - xOf(0.28)) * photon} cy={240} r={7} fill="#fff" style={{filter: `drop-shadow(0 0 8px ${C.cyan})`}} />
            </>
          ) : null}
          <circle cx={xOf(0.28)} cy={240} r={6} fill={C.hot} opacity={ramp(f, b.left, 8)} />
          <line x1={xOf(4.6 + 4.6)} x2={xOf(9.2)} y1={226} y2={254} stroke={C.hot} opacity={ramp(f, b.baby + 20, 8)} />
        </svg>
        <Tag x={X0} y={262} at={b.light} size={12} color={C.dim}>Big Bang</Tag>
        <Tag x={X1} y={262} at={b.light} size={12} color={C.dim} align="right">Today · 13.8 billion years</Tag>
        <BigStat x={427} y={90} at={b.light + 10} value={`${yearsGone.toFixed(1)} BILLION YEARS`} label="the light has been travelling" size={36} color={C.cyan} />
        <Tag x={xOf(0.28)} y={204} at={b.left + 4} size={12} color={C.hot}>280 million years after the Big Bang</Tag>
        <BigStat x={200} y={300} at={b.two} value="2%" label="of the universe's age today" size={60} color={C.hot} />
      </AbsoluteFill>

      {/* baby galaxy forming (illustration) and where the Sun appears */}
      <AbsoluteFill style={{opacity: ramp(f, b.so - 2, 8) * (1 - ramp(f, b.bright - 4, 8))}}>
        <Particles cx={427} cy={220} n={240} at={b.so} converge color="#CFE4FF" spread={300} />
        <div style={{position: 'absolute', left: 427 - 60, top: 220 - 60, width: 120, height: 120, borderRadius: '50%', background: 'radial-gradient(circle, rgba(220,235,255,0.95), rgba(140,170,255,0.4) 40%, transparent 70%)', opacity: ramp(f, b.so + 30, 20), transform: `scale(${lerp(0.4, 1, ramp(f, b.so + 30, 30, 0, 1, easeOut))})`}} />
        <Tag x={427} y={320} at={b.so + 30} align="center" size={16} color={C.cyan}>a baby galaxy at cosmic dawn</Tag>
        <Tag x={427} y={344} at={b.so + 30} align="center" size={10} color={C.dim}>Illustration</Tag>
        <div style={{position: 'absolute', left: 0, right: 0, top: 380, opacity: ramp(f, b.baby + 20, 10)}}>
          <svg width={854} height={60}>
            <line x1={X0} x2={X1} y1={20} y2={20} stroke={C.faint} strokeWidth={3} />
            <circle cx={xOf(0.28)} cy={20} r={6} fill={C.cyan} />
            <circle cx={xOf(9.2)} cy={20} r={6} fill={C.hot} />
          </svg>
          <div style={{position: 'absolute', left: xOf(0.28), top: 30, fontFamily: TEXT, fontSize: 11, color: C.cyan, fontWeight: 700}}>MoM-z14's light leaves</div>
          <div style={{position: 'absolute', left: xOf(9.2), top: 30, transform: 'translateX(-50%)', fontFamily: TEXT, fontSize: 11, color: C.hot, fontWeight: 700}}>Sun & Earth form (~9 billion years later)</div>
        </div>
        <SunIcon cx={xOf(9.2)} cy={366} r={9 * ramp(f, b.baby + 26, 10)} />
      </AbsoluteFill>

      {/* brighter than expected */}
      <AbsoluteFill style={{opacity: ramp(f, b.bright - 2, 8)}}>
        <AbsoluteFill style={{background: '#070A16'}} />
        <svg width={854} height={480} style={{position: 'absolute'}}>
          <line x1={250} x2={600} y1={200} y2={200} stroke={C.dim} strokeDasharray="6 6" />
          <rect x={385} y={380 - 260 * ramp(f, b.bright + 10, 40, 0, 1, easeOut)} width={84} height={260 * ramp(f, b.bright + 10, 40, 0, 1, easeOut)} fill={C.cyan} rx={4} />
          <rect x={250} y={380} width={350} height={3} fill={C.dim} />
        </svg>
        <Tag x={610} y={190} at={b.bright + 4} size={12} color={C.dim}>what many expected</Tag>
        <BigStat x={427} y={50} at={b.bright + 40} value="SURPRISINGLY BRIGHT" size={36} color={C.cyan} />
        <Tag x={427} y={400} at={b.bright + 20} align="center" size={10} color={C.dim}>Schematic · record holder as of Nov 2026 (z = 14.44, Naidu et al.)</Tag>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};
