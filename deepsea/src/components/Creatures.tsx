import React from 'react';
import {useCurrentFrame} from 'remotion';
import {C} from '../theme';
import {rnd} from '../lib/anim';

type P = {x: number; y: number; s?: number; o?: number};
const Svg: React.FC<{children: React.ReactNode; o?: number}> = ({children, o = 1}) => (
  <svg width={1280} height={720} style={{position: 'absolute', left: 0, top: 0, overflow: 'visible', opacity: o}}>{children}</svg>
);

// Human silhouette for scale (height 1.75 m → `h` px).
export const Diver: React.FC<{x: number; y: number; h: number; o?: number; label?: boolean}> = ({x, y, h, o = 1}) => {
  const k = h / 175;
  return (
    <Svg o={o}>
      <g transform={`translate(${x} ${y}) scale(${k})`} fill="rgba(235,245,250,0.85)">
        <circle cx={0} cy={-162} r={13} />
        <rect x={-15} y={-147} width={30} height={62} rx={12} />
        <rect x={-14} y={-88} width={12} height={88} rx={6} />
        <rect x={2} y={-88} width={12} height={88} rx={6} />
        <rect x={-27} y={-145} width={10} height={58} rx={5} />
        <rect x={17} y={-145} width={10} height={58} rx={5} />
      </g>
    </Svg>
  );
};

// Japanese spider crab: body + 8 jointed walking legs + 2 long claws, alternating walking gait.
export const SpiderCrab: React.FC<P & {walk?: number}> = ({x, y, s = 1, o = 1, walk = 1}) => {
  const f = useCurrentFrame();
  const legs = [];
  for (const side of [-1, 1]) {
    for (let k = 0; k < 5; k++) {
      const claw = k === 0;
      const phase = f * 0.14 * walk + k * 1.25 + (side > 0 ? Math.PI : 0);
      const hipX = x + side * 34 * s, hipY = y + (k - 2) * 12 * s;
      const L1 = (claw ? 120 : 150 + k * 8) * s, L2 = (claw ? 110 : 170) * s;
      const up = ((claw ? 55 : 38 - k * 4) + Math.sin(phase) * 7 * walk) * (Math.PI / 180);
      const kx = hipX + side * Math.cos(up) * L1, ky = hipY - Math.sin(up) * L1;
      const fx = claw ? kx + side * L2 * 0.9 : kx + side * L2 * (0.35 + 0.08 * Math.cos(phase) * walk);
      const fy = claw ? ky - L2 * 0.25 : y + 120 * s - Math.max(0, Math.sin(phase)) * 10 * s * walk;
      legs.push(
        <g key={`${side}${k}`}>
          <path d={`M${hipX} ${hipY} L${kx} ${ky} L${fx} ${fy}`} stroke="#E7804A" strokeWidth={(claw ? 8 : 6) * s} fill="none" strokeLinejoin="round" strokeLinecap="round" />
          <path d={`M${hipX} ${hipY} L${kx} ${ky} L${fx} ${fy}`} stroke="rgba(255,235,215,0.45)" strokeWidth={2 * s} fill="none" strokeDasharray={`${3 * s} ${12 * s}`} />
          {claw ? <circle cx={fx} cy={fy} r={7 * s} fill="#F2A070" /> : null}
        </g>,
      );
    }
  }
  return (
    <Svg o={o}>
      <defs>
        <radialGradient id="crab" cx="45%" cy="40%">
          <stop offset="0" stopColor="#FFB07A" />
          <stop offset="1" stopColor="#C2502A" />
        </radialGradient>
      </defs>
      {legs}
      <ellipse cx={x} cy={y} rx={46 * s} ry={38 * s} fill="url(#crab)" />
      {Array.from({length: 9}).map((_, i) => (
        <circle key={i} cx={x + (rnd(i) - 0.5) * 60 * s} cy={y + (rnd(i + 5) - 0.5) * 46 * s} r={3 * s} fill="rgba(255,240,225,0.8)" />
      ))}
      <circle cx={x - 10 * s} cy={y - 34 * s} r={4 * s} fill="#222" />
      <circle cx={x + 10 * s} cy={y - 34 * s} r={4 * s} fill="#222" />
    </Svg>
  );
};

