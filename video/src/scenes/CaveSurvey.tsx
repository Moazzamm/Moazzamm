import React from 'react';
import {AbsoluteFill, Img, staticFile, useCurrentFrame} from 'remotion';
import {C, T} from '../theme';
import {ramp, lerp, window} from '../lib/anim';
import {paraFrame, cueFrame, type SceneTiming, FPS} from '../lib/timing';
import {ChapterTag, Credit, Label, Stat} from '../components/Text';

// Example survey stations for the METHOD diagram (schematic, not Lechuguilla's passages).
const ST: [number, number][] = [
  [110, 150], [190, 182], [262, 170], [330, 214], [415, 226], [478, 270], [560, 262],
];

export const CaveSurvey: React.FC<{s: SceneTiming}> = ({s}) => {
  const f = useCurrentFrame();
  const p = (i: number, o = 0) => paraFrame(s, i, o);

  const intro = window(f, 0, p(2) + 6, 16);
  const wind = f > cueFrame(s, 'But in the 1950s') && f < p(2) ? 1 : 0;
  const breakthrough = ramp(f, cueFrame(s, 'On May 26'), 30);
  const method = window(f, p(2), p(3) + 8, 16);
  const survey = ramp(f, p(2) + 20, Math.round(7 * FPS));
  const map = window(f, p(3), cueFrame(s, 'The cave was dissolved', 0.5), 16);
  const reveal = ramp(f, p(3) + 6, Math.round(6.5 * FPS));
  const photo = window(f, cueFrame(s, 'The cave was dissolved'), p(4) + 8, 16);
  const microbes = window(f, p(4), p(5) + 8, 16);
  const end = window(f, p(5), p(6, 4), 16);
  const outro = ramp(f, p(6), 40);

  const nShown = (t: number) => Math.min(ST.length, 1 + Math.floor(t * (ST.length - 1) + 0.0001));

  return (
    <AbsoluteFill style={{backgroundColor: '#0A0F1A'}}>
      {/* P0–P1: the historic cave, schematic */}
      <AbsoluteFill style={{opacity: intro}}>
        <svg width={854} height={480} style={{position: 'absolute'}}>
          <rect y={0} width={854} height={110} fill="#22324A" />
          <path d="M0 110 L330 110 L330 112 L854 112" stroke="#C9B79C" strokeWidth={2} fill="none" />
          <rect y={112} width={854} height={290} fill="#2B2520" />
          {/* entrance pit + dead-end passage */}
          <path d="M330 110 L360 110 L360 220 L640 220 L640 252 L330 252 Z" fill="#0A0F1A" />
          {/* rubble */}
          {Array.from({length: 26}).map((_, i) => (
            <circle key={i} cx={360 + (i % 13) * 10 + (i > 12 ? 5 : 0)} cy={246 - (i > 12 ? 7 : 0)} r={5} fill="#5A4E43" opacity={1 - breakthrough * (i < 8 ? 1 : 0)} />
          ))}
          {/* wind rising through the rubble */}
          {[0, 1, 2, 3].map((k) => {
            const t = (((f - cueFrame(s, 'But in the 1950s')) / 45 + k / 4) % 1 + 1) % 1;
            return (
              <path key={k} d={`M${400 + k * 22} ${300 - t * 70} l -5 7 m 5 -7 l 5 7`} stroke={C.cyan} strokeWidth={1.4} fill="none" opacity={wind * Math.sin(t * Math.PI)} />
            );
          })}
          {/* breakthrough: passage continues below */}
          <path d={`M380 252 L380 ${252 + 120 * breakthrough} L${380 + 260 * breakthrough} ${300 + 70 * breakthrough}`} stroke={C.cyan} strokeWidth={3} fill="none" opacity={breakthrough} />
        </svg>
        <Label x={300} y={150} at={p(0, 2)} until={p(2)} size={11} align="right">
          Entrance pit ≈ 27 m (90 ft)
        </Label>
        <Label x={480} y={196} at={p(0, 3)} until={p(2)} size={11}>
          ≈ 120 m (400 ft) of dead-end passage
        </Label>
        <Label x={520} y={300} at={cueFrame(s, 'But in the 1950s')} until={p(1)} size={11.5} width={300} color={C.cyan}>
          1950s · cavers hear wind roaring up through the rubble floor
        </Label>
        <Label x={520} y={300} at={p(1)} until={p(2)} size={11.5} width={300}>
          1984 · digging begins, with park permission
        </Label>
        <Label x={520} y={330} at={cueFrame(s, 'On May 26')} until={p(2)} size={13} weight={600} width={300} color={C.amber}>
          26 May 1986 · breakthrough into large walking passages
        </Label>
        <Label x={826} y={125} at={p(0, 2)} until={p(2)} align="right" size={10.5} color={C.amber} bg>
          SCHEMATIC · not to scale
        </Label>
      </AbsoluteFill>

      {/* P2: how a survey line is built */}
      <AbsoluteFill style={{opacity: method}}>
        <svg width={854} height={480} style={{position: 'absolute'}}>
          {ST.slice(0, nShown(survey)).map(([x, y], i) => {
            if (i === 0) return null;
            const [px, py] = ST[i - 1];
            const seg = i === nShown(survey) - 1 ? ramp(f, p(2) + 20 + ((i - 1) / (ST.length - 1)) * 7 * FPS, 20) : 1;
            return <line key={i} x1={px} y1={py} x2={lerp(px, x, seg)} y2={lerp(py, y, seg)} stroke={C.amber} strokeWidth={2} />;
          })}
          {ST.slice(0, nShown(survey)).map(([x, y], i) => (
            <g key={i}>
              <circle cx={x} cy={y} r={4} fill={C.paper} />
              <text x={x} y={y - 10} fill={C.paperDim} fontSize={9} textAnchor="middle" fontFamily="Inter">
                S{i + 1}
              </text>
            </g>
          ))}
        </svg>
        <div style={{position: 'absolute', left: 120, top: 270, width: 260, opacity: ramp(f, p(2, 3), 14)}}>
          <div style={{...T.kicker, color: C.cyan}}>Each shot S1 → S2 records</div>
          <div style={{...T.label, color: C.paper, fontSize: 12.5, marginTop: 4}}>distance · direction · slope</div>
          <div style={{...T.small, color: C.paperDim, marginTop: 4}}>plus a hand sketch of the passage around each station</div>
        </div>
        <Label x={826} y={70} at={p(2) + 6} align="right" size={10.5} color={C.amber}>
          SCHEMATIC · the survey method, not Lechuguilla&apos;s passages
        </Label>
      </AbsoluteFill>

      {/* P3: the real NPS survey map, revealed outward from the entrance */}
      <AbsoluteFill style={{opacity: map}}>
        <div
          style={{
            position: 'absolute',
            left: 27,
            top: 62,
            width: 610,
            height: 289,
            clipPath: `circle(${reveal * 110}% at 58% 15%)`,
          }}
        >
          <Img src={staticFile('img/cave_map_nps_2019.jpg')} style={{width: 610}} />
        </div>
        <Stat x={660} y={80} at={p(3, 2)} value="> 145 mi" caption="surveyed since 1984 (≈ 233 km) · NPS page, updated July 2025" size={26} width={170} />
        <Stat x={660} y={185} at={p(3, 4)} value="489 m" caption="surveyed depth (1,604 ft)" size={26} width={170} />
        <Label x={660} y={270} at={p(3, 5)} width={170} size={10.5} color={C.amber}>
          The 2019 map itself is labelled 149 miles; NPS text says &ldquo;over 145&rdquo;.
        </Label>
        <Label x={27} y={356} at={p(3, 1)} width={610} size={10.5} color={C.paperDim}>
          Plan view of every surveyed passage. The drawing stops where the survey stops.
        </Label>
      </AbsoluteFill>

      {/* P3 (end): photograph — the gypsum chandeliers the narration describes */}
      <AbsoluteFill style={{opacity: photo}}>
        <div style={{position: 'absolute', left: 28, top: 70, width: 450, height: 323, overflow: 'hidden', borderRadius: 2}}>
          <Img
            src={staticFile('img/cave_chandeliers_nps.jpg')}
            style={{width: 450, transform: `scale(${1 + 0.05 * ramp(f, cueFrame(s, 'The cave was dissolved'), 300)})`, transformOrigin: '70% 55%'}}
          />
        </div>
        <Label x={505} y={120} at={cueFrame(s, 'The cave was dissolved', 0.5)} width={320} size={16} weight={600}>
          Dissolved from below by sulfuric acid
        </Label>
        <Label x={505} y={156} at={cueFrame(s, 'The cave was dissolved', 2)} width={320} size={12.5} color={C.paperDim}>
          Gypsum &ldquo;chandeliers&rdquo; up to about 6 m (20 ft) long hang in parts of the cave.
        </Label>
        <Label x={505} y={220} at={cueFrame(s, 'The cave was dissolved', 1)} width={320} size={11} color={C.paperDim}>
          Photo: the Chandelier Ballroom, Lechuguilla Cave. Note the caver for scale (right of centre).
        </Label>
      </AbsoluteFill>

      {/* P4: microbes */}
      <AbsoluteFill style={{opacity: microbes}}>
        <Stat x={60} y={90} at={p(4) + 8} value="> 4 million years" caption="that cave section has been isolated from surface input" size={30} width={420} />
        <Stat x={60} y={180} at={cueFrame(s, 'researchers found bacteria')} value="14" caption="commercial antibiotics some cave strains already resisted — incl. daptomycin, a drug of last resort" size={44} color={C.amber} width={420} />
        <Label x={60} y={300} at={cueFrame(s, 'Resistance, it turns out')} width={500} size={14} weight={600}>
          Antibiotic resistance is natural — and ancient.
        </Label>
      </AbsoluteFill>

      {/* P5: the map stops at the last station */}
      <AbsoluteFill style={{opacity: end}}>
        <svg width={854} height={480} style={{position: 'absolute'}}>
          {ST.map(([x, y], i) => (i ? <line key={i} x1={ST[i - 1][0]} y1={ST[i - 1][1]} x2={x} y2={y} stroke={C.amber} strokeWidth={2} /> : null))}
          {ST.map(([x, y], i) => (
            <circle key={i} cx={x} cy={y} r={4} fill={C.paper} />
          ))}
          <path
            d="M560 262 C 620 250, 650 300, 700 286 C 740 276, 770 320, 800 312"
            stroke={C.amber}
            strokeWidth={1.4}
            strokeDasharray="5 5"
            fill="none"
            opacity={ramp(f, p(5, 2), 20) * 0.8}
          />
          <text x={705} y={262} fill={C.amber} fontSize={22} fontFamily="Inter" fontWeight={700} opacity={ramp(f, p(5, 2.5), 20)}>
            ?
          </text>
        </svg>
        <Label x={560} y={300} at={p(5, 1)} size={11.5} align="right">
          last survey station
        </Label>
        <Label x={640} y={330} at={p(5, 3)} width={190} size={11} color={C.amber}>
          Illustrative only: beyond the last station there may be passage — or none.
        </Label>
      </AbsoluteFill>

      {/* P6: hand-off to the forest — a top-down view */}
      <AbsoluteFill style={{opacity: outro, backgroundColor: C.navy}}>
        <Label x={427} y={190} at={p(6) + 4} align="center" size={18} weight={600} width={600}>
          From above, a forest is visible. Is it known?
        </Label>
      </AbsoluteFill>

      <ChapterTag n="03" word="Rock" place="Lechuguilla Cave, Carlsbad Caverns NP, New Mexico" />
      <Credit at={p(3)} until={cueFrame(s, 'The cave was dissolved', 0.5)}>Map: U.S. National Park Service, Lechuguilla Cave overview, July 2019 (public domain)</Credit>
      <Credit at={cueFrame(s, 'The cave was dissolved', 0.5)} until={p(4) + 8}>Photo: NPS / Max Wisshak (public domain, NPGallery) · Facts: NPS</Credit>
      <Credit at={p(4)} until={p(5) + 8}>Bhullar et al. 2012, PLOS ONE 7(4): e34953</Credit>
      <Credit at={0} until={p(2)}>History: NPS, Carlsbad Caverns NP</Credit>
    </AbsoluteFill>
  );
};
