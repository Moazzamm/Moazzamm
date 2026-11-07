import React from 'react';
import {AbsoluteFill, Img, staticFile, useCurrentFrame} from 'remotion';
import {C, T} from '../theme';
import {ramp, lerp, window} from '../lib/anim';
import {paraFrame, cueFrame, type SceneTiming, FPS} from '../lib/timing';
import {Globe} from './MapReveal';
import {ChapterTag, Credit, Label, Stat} from '../components/Text';

// One continuous cross-section, linear depth scale 0–5,500 m (never changes).
const Y0 = 70; // sea surface
const Y1 = 380; // 5,500 m
const yOf = (m: number) => Y0 + (m / 5500) * (Y1 - Y0);
const FLOOR = 5000; // average CCZ depth (NHM)
const SHIP_X = 470;

export const Descent: React.FC<{s: SceneTiming}> = ({s}) => {
  const f = useCurrentFrame();
  const p = (i: number, o = 0) => paraFrame(s, i, o);

  // P0 — zoom from the opening globe into the region.
  const zoom = ramp(f, 0, p(1) - 20);
  const toSection = ramp(f, p(1) - 20, 24);
  // P1 — a probe marker descends to show light and pressure changing with depth.
  const probe = ramp(f, p(1) + 20, p(2) - p(1) - 40);
  const depth = probe * FLOOR;
  // P2 — sonar swath, then ROV, then box corer.
  const swath = ramp(f, p(2) + 10, 40);
  const rov = ramp(f, cueFrame(s, 'Remotely operated'), 90);
  const corer = ramp(f, cueFrame(s, 'Box corers'), 50);
  // P3/P4 — specimen photo + numbers; P5 — sonar rings expand into the next chapter.
  const section = window(f, p(1) - 20, p(3) + 10, 20);
  const outro = ramp(f, p(5), Math.round(3.5 * FPS));

  const waffle = ramp(f, cueFrame(s, 'Roughly nine in ten'), 45);

  return (
    <AbsoluteFill style={{backgroundColor: C.navy}}>
      {/* P0: regional globe */}
      <AbsoluteFill style={{opacity: 1 - toSection}}>
        <Globe rot={[128, -12]} r={lerp(175, 900, zoom)} cx={427} cy={lerp(205, 330, zoom)} />
        <Label x={300} y={150} at={30} until={p(1)} color={C.amber} size={13} weight={600}>
          Clarion-Clipperton Zone
          <br />
          <span style={{color: C.paperDim, fontSize: 11, fontWeight: 400}}>approximate centre · between Hawaii and Mexico</span>
        </Label>
        <Stat x={560} y={250} at={Math.round(4 * FPS)} until={p(1)} value="≈ 6 million km²" caption="muddy abyssal plain" size={26} />
        <Stat x={560} y={315} at={Math.round(6.5 * FPS)} until={p(1)} value="≈ 5,000 m" caption="average depth (NHM, 2023)" size={26} />
      </AbsoluteFill>

      {/* The depth section */}
      <AbsoluteFill style={{opacity: section}}>
        <svg width={854} height={480} style={{position: 'absolute'}}>
          <defs>
            <linearGradient id="light" x1="0" y1={Y0} x2="0" y2={yOf(1000)} gradientUnits="userSpaceOnUse">
              <stop offset="0" stopColor="#2F6E8C" />
              <stop offset={200 / 1000} stopColor="#1B3D5C" />
              <stop offset="1" stopColor={C.navy} />
            </linearGradient>
          </defs>
          <rect x={60} y={Y0} width={780} height={yOf(1000) - Y0} fill="url(#light)" />
          <line x1={60} x2={840} y1={Y0} y2={Y0} stroke={C.cyan} strokeWidth={1} />
          {/* Seafloor */}
          <path d={`M60 ${yOf(FLOOR)} Q 300 ${yOf(FLOOR) - 4} 500 ${yOf(FLOOR) + 2} T 840 ${yOf(FLOOR) - 2} L840 ${Y1 + 20} L60 ${Y1 + 20} Z`} fill="#2A2621" />
          {/* Depth axis */}
          {[0, 1000, 2000, 3000, 4000, 5000].map((m) => (
            <g key={m}>
              <line x1={52} x2={60} y1={yOf(m)} y2={yOf(m)} stroke={C.paperDim} />
              <text x={48} y={yOf(m) + 3.5} fill={C.paperDim} fontSize={9.5} textAnchor="end" fontFamily="Inter">
                {m.toLocaleString('en-US')} m
              </text>
            </g>
          ))}
          {/* Ship */}
          <path d={`M${SHIP_X - 22} ${Y0 - 2} L${SHIP_X + 22} ${Y0 - 2} L${SHIP_X + 16} ${Y0 + 5} L${SHIP_X - 16} ${Y0 + 5} Z`} fill={C.paper} />
          <rect x={SHIP_X - 6} y={Y0 - 10} width={12} height={8} fill={C.paper} />
          {/* P2: multibeam swath (fan) and pings */}
          <path
            d={`M${SHIP_X} ${Y0 + 5} L${SHIP_X - 150 * swath} ${lerp(Y0 + 5, yOf(FLOOR), swath)} L${SHIP_X + 150 * swath} ${lerp(Y0 + 5, yOf(FLOOR), swath)} Z`}
            fill={C.cyan}
            opacity={0.1 * window(f, p(2), p(3), 15)}
          />
          {[0, 1, 2].map((k) => {
            const t = ((f - p(2) - 10 + k * 20) % 60) / 60;
            const vis = f > p(2) + 10 && f < p(3) ? 1 : 0;
            return (
              <path
                key={k}
                d={`M${SHIP_X - 150 * t} ${lerp(Y0 + 5, yOf(FLOOR), t)} Q ${SHIP_X} ${lerp(Y0 + 5, yOf(FLOOR), t) + 14 * t} ${SHIP_X + 150 * t} ${lerp(Y0 + 5, yOf(FLOOR), t)}`}
                stroke={C.cyan}
                strokeWidth={1}
                fill="none"
                opacity={vis * (1 - t) * 0.8}
              />
            );
          })}
          {/* ROV on its tether (enlarged — see label) */}
          <g opacity={ramp(f, cueFrame(s, 'Remotely operated'), 12) * window(f, p(2), p(3) + 10, 12)}>
            <line x1={SHIP_X + 10} y1={Y0 + 4} x2={640} y2={lerp(Y0 + 10, yOf(FLOOR) - 12, rov)} stroke={C.paperDim} strokeWidth={0.8} />
            <rect x={630} y={lerp(Y0 + 10, yOf(FLOOR) - 12, rov) - 6} width={20} height={12} rx={2} fill={C.amber} />
            <circle cx={652} cy={lerp(Y0 + 10, yOf(FLOOR) - 12, rov)} r={2} fill={C.paper} />
          </g>
          {/* Box corer */}
          <g opacity={ramp(f, cueFrame(s, 'Box corers'), 12) * window(f, p(2), p(3) + 10, 12)}>
            <line x1={SHIP_X - 12} y1={Y0 + 4} x2={300} y2={lerp(Y0 + 10, yOf(FLOOR) - 8, corer)} stroke={C.paperDim} strokeWidth={0.8} />
            <rect x={294} y={lerp(Y0 + 10, yOf(FLOOR) - 8, corer) - 4} width={12} height={10} fill="none" stroke={C.paper} />
          </g>
          {/* P1: probe marker */}
          <g opacity={window(f, p(1) + 10, p(2) + 10, 12)}>
            <line x1={150} x2={760} y1={yOf(depth)} y2={yOf(depth)} stroke={C.paperFaint} strokeDasharray="3 3" />
            <circle cx={150} cy={yOf(depth)} r={3.5} fill={C.amber} />
          </g>
        </svg>

        {/* P1 labels */}
        <Label x={160} y={yOf(200) - 7} at={p(1, 2)} until={p(2) + 10} size={11} color={C.paperDim}>
          200 m · little sunlight remains
        </Label>
        <Label x={160} y={yOf(1000) - 7} at={p(1, 3)} until={p(2) + 10} size={11} color={C.paperDim}>
          1,000 m · no sunlight (NOAA)
        </Label>
        <div style={{position: 'absolute', left: 600, top: 120, opacity: window(f, p(1) + 15, p(2) + 10, 12)}}>
          <div style={{...T.kicker, color: C.cyan}}>Probe depth</div>
          <div style={{...T.stat, fontSize: 26, color: C.paper}}>{Math.round(depth).toLocaleString('en-US')} m</div>
          <div style={{...T.kicker, color: C.cyan, marginTop: 8}}>Pressure ≈ 1 atm per 10 m</div>
          <div style={{...T.stat, fontSize: 26, color: depth > 4900 ? C.amber : C.paper}}>≈ {Math.round(1 + depth / 10)} atm</div>
        </div>
        <Label x={160} y={yOf(FLOOR) + 8} at={p(1, 5)} color={C.paperDim} size={10.5}>
          Abyssal plain ≈ 5,000 m · depth scale is linear and constant in this section
        </Label>

        {/* P2 labels */}
        <Label x={SHIP_X - 150} y={150} at={p(2) + 25} until={p(3) + 10} width={140} size={11.5} align="left">
          Multibeam sonar maps depth across a swath
        </Label>
        <Label x={662} y={yOf(FLOOR) - 52} at={cueFrame(s, 'Remotely operated', 1)} until={p(3) + 10} width={170} size={11.5}>
          Remotely operated vehicle — films and collects
          <br />
          <span style={{color: C.amber, fontSize: 10}}>drawn ×100s larger than scale</span>
        </Label>
        <Label x={190} y={yOf(FLOOR) - 52} at={cueFrame(s, 'Box corers', 0.5)} until={p(3) + 10} width={150} size={11.5}>
          Box corer — lifts a block of seafloor mud
        </Label>
      </AbsoluteFill>

      {/* P3: real specimen photo + checklist numbers */}
      <AbsoluteFill style={{opacity: window(f, p(3), p(5) + 20, 18)}}>
        <div style={{position: 'absolute', left: 28, top: 70, width: 380, height: 180, overflow: 'hidden', borderRadius: 2}}>
          <Img
            src={staticFile('img/ccz_psychropotes.jpg')}
            style={{width: 420, position: 'absolute', left: -20, top: -14, transform: `scale(${1 + 0.04 * ramp(f, p(3), 400)})`, transformOrigin: '50% 20%'}}
          />
        </div>
        <Label x={28} y={258} at={p(3) + 10} width={380} size={11} color={C.paperDim}>
          Sea cucumber <i>Psychropotes semperiana</i>, photographed alive on the CCZ seafloor.
        </Label>
        <Stat x={450} y={62} at={cueFrame(s, 'They counted')} value="5,578" caption="species recorded in the CCZ checklist" />
        <svg width={854} height={480} style={{position: 'absolute'}}>
          {Array.from({length: 100}).map((_, i) => {
            const named = i >= 90;
            const x = 452 + (i % 20) * 15;
            const y = 140 + Math.floor(i / 20) * 15;
            const o = ramp(f, cueFrame(s, 'Roughly nine in ten') + i * 0.6, 6) * (named ? 1 : 1);
            return named ? (
              <rect key={i} x={x} y={y} width={11} height={11} fill={C.paper} opacity={o} />
            ) : (
              <rect key={i} x={x + 0.5} y={y + 0.5} width={10} height={10} fill="none" stroke={C.amber} strokeWidth={1} opacity={o * (0.4 + 0.6 * waffle)} />
            );
          })}
        </svg>
        <Label x={452} y={218} at={cueFrame(s, 'Roughly nine in ten', 1.5)} width={330} size={12.5}>
          <span style={{color: C.amber}}>□ ≈ 9 in 10 had no formal scientific name</span> (88–92%)
          <br />
          <span style={{color: C.paper}}>■ ≈ 1 in 10 formally described</span>
        </Label>
      </AbsoluteFill>

      {/* P4: what "known" means here */}
      <AbsoluteFill style={{opacity: window(f, p(4), p(5) + 20, 18)}}>
        <div style={{position: 'absolute', left: 452, top: 262, width: 360}}>
          {[
            ['Found & photographed', '✓', C.cyan],
            ['Sampled & preserved', '✓', C.cyan],
            ['Formally described', '≈ 10%', C.amber],
            ['How they live · how far they range', 'largely unknown', C.amber],
          ].map(([a, b, col], i) => (
            <div key={a} style={{display: 'flex', justifyContent: 'space-between', borderTop: `1px solid ${C.paperFaint}`, padding: '3px 0', opacity: ramp(f, p(4) + 20 + i * 25, 14)}}>
              <span style={{...T.label, fontSize: 12, color: C.paper}}>{a}</span>
              <span style={{...T.label, fontSize: 12, color: col, fontWeight: 600}}>{b}</span>
            </div>
          ))}
        </div>
      </AbsoluteFill>

      {/* P5: sonar rings expand — match cut to radar in the ice chapter */}
      <svg width={854} height={480} style={{position: 'absolute', opacity: ramp(f, p(5), 10)}}>
        {[0, 1, 2, 3].map((k) => {
          const t = Math.max(0, outro - k * 0.18);
          return <circle key={k} cx={427} cy={200} r={t * 520} fill="none" stroke={C.cyan} strokeWidth={1.2} opacity={(1 - t) * 0.7} />;
        })}
      </svg>
      <Label x={427} y={190} at={p(5) + 10} align="center" size={18} weight={600}>
        What if the barrier is solid?
      </Label>

      <ChapterTag n="01" word="Water" place="Clarion-Clipperton Zone, Pacific Ocean" />
      <Credit at={p(3) + 10} until={p(5) + 20}>
        Photo: Smith &amp; Amon 2013, in Glover et al. 2016, Biodiversity Data Journal (CC BY 4.0) · Data: Rabone et al. 2023, Current Biology
      </Credit>
      <Credit at={p(1)} until={p(3)}>Light zones: NOAA Ocean Service · Diagram: schematic, depth to scale</Credit>
    </AbsoluteFill>
  );
};
