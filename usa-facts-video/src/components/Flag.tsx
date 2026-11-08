import React from "react";
import { useCurrentFrame } from "remotion";
import { pop, ramp } from "../lib/anim";

const starPath = (cx: number, cy: number, r: number) => {
  let d = "";
  for (let i = 0; i < 10; i++) {
    const rr = i % 2 === 0 ? r : r * 0.4;
    const a = -Math.PI / 2 + (i * Math.PI) / 5;
    d += `${i === 0 ? "M" : "L"}${cx + rr * Math.cos(a)},${cy + rr * Math.sin(a)}`;
  }
  return d + "Z";
};

/** 50-star flag that builds itself: stripes wipe in from `at`, stars pop one by one from `starsAt`. */
export const Flag50: React.FC<{ width: number; at: number; starsAt: number; starsDur?: number }> = ({ width, at, starsAt, starsDur = 50 }) => {
  const f = useCurrentFrame();
  const h = (width * 10) / 19;
  const sh = h / 13;
  const cw = width * 0.4;
  const ch = sh * 7;
  const stars: [number, number][] = [];
  for (let row = 0; row < 9; row++) {
    const n = row % 2 === 0 ? 6 : 5;
    for (let k = 0; k < n; k++) {
      const x = row % 2 === 0 ? cw / 12 + (k * cw) / 6 : cw / 6 + (k * cw) / 6;
      const y = ch / 10 + (row * ch) / 10;
      stars.push([x, y]);
    }
  }
  return (
    <svg width={width} height={h} viewBox={`0 0 ${width} ${h}`} style={{ filter: "drop-shadow(0 25px 50px rgba(0,0,0,.5))" }}>
      <rect width={width} height={h} fill="#f4f1ea" opacity={ramp(f, at, 8)} />
      {Array.from({ length: 13 }, (_, i) =>
        i % 2 === 0 ? <rect key={i} x={0} y={i * sh} width={width * ramp(f, at + i * 2, 18)} height={sh} fill="#b22234" /> : null,
      )}
      <rect width={cw} height={ch} fill="#3c3b6e" opacity={ramp(f, at + 10, 12)} />
      {stars.map(([x, y], i) => {
        const p = pop(f, starsAt + (i * starsDur) / 50, 10);
        return <path key={i} d={starPath(x, y, (cw / 12) * 0.62 * p)} fill="#fff" />;
      })}
    </svg>
  );
};