// Giant oarfish: long silver ribbon hanging upright, undulating, red dorsal fin rippling.
export const Oarfish: React.FC<P & {len?: number}> = ({x, y, len = 560, o = 1}) => {
  const f = useCurrentFrame();
  const N = 70;
  const pts: [number, number][] = [];
  for (let i = 0; i <= N; i++) {
    const t = i / N;
    pts.push([x + Math.sin(t * 7 - f * 0.08) * (8 + t * 26), y + t * len]);
  }
  const body = pts.map((p, i) => `${i ? 'L' : 'M'}${p[0]} ${p[1]}`).join(' ');
  return (
    <Svg o={o}>
      <defs>
        <linearGradient id="oar" x1="0" x2="1">
          <stop offset="0" stopColor="#D9E4EC" />
          <stop offset="0.5" stopColor="#FFFFFF" />
          <stop offset="1" stopColor="#8FA4B4" />
        </linearGradient>
      </defs>
      {/* dorsal fin rays */}
      {pts.map(([px, py], i) =>
        i % 2 ? null : <line key={i} x1={px - 6} y1={py} x2={px - 22 - Math.sin(i * 0.6 - f * 0.3) * 6} y2={py - 4} stroke="#E8433A" strokeWidth={2} opacity={0.9} />,
      )}
      <path d={body} stroke="url(#oar)" strokeWidth={22} fill="none" strokeLinecap="round" />
      <path d={body} stroke="rgba(120,150,170,0.6)" strokeWidth={22} fill="none" strokeDasharray="2 9" strokeLinecap="round" />
      {/* head crest */}
      {Array.from({length: 6}).map((_, k) => (
        <line key={k} x1={pts[0][0] - 4} y1={y + 4} x2={pts[0][0] - 10 - k * 6} y2={y - 26 - k * 10 + Math.sin(f / 8 + k) * 4} stroke="#E8433A" strokeWidth={3} />
      ))}
      <circle cx={pts[1][0] + 4} cy={y + 8} r={3.5} fill="#111" />
    </Svg>
  );
};

// Giant siphonophore: glowing spiral of beads with drifting tentacles. `unroll` 0→1 straightens it.
export const Siphonophore: React.FC<P & {unroll?: number; R?: number}> = ({x, y, unroll = 0, R = 210, o = 1}) => {
  const f = useCurrentFrame();
  const N = 260;
  const beads = [];
  const ten = [];
  for (let i = 0; i < N; i++) {
    const t = i / N;
    const ang = t * Math.PI * 2 * 1.05 + f * 0.004;
    const sx = x + Math.cos(ang) * R * (0.7 + 0.3 * t), sy = y + Math.sin(ang) * R * 0.42 * (0.7 + 0.3 * t);
    const lx = x - 520 + t * 1040, ly = y;
    const px = sx + (lx - sx) * unroll, py = sy + (ly - sy) * unroll;
    const glow = 0.5 + 0.5 * Math.sin(f / 6 - i * 0.25);
    beads.push(<circle key={i} cx={px} cy={py} r={4.2} fill={glow > 0.7 ? '#FFD2E0' : '#FF8FB0'} opacity={0.65 + 0.35 * glow} />);
    if (i % 3 === 0) ten.push(<path key={`t${i}`} d={`M${px} ${py} q ${Math.sin(f / 20 + i) * 10} 40 ${Math.sin(f / 25 + i) * 6} ${70 + rnd(i) * 60}`} stroke="rgba(255,170,200,0.28)" strokeWidth={1} fill="none" />);
  }
  return (
    <Svg o={o}>
      <g style={{filter: 'drop-shadow(0 0 6px rgba(255,140,180,0.8))'}}>{beads}</g>
      {ten}
    </Svg>
  );
};

export const BlueWhale: React.FC<{x: number; y: number; len: number; o?: number}> = ({x, y, len, o = 1}) => {
  const f = useCurrentFrame();
  const k = len / 300;
  const sway = Math.sin(f / 14) * 6;
  return (
    <Svg o={o}>
      <g transform={`translate(${x} ${y}) scale(${k})`} fill="rgba(160,190,215,0.55)" stroke="rgba(220,235,245,0.7)" strokeWidth={1.5 / k}>
        <path d={`M0 0 C 40 -28, 180 -30, 255 -8 C 270 -4, 280 ${-14 + sway}, 300 ${-24 + sway} C 296 ${-6 + sway}, 296 ${6 + sway}, 300 ${22 + sway} C 280 ${12 + sway}, 270 6, 255 8 C 180 26, 40 26, 0 0 Z`} />
        <path d="M70 12 C 80 30, 100 34, 112 30" fill="none" />
      </g>
    </Svg>
  );
};

