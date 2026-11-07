import React from 'react';
import {useCurrentFrame} from 'remotion';
import {geoCircle, geoGraticule10, geoOrthographic, geoPath} from 'd3-geo';
import {feature} from 'topojson-client';
import landTopo from 'world-atlas/land-110m.json';
import type {FeatureCollection} from 'geojson';
import {C} from '../theme';
import {rnd} from '../lib/anim';

// eslint-disable-next-line @typescript-eslint/no-explicit-any
const LAND = feature(landTopo as any, (landTopo as any).objects.land) as unknown as FeatureCollection;

type P = {cx: number; cy: number; r: number; spin?: number};

const Glow: React.FC<{cx: number; cy: number; r: number; color: string; k?: number}> = ({cx, cy, r, color, k = 1.35}) => (
  <div
    style={{
      position: 'absolute', left: cx - r * k, top: cy - r * k, width: r * 2 * k, height: r * 2 * k, borderRadius: '50%',
      background: `radial-gradient(circle, ${color} 0%, transparent 70%)`, pointerEvents: 'none',
    }}
  />
);

// Rotating Earth with real continents (Natural Earth 110m).
export const Earth: React.FC<P> = ({cx, cy, r, spin = 0.6}) => {
  const f = useCurrentFrame();
  const proj = geoOrthographic().rotate([-f * spin, -18]).scale(r).translate([cx, cy]).clipAngle(90);
  const path = geoPath(proj);
  const id = `e${Math.round(cx)}${Math.round(cy)}${Math.round(r)}`;
  return (
    <>
      <Glow cx={cx} cy={cy} r={r} color="rgba(92,170,255,0.45)" k={1.25} />
      <svg width={854} height={480} style={{position: 'absolute', left: 0, top: 0, overflow: 'visible'}}>
        <defs>
          <radialGradient id={`${id}o`} cx="38%" cy="35%" r="70%">
            <stop offset="0" stopColor="#3C8FE0" />
            <stop offset="1" stopColor="#0D2E66" />
          </radialGradient>
          <radialGradient id={`${id}s`} cx="35%" cy="32%" r="75%">
            <stop offset="0.55" stopColor="rgba(0,0,0,0)" />
            <stop offset="1" stopColor="rgba(0,0,0,0.65)" />
          </radialGradient>
        </defs>
        <circle cx={cx} cy={cy} r={r} fill={`url(#${id}o)`} />
        <path d={path(LAND) ?? ''} fill="#4E9A5B" />
        <circle cx={cx} cy={cy} r={r} fill={`url(#${id}s)`} />
        <circle cx={cx} cy={cy} r={r} fill="none" stroke="rgba(160,210,255,0.6)" strokeWidth={Math.max(0.6, r * 0.03)} />
      </svg>
    </>
  );
};

// Mars with procedurally placed craters that rotate with the planet; Olympus Mons marked.
const CRATERS = Array.from({length: 46}).map((_, i) => ({lon: rnd(i) * 360 - 180, lat: rnd(i + 50) * 140 - 70, rad: 1.5 + rnd(i + 99) * 6}));
export const Mars: React.FC<P & {highlight?: number}> = ({cx, cy, r, spin = 0.35, highlight = 0}) => {
  const f = useCurrentFrame();
  const proj = geoOrthographic().rotate([110 - f * spin, -12]).scale(r).translate([cx, cy]).clipAngle(90);
  const path = geoPath(proj);
  const id = `m${Math.round(r)}`;
  const om = geoCircle().center([-134, 18.6]).radius(5.2)();
  return (
    <>
      <Glow cx={cx} cy={cy} r={r} color="rgba(255,120,60,0.35)" k={1.2} />
      <svg width={854} height={480} style={{position: 'absolute', left: 0, top: 0, overflow: 'visible'}}>
        <defs>
          <radialGradient id={`${id}b`} cx="38%" cy="35%" r="75%">
            <stop offset="0" stopColor="#E38A55" />
            <stop offset="0.6" stopColor="#B2502C" />
            <stop offset="1" stopColor="#5A2010" />
          </radialGradient>
        </defs>
        <circle cx={cx} cy={cy} r={r} fill={`url(#${id}b)`} />
        {CRATERS.map((c, i) => (
          <path key={i} d={path(geoCircle().center([c.lon, c.lat]).radius(c.rad)()) ?? ''} fill="rgba(70,25,10,0.28)" stroke="rgba(255,190,150,0.18)" strokeWidth={0.6} />
        ))}
        <path d={path(om) ?? ''} fill="rgba(255,205,160,0.55)" stroke={C.hot} strokeWidth={highlight * 2} />
        <circle cx={cx} cy={cy} r={r} fill="none" stroke="rgba(255,170,120,0.35)" strokeWidth={1} />
      </svg>
    </>
  );
};

