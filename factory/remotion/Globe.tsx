import React from 'react';
import {AbsoluteFill, interpolate, Easing} from 'remotion';
import {geoOrthographic, geoPath, geoGraticule10, geoContains, geoInterpolate, geoCircle} from 'd3-geo';
import {feature} from 'topojson-client';
import world from 'world-atlas/countries-110m.json';

const C0 = {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'} as const;
const countries: any = feature(world as any, (world as any).objects.countries);
const grat = geoGraticule10();
const VIEW_R: Record<string, number> = {world: 430, africa: 900, europe: 820, asia: 980, pacific: 820, atlantic: 900, japan: 1500};
const SPREAD = [[-74, 40.7], [-0.1, 51.5], [77.2, 28.6], [100.5, 13.7], [-46.6, -23.5], [28, -26.2], [151.2, -33.9], [-99.1, 19.4], [2.35, 48.85]];
const ZEALANDIA = [[160, -19], [168, -18], [174, -28], [179, -36], [180, -45], [176, -50], [168, -53], [160, -48], [157, -38], [155, -28], [160, -19]];
const STARS = Array.from({length: 140}, (_, i) => [(i * 7919) % 1920, (i * 104729) % 1080, ((i * 31) % 10) / 10]);

export const Globe: React.FC<{m: any; t: number; dur: number; accent: string}> = ({m, t, dur, accent}) => {
  const e = Easing.bezier(0.2, 0.8, 0.2, 1);
  const p = interpolate(t, [0, Math.min(1.3, dur * 0.45)], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: e});
  const target = VIEW_R[m.view] ?? 700;
  const r = interpolate(p, [0, 1], [380, target]) * (1 + 0.04 * Math.max(0, t - 1.3) / Math.max(1, dur));
  const rot: [number, number] = [-m.lon + interpolate(p, [0, 1], [70, 0]), -m.lat + interpolate(p, [0, 1], [-18, 0])];
  const cx = 960, cy = 540;
  const proj = geoOrthographic().scale(r).translate([cx, cy]).rotate(rot).clipAngle(90);
  const path = geoPath(proj as any);
  const pin = proj([m.lon, m.lat]) || [cx, cy];
  const hit = countries.features.find((f: any) => geoContains(f, [m.lon, m.lat]));
  const pinIn = interpolate(t, [0.7, 1.0], [0, 1], C0);
  const labelIn = interpolate(t, [0.9, 1.25], [0, 1], C0);
  const draw = interpolate(t, [0.7, 2.2], [0, 1], C0);
  const arc = (a: number[], b: number[]) => {
    const ip = geoInterpolate(a as any, b as any);
    const pts = Array.from({length: 40}, (_, i) => ip((i / 39) * draw));
    return path({type: 'LineString', coordinates: pts} as any) || '';
  };
  const lx = pin[0] + (pin[0] > 1300 ? -520 : 70), ly = pin[1] - 150;
  return (
    <AbsoluteFill style={{background: 'radial-gradient(circle at 50% 50%, #0d1b2e 0%, #04070d 70%)'}}>
      <svg width={1920} height={1080}>
        {STARS.map(([x, y, b], i) => <circle key={i} cx={x} cy={y} r={0.6 + b} fill="#fff" opacity={0.15 + 0.35 * b} />)}
        <defs>
          <radialGradient id="atm"><stop offset="85%" stopColor={accent} stopOpacity={0.0} /><stop offset="100%" stopColor="#5fb4ff" stopOpacity={0.35} /></radialGradient>
          <radialGradient id="sea" cx="40%" cy="35%"><stop offset="0%" stopColor="#173a5c" /><stop offset="100%" stopColor="#07121f" /></radialGradient>
        </defs>
        <circle cx={cx} cy={cy} r={r * 1.06} fill="url(#atm)" />
        <circle cx={cx} cy={cy} r={r} fill="url(#sea)" />
        <path d={path(grat as any) || ''} fill="none" stroke="#ffffff" strokeOpacity={0.06} strokeWidth={1} />
        {countries.features.map((f: any, i: number) => (
          <path key={i} d={path(f) || ''} fill={f === hit ? accent : '#2b4a4f'} fillOpacity={f === hit ? 0.25 + 0.6 * pinIn : 0.95} stroke="#9fd3d0" strokeOpacity={0.35} strokeWidth={0.8} />
        ))}
        {m.zealandia && <path d={path({type: 'Polygon', coordinates: [ZEALANDIA.slice().reverse()]} as any) || ''} fill={accent} fillOpacity={0.28 * draw} stroke={accent} strokeWidth={3} strokeDasharray="10 8" />}
        {m.equator && <path d={path({type: 'LineString', coordinates: Array.from({length: 73}, (_, i) => [-180 + i * 5, 0])} as any) || ''} fill="none" stroke={accent} strokeWidth={4} strokeDasharray="14 10" opacity={draw} />}
        {m.spread && SPREAD.map((d, i) => <path key={i} d={arc([m.lon, m.lat], d)} fill="none" stroke={accent} strokeWidth={3} opacity={0.85} />)}
        {m.from && <path d={arc(m.from, m.to ?? [m.lon, m.lat])} fill="none" stroke={accent} strokeWidth={5} />}
        {m.rings && [0.6, 1.2, 1.8].map((rr, i) => <path key={i} d={path(geoCircle().center([m.lon, m.lat]).radius(rr * draw)() as any) || ''} fill={accent} fillOpacity={0.08} stroke={accent} strokeWidth={2.5} />)}
        {[0, 1, 2].map((i) => {
          const ph = ((t * 0.9 + i / 3) % 1);
          return <circle key={i} cx={pin[0]} cy={pin[1]} r={10 + ph * 70} fill="none" stroke={accent} strokeWidth={3} opacity={(1 - ph) * pinIn} />;
        })}
        <circle cx={pin[0]} cy={pin[1]} r={11 * pinIn} fill={accent} stroke="#fff" strokeWidth={4} />
        <line x1={pin[0]} y1={pin[1]} x2={lx + (lx < pin[0] ? 450 : 0)} y2={ly + 40} stroke="#fff" strokeWidth={2} opacity={labelIn} />
      </svg>
      <div style={{position: 'absolute', left: lx, top: ly, opacity: labelIn, transform: `translateY(${(1 - labelIn) * 20}px)`,
        background: 'rgba(5,10,18,0.85)', borderLeft: `8px solid ${accent}`, padding: '16px 26px', maxWidth: 470,
        fontFamily: 'Inter', fontWeight: 900, fontSize: 34, color: '#fff', letterSpacing: 1, lineHeight: 1.15}}>{m.label}</div>
    </AbsoluteFill>
  );
};