// Greenland shark: slow, heavy swimmer with swaying tail.
export const GreenlandShark: React.FC<P & {len?: number}> = ({x, y, len = 520, o = 1}) => {
  const f = useCurrentFrame();
  const k = len / 500;
  const t = Math.sin(f / 16) * 14;
  return (
    <Svg o={o}>
      <defs>
        <linearGradient id="gs" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0" stopColor="#6E7C86" />
          <stop offset="1" stopColor="#3B464E" />
        </linearGradient>
      </defs>
      <g transform={`translate(${x} ${y}) scale(${k})`}>
        <path d={`M0 0 C 60 -46, 250 -58, 380 -22 L ${470} ${-50 + t} L ${450} ${0 + t * 0.4} L ${478} ${44 + t} L 380 18 C 250 54, 60 46, 0 0 Z`} fill="url(#gs)" />
        <path d="M150 -48 L 175 -82 L 205 -50 Z" fill="#56626B" />
        <path d="M290 -40 L 305 -62 L 322 -36 Z" fill="#56626B" />
        <path d="M120 30 L 160 72 L 175 34 Z" fill="#4A555D" />
        <circle cx={44} cy={-8} r={4} fill="#9FE8E0" opacity={0.8} />
        {Array.from({length: 5}).map((_, i) => <line key={i} x1={90 + i * 9} y1={-14} x2={86 + i * 9} y2={12} stroke="rgba(30,35,40,0.6)" strokeWidth={2} />)}
      </g>
    </Svg>
  );
};

// Colossal squid: mantle, fins, 8 arms + 2 tentacles flowing, huge glowing eye.
export const ColossalSquid: React.FC<P & {len?: number; eyeGlow?: number}> = ({x, y, len = 600, o = 1, eyeGlow = 1}) => {
  const f = useCurrentFrame();
  const k = len / 600;
  const arms = [];
  for (let i = 0; i < 10; i++) {
    const tent = i >= 8;
    const L = tent ? 360 : 230;
    const spread = (i - 4.5) * 9;
    const pts: string[] = [];
    for (let j = 0; j <= 16; j++) {
      const t = j / 16;
      const ax = 200 + t * L;
      const ay = spread * (0.4 + t) + Math.sin(t * 5 - f * 0.09 + i) * 14 * t;
      pts.push(`${j ? 'L' : 'M'}${ax} ${ay}`);
    }
    arms.push(<path key={i} d={pts.join(' ')} stroke={tent ? '#B8433A' : '#C8584A'} strokeWidth={tent ? 5 : 9 - i * 0.3} fill="none" strokeLinecap="round" />);
  }
  return (
    <Svg o={o}>
      <defs>
        <linearGradient id="sq" x1="0" x2="1">
          <stop offset="0" stopColor="#7A1E1A" />
          <stop offset="1" stopColor="#D0614E" />
        </linearGradient>
        <radialGradient id="eye">
          <stop offset="0" stopColor="#FFFFFF" />
          <stop offset="0.35" stopColor="#9FF2FF" />
          <stop offset="1" stopColor="#0B3A4A" />
        </radialGradient>
      </defs>
      <g transform={`translate(${x} ${y}) scale(${k})`}>
        {arms}
        <path d={`M200 -34 C 120 -50, 20 -40, -40 ${-6 + Math.sin(f / 12) * 3} C 20 30, 120 46, 200 34 Z`} fill="url(#sq)" />
        <path d={`M-40 ${-6 + Math.sin(f / 12) * 3} L -78 -48 L -20 -26 Z`} fill="#8A2A22" />
        <path d={`M-40 ${-6 + Math.sin(f / 12) * 3} L -78 40 L -20 18 Z`} fill="#8A2A22" />
        <circle cx={182} cy={-4} r={22} fill="url(#eye)" style={{filter: `drop-shadow(0 0 ${14 * eyeGlow}px #7FF0FF)`}} />
      </g>
    </Svg>
  );
};

// Giant isopod: segmented armoured body, antennae, paddling legs.
export const Isopod: React.FC<P & {len?: number}> = ({x, y, len = 300, o = 1}) => {
  const f = useCurrentFrame();
  const k = len / 300;
  return (
    <Svg o={o}>
      <defs>
        <linearGradient id="iso" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0" stopColor="#E9DCCB" />
          <stop offset="1" stopColor="#A98F78" />
        </linearGradient>
      </defs>
      <g transform={`translate(${x} ${y}) scale(${k})`}>
        {Array.from({length: 7}).map((_, i) => (
          <line key={`l${i}`} x1={-90 + i * 30} y1={40} x2={-96 + i * 30 + Math.sin(f / 4 + i) * 8} y2={70} stroke="#A98F78" strokeWidth={5} strokeLinecap="round" />
        ))}
        <ellipse cx={0} cy={0} rx={150} ry={62} fill="url(#iso)" />
        {Array.from({length: 7}).map((_, i) => (
          <path key={i} d={`M${-100 + i * 30} -58 Q ${-92 + i * 30} 0 ${-100 + i * 30} 58`} stroke="rgba(110,85,65,0.55)" strokeWidth={3} fill="none" />
        ))}
        <path d={`M140 -20 C 200 ${-60 + Math.sin(f / 10) * 8}, 240 -70, 270 -60`} stroke="#C8B29C" strokeWidth={4} fill="none" />
        <path d={`M140 20 C 200 ${60 + Math.sin(f / 11) * 8}, 240 70, 270 62`} stroke="#C8B29C" strokeWidth={4} fill="none" />
        <ellipse cx={128} cy={-30} rx={10} ry={6} fill="#2A2A2A" />
        <ellipse cx={128} cy={30} rx={10} ry={6} fill="#2A2A2A" />
      </g>
    </Svg>
  );
};

