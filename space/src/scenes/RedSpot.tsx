import React from 'react';
import {AbsoluteFill, useCurrentFrame} from 'remotion';
import {C} from '../theme';
import {ramp, lerp, win, easeOut, shake} from '../lib/anim';
import {beats, type SceneTiming} from '../lib/timing';
import {SpaceBG, Camera} from '../components/Space';
import {Jupiter, Earth} from '../components/Bodies';
import {BigStat, Tag} from '../components/Type';
import {PhotoInsert, Dim, Flash} from '../components/Extras';

// Swirling storm oval drawn standalone for scale comparisons.
const Storm: React.FC<{cx: number; cy: number; w: number; h: number}> = ({cx, cy, w, h}) => {
  const f = useCurrentFrame();
  return (
    <svg width={854} height={480} style={{position: 'absolute', overflow: 'visible'}}>
      <defs>
        <radialGradient id="grs">
          <stop offset="0" stopColor="#E86A3E" />
          <stop offset="0.7" stopColor="#C2502F" />
          <stop offset="1" stopColor="#E9B08A" />
        </radialGradient>
      </defs>
      <ellipse cx={cx} cy={cy} rx={w / 2} ry={h / 2} fill="url(#grs)" />
      {[0.85, 0.65, 0.45, 0.25].map((k, i) => (
        <ellipse key={i} cx={cx} cy={cy} rx={(w / 2) * k} ry={(h / 2) * k} fill="none" stroke="rgba(255,225,200,0.5)" strokeWidth={2} strokeDasharray={`${w * k * 0.4} ${w * k * 0.25}`} strokeDashoffset={-f * (3 + i)} />
      ))}
    </svg>
  );
};

