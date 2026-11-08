import React from "react";
import { AbsoluteFill, Img, Sequence, interpolate, staticFile, useCurrentFrame } from "remotion";
import { Audio } from "@remotion/media";
import { BODY, C, FPS, HEAD as HEADFONT } from "../lib/theme";
import { EASE, lerp, pop, ramp } from "../lib/anim";

/* ---------- Photo with Ken Burns move + grade + vignette ---------- */
export const Photo: React.FC<{
  src: string;
  from?: number;
  dur: number;
  zoom?: [number, number];
  pan?: [string, string];
  filter?: string;
  dim?: number;
  origin?: string;
}> = ({ src, from = 0, dur, zoom = [1.05, 1.18], pan = ["0px 0px", "-40px -10px"], filter, dim = 0.35, origin = "50% 50%" }) => {
  const f = useCurrentFrame();
  const t = (f - from) / Math.max(1, dur);
  return (
    <AbsoluteFill style={{ overflow: "hidden", backgroundColor: C.bg }}>
      <Img
        src={staticFile(`img/${src}`)}
        style={{
          width: "100%",
          height: "100%",
          objectFit: "cover",
          scale: String(interpolate(t, [0, 1], zoom, { extrapolateLeft: "clamp", extrapolateRight: "clamp" })),
          translate: lerpPan(pan, t),
          transformOrigin: origin,
          filter,
        }}
      />
      <AbsoluteFill
        style={{
          background: `radial-gradient(ellipse at center, rgba(0,0,0,0) 45%, rgba(5,8,16,${0.55 + dim * 0.4}) 100%), linear-gradient(rgba(5,8,16,${dim * 0.6}), rgba(5,8,16,${dim}))`,
        }}
      />
    </AbsoluteFill>
  );
};
const lerpPan = (pan: [string, string], t: number) => {
  const a = pan[0].split(" ").map(parseFloat);
  const b = pan[1].split(" ").map(parseFloat);
  const k = Math.min(1, Math.max(0, t));
  return `${a[0] + (b[0] - a[0]) * k}px ${a[1] + (b[1] - a[1]) * k}px`;
};