// Hadal snailfish: small, pale, translucent, tail fluttering.
export const Snailfish: React.FC<P> = ({x, y, s = 1, o = 1}) => {
  const f = useCurrentFrame();
  const t = Math.sin(f / 5) * 10;
  return (
    <Svg o={o}>
      <g transform={`translate(${x} ${y}) scale(${s})`}>
        <path d={`M0 0 C 20 -34, 90 -30, 140 -6 C 170 ${-4 + t}, 190 ${-10 + t}, 210 ${t} C 190 ${10 + t}, 170 ${6 + t}, 140 8 C 90 30, 20 34, 0 0 Z`} fill="rgba(240,225,235,0.75)" stroke="rgba(255,240,250,0.9)" strokeWidth={1.5} />
        <path d={`M40 -24 C 80 -40, 140 -26, ${200} ${-4 + t}`} stroke="rgba(255,240,250,0.45)" strokeWidth={6} fill="none" />
        <circle cx={22} cy={-6} r={5} fill="#3A2A33" />
      </g>
    </Svg>
  );
};

// Shrimp-like amphipod.
export const Amphipod: React.FC<P> = ({x, y, s = 1, o = 1}) => {
  const f = useCurrentFrame();
  return (
    <Svg o={o}>
      <g transform={`translate(${x} ${y}) scale(${s})`}>
        <path d="M0 0 C 10 -14, 40 -16, 56 -4 C 50 6, 20 10, 0 0 Z" fill="#F2E6D8" />
        {Array.from({length: 5}).map((_, i) => <line key={i} x1={12 + i * 8} y1={4} x2={10 + i * 8 + Math.sin(f / 3 + i) * 3} y2={14} stroke="#E8D8C8" strokeWidth={1.5} />)}
        <path d={`M0 -2 C -10 -14, -20 -16, -28 ${-12 + Math.sin(f / 6) * 3}`} stroke="#E8D8C8" strokeWidth={1.2} fill="none" />
      </g>
    </Svg>
  );
};

export const ROVLight: React.FC<{x: number; y: number; ang?: number; o?: number}> = ({x, y, ang = 20, o = 1}) => (
  <div
    style={{
      position: 'absolute', left: x, top: y - 160, width: 900, height: 320, transformOrigin: '0 50%', transform: `rotate(${ang}deg)`, opacity: o,
      background: 'linear-gradient(90deg, rgba(220,245,255,0.55), rgba(180,230,255,0.15) 50%, transparent)', clipPath: 'polygon(0 46%, 100% 0, 100% 100%, 0 54%)', filter: 'blur(4px)',
    }}
  />
);

export const Glow: React.FC<{x: number; y: number; r: number; color?: string; o?: number}> = ({x, y, r, color = 'rgba(92,242,224,0.35)', o = 1}) => (
  <div style={{position: 'absolute', left: x - r, top: y - r, width: r * 2, height: r * 2, borderRadius: '50%', background: `radial-gradient(circle, ${color}, transparent 70%)`, opacity: o}} />
);

export {C};

// Bioluminescent jellyfish: pulsing bell, glowing rim, trailing tentacles.
export const Jelly: React.FC<P & {hue?: string}> = ({x, y, s = 1, o = 1, hue = '#7FF0FF'}) => {
  const f = useCurrentFrame();
  const p = Math.sin(f / 9 + x);
  const w = 60 * s * (1 + 0.12 * p), h = 46 * s * (1 - 0.1 * p);
  return (
    <Svg o={o}>
      <g style={{filter: `drop-shadow(0 0 10px ${hue})`}}>
        <path d={`M${x - w} ${y} Q ${x - w} ${y - h * 1.6} ${x} ${y - h * 1.6} Q ${x + w} ${y - h * 1.6} ${x + w} ${y} Q ${x} ${y - h * 0.3} ${x - w} ${y} Z`} fill={`${hue}33`} stroke={hue} strokeWidth={1.5} />
        {Array.from({length: 7}).map((_, i) => {
          const tx = x - w * 0.8 + (i / 6) * w * 1.6;
          return <path key={i} d={`M${tx} ${y - 4} q ${Math.sin(f / 12 + i) * 12 * s} ${60 * s} ${Math.sin(f / 15 + i * 2) * 8 * s} ${130 * s}`} stroke={hue} strokeWidth={1} fill="none" opacity={0.55} />;
        })}
      </g>
    </Svg>
  );
};