// Jupiter: bands drift at different speeds (as they really do), plus a swirling Great Red Spot.
export const Jupiter: React.FC<P & {spot?: number}> = ({cx, cy, r, spot = 1}) => {
  const f = useCurrentFrame();
  const bands = 15;
  const colors = ['#E9D8BE', '#C9A27E', '#F1E4CF', '#B98A64', '#E3CDB0', '#A9775A', '#EEDFC6', '#C69C78', '#F2E6D2', '#B2845F', '#E6D2B4', '#9F6E52', '#EBDCC2', '#C49773', '#E8D6BA'];
  const id = `j${Math.round(r)}`;
  const gx = cx + r * 0.32, gy = cy + r * 0.3, gw = r * 0.36, gh = r * 0.2;
  return (
    <>
      <Glow cx={cx} cy={cy} r={r} color="rgba(255,210,160,0.22)" k={1.2} />
      <svg width={854} height={480} style={{position: 'absolute', left: 0, top: 0, overflow: 'visible'}}>
        <defs>
          <clipPath id={`${id}c`}>
            <circle cx={cx} cy={cy} r={r} />
          </clipPath>
          <radialGradient id={`${id}s`} cx="36%" cy="34%" r="78%">
            <stop offset="0.5" stopColor="rgba(0,0,0,0)" />
            <stop offset="1" stopColor="rgba(0,0,0,0.75)" />
          </radialGradient>
          <radialGradient id={`${id}g`}>
            <stop offset="0" stopColor="#E0663A" />
            <stop offset="0.6" stopColor="#C2502F" />
            <stop offset="1" stopColor="#D88A62" />
          </radialGradient>
        </defs>
        <g clipPath={`url(#${id}c)`}>
          <circle cx={cx} cy={cy} r={r} fill="#D9BE9C" />
          {Array.from({length: bands}).map((_, i) => {
            const y0 = cy - r + (i * 2 * r) / bands;
            const h = (2 * r) / bands + r * 0.05;
            const speed = (i % 2 ? -1 : 1) * (0.6 + rnd(i) * 0.9);
            const pts: string[] = [];
            for (let k = 0; k <= 24; k++) {
              const x = cx - r + (k * 2 * r) / 24;
              pts.push(`${x},${y0 + Math.sin(k * 0.9 + f * 0.04 * speed + i) * r * 0.012}`);
            }
            return <polygon key={i} points={`${pts.join(' ')} ${cx + r},${y0 + h} ${cx - r},${y0 + h}`} fill={colors[i]} />;
          })}
          {/* swirl streaks carried by the bands */}
          {Array.from({length: 26}).map((_, i) => {
            const band = Math.floor(rnd(i) * bands);
            const y = cy - r + (band + 0.5) * (2 * r) / bands;
            const speed = (band % 2 ? -1 : 1) * (0.6 + rnd(band) * 0.9) * 0.9;
            const x = ((rnd(i + 3) * 4 * r + f * speed) % (2.4 * r) + 2.4 * r) % (2.4 * r) + cx - 1.2 * r;
            return <ellipse key={i} cx={x} cy={y} rx={r * 0.09} ry={r * 0.012} fill="rgba(255,255,255,0.25)" />;
          })}
          {/* Great Red Spot */}
          <g opacity={spot}>
            <ellipse cx={gx} cy={gy} rx={gw} ry={gh} fill={`url(#${id}g)`} />
            {[0.8, 0.55, 0.32].map((k, i) => (
              <ellipse key={i} cx={gx} cy={gy} rx={gw * k} ry={gh * k} fill="none" stroke="rgba(255,220,190,0.45)" strokeWidth={1.2} strokeDasharray={`${gw * k * 1.2} ${gw * k * 0.6}`} strokeDashoffset={-f * (2 + i)} />
            ))}
          </g>
          <circle cx={cx} cy={cy} r={r} fill={`url(#${id}s)`} />
        </g>
      </svg>
    </>
  );
};

