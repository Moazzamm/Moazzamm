import React from 'react';
import {AbsoluteFill, useCurrentFrame} from 'remotion';
import {geoEqualEarth, geoGraticule10, geoOrthographic, geoPath} from 'd3-geo';
import {C, T} from '../theme';
import {ramp, lerp, window} from '../lib/anim';
import {paraFrame, type SceneTiming, FPS} from '../lib/timing';
import {LAND, BORDERS, PLACES} from '../lib/geo';
import {Credit, Label} from '../components/Text';

const GRAT = geoGraticule10();

// Orthographic globe whose rotation, size and position are driven by props.
export const Globe: React.FC<{rot: [number, number]; r: number; cx: number; cy: number; stipple?: number; dim?: number}> = ({
  rot, r, cx, cy, stipple = 0, dim = 1,
}) => {
  const proj = geoOrthographic().rotate(rot).scale(r).translate([cx, cy]).clipAngle(90);
  const path = geoPath(proj);
  return (
    <svg width={854} height={480} style={{position: 'absolute', opacity: dim}}>
      <defs>
        <pattern id="stip" width="6" height="6" patternUnits="userSpaceOnUse">
          <circle cx="3" cy="3" r="0.9" fill={C.cyan} />
        </pattern>
        <radialGradient id="oceanG" cx="45%" cy="40%" r="65%">
          <stop offset="0%" stopColor="#1A2E4F" />
          <stop offset="100%" stopColor="#0E1A31" />
        </radialGradient>
      </defs>
      <circle cx={cx} cy={cy} r={r} fill="url(#oceanG)" stroke={C.paperFaint} strokeWidth={1} />
      {/* Layer: satellite-estimated seafloor shape — applies to the whole ocean, so it is a uniform texture, not a coverage map */}
      <circle cx={cx} cy={cy} r={r} fill="url(#stip)" opacity={stipple * 0.55} />
      <path d={path(GRAT) ?? ''} fill="none" stroke={C.paperFaint} strokeWidth={0.5} opacity={0.6} />
      <path d={path(LAND) ?? ''} fill="#D9D2C5" fillOpacity={0.92} stroke="none" />
      <path d={path(BORDERS) ?? ''} fill="none" stroke={C.navy} strokeWidth={0.4} opacity={0.5} />
    </svg>
  );
};

// Flat Equal Earth map with the four locations.
export const FlatMap: React.FC<{opacity: number; markersAt: number[]; frame: number; highlight?: number}> = ({opacity, markersAt, frame, highlight}) => {
  const proj = geoEqualEarth().fitExtent([[60, 52], [794, 388]], {type: 'Sphere'} as never);
  const path = geoPath(proj);
  const places = [PLACES.ccz, PLACES.whillans, PLACES.lechuguilla, PLACES.mabu];
  const offsets: [number, number, 'left' | 'right'][] = [[-14, -14, 'right'], [14, -78, 'left'], [14, -15, 'left'], [14, -15, 'left']];
  return (
    <AbsoluteFill style={{opacity}}>
      <svg width={854} height={480} style={{position: 'absolute'}}>
        <path d={path({type: 'Sphere'} as never) ?? ''} fill="#0F1C33" stroke={C.paperFaint} />
        <path d={path(GRAT) ?? ''} fill="none" stroke={C.paperFaint} strokeWidth={0.4} opacity={0.5} />
        <path d={path(LAND) ?? ''} fill="#D9D2C5" fillOpacity={0.9} />
        {places.map((p, i) => {
          const [x, y] = proj([p.lon, p.lat])!;
          const o = ramp(frame, markersAt[i], 12);
          const pulse = highlight === i ? 1 + 0.25 * Math.sin(frame / 6) : 1;
          return (
            <g key={p.name} opacity={o}>
              <circle cx={x} cy={y} r={9 * pulse} fill="none" stroke={C.amber} strokeWidth={1.2} opacity={0.7} />
              <circle cx={x} cy={y} r={3.2} fill={C.amber} />
              {i === 1 ? <line x1={x + 4} y1={y - 8} x2={x + 14} y2={y - 46} stroke={C.amber} strokeWidth={0.8} /> : null}
            </g>
          );
        })}
      </svg>
      {places.map((p, i) => {
        const [x, y] = proj([p.lon, p.lat])!;
        const [dx, dy, al] = offsets[i];
        return (
          <Label key={p.name} x={x + dx} y={y + dy} at={markersAt[i] + 4} align={al} bg>
            <span style={{...T.kicker, color: C.cyan, fontSize: 10}}>{p.barrier}</span>
            <br />
            <span style={{fontSize: 12.5}}>{p.name}</span>
          </Label>
        );
      })}
    </AbsoluteFill>
  );
};

