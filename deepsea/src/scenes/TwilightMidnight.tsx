import React from 'react';
import {AbsoluteFill, useCurrentFrame} from 'remotion';
import {C, DISPLAY, TEXT} from '../theme';
import {ramp, lerp, win, easeOut, shake, rnd} from '../lib/anim';
import {beats, cueFrame, type SceneTiming} from '../lib/timing';
import {Oarfish, Siphonophore, BlueWhale, GreenlandShark, Isopod, Diver, Glow, Jelly} from '../components/Creatures';
import {ZoneTitle} from '../components/Ocean';
import {BigStat, Tag, ScaleBar, RealInsert, Panel} from '../components/Ui';

// ---------- TWILIGHT ZONE ----------
export const twilightDepth = (s: SceneTiming, f: number) => lerp(200, 960, ramp(f, 0, s.durationInFrames, 0, 1, (t) => t));

export const Twilight: React.FC<{s: SceneTiming}> = ({s}) => {
  const f = useCurrentFrame();
  const b = beats(s, {
    two: ['Two hundred metres'], here: ['Here lives a fish'], oar: ['The giant oarfish'], seen: ['It has been seen'], even: ['But even the oarfish'],
    in2020: ['In 2020'], ring: ['Its outer ring'], whale: ["That's longer than a blue whale"], twist: ["And here's the twist"], colony: ["It's a colony"],
  });
  // oarfish scale: 1 m = 70 px → 8 m ≈ 560 px; diver 1.75 m ≈ 122 px
  const oarIn = ramp(f, b.here, 40, 0, 1, easeOut);
  const siphIn = ramp(f, b.in2020, 40, 0, 1, easeOut);
  const unroll = ramp(f, b.ring + 20, 50, 0, 1, easeOut);
  const sh = shake(f, b.whale, 7, 18);
  const zoomColony = ramp(f, b.colony, 40, 0, 1, easeOut);
  return (
    <AbsoluteFill>
      <ZoneTitle at={4} title="Twilight Zone" sub="200 metres · light fades" dur={84} />
      <AbsoluteFill style={{opacity: oarIn * (1 - ramp(f, b.in2020 - 6, 12)), transform: `translateY(${(1 - oarIn) * -300}px)`}}>
        <Glow x={560} y={360} r={330} color="rgba(200,230,255,0.12)" />
        <Oarfish x={560} y={80} len={560} />
        <Diver x={760} y={640} h={122} />
        <svg width={1280} height={720} style={{position: 'absolute'}}>
          <line x1={470} x2={470} y1={80} y2={640} stroke={C.cyan} strokeWidth={2.5} opacity={ramp(f, b.oar, 10)} />
          <line x1={460} x2={480} y1={80} y2={80} stroke={C.cyan} strokeWidth={2.5} opacity={ramp(f, b.oar, 10)} />
          <line x1={460} x2={480} y1={640} y2={640} stroke={C.cyan} strokeWidth={2.5} opacity={ramp(f, b.oar, 10)} />
        </svg>
        <BigStat x={440} y={300} at={b.oar} value="≈ 8 M" label="longest bony fish" size={62} color={C.cyan} align="right" />
        <Tag x={760} y={660} at={b.oar} align="center" size={13} color={C.dim}>you</Tag>
        <Tag x={640} y={200} at={b.seen} until={b.even} size={16} color={C.coral}>hangs upright · red fin rippling</Tag>
      </AbsoluteFill>
      <RealInsert src="img/oarfish_1996_usnavy.jpg" at={b.oar + 35} until={b.seen - 4} x={90} y={130} w={900} h={320} zoom={[1.02, 1.1]} tilt={-1}
        label="A real 7-metre giant oarfish · found near San Diego, 1996" credit="U.S. Navy photo · public domain" />

      {/* giant siphonophore: spiral, then unrolled next to a blue whale */}
      <AbsoluteFill style={{opacity: siphIn * (1 - ramp(f, b.colony + 50, 12)), transform: `translate(${sh.x}px, ${sh.y}px) scale(${lerp(1, 3.2, zoomColony)})`, transformOrigin: '640px 330px'}}>
        <Siphonophore x={640} y={330} R={240} unroll={unroll} />
        <AbsoluteFill style={{opacity: ramp(f, b.whale, 14) * (1 - zoomColony)}}>
          {/* whale ≈ 30 m at 20 px/m = 600 px; siphonophore ring ≈ 45 m ≈ 900 px (unrolled line is 1040 px wide → drawn ≈ to scale) */}
          <BlueWhale x={340} y={470} len={600} />
        </AbsoluteFill>
      </AbsoluteFill>
      <Tag x={640} y={80} at={b.in2020 + 10} until={b.ring} align="center" size={16} color={C.cyan}>Ningaloo Canyons, Western Australia · 2020</Tag>
      <ScaleBar x1={120} x2={1160} y={270} at={b.ring + 60} label="RING ≈ 45 M" color={C.coral} />
      <Tag x={640} y={540} at={b.whale} until={b.twist} align="center" size={18}>blue whale ≈ 30 m</Tag>
      <BigStat x={640} y={560} at={b.twist} until={b.colony + 60} value="NOT ONE ANIMAL" label="a colony of tiny clones" size={56} color={C.amber} />
      <Tag x={40} y={24} at={b.in2020} until={b.colony + 60} size={12} color={C.dim}>Illustration · scale approximate</Tag>
      <RealInsert src="img/siphonophore_noaa_2015.jpg" at={b.colony + 40} until={s.durationInFrames - 2} x={300} y={86} w={680} h={384} origin="78% 40%" zoom={[1.0, 1.18]}
        label="A real siphonophore (a smaller species) · each segment is its own animal" credit="NOAA Ocean Exploration, 2015 · public domain" />
    </AbsoluteFill>
  );
};