/* ---------- Headline: words rise in with stagger; *word* = highlight ---------- */
export const Headline: React.FC<{
  text: string;
  at: number;
  size?: number;
  color?: string;
  hi?: string;
  align?: "center" | "left";
  stagger?: number;
  style?: React.CSSProperties;
  out?: number;
}> = ({ text, at, size = 110, color = C.ink, hi = C.gold, align = "center", stagger = 3, style, out }) => {
  const f = useCurrentFrame();
  const words = text.split(" ");
  const o = out === undefined ? 1 : interpolate(f, [out - 8, out], [1, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  return (
    <div
      style={{
        fontFamily: HEADFONT,
        fontSize: size,
        lineHeight: 1.02,
        textTransform: "uppercase",
        color,
        textAlign: align,
        letterSpacing: 1,
        opacity: o,
        textShadow: "0 6px 30px rgba(0,0,0,0.65)",
        ...style,
      }}
    >
      {(() => {
        let on = false;
        return words.map((w, i) => {
          const p = pop(f, at + i * stagger, 14);
          const starts = w.startsWith("*");
          const ends = w.endsWith("*") && (w.length > 1 || !starts);
          if (starts) on = true;
          const isHi = on;
          if (ends) on = false;
          const clean = w.replace(/\*/g, "");
          return (
            <span
              key={i}
              style={{
                display: "inline-block",
                marginRight: size * 0.22,
                opacity: Math.min(1, p * 1.4),
                translate: `0px ${(1 - p) * size * 0.6}px`,
                color: isHi ? hi : undefined,
              }}
            >
              {clean}
            </span>
          );
        });
      })()}
    </div>
  );
};

/* ---------- Small label chip ---------- */
export const Chip: React.FC<{ children: React.ReactNode; at: number; color?: string; style?: React.CSSProperties; size?: number }> = ({
  children, at, color = C.red, style, size = 40,
}) => {
  const f = useCurrentFrame();
  const p = pop(f, at, 13);
  return (
    <div
      style={{
        display: "inline-flex",
        alignItems: "center",
        gap: 14,
        padding: `${size * 0.3}px ${size * 0.6}px`,
        background: color,
        color: "#fff",
        borderRadius: size * 0.35,
        fontFamily: BODY,
        fontWeight: 900,
        fontSize: size,
        letterSpacing: 1,
        textTransform: "uppercase",
        boxShadow: "0 12px 40px rgba(0,0,0,0.45)",
        scale: String(p),
        opacity: Math.min(1, p * 2),
        ...style,
      }}
    >
      {children}
    </div>
  );
};

/* ---------- Rubber stamp ---------- */
export const Stamp: React.FC<{ text: string; at: number; color?: string; rotate?: number; size?: number; style?: React.CSSProperties }> = ({
  text, at, color = C.red, rotate = -12, size = 120, style,
}) => {
  const f = useCurrentFrame();
  const p = pop(f, at, 9);
  if (f < at) return null;
  return (
    <div
      style={{
        fontFamily: HEADFONT,
        fontSize: size,
        color,
        border: `${size * 0.08}px solid ${color}`,
        borderRadius: size * 0.15,
        padding: `${size * 0.05}px ${size * 0.25}px`,
        rotate: `${rotate}deg`,
        scale: String(interpolate(p, [0, 1], [2.4, 1])),
        opacity: Math.min(1, p * 1.5),
        textTransform: "uppercase",
        background: "rgba(10,15,28,0.35)",
        ...style,
      }}
    >
      {text}
    </div>
  );
};

/* ---------- Animated number counter ---------- */
export const Counter: React.FC<{
  from: number; to: number; at: number; dur?: number; decimals?: number; prefix?: string; suffix?: string;
  size?: number; color?: string; comma?: boolean; style?: React.CSSProperties;
}> = ({ from, to, at, dur = 30, decimals = 0, prefix = "", suffix = "", size = 200, color = C.ink, comma = true, style }) => {
  const f = useCurrentFrame();
  const v = from + (to - from) * ramp(f, at, dur, EASE);
  const s = v.toFixed(decimals);
  const txt = comma ? Number(s).toLocaleString("en-US", { minimumFractionDigits: decimals, maximumFractionDigits: decimals }) : s;
  return (
    <div style={{ fontFamily: HEADFONT, fontSize: size, color, lineHeight: 1, opacity: ramp(f, at, 8), textShadow: "0 8px 40px rgba(0,0,0,.6)", fontVariantNumeric: "tabular-nums", ...style }}>
      {prefix}
      {txt}
      {suffix}
    </div>
  );
};

/* ---------- Sound effect at a frame ---------- */
export const Sfx: React.FC<{ src: string; at: number; volume?: number }> = ({ src, at, volume = 0.5 }) => (
  <Sequence from={Math.max(0, at)} durationInFrames={3 * FPS} layout="none">
    <Audio src={staticFile(`audio/${src}`)} volume={volume} />
  </Sequence>
);

/* ---------- Panel / card ---------- */
export const Panel: React.FC<{ at: number; children: React.ReactNode; style?: React.CSSProperties; from?: "up" | "left" | "right" }> = ({
  at, children, style, from = "up",
}) => {
  const f = useCurrentFrame();
  const p = pop(f, at, 16);
  const d = (1 - p) * 120;
  const tr = from === "up" ? `0px ${d}px` : from === "left" ? `${-d}px 0px` : `${d}px 0px`;
  return (
    <div
      style={{
        background: "rgba(14,22,40,0.82)",
        border: "2px solid rgba(255,255,255,0.12)",
        borderRadius: 28,
        padding: 40,
        boxShadow: "0 30px 80px rgba(0,0,0,0.5)",
        backdropFilter: "blur(6px)",
        opacity: Math.min(1, p * 1.6),
        translate: tr,
        ...style,
      }}
    >
      {children}
    </div>
  );
};

/* ---------- Big number stinger ("NUMBER 7") ---------- */
export const Stinger: React.FC<{ n: number; dur?: number }> = ({ n, dur = 40 }) => {
  const f = useCurrentFrame();
  if (f > dur + 12) return null;
  const p = pop(f, 2, 10);
  const out = interpolate(f, [dur, dur + 12], [1, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const ring = ramp(f, 0, 28);
  return (
    <AbsoluteFill style={{ justifyContent: "center", alignItems: "center", opacity: out, background: `rgba(5,8,16,${0.7 * out})` }}>
      <div
        style={{
          position: "absolute",
          width: 900,
          height: 900,
          borderRadius: "50%",
          border: `10px solid ${C.red}`,
          scale: String(0.3 + ring * 1.1),
          opacity: 1 - ring,
        }}
      />
      <div style={{ fontFamily: BODY, fontWeight: 900, color: C.gold, fontSize: 54, letterSpacing: 18, marginBottom: -20, opacity: ramp(f, 4, 10) }}>
        FACT
      </div>
      <div
        style={{
          fontFamily: HEADFONT,
          fontSize: 420,
          lineHeight: 1,
          color: "#fff",
          scale: String(interpolate(p, [0, 1], [1.8, 1])),
          opacity: Math.min(1, p * 2),
          textShadow: `0 0 60px ${C.red}, 0 20px 60px rgba(0,0,0,.7)`,
        }}
      >
        #{n}
      </div>
    </AbsoluteFill>
  );
};

/* ---------- Simple line "draw-on" arrow (SVG) ---------- */
export const DrawPath: React.FC<{ d: string; at: number; dur?: number; color?: string; width?: number; dash?: boolean; len?: number; head?: boolean }> = ({
  d, at, dur = 25, color = C.gold, width = 8, dash = false, len = 3000, head = false,
}) => {
  const f = useCurrentFrame();
  const p = ramp(f, at, dur, EASE);
  return (
    <g>
      <path
        d={d}
        fill="none"
        stroke={color}
        strokeWidth={width}
        strokeLinecap="round"
        strokeDasharray={dash ? undefined : `${len}`}
        strokeDashoffset={dash ? undefined : len * (1 - p)}
        style={dash ? { strokeDasharray: "18 14", opacity: p } : undefined}
        markerEnd={head && p > 0.95 ? "url(#arrowhead)" : undefined}
      />
    </g>
  );
};

export const ArrowDefs: React.FC<{ color?: string }> = ({ color = C.gold }) => (
  <defs>
    <marker id="arrowhead" markerWidth="6" markerHeight="6" refX="3" refY="3" orient="auto">
      <path d="M0,0 L6,3 L0,6 z" fill={color} />
    </marker>
  </defs>
);

/* ---------- Copper penny graphic ---------- */
export const Penny: React.FC<{ size?: number; at: number; spin?: boolean; style?: React.CSSProperties; label?: string }> = ({
  size = 320, at, spin = true, style, label = "1¢",
}) => {
  const f = useCurrentFrame();
  const p = pop(f, at, 12);
  const rot = spin ? lerp(f, [at, at + 30], [540, 0]) : 0;
  return (
    <div style={{ perspective: 1200, ...style }}>
      <div
        style={{
          width: size,
          height: size,
          borderRadius: "50%",
          background: "radial-gradient(circle at 35% 30%, #ffc9a0 0%, #d98a4e 25%, #a8562a 60%, #6b3115 100%)",
          boxShadow: `inset 0 0 0 ${size * 0.04}px #8a4420, inset 0 0 ${size * 0.08}px rgba(0,0,0,.5), 0 20px 50px rgba(0,0,0,.55)`,
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          flexDirection: "column",
          rotate: `y ${rot}deg`,
          scale: String(p),
          opacity: Math.min(1, p * 2),
        }}
      >
        <div style={{ fontFamily: BODY, fontWeight: 900, color: "rgba(60,22,6,.75)", fontSize: size * 0.09, letterSpacing: size * 0.02 }}>LIBERTY</div>
        <div style={{ fontFamily: HEADFONT, color: "rgba(60,22,6,.85)", fontSize: size * 0.36, lineHeight: 1 }}>{label}</div>
        <div style={{ fontFamily: BODY, fontWeight: 900, color: "rgba(60,22,6,.75)", fontSize: size * 0.07 }}>UNITED STATES</div>
      </div>
    </div>
  );
};

export const Center: React.FC<{ children: React.ReactNode; style?: React.CSSProperties }> = ({ children, style }) => (
  <AbsoluteFill style={{ justifyContent: "center", alignItems: "center", ...style }}>{children}</AbsoluteFill>
);

/* Fade a whole layer in/out between two frames. */
export const Layer: React.FC<{ a: number; b: number; children: React.ReactNode; fade?: number; style?: React.CSSProperties }> = ({
  a, b, children, fade = 10, style,
}) => {
  const f = useCurrentFrame();
  if (f < a - 1 || f > b + 1) return null;
  const o = interpolate(f, [a, a + fade, b - fade, b], [0, 1, 1, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  return <AbsoluteFill style={{ opacity: o, ...style }}>{children}</AbsoluteFill>;
};