// Saturn's north pole seen from above, with the hexagonal jet stream and central vortex.
export const SaturnPole: React.FC<P & {flow?: number}> = ({cx, cy, r, flow = 1}) => {
  const f = useCurrentFrame();
  const rot = f * 0.05;
  const hexR = r * 0.55;
  const hex = Array.from({length: 7}).map((_, k) => {
    const a = (k / 6) * Math.PI * 2 + rot * 0.02;
    return `${cx + Math.cos(a) * hexR},${cy + Math.sin(a) * hexR}`;
  }).join(' ');
  return (
    <>
      <Glow cx={cx} cy={cy} r={r} color="rgba(240,210,150,0.25)" k={1.25} />
      <svg width={854} height={480} style={{position: 'absolute', left: 0, top: 0, overflow: 'visible'}}>
        <defs>
          <radialGradient id="sat" cx="50%" cy="50%" r="50%">
            <stop offset="0" stopColor="#4C6E7E" />
            <stop offset="0.45" stopColor="#7E8B79" />
            <stop offset="0.75" stopColor="#C8B289" />
            <stop offset="1" stopColor="#9E8660" />
          </radialGradient>
        </defs>
        <circle cx={cx} cy={cy} r={r} fill="url(#sat)" />
        {[0.95, 0.85, 0.75, 0.68].map((k, i) => (
          <circle key={i} cx={cx} cy={cy} r={r * k} fill="none" stroke="rgba(255,240,210,0.12)" strokeWidth={r * 0.04} />
        ))}
        <polygon points={hex} fill="rgba(60,90,110,0.55)" stroke="rgba(240,230,200,0.55)" strokeWidth={r * 0.05} strokeLinejoin="round" />
        {/* wind flowing along the hexagon */}
        <polygon points={hex} fill="none" stroke={C.hot} strokeWidth={2} strokeDasharray="6 22" strokeDashoffset={-f * 4 * flow} opacity={0.85 * flow} strokeLinejoin="round" />
        {/* central vortex */}
        {Array.from({length: 5}).map((_, i) => {
          const pts: string[] = [];
          for (let k = 0; k < 40; k++) {
            const a = k * 0.32 + i * (Math.PI * 2 / 5) + f * 0.12;
            const rr = (k / 40) * r * 0.2;
            pts.push(`${cx + Math.cos(a) * rr},${cy + Math.sin(a) * rr}`);
          }
          return <polyline key={i} points={pts.join(' ')} fill="none" stroke="rgba(255,240,220,0.55)" strokeWidth={1.4} />;
        })}
        <circle cx={cx} cy={cy} r={r} fill="none" stroke="rgba(255,235,200,0.3)" />
      </svg>
    </>
  );
};

// Neutron star / pulsar: tiny blazing sphere with two sweeping beams.
export const Pulsar: React.FC<P & {beams?: number; beamSpeed?: number}> = ({cx, cy, r, beams = 1, beamSpeed = 6}) => {
  const f = useCurrentFrame();
  const a = f * beamSpeed;
  return (
    <>
      <Glow cx={cx} cy={cy} r={r * 4} color="rgba(150,210,255,0.45)" k={1} />
      <div style={{position: 'absolute', left: cx, top: cy, width: 0, height: 0, transform: `rotate(${a}deg)`, opacity: beams}}>
        {[0, 180].map((d) => (
          <div
            key={d}
            style={{
              position: 'absolute', left: 0, top: -14, width: 700, height: 28, transformOrigin: '0 50%', transform: `rotate(${d}deg)`,
              background: 'linear-gradient(90deg, rgba(200,235,255,0.95), rgba(120,200,255,0.35) 40%, transparent 90%)',
              clipPath: 'polygon(0 45%, 100% 0, 100% 100%, 0 55%)',
            }}
          />
        ))}
      </div>
      <div
        style={{
          position: 'absolute', left: cx - r, top: cy - r, width: r * 2, height: r * 2, borderRadius: '50%',
          background: 'radial-gradient(circle at 40% 38%, #FFFFFF, #CFE9FF 45%, #6FB6FF 80%)', boxShadow: `0 0 ${r * 2}px #9FD4FF`,
        }}
      />
    </>
  );
};

