import React, { useMemo } from "react";
import { AbsoluteFill, interpolate, useCurrentFrame } from "remotion";
import { BODY, C, FPS, HEAD as HEADFONT } from "../lib/theme";
import { HEAD, SceneId, Word, words } from "../lib/timeline";
import { pop, ramp } from "../lib/anim";

type Group = { words: Word[]; s: number; e: number };

const groupWords = (ws: Word[]): Group[] => {
  const out: Group[] = [];
  let cur: Word[] = [];
  const flush = () => {
    if (cur.length) out.push({ words: cur, s: cur[0].s, e: cur[cur.length - 1].e });
    cur = [];
  };
  ws.forEach((w, i) => {
    cur.push(w);
    const punct = /[.,?!;:]$/.test(w.w);
    const gap = i + 1 < ws.length ? ws[i + 1].s - w.e : 1;
    const chars = cur.map((x) => x.w).join(" ").length;
    if (punct || gap > 0.35 || cur.length >= 4 || chars > 22) flush();
  });
  flush();
  return out;
};

/** Kinetic word-by-word captions, synced to the narrator's word timings. */
export const Captions: React.FC<{ id: SceneId; bottom?: number }> = ({ id, bottom = 120 }) => {
  const f = useCurrentFrame();
  const groups = useMemo(() => groupWords(words(id)), [id]);
  const t = (f - HEAD) / FPS;
  const gi = groups.findIndex((g, i) => t >= g.s - 0.05 && (i + 1 >= groups.length || t < groups[i + 1].s - 0.05) && t < g.e + 0.6);
  if (gi < 0) return null;
  const g = groups[gi];
  const enter = pop(f, HEAD + Math.round((g.s - 0.05) * FPS), 15);
  return (
    <AbsoluteFill style={{ justifyContent: "flex-end", alignItems: "center", paddingBottom: bottom, pointerEvents: "none" }}>
      <div
        style={{
          fontFamily: HEADFONT,
          fontSize: 76,
          textTransform: "uppercase",
          letterSpacing: 1,
          color: "#fff",
          textAlign: "center",
          maxWidth: 1500,
          scale: String(0.92 + 0.08 * enter),
          WebkitTextStroke: "3px rgba(0,0,0,0.85)",
          paintOrder: "stroke fill",
          textShadow: "0 6px 0 rgba(0,0,0,0.55), 0 0 30px rgba(0,0,0,0.6)",
        }}
      >
        {g.words.map((w, i) => {
          const active = t >= w.s - 0.03;
          const cur = active && (i + 1 >= g.words.length || t < g.words[i + 1].s - 0.03);
          return (
            <span
              key={i}
              style={{
                display: "inline-block",
                margin: "0 14px",
                color: cur ? C.gold : active ? "#fff" : "rgba(255,255,255,0.55)",
                scale: cur ? "1.08" : "1",
              }}
            >
              {w.w}
            </span>
          );
        })}
      </div>
    </AbsoluteFill>
  );
};

/** Persistent top HUD: brand tag + fact countdown pips. */
export const Hud: React.FC<{ n?: number; label?: string }> = ({ n, label }) => {
  const f = useCurrentFrame();
  const show = ramp(f, 30, 15);
  return (
    <AbsoluteFill style={{ pointerEvents: "none" }}>
      <div style={{ position: "absolute", top: 54, left: 70, display: "flex", alignItems: "center", gap: 18, opacity: show }}>
        {n !== undefined && (
          <div style={{ fontFamily: HEADFONT, fontSize: 64, color: "#fff", background: C.red, padding: "2px 26px", borderRadius: 16, boxShadow: "0 10px 30px rgba(0,0,0,.4)" }}>
            #{n}
          </div>
        )}
        <div style={{ fontFamily: BODY, fontWeight: 900, fontSize: 30, color: "#fff", letterSpacing: 4, textShadow: "0 3px 12px rgba(0,0,0,.8)" }}>
          {label ?? "USA FACTS THAT SOUND FAKE"}
        </div>
      </div>
      {n !== undefined && (
        <div style={{ position: "absolute", top: 70, right: 80, display: "flex", gap: 10, opacity: show }}>
          {Array.from({ length: 10 }, (_, i) => 10 - i).map((k) => (
            <div
              key={k}
              style={{
                width: 34,
                height: 34,
                borderRadius: 9,
                fontFamily: BODY,
                fontWeight: 900,
                fontSize: 17,
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                color: k === n ? "#fff" : k > n ? "rgba(255,255,255,.75)" : "rgba(255,255,255,.35)",
                background: k === n ? C.red : k > n ? "rgba(255,255,255,.18)" : "rgba(0,0,0,.35)",
                border: "2px solid rgba(255,255,255,.15)",
                scale: k === n ? String(1 + 0.15 * Math.sin(f / 8)) : "1",
              }}
            >
              {k}
            </div>
          ))}
        </div>
      )}
    </AbsoluteFill>
  );
};

/** Thin global progress bar along the bottom edge. */
export const ProgressBar: React.FC<{ total: number }> = ({ total }) => {
  const f = useCurrentFrame();
  return (
    <AbsoluteFill style={{ justifyContent: "flex-end", pointerEvents: "none" }}>
      <div style={{ height: 8, background: "rgba(255,255,255,.12)" }}>
        <div style={{ height: 8, width: `${interpolate(f, [0, total], [0, 100])}%`, background: `linear-gradient(90deg, ${C.red}, ${C.gold})` }} />
      </div>
    </AbsoluteFill>
  );
};

/** Film grain + subtle light leak to give the edit a premium texture. */
export const Grain: React.FC = () => {
  const f = useCurrentFrame();
  const x = (f * 37) % 200;
  const y = (f * 53) % 200;
  return (
    <AbsoluteFill style={{ pointerEvents: "none", mixBlendMode: "overlay", opacity: 0.18 }}>
      <svg width="100%" height="100%">
        <filter id="grain">
          <feTurbulence type="fractalNoise" baseFrequency="0.9" numOctaves="2" seed={f % 30} />
        </filter>
        <rect x={-x} y={-y} width="120%" height="120%" filter="url(#grain)" />
      </svg>
    </AbsoluteFill>
  );
};