export const RedSpot: React.FC<{s: SceneTiming}> = ({s}) => {
  const f = useCurrentFrame();
  const b = beats(s, {
    grs: ['The Great Red Spot'],
    wider: ['This storm on Jupiter'],
    nasa: ['When NASA measured'],
    onept: ["That's one point three"],
    twist: ["But here's the twist"],
    shrink: ["It's shrinking"],
    c19: ['In the nineteenth century'],
    juno: ["NASA's Juno spacecraft"],
    fifty: ["That's fifty to a hundred"],
  });
  // Scale for comparisons: Earth 12,742 km → 190 px.
  const pxPerKm = 190 / 12742;
  const earthR = 95;
  const sh = shake(f, b.twist, 8, 18);
  // Width over time: >2 Earths (1800s) → ~2 (1979) → 1.3 (2017)
  const tl = ramp(f, b.c19 + 10, 70, 0, 1, (t) => t);
  const widthEarths = f < b.twist ? 1.28 : f < b.c19 ? lerp(1.28, 2.3, ramp(f, b.shrink, 20)) : lerp(2.3, 1.28, tl);
  const yearLabel = f < b.c19 ? '2017' : tl < 0.45 ? '1800s' : tl < 0.8 ? '1979' : '2017';

  return (
    <AbsoluteFill style={{background: C.space}}>
      <SpaceBG seed={5} a="#FF8A3D" b="#E3B566" drift={[0.25, 0.03]} neb={0.25} />

      {/* Jupiter, camera diving to the storm */}
      <AbsoluteFill style={{opacity: win(f, 30, b.nasa + 2, 10)}}>
        <Camera zoom={lerp(0.85, 2.3, ramp(f, 40, b.nasa - 40, 0, 1, (t) => t))} x={-lerp(0, 120, ramp(f, 40, b.nasa - 40))} y={-lerp(0, 110, ramp(f, 40, b.nasa - 40))}>
          <Jupiter cx={427} cy={235} r={190} />
        </Camera>
        <Tag x={427} y={70} at={b.wider} align="center" size={18} color={C.hot}>wider than Earth</Tag>
      </AbsoluteFill>

      {/* Real Hubble image as proof */}
      <PhotoInsert src="img/jupiter_grs_hubble2014.jpg" at={b.nasa} until={b.nasa + 75} credit="NASA, ESA, A. Simon (GSFC) · Hubble, 2014 · public domain" zoom={[1.4, 2.6]} origin="52% 66%" />

      {/* Storm vs Earth, to scale, and the shrink */}
      <AbsoluteFill style={{opacity: win(f, b.nasa + 70, b.juno + 4, 8)}}>
        <Camera x={sh.x} y={sh.y}>
          <Storm cx={427} cy={225} w={widthEarths * 12742 * pxPerKm} h={widthEarths * 12742 * pxPerKm * 0.58} />
          <AbsoluteFill style={{opacity: 0.55}}>
            <Earth cx={lerp(950, 427, ramp(f, b.nasa + 80, 24, 0, 1, easeOut))} cy={225} r={earthR} spin={1} />
          </AbsoluteFill>
        </Camera>
        <Dim x1={427 - (widthEarths * 12742 * pxPerKm) / 2} x2={427 + (widthEarths * 12742 * pxPerKm) / 2} y={70} at={b.nasa + 90} label={f < b.c19 ? '≈ 16,350 KM (2017)' : `${yearLabel}`} />
        <BigStat x={120} y={330} at={b.onept} value={f < b.c19 ? '1.3' : widthEarths > 2.05 ? '>2' : widthEarths.toFixed(1)} label="Earths wide" size={58} color={C.hot} />
        <BigStat x={710} y={340} at={b.shrink} value="SHRINKING" size={30} color={C.red} />
        <Tag x={710} y={384} at={b.c19 + 10} align="center" size={11} color={C.dim}>1800s: well over 2 Earths</Tag>
      </AbsoluteFill>
      <Flash at={b.twist} k={0.5} />

      {/* Depth: storm roots vs Earth's oceans */}
      <AbsoluteFill style={{opacity: ramp(f, b.juno - 2, 10)}}>
        <AbsoluteFill style={{background: 'linear-gradient(#0A1024, #2A160E)'}} />
        <svg width={854} height={480} style={{position: 'absolute'}}>
          <rect x={0} y={110} width={854} height={6} fill="#E9C9A0" />
          {/* storm root funnel growing down: 320 km → 300 px */}
          <path d={`M330 113 Q 360 ${113 + 300 * ramp(f, b.juno + 20, 50)} 427 ${113 + 300 * ramp(f, b.juno + 20, 50)} Q 494 ${113 + 300 * ramp(f, b.juno + 20, 50)} 524 113 Z`} fill="rgba(194,80,47,0.85)" />
          {/* Earth's average ocean depth ≈ 3.7 km → 3.5 px; deepest ≈ 11 km → 10 px */}
          <rect x={620} y={116} width={160} height={3.5} fill={C.cyan} opacity={ramp(f, b.fifty, 8)} />
          {/* Juno flyby */}
          <g transform={`translate(${lerp(-60, 914, ramp(f, b.juno, 90, 0, 1, (t) => t))} 70)`}>
            <rect x={-8} y={-5} width={16} height={10} fill="#ddd" />
            <rect x={-40} y={-2} width={30} height={4} fill="#6FA8FF" />
            <rect x={10} y={-2} width={30} height={4} fill="#6FA8FF" />
          </g>
        </svg>
        <Tag x={36} y={90} at={b.juno} size={11} color={C.dim}>cloud tops</Tag>
        <BigStat x={427} y={425} at={b.juno + 60} value="300+ KM DEEP" size={28} color={C.hot} />
        <Tag x={700} y={130} at={b.fifty} align="center" size={11} color={C.cyan}>Earth's oceans (same scale)</Tag>
        <BigStat x={700} y={170} at={b.fifty + 10} value="50–100×" label="deeper" size={44} color={C.white} />
      </AbsoluteFill>
    </AbsoluteFill>
  );
};