// Black hole: lensed accretion disk, photon ring with Doppler-brightened side, infalling sparks.
export const BlackHole: React.FC<P & {tilt?: number}> = ({cx, cy, r, tilt = 0.28}) => {
  const f = useCurrentFrame();
  const disk = (front: boolean) => (
    <div
      style={{
        position: 'absolute', left: cx - r * 3.2, top: cy - r * 3.2 * tilt, width: r * 6.4, height: r * 6.4 * tilt, borderRadius: '50%',
        background: `conic-gradient(from ${f * 2}deg, #FFB547, #FF6A2B, #7A1E0E, #FF8A3D, #FFE3A3, #FFB547)`,
        WebkitMaskImage: 'radial-gradient(ellipse, transparent 30%, black 34%, black 62%, transparent 72%)',
        maskImage: 'radial-gradient(ellipse, transparent 30%, black 34%, black 62%, transparent 72%)',
        clipPath: front ? 'inset(50% 0 0 0)' : 'inset(0 0 50% 0)',
        opacity: 0.95,
      }}
    />
  );
  return (
    <>
      <Glow cx={cx} cy={cy} r={r * 3} color="rgba(255,140,60,0.28)" k={1} />
      {disk(false)}
      {/* lensed image of the far side of the disk, arching over the hole */}
      <div
        style={{
          position: 'absolute', left: cx - r * 1.75, top: cy - r * 1.75, width: r * 3.5, height: r * 3.5, borderRadius: '50%',
          background: `conic-gradient(from ${-f * 1.5}deg, #FFD27A, #FF7A30 30%, #FFE3A3 55%, #FF7A30 80%, #FFD27A)`,
          WebkitMaskImage: 'radial-gradient(circle, transparent 54%, black 57%, black 64%, transparent 71%)',
          maskImage: 'radial-gradient(circle, transparent 54%, black 57%, black 64%, transparent 71%)',
        }}
      />
      <div style={{position: 'absolute', left: cx - r, top: cy - r, width: r * 2, height: r * 2, borderRadius: '50%', background: '#000', boxShadow: '0 0 18px 6px rgba(255,150,60,0.55)'}} />
      {disk(true)}
      {/* infalling sparks */}
      <svg width={854} height={480} style={{position: 'absolute', left: 0, top: 0, overflow: 'visible'}}>
        {Array.from({length: 40}).map((_, i) => {
          const t = ((f * 0.006 + rnd(i)) % 1);
          const rr = r * (3.1 - 2.0 * t);
          const ang = rnd(i + 7) * Math.PI * 2 + t * 9;
          return <circle key={i} cx={cx + Math.cos(ang) * rr} cy={cy + Math.sin(ang) * rr * tilt} r={1.1} fill="#FFE3B0" opacity={0.3 + 0.6 * t} />;
        })}
      </svg>
    </>
  );
};

// Spiral galaxy made of particles with differential rotation.
export const Galaxy: React.FC<P & {tilt?: number; count?: number}> = ({cx, cy, r, tilt = 0.55, count = 520}) => {
  const f = useCurrentFrame();
  const dots = [];
  for (let i = 0; i < count; i++) {
    const arm = i % 2;
    const t = rnd(i);
    const rr = r * Math.pow(t, 0.7);
    const spread = (rnd(i + 3) - 0.5) * 0.9 * (1 - t * 0.4);
    const ang = arm * Math.PI + t * 7.5 + spread - f * 0.012 * (1.4 - t);
    const x = cx + Math.cos(ang) * rr;
    const y = cy + Math.sin(ang) * rr * tilt;
    const hot = t < 0.18;
    dots.push(<circle key={i} cx={x} cy={y} r={hot ? 1.3 : 0.8 + rnd(i + 8) * 0.6} fill={hot ? '#FFE6B8' : rnd(i + 5) > 0.7 ? '#BFD8FF' : '#F2E6FF'} opacity={0.35 + 0.55 * (1 - t)} />);
  }
  return (
    <>
      <Glow cx={cx} cy={cy} r={r * 0.5} color="rgba(255,225,180,0.55)" k={1} />
      <svg width={854} height={480} style={{position: 'absolute', left: 0, top: 0, overflow: 'visible'}}>{dots}</svg>
    </>
  );
};

export const GRAT = geoGraticule10();
