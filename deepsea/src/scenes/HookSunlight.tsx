import React from 'react';
import {AbsoluteFill, useCurrentFrame} from 'remotion';
import {C, DISPLAY} from '../theme';
import {ramp, lerp, win, easeOut, pop, shake} from '../lib/anim';
import {beats, cueFrame, type SceneTiming} from '../lib/timing';
import {ColossalSquid, Diver, ROVLight, SpiderCrab, Oarfish, GreenlandShark, Isopod, Glow} from '../components/Creatures';
import {BigStat, Tag, ScaleBar} from '../components/Ui';

// ---------- HOOK (dive depth ~600 m, where the juvenile was filmed) ----------
export const hookDepth = () => 600;

export const Hook: React.FC<{s: SceneTiming}> = ({s}) => {
  const f = useCurrentFrame();
  const b = beats(s, {
    march: ['In March 2025'], squid: ['A colossal squid'], baby: ['It was only a baby'], adults: ['But adults are thought'],
    eyes: ['Their eyes are believed'], rule: ["And that's the strange rule"], further: ['The further down'], dive: ["So let's dive"], line: ['And to find the invisible line'],
  });
  const rov = ramp(f, 0, b.squid, 0, 1, easeOut);
  const pull = ramp(f, b.adults, 40, 0, 1, easeOut);
  const eyeZoom = ramp(f, b.eyes, 30, 0, 1, easeOut) * (1 - ramp(f, b.rule - 6, 10));
  const sh = shake(f, b.adults + 6, 8, 20);
  const fly = (start: number) => {
    const t = (f - start) / 28;
    return {o: t < 0 || t > 1 ? 0 : Math.sin(t * Math.PI), z: lerp(0.4, 2.6, Math.max(0, Math.min(1, t)))};
  };
  const m1 = fly(b.rule + 4), m2 = fly(b.rule + 30), m3 = fly(b.further + 20);
  return (
    <AbsoluteFill>
      {/* ROV searching with its lights */}
      <AbsoluteFill style={{opacity: 1 - ramp(f, b.adults - 4, 10)}}>
        <ROVLight x={lerp(-120, 200, rov)} y={300} ang={lerp(14, 6, rov) + Math.sin(f / 30) * 3} o={0.9} />
        <div style={{position: 'absolute', left: lerp(-200, 120, rov), top: 270, width: 90, height: 60, borderRadius: 8, background: 'linear-gradient(#F3C24A, #C7921E)', boxShadow: '0 0 20px rgba(0,0,0,0.6)'}}>
          <div style={{position: 'absolute', right: -6, top: 22, width: 14, height: 14, borderRadius: '50%', background: '#fff', boxShadow: '0 0 20px #fff'}} />
        </div>
        <AbsoluteFill style={{opacity: ramp(f, b.squid, 12)}}>
          <Glow x={760} y={330} r={120} color="rgba(255,140,120,0.25)" />
          <ColossalSquid x={700} y={330} len={110} />
        </AbsoluteFill>
        <Tag x={60} y={60} at={b.march} until={b.adults} size={16} color={C.cyan}>March 2025 · South Sandwich Islands · ~600 m</Tag>
        <Tag x={760} y={420} at={b.squid + 6} until={b.adults} align="center" size={16}>First confirmed footage of a live colossal squid</Tag>
        <BigStat x={760} y={460} at={b.baby} until={b.adults} value="≈ 30 cm" label="juvenile" size={48} color={C.cyan} />
        <Tag x={60} y={90} at={b.squid} until={b.adults} size={12} color={C.dim}>Illustration · real footage: Schmidt Ocean Institute</Tag>
      </AbsoluteFill>

      {/* adult scale reveal */}
      <AbsoluteFill style={{opacity: win(f, b.adults - 2, b.rule + 4, 10), transform: `translate(${sh.x}px, ${sh.y}px) scale(${lerp(1.4, 1, pull) * (1 + eyeZoom * 1.6)})`, transformOrigin: `${380 + 182}px 360px`}}>
        <ColossalSquid x={380} y={360} len={600} eyeGlow={1 + eyeZoom * 2} />
        <Diver x={250} y={520} h={150} />
        <ScaleBar x1={340} x2={940} y={150} at={b.adults + 20} label="≈ 7 METRES" />
        <Tag x={250} y={540} at={b.adults + 20} align="center" size={13} color={C.dim}>you · 1.75 m</Tag>
      </AbsoluteFill>
      <BigStat x={1010} y={420} at={b.adults + 40} until={b.eyes} value="½ TONNE" label="up to · heaviest invertebrate" size={56} color={C.amber} />
      <BigStat x={640} y={80} at={b.eyes + 10} until={b.rule} value="LARGEST EYES" label="of any animal alive (believed)" size={54} color={C.cyan} />

      {/* teaser fly-through */}
      <AbsoluteFill style={{opacity: m1.o, transform: `scale(${m1.z})`}}><Oarfish x={640} y={160} len={420} /></AbsoluteFill>
      <AbsoluteFill style={{opacity: m2.o, transform: `scale(${m2.z})`}}><GreenlandShark x={420} y={360} len={460} /></AbsoluteFill>
      <AbsoluteFill style={{opacity: m3.o, transform: `scale(${m3.z})`}}><Isopod x={640} y={360} len={300} /></AbsoluteFill>
      <Tag x={640} y={110} at={b.further} until={b.dive} align="center" size={26} color={C.white}>Deeper → bigger</Tag>

      {/* the invisible line teaser */}
      <AbsoluteFill style={{opacity: win(f, b.line, s.durationInFrames, 8)}}>
        <div style={{position: 'absolute', left: 0, right: 0, top: 360, height: 3, background: C.cyan, boxShadow: `0 0 30px ${C.cyan}`, transform: `scaleX(${ramp(f, b.line, 20, 0, 1, easeOut)})`}} />
        <div style={{position: 'absolute', left: 0, right: 0, top: 300, textAlign: 'center', transform: `scale(${pop(f, b.line + 10)})`, opacity: f > b.line + 10 ? 1 : 0, fontFamily: DISPLAY, fontWeight: 800, fontSize: 44, color: C.white, textShadow: '0 4px 20px #000'}}>≈ 8 KM · WHERE FISH GIVE UP</div>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};

// ---------- SUNLIGHT ZONE ----------
export const sunlightDepth = (s: SceneTiming, f: number) => {
  const a = cueFrame(s, 'But within a few hundred');
  return f < a ? lerp(0, 40, ramp(f, 0, a)) : lerp(40, 260, ramp(f, a, s.durationInFrames - a, 0, 1, (t) => t));
};

export const Sunlight: React.FC<{s: SceneTiming}> = ({s}) => {
  const f = useCurrentFrame();
  const b = beats(s, {zero: ['Zero metres'], within: ['But within a few hundred'], japan: ['Off the coast of Japan'], longer: ["That's longer than two people"], largest: ['The Japanese spider crab is'], only: ["And it's only the beginning"]});
  const crabIn = ramp(f, b.japan, 40, 0, 1, easeOut);
  // scale: 1 m = 150 px. Leg span ≈ 3.8 m → ≈ 570 px claw to claw.
  return (
    <AbsoluteFill>
      {/* bubbles rising near the surface */}
      <svg width={1280} height={720} style={{position: 'absolute', opacity: 1 - ramp(f, b.within, 30)}}>
        {Array.from({length: 40}).map((_, i) => {
          const y = 720 - ((f * (2 + (i % 5)) + i * 53) % 820);
          return <circle key={i} cx={(i * 97) % 1280 + Math.sin(f / 10 + i) * 6} cy={y} r={2 + (i % 4)} fill="none" stroke="rgba(255,255,255,0.6)" />;
        })}
      </svg>
      <AbsoluteFill style={{opacity: crabIn, transform: `translateX(${(1 - crabIn) * 400}px)`}}>
        {/* rocky seafloor */}
        <svg width={1280} height={720} style={{position: 'absolute'}}>
          <path d="M0 600 Q 200 570 400 590 T 800 585 T 1280 600 L1280 720 L0 720 Z" fill="rgba(20,40,55,0.85)" />
        </svg>
        <SpiderCrab x={600 + Math.sin(f / 40) * 20} y={470} s={1.15} />
      </AbsoluteFill>
      <ScaleBar x1={315} x2={885} y={180} at={b.japan + 40} label="≈ 3.8 M CLAW TO CLAW" color={C.amber} />
      <AbsoluteFill style={{opacity: ramp(f, b.longer, 12)}}>
        <svg width={1280} height={720} style={{position: 'absolute'}}>
          {[0, 1].map((k) => (
            <g key={k} transform={`translate(${340 + k * 265} 225)`} fill="rgba(235,245,250,0.8)">
              <circle cx={250} cy={0} r={18} />
              <rect x={22} y={-20} width={210} height={40} rx={18} />
            </g>
          ))}
        </svg>
        <Tag x={600} y={252} at={b.longer} align="center" size={14} color={C.dim}>two people, end to end (3.5 m)</Tag>
      </AbsoluteFill>
      <BigStat x={50} y={40} at={b.largest} until={b.only + 20} value="LARGEST CRAB ALIVE" label="Japanese spider crab" size={40} color={C.white} align="left" />
    </AbsoluteFill>
  );
};