export const MapReveal: React.FC<{s: SceneTiming}> = ({s}) => {
  const f = useCurrentFrame();
  const p1 = paraFrame(s, 1);
  const p2 = paraFrame(s, 2);
  const p3 = paraFrame(s, 3);

  // P0: rotate from the Atlantic to the Pacific; settle on the CCZ longitude.
  const spin = ramp(f, 0, p1 - 30);
  const lon = lerp(10, 128, spin);
  // P1: globe slides left to make room for the measurement panel.
  const slide = ramp(f, p1, 30);
  const cx = lerp(427, 290, slide);
  const stipple = ramp(f, p1 + 15, 30);
  // P2: globe recedes; the to-scale comparison takes over.
  const recede = ramp(f, p2, 24);
  // P3: switch to a flat map that can show all four places at once.
  const flat = ramp(f, p3 - 10, 30);

  const bar = ramp(f, p1 + Math.round(8.5 * FPS), 40);

  // To-scale squares. Scale: 220 px = side of a 6,000,000 km² square (2,449 km).
  const pxPerKm = 220 / Math.sqrt(6_000_000);
  const seen = Math.sqrt(2130) * pxPerKm; // Bell et al. 2025, max estimate
  const belgium = Math.sqrt(30_689) * pxPerKm;

  return (
    <AbsoluteFill style={{backgroundColor: C.navy}}>
      <AbsoluteFill style={{opacity: 1 - flat}}>
        <Globe rot={[lon, -12]} r={lerp(175, 175, 0)} cx={cx} cy={205} stipple={stipple} dim={lerp(1, 0.18, recede)} />
      </AbsoluteFill>

      <Label x={cx} y={150} at={p1 - 70} until={p1 + 10} align="center" color={C.paperDim} size={12}>
        PACIFIC OCEAN
      </Label>

      {/* P1: the satellite layer and the 28.7% bar (a global share, deliberately not drawn as locations) */}
      <div style={{opacity: window(f, p1 + 10, p2 + 6)}}>
        <Label x={490} y={70} at={p1 + 20} width={330}>
          <span style={{...T.kicker, color: C.cyan}}>Layer · estimated</span>
          <br />
          Most of the seafloor&apos;s shape is inferred from satellite altimetry — sea-surface height, not direct sounding.
        </Label>
        <Label x={490} y={185} at={p1 + Math.round(8 * FPS)} width={330}>
          <span style={{...T.kicker, color: C.cyan}}>Layer · measured</span>
          <br />
          Ocean floor mapped to modern standards
        </Label>
        <div style={{position: 'absolute', left: 490, top: 236, width: 300, height: 16, border: `1px dashed ${C.amber}`, opacity: ramp(f, p1 + Math.round(8 * FPS), 14)}}>
          <div style={{width: `${28.7 * bar}%`, height: '100%', background: C.cyan}} />
        </div>
        <Label x={490} y={258} at={p1 + Math.round(9.5 * FPS)} color={C.cyan} size={22} weight={700}>
          28.7%
        </Label>
        <Label x={790} y={262} at={p1 + Math.round(10 * FPS)} color={C.amber} size={11} align="right" width={180}>
          not yet mapped in detail
        </Label>
        <Label x={490} y={300} at={p1 + Math.round(10 * FPS)} color={C.paperDim} size={10.5} width={320}>
          Global share as of 20 April 2026 (Seabed 2030). Shown as a proportion, not as locations.
        </Label>
      </div>

      {/* P2: everything ever seen by deep-sea cameras, to scale */}
      <div style={{opacity: window(f, p2 + 8, p3 + 4)}}>
        <svg width={854} height={480} style={{position: 'absolute'}}>
          <rect x={130} y={95} width={220} height={220} fill="none" stroke={C.cyan} strokeWidth={1.2} opacity={ramp(f, p2 + 10, 20)} />
          <rect x={520} y={200 - belgium / 2} width={belgium} height={belgium} fill="none" stroke={C.paper} strokeDasharray="2 2" opacity={ramp(f, p2 + Math.round(9 * FPS), 16)} />
          <rect x={480} y={200 - seen / 2} width={seen} height={seen} fill={C.amber} opacity={ramp(f, p2 + Math.round(4 * FPS), 16)} />
          <line x1={480 + seen / 2} y1={200 - seen} x2={480 + seen / 2} y2={150} stroke={C.amber} strokeWidth={0.8} opacity={ramp(f, p2 + Math.round(4.3 * FPS), 16)} />
        </svg>
        <Label x={130} y={322} at={p2 + 16} width={240} size={12}>
          Clarion-Clipperton Zone, Pacific
          <br />
          <span style={{color: C.paperDim, fontSize: 11}}>≈ 6,000,000 km² (for scale)</span>
        </Label>
        <Label x={420} y={92} at={p2 + Math.round(4.3 * FPS)} width={380} color={C.amber} size={12.5}>
          Every deep-sea camera view since 1958, combined
          <br />
          <span style={{color: C.paperDim, fontSize: 11}}>≤ 2,130 km² · under 0.001% of the deep seafloor (≥200 m)</span>
        </Label>
        <Label x={545} y={190} at={p2 + Math.round(9 * FPS)} size={11.5} color={C.paperDim}>
          Belgium (≈ 30,700 km²)
        </Label>
        <Label x={420} y={330} at={p2 + 30} size={10.5} color={C.paperDim} width={380}>
          All three squares drawn to the same scale. Seen area: Bell et al., Science Advances, May 2025 (maximum estimate).
        </Label>
      </div>

      <FlatMap opacity={flat} frame={f} markersAt={[p3 + Math.round(5.5 * FPS), p3 + Math.round(6.2 * FPS), p3 + Math.round(6.9 * FPS), p3 + Math.round(7.6 * FPS)]} />

      <Credit at={10} until={p2}>Map data: Natural Earth via world-atlas (public domain)</Credit>
    </AbsoluteFill>
  );
};