// ---------- MIDNIGHT ZONE ----------
export const midnightDepth = (s: SceneTiming, f: number) => lerp(1000, 2600, ramp(f, 0, s.durationInFrames, 0, 1, (t) => t));

export const Midnight: React.FC<{s: SceneTiming}> = ({s}) => {
  const f = useCurrentFrame();
  const b = beats(s, {
    one: ['One thousand metres'], from: ['From here down'], freezing: ['The water is close'], snow: ['Most of it is marine snow'], strange: ['This is where the giants'],
    cold: ['In the cold,'], grow: ['It can grow over six'], dated: ['When scientists carbon-dated'], low: ['Even at the low end'],
    floor: ['On the seafloor'], relative: ['A relative of the little'], iso: ['The giant isopod'], aquarium: ['One, at an aquarium'], refused: ['Then it refused'],
  });
  const sharkX = lerp(1400, -700, ramp(f, b.cold, 420, 0, 1, (t) => t));
  const tl = ramp(f, b.dated + 10, 70, 0, 1, easeOut);
  const yearX = (y: number) => 120 + ((y - 1480) / (2030 - 1480)) * 880;
  const days = Math.round(1869 * ramp(f, b.refused + 10, 80, 0, 1, (t) => t));
  return (
    <AbsoluteFill>
      {/* living lights before the giants arrive */}
      <AbsoluteFill style={{opacity: win(f, 10, b.cold + 20, 20)}}>
        <Jelly x={260 + Math.sin(f / 90) * 30} y={250 - f * 0.15} s={0.9} />
        <Jelly x={880} y={420 - f * 0.1} s={0.6} hue="#B79CFF" />
        <Jelly x={620} y={520 - f * 0.12} s={0.45} />
        <svg width={1280} height={720} style={{position: 'absolute'}}>
          {Array.from({length: 14}).map((_, i) => {
            const fl = Math.max(0, Math.sin(f / (6 + (i % 5)) + i * 2.3)) ** 10;
            return <circle key={i} cx={(i * 173 + f * (0.6 + (i % 3) * 0.3)) % 1100 + 40} cy={140 + (i * 97) % 380} r={3} fill="#9FF7FF" opacity={fl} style={{filter: 'drop-shadow(0 0 8px #9FF7FF)'}} />;
          })}
        </svg>
      </AbsoluteFill>
      <ZoneTitle at={4} title="Midnight Zone" sub="1,000 metres · no sunlight" dur={84} />
      <Tag x={640} y={300} at={b.snow} until={b.strange} align="center" size={22} color={C.white}>↓ marine snow ↓</Tag>
      <Tag x={640} y={334} at={b.snow + 10} until={b.strange} align="center" size={14} color={C.dim}>the main food supply down here</Tag>

      {/* Greenland shark crossing */}
      <AbsoluteFill style={{opacity: win(f, b.cold - 4, b.dated + 6, 12)}}>
        <GreenlandShark x={sharkX} y={340} len={540} />
        <Diver x={sharkX + 600} y={520} h={160} />
        <BigStat x={640} y={70} at={b.grow} value="6+ M LONG" label="grows < 1 cm a year" size={56} color={C.white} />
      </AbsoluteFill>
      <RealInsert src="img/greenland_shark_noaa_2013.jpg" at={b.grow + 30} until={b.dated + 14} x={330} y={150} w={620} h={347} tilt={2}
        label="A real Greenland shark · NOAA expedition, 2013" credit="NOAA Okeanos Explorer · public domain" />

      {/* age timeline */}
      <AbsoluteFill style={{opacity: win(f, b.dated, b.floor + 4, 10)}}>
        <AbsoluteFill style={{background: 'rgba(1,6,14,0.55)'}} />
        <svg width={1280} height={720} style={{position: 'absolute'}}>
          <line x1={120} x2={120 + 880 * tl} y1={400} y2={400} stroke={C.faint} strokeWidth={3} />
          <rect x={yearX(1504)} y={384} width={(yearX(1744) - yearX(1504)) * ramp(f, b.dated + 40, 30)} height={32} fill="rgba(255,184,77,0.35)" stroke={C.amber} />
          <line x1={yearX(1776)} x2={yearX(1776)} y1={350} y2={450} stroke={C.cyan} strokeWidth={3} opacity={ramp(f, b.low, 8)} />
          <circle cx={yearX(2016)} cy={400} r={8} fill={C.white} opacity={ramp(f, b.dated + 20, 8)} />
        </svg>
        {[1500, 1600, 1700, 1800, 1900, 2000].map((y) => (
          <Tag key={y} x={yearX(y)} y={440} at={b.dated + 10} align="center" size={13} color={C.dim}>{y}</Tag>
        ))}
        <Tag x={(yearX(1504) + yearX(1744)) / 2} y={340} at={b.dated + 50} align="center" size={16} color={C.amber}>born: between ~1504 and ~1744</Tag>
        <Tag x={yearX(1776)} y={460} at={b.low} align="center" size={16} color={C.cyan}>1776 · USA</Tag>
        <Tag x={yearX(2016)} y={360} at={b.dated + 20} align="center" size={13}>studied 2016</Tag>
        <BigStat x={640} y={120} at={b.dated + 30} value="272–512 YEARS" label="estimated age · longest-lived vertebrate known" size={64} color={C.amber} />
      </AbsoluteFill>

      {/* giant isopod */}
      <AbsoluteFill style={{opacity: ramp(f, b.floor - 2, 12)}}>
        <svg width={1280} height={720} style={{position: 'absolute'}}>
          <path d="M0 560 Q 320 540 640 560 T 1280 556 L1280 720 L0 720 Z" fill="rgba(30,30,40,0.9)" />
        </svg>
        <AbsoluteFill style={{opacity: 1 - ramp(f, b.aquarium - 6, 10)}}>
          <Isopod x={lerp(1500, 620, ramp(f, b.floor, 60, 0, 1, easeOut))} y={470} len={480} />
          {/* woodlouse ~1.5 cm vs isopod ~50 cm at the same scale (≈ 9.6 px/cm) */}
          <AbsoluteFill style={{opacity: ramp(f, b.relative + 30, 10)}}>
            <Isopod x={180} y={520} len={14} />
            <Tag x={180} y={545} at={b.relative + 30} align="center" size={13} color={C.dim}>garden woodlouse · 1.5 cm</Tag>
          </AbsoluteFill>
          <BigStat x={640} y={70} at={b.iso} value="≈ 50 CM" label="giant isopod · same scale" size={60} color={C.cyan} />
        </AbsoluteFill>
        <RealInsert src="img/isopod_noaa_okeanos.jpg" at={b.iso + 20} until={b.aquarium + 150} x={180} y={60} w={820} h={461} zoom={[1.02, 1.2]} origin="55% 50%"
          label="A real giant isopod on the deep seafloor" credit="NOAA Okeanos Explorer · public domain" />
        <AbsoluteFill style={{opacity: ramp(f, b.aquarium + 140, 10)}}>
          <AbsoluteFill style={{background: 'rgba(1,6,14,0.6)'}} />
          <Isopod x={640} y={430} len={360} />
          <Panel x={420} y={70} w={440} h={150} at={b.aquarium + 140}>
            <div style={{textAlign: 'center', paddingTop: 18}}>
              <div style={{fontFamily: TEXT, fontWeight: 700, fontSize: 14, letterSpacing: 2.5, color: C.cyan}}>TOBA AQUARIUM, JAPAN · LAST MEAL: JAN 2009</div>
              <div style={{fontFamily: DISPLAY, fontWeight: 800, fontSize: 64, color: C.white, marginTop: 6}}>{f > b.refused ? `${days.toLocaleString('en-US')} days` : '—'}</div>
            </div>
          </Panel>
          <BigStat x={640} y={600} at={b.refused + 90} value="5 YEARS · 43 DAYS" label="without eating" size={48} color={C.amber} />
        </AbsoluteFill>
      </AbsoluteFill>
      {rnd(0) > 2 ? null : null}
    </AbsoluteFill>
  );
};
