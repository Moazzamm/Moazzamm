import React from 'react';
import {AbsoluteFill, useCurrentFrame} from 'remotion';
import {geoOrthographic, geoPath} from 'd3-geo';
import {C, T} from '../theme';
import {ramp, lerp, window} from '../lib/anim';
import {paraFrame, type SceneTiming, FPS} from '../lib/timing';
import {LAND, PLACES} from '../lib/geo';
import {ChapterTag, Credit, Label, Stat} from '../components/Text';

// Deterministic pseudo-random for snow streaks.
const rnd = (i: number) => {
  const x = Math.sin(i * 127.1) * 43758.5453;
  return x - Math.floor(x);
};

// Section geometry (SCHEMATIC). Ice 0–800 m maps to y 120–330; the 2 m lake is exaggerated.
const SURF = 120;
const BASE = 330;
const DRILL_X = 427;

export const IceCutaway: React.FC<{s: SceneTiming}> = ({s}) => {
  const f = useCurrentFrame();
  const p = (i: number, o = 0) => paraFrame(s, i, o);

  // P0 surface view → P1 cut into the section (camera moves down; motivated by "beneath").
  const cut = ramp(f, p(1, 7), 40);
  const sat = ramp(f, p(1), Math.round(7 * FPS));
  const radar = f > p(1, 8.5) && f < p(2) ? 1 : 0;
  const drill = ramp(f, p(2) + 10, Math.round(9 * FPS));
  const inset = ramp(f, p(3), 24);
  const polar = ramp(f, p(4) - 6, 24);
  const outro = ramp(f, p(5), 30);

  const proj = geoOrthographic().rotate([0, 90]).scale(330).translate([250, 215]).clipAngle(90);
  const path = geoPath(proj);
  const [wx, wy] = proj([PLACES.whillans.lon, PLACES.whillans.lat])!;

  return (
    <AbsoluteFill style={{backgroundColor: C.navy}}>
      {/* SURFACE VIEW */}
      <AbsoluteFill style={{opacity: 1 - cut}}>
        <svg width={854} height={480} style={{position: 'absolute'}}>
          <defs>
            <linearGradient id="sky" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0" stopColor="#1B2C49" />
              <stop offset="1" stopColor="#5D7A92" />
            </linearGradient>
            <linearGradient id="snow" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0" stopColor="#C9D9E2" />
              <stop offset="1" stopColor="#EEF3F5" />
            </linearGradient>
          </defs>
          <rect width={854} height={240} fill="url(#sky)" />
          <rect y={240} width={854} height={240} fill="url(#snow)" />
          {Array.from({length: 70}).map((_, i) => {
            const y = 245 + rnd(i) * 160;
            const speed = 2 + rnd(i + 9) * 4;
            const x = ((rnd(i + 3) * 900 + f * speed) % 960) - 60;
            return <line key={i} x1={x} y1={y} x2={x + 26} y2={y - 1} stroke="#FFFFFF" strokeWidth={0.8} opacity={0.35} />;
          })}
          {/* ICESat (schematic): laser footprint sweeping the surface */}
          <g opacity={window(f, p(1), p(1, 8), 12)}>
            <rect x={lerp(80, 760, sat) - 8} y={52} width={16} height={8} fill={C.paper} />
            <line x1={lerp(80, 760, sat)} y1={60} x2={lerp(80, 760, sat)} y2={300} stroke={C.cyan} strokeWidth={1} opacity={0.8} />
          </g>
        </svg>
        <div style={{position: 'absolute', right: 28, top: 70, width: 230, opacity: window(f, p(1, 1), p(1, 8), 12)}}>
          <div style={{...T.kicker, color: C.cyan}}>Ice-surface height (schematic)</div>
          <svg width={230} height={60}>
            <path
              d={Array.from({length: 46}).map((_, i) => `${i ? 'L' : 'M'}${i * 5} ${30 - 18 * Math.sin(i / 6) * (i < 46 * sat ? 1 : 0)}`).join(' ')}
              stroke={C.amber}
              fill="none"
              strokeWidth={1.4}
            />
          </svg>
          <div style={{...T.small, color: C.navy, background: 'rgba(242,237,228,0.85)', padding: '3px 6px'}}>
            ICESat (2003–2009) saw the surface rise and fall as water filled and drained below. Curve is illustrative.
          </div>
        </div>
      </AbsoluteFill>

      {/* CROSS-SECTION (schematic) */}
      <AbsoluteFill style={{opacity: cut * (1 - polar)}}>
        <svg width={854} height={480} style={{position: 'absolute'}}>
          <rect y={0} width={854} height={SURF} fill="#16243F" />
          <rect y={SURF} width={854} height={BASE - SURF} fill="#BFD6E2" />
          {[0.25, 0.5, 0.75].map((k) => (
            <line key={k} x1={0} x2={854} y1={SURF + (BASE - SURF) * k} y2={SURF + (BASE - SURF) * k + 2} stroke="#A9C3D1" strokeWidth={0.7} />
          ))}
          {/* lake: exaggerated thickness */}
          <path d={`M180 ${BASE} Q427 ${BASE + 26} 690 ${BASE} Z`} fill={C.cyan} />
          <rect y={BASE} width={854} height={60} fill="#4A4038" />
          <path d={`M180 ${BASE} Q427 ${BASE + 26} 690 ${BASE}`} fill="none" stroke={C.cyan} />
          {/* radar pulses (match cut from sonar) */}
          {[0, 1, 2].map((k) => {
            const t = (((f - p(1, 8.5)) / 40 + k / 3) % 1 + 1) % 1;
            return <path key={k} d={`M${300} ${SURF + (BASE - SURF) * t} Q 427 ${SURF + (BASE - SURF) * t + 10} 554 ${SURF + (BASE - SURF) * t}`} stroke={C.navy} fill="none" strokeWidth={1.2} opacity={radar * (1 - t)} />;
          })}
          {/* borehole */}
          <rect x={DRILL_X - 2} y={SURF} width={4} height={(BASE + 12 - SURF) * drill} fill={C.navy} opacity={drill > 0 ? 1 : 0} />
          <rect x={DRILL_X - 9} y={SURF - 22} width={18} height={22} fill={C.amber} opacity={ramp(f, p(2), 12)} />
        </svg>
        <Label x={28} y={SURF + 6} at={p(1, 8)} size={11} color={C.navy}>
          Ice ≈ 800 m thick
        </Label>
        <Label x={700} y={BASE + 6} at={p(1, 9)} size={11} color={C.cyan} weight={600}>
          Subglacial Lake Whillans
        </Label>
        <Label x={28} y={BASE + 30} at={p(1, 9)} size={10.5} color={C.paperDim}>
          Sediment / bedrock
        </Label>
        <Label x={826} y={SURF - 40} at={p(1, 9)} align="right" size={10} color={C.amber} bg>
          SCHEMATIC · lake thickness greatly exaggerated
        </Label>
        <Label x={600} y={SURF + 40} at={p(1, 10)} until={p(2)} size={11.5} width={220} color={C.navy}>
          Radar and seismic surveys traced the lake&apos;s outline
        </Label>
        <div style={{position: 'absolute', left: DRILL_X + 18, top: SURF + 12, opacity: window(f, p(2) + 10, p(3) + 20, 12)}}>
          <div style={{...T.kicker, color: C.navy}}>Borehole depth</div>
          <div style={{...T.stat, fontSize: 26, color: C.navy}}>{Math.round(801 * drill)} m</div>
          <div style={{...T.small, color: C.navy, width: 230, marginTop: 2}}>
            Clean hot-water drill · hole ≈ 0.6 m wide · late January 2013 · WISSARD project
          </div>
        </div>
      </AbsoluteFill>

      {/* INSET: different scale */}
      <AbsoluteFill style={{opacity: inset * (1 - polar)}}>
        <svg width={854} height={480} style={{position: 'absolute'}}>
          <line x1={DRILL_X} y1={BASE + 6} x2={170} y2={250} stroke={C.amber} strokeWidth={0.8} />
          <circle cx={170} cy={250} r={92} fill={C.navy} stroke={C.amber} strokeWidth={1.2} />
          <clipPath id="ins">
            <circle cx={170} cy={250} r={91} />
          </clipPath>
          <g clipPath="url(#ins)">
            <rect x={70} y={150} width={200} height={70} fill="#BFD6E2" />
            <rect x={70} y={220} width={200} height={55} fill={C.cyan} opacity={0.85} />
            <rect x={70} y={275} width={200} height={80} fill="#4A4038" />
            <rect x={167} y={150} width={6} height={70} fill={C.navy} />
          </g>
          <line x1={262} y1={220} x2={262} y2={275} stroke={C.amber} />
        </svg>
        <Label x={110} y={141} at={p(3) + 6} size={10} color={C.amber} bg>
          INSET · scale changed
        </Label>
        <Label x={268} y={238} at={p(3, 3)} size={11.5} color={C.amber} weight={600} bg>
          ≈ 2.2 m of water
          <br />
          <span style={{fontWeight: 400, color: C.paperDim}}>at the borehole</span>
        </Label>
      </AbsoluteFill>
      <AbsoluteFill style={{opacity: window(f, p(3) + 10, p(4) + 4, 14), backgroundColor: 'rgba(11,20,38,0.0)'}}>
        <div style={{position: 'absolute', left: 520, top: 128, width: 300, height: 182, padding: 10, background: 'rgba(11,20,38,0.88)'}}>
          <Stat x={12} y={8} at={p(3, 5)} value="≈ 130,000" caption="microbial cells per millilitre of lake water" size={28} width={290} />
          <Stat x={12} y={78} at={p(3, 9.5)} value="≥ 3,931" caption="distinct microbial types, identified by DNA (OTUs)" size={28} width={290} />
          <Label x={12} y={146} at={p(3, 15)} width={280} size={11.5} color={C.paper}>
            Many related to microbes that draw energy from ammonium, iron or sulfur compounds — not sunlight
          </Label>
        </div>
      </AbsoluteFill>

      {/* P4: Antarctica — the count, without inventing lake positions */}
      <AbsoluteFill style={{opacity: polar * (1 - outro)}}>
        <svg width={854} height={480} style={{position: 'absolute'}}>
          <path d={path({type: 'Sphere'} as never) ?? ''} fill="#0F1C33" stroke={C.paperFaint} />
          <path d={path(LAND) ?? ''} fill={C.ice} opacity={0.92} />
          <circle cx={wx} cy={wy} r={4} fill={C.amber} />
          <circle cx={wx} cy={wy} r={10} fill="none" stroke={C.amber} opacity={0.6} />
        </svg>
        <Label x={wx + 14} y={wy - 8} at={p(4) + 10} size={11} color={C.amber} bg>
          Whillans drill site
        </Label>
        <Stat x={500} y={110} at={p(4) + 12} value="675" caption="subglacial lakes in Antarctica's 2022 inventory (Livingstone et al.)" size={44} width={300} />
        <Stat x={500} y={210} at={p(4, 3)} value="a handful" caption="sampled directly by drilling" size={30} color={C.amber} width={300} />
        <Label x={500} y={290} at={p(4, 6)} width={300} size={10.5} color={C.paperDim}>
          Lake positions are not plotted here. One borehole = one point in one lake (≈ 59 km² in area).
        </Label>
      </AbsoluteFill>

      {/* P5: the borehole line alone — it becomes the cave survey line */}
      <svg width={854} height={480} style={{position: 'absolute', opacity: outro}}>
        <line x1={427} y1={60} x2={427} y2={lerp(60, 300, ramp(f, p(5), 40))} stroke={C.amber} strokeWidth={2} />
      </svg>

      <ChapterTag n="02" word="Ice" place="Whillans Ice Stream, West Antarctica · 84.24° S" />
      <Credit at={p(2)} until={p(4)}>Data: Christner et al. 2014, Nature 512 · Diagram: schematic</Credit>
      <Credit at={p(4)} until={p(5) + 10}>Inventory: Livingstone et al. 2022, Nature Reviews Earth &amp; Environment · Map: Natural Earth</Credit>
    </AbsoluteFill>
  );
};
