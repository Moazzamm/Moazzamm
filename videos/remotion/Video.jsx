import React, { useEffect, useState } from "react";
import { AbsoluteFill, OffthreadVideo, Sequence, staticFile, useCurrentFrame, useVideoConfig,
  interpolate, spring, Easing, delayRender, continueRender } from "remotion";

const ANTON = "Anton, Impact, sans-serif";
const INTER = "Inter, Arial, sans-serif";
const clamp = { extrapolateLeft: "clamp", extrapolateRight: "clamp" };

const useFonts = () => {
  const [h] = useState(() => delayRender("fonts"));
  useEffect(() => {
    Promise.all([document.fonts.load("100px Anton"), document.fonts.load("800 60px Inter"),
      document.fonts.load("900 60px Inter"), document.fonts.load("600 40px Inter")])
      .then(() => document.fonts.ready).then(() => continueRender(h));
  }, [h]);
};

// ---------- B-roll shot with Ken Burns + section punch-in ----------
const Shot = ({ s }) => {
  const fr = useCurrentFrame();
  const p = fr / Math.max(1, s.dur);
  let z = s.zin ? interpolate(p, [0, 1], [1.04, 1.13]) : interpolate(p, [0, 1], [1.13, 1.04]);
  if (s.punch) z *= interpolate(fr, [0, 12], [1.22, 1], { ...clamp, easing: Easing.out(Easing.cubic) });
  const x = s.zin ? interpolate(p, [0, 1], [-14, 14]) : interpolate(p, [0, 1], [12, -12]);
  return (
    <AbsoluteFill style={{ overflow: "hidden", backgroundColor: "#000" }}>
      <OffthreadVideo src={staticFile(s.src)} startFrom={s.offset} playbackRate={s.rate} muted
        style={{ width: "100%", height: "100%", objectFit: "cover", transform: `scale(${z}) translateX(${x}px)`,
          filter: "contrast(1.07) saturate(1.12) brightness(0.97)" }} />
    </AbsoluteFill>
  );
};

const Grade = () => (
  <AbsoluteFill style={{ pointerEvents: "none" }}>
    <AbsoluteFill style={{ background: "radial-gradient(ellipse at center, rgba(0,0,0,0) 45%, rgba(0,0,0,0.62) 100%)" }} />
    <AbsoluteFill style={{ background: "linear-gradient(to top, rgba(0,0,0,0.62) 0%, rgba(0,0,0,0) 32%)" }} />
    <AbsoluteFill style={{ background: "linear-gradient(to bottom, rgba(0,0,0,0.35) 0%, rgba(0,0,0,0) 18%)" }} />
  </AbsoluteFill>
);

const Flash = () => {
  const fr = useCurrentFrame();
  const o = interpolate(fr, [0, 2, 9], [0, 0.55, 0], clamp);
  return <AbsoluteFill style={{ backgroundColor: "#fff", opacity: o, mixBlendMode: "screen" }} />;
};

// ---------- Kinetic captions ----------
const Caption = ({ c, accent }) => {
  const fr = useCurrentFrame();
  const { fps } = useVideoConfig();
  const sc = spring({ frame: fr, fps, config: { damping: 14, stiffness: 220, mass: 0.6 } });
  const out = interpolate(fr, [c.dur - 3, c.dur], [1, 0], clamp);
  return (
    <AbsoluteFill style={{ justifyContent: "flex-end", alignItems: "center", paddingBottom: 92 }}>
      <div style={{ display: "flex", flexWrap: "wrap", justifyContent: "center", maxWidth: 1500, gap: "0 20px",
        transform: `scale(${0.86 + 0.14 * sc}) translateY(${(1 - sc) * 16}px)`, opacity: out }}>
        {c.words.map((w, i) => {
          const on = fr >= w.at && (i === c.words.length - 1 || fr < c.words[i + 1].at);
          const seen = fr >= w.at;
          return (
            <span key={i} style={{ fontFamily: INTER, fontWeight: 900, fontSize: 66, letterSpacing: 0.5, lineHeight: 1.12,
              color: on ? accent : "#fff", opacity: seen ? 1 : 0.55, transform: `scale(${on ? 1.08 : 1})`, display: "inline-block",
              textShadow: "0 0 3px #000, 0 4px 0 rgba(0,0,0,0.85), 0 8px 28px rgba(0,0,0,0.85)" }}>{w.w}</span>
          );
        })}
      </div>
    </AbsoluteFill>
  );
};

// ---------- Fact title card ----------
const Card = ({ c, accent, accent2 }) => {
  const fr = useCurrentFrame();
  const { fps } = useVideoConfig();
  const inN = spring({ frame: fr - 2, fps, config: { damping: 12, stiffness: 160 } });
  const bar = spring({ frame: fr - 6, fps, config: { damping: 18, stiffness: 120 } });
  const exit = interpolate(fr, [c.dur - 10, c.dur], [0, 1], { ...clamp, easing: Easing.in(Easing.cubic) });
  const dim = interpolate(fr, [0, 6, c.dur - 8, c.dur], [0, 0.72, 0.72, 0], clamp);
  const words = c.head.split(" ");
  const shake = fr < 10 ? Math.sin(fr * 3.1) * (10 - fr) * 0.9 : 0;
  return (
    <AbsoluteFill>
      <AbsoluteFill style={{ background: "radial-gradient(ellipse at 30% 50%, rgba(0,0,0,0.55), rgba(0,0,0,0.95))", opacity: dim }} />
      <AbsoluteFill style={{ flexDirection: "row", alignItems: "center", paddingLeft: 150,
        transform: `translate(${shake}px, ${-exit * 60}px)`, opacity: 1 - exit }}>
        <div style={{ display: "flex", flexDirection: "column", alignItems: "flex-start",
          transform: `translateX(${(1 - inN) * -220}px) scale(${0.7 + 0.3 * inN})`, filter: `blur(${(1 - inN) * 14}px)` }}>
          <div style={{ fontFamily: INTER, fontWeight: 900, fontSize: 44, letterSpacing: 14, color: "#fff", opacity: 0.9, marginBottom: -18 }}>FACT</div>
          <div style={{ fontFamily: ANTON, fontSize: 330, lineHeight: 1, color: accent,
            textShadow: `0 0 60px ${accent}88, 0 12px 0 rgba(0,0,0,0.6)` }}>
            <span style={{ fontSize: 170, verticalAlign: "top", color: "#fff", opacity: 0.9 }}>#</span>{c.num}
          </div>
        </div>
        <div style={{ width: 10, height: 330 * bar, background: accent2, margin: "0 58px", borderRadius: 6, boxShadow: `0 0 30px ${accent2}` }} />
        <div style={{ display: "flex", flexWrap: "wrap", maxWidth: 1020, gap: "0 26px" }}>
          {words.map((w, i) => {
            const p = spring({ frame: fr - 8 - i * 3, fps, config: { damping: 15, stiffness: 180 } });
            return (
              <div key={i} style={{ overflow: "hidden", paddingBottom: 6 }}>
                <div style={{ fontFamily: ANTON, fontSize: 112, lineHeight: 1.05, color: "#fff",
                  transform: `translateY(${(1 - p) * 120}%)`, textShadow: "0 8px 30px rgba(0,0,0,0.7)" }}>{w}</div>
              </div>
            );
          })}
        </div>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};

// ---------- Big stat callout with count-up ----------
const parseVal = (v) => {
  const m = v.match(/^([^0-9]*)([0-9][0-9,]*(?:\.[0-9]+)?)(.*)$/);
  if (!m) return null;
  return { pre: m[1], num: parseFloat(m[2].replace(/,/g, "")), dec: (m[2].split(".")[1] || "").length, comma: m[2].includes(","), post: m[3] };
};
const fmt = (n, dec, comma) => {
  const s = n.toFixed(dec);
  if (!comma) return s;
  const [a, b] = s.split(".");
  return a.replace(/\B(?=(\d{3})+(?!\d))/g, ",") + (b ? "." + b : "");
};
const Stat = ({ s, accent, accent2 }) => {
  const fr = useCurrentFrame();
  const { fps } = useVideoConfig();
  const pop = spring({ frame: fr, fps, config: { damping: 11, stiffness: 170, mass: 0.7 } });
  const lab = spring({ frame: fr - 7, fps, config: { damping: 16, stiffness: 140 } });
  const out = interpolate(fr, [s.dur - 8, s.dur], [1, 0], clamp);
  const pv = parseVal(s.value);
  const cnt = interpolate(fr, [0, 22], [0, 1], { ...clamp, easing: Easing.out(Easing.cubic) });
  let text = s.value;
  if (pv && !/^1-3/.test(s.value) && !/^pH/.test(s.value)) text = pv.pre + fmt(pv.num * cnt, pv.dec, pv.comma) + pv.post;
  const size = text.length > 9 ? 150 : 200;
  return (
    <AbsoluteFill style={{ justifyContent: "center", alignItems: "center", paddingBottom: 150, opacity: out }}>
      <AbsoluteFill style={{ background: "radial-gradient(ellipse at 50% 42%, rgba(0,0,0,0.6), rgba(0,0,0,0) 60%)", opacity: pop }} />
      <div style={{ fontFamily: ANTON, fontSize: size, lineHeight: 1, color: "#fff", letterSpacing: 2,
        transform: `scale(${0.55 + 0.45 * pop})`, filter: `blur(${(1 - Math.min(1, pop)) * 10}px)`,
        textShadow: `0 0 50px ${accent}aa, 0 10px 0 rgba(0,0,0,0.55)` }}>{text}</div>
      <div style={{ marginTop: 22, padding: "12px 30px", background: accent, borderRadius: 10,
        fontFamily: INTER, fontWeight: 900, fontSize: 38, letterSpacing: 3, color: "#0b0b0f", textTransform: "uppercase",
        transform: `translateY(${(1 - lab) * 40}px)`, opacity: lab, boxShadow: `0 10px 40px ${accent}66` }}>{s.label}</div>
    </AbsoluteFill>
  );
};

// ---------- Intro title slam ----------
const Intro = ({ it, accent, accent2 }) => {
  const fr = useCurrentFrame();
  const { fps } = useVideoConfig();
  const a = spring({ frame: fr, fps, config: { damping: 12, stiffness: 200 } });
  const b = spring({ frame: fr - 7, fps, config: { damping: 12, stiffness: 200 } });
  const c = spring({ frame: fr - 16, fps, config: { damping: 14, stiffness: 160 } });
  const out = interpolate(fr, [it.dur - 8, it.dur], [1, 0], clamp);
  const shake = fr < 12 ? Math.sin(fr * 2.7) * (12 - fr) * 1.2 : 0;
  const L = (p, extra) => ({ transform: `scale(${2 - p}) translateX(${shake}px)`, opacity: Math.min(1, p * 1.4), filter: `blur(${(1 - Math.min(1, p)) * 16}px)`, ...extra });
  return (
    <AbsoluteFill style={{ justifyContent: "center", alignItems: "center", opacity: out }}>
      <AbsoluteFill style={{ background: "rgba(0,0,0,0.62)", opacity: a }} />
      <div style={L(a, { fontFamily: ANTON, fontSize: 132, color: "#fff", lineHeight: 1.02, textShadow: "0 10px 40px rgba(0,0,0,0.8)" })}>{it.lines[0]}</div>
      <div style={L(b, { fontFamily: ANTON, fontSize: 176, color: accent, lineHeight: 1.02, textShadow: `0 0 70px ${accent}99` })}>{it.lines[1]}</div>
      <div style={{ marginTop: 26, padding: "10px 34px", border: `4px solid ${accent2}`, borderRadius: 12, fontFamily: INTER, fontWeight: 900,
        fontSize: 52, letterSpacing: 4, color: accent2, transform: `scale(${0.6 + 0.4 * c})`, opacity: c }}>(BUT ARE 100% TRUE)</div>
    </AbsoluteFill>
  );
};

// ---------- Countdown tracker (top-right) ----------
const Tracker = ({ tracker, total, accent }) => {
  const fr = useCurrentFrame();
  if (!tracker.length || fr < tracker[0].from + 70) return null;
  let cur = tracker[0].num;
  tracker.forEach((t) => { if (fr >= t.from) cur = t.num; });
  const done = total - cur + 1;
  return (
    <div style={{ position: "absolute", top: 46, right: 56, display: "flex", alignItems: "center", gap: 16, opacity: 0.92 }}>
      <div style={{ fontFamily: INTER, fontWeight: 900, fontSize: 26, letterSpacing: 4, color: "#fff", textShadow: "0 2px 10px #000" }}>
        FACT <span style={{ color: accent }}>#{cur}</span>
      </div>
      <div style={{ display: "flex", gap: 5 }}>
        {Array.from({ length: total }).map((_, i) => (
          <div key={i} style={{ width: 16, height: 6, borderRadius: 3, background: i < done ? accent : "rgba(255,255,255,0.35)",
            boxShadow: i < done ? `0 0 10px ${accent}` : "none" }} />
        ))}
      </div>
    </div>
  );
};

// ---------- Comment prompt ----------
const Comment = ({ c, accent }) => {
  const fr = useCurrentFrame();
  const { fps } = useVideoConfig();
  const p = spring({ frame: fr, fps, config: { damping: 12, stiffness: 160 } });
  const out = interpolate(fr, [c.dur - 8, c.dur], [1, 0], clamp);
  const bob = Math.sin(fr / 5) * 8;
  return (
    <AbsoluteFill style={{ alignItems: "center", paddingTop: 120, opacity: out }}>
      <div style={{ display: "flex", alignItems: "center", gap: 22, padding: "20px 38px", borderRadius: 60, background: "rgba(10,10,14,0.82)",
        border: `3px solid ${accent}`, transform: `scale(${p})`, boxShadow: `0 0 40px ${accent}55` }}>
        <svg width="52" height="52" viewBox="0 0 24 24"><path fill={accent} d="M4 3h16a2 2 0 0 1 2 2v11a2 2 0 0 1-2 2H9l-5 4v-4H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2z" /></svg>
        <div style={{ fontFamily: INTER, fontWeight: 900, fontSize: 44, color: "#fff", letterSpacing: 1 }}>DO YOU HAVE IT? <span style={{ color: accent }}>COMMENT BELOW</span></div>
        <div style={{ fontFamily: INTER, fontWeight: 900, fontSize: 48, color: accent, transform: `translateY(${bob}px)` }}>↓</div>
      </div>
    </AbsoluteFill>
  );
};

// ---------- End screen ----------
const End = ({ e, accent, accent2 }) => {
  const fr = useCurrentFrame();
  const { fps } = useVideoConfig();
  const dim = interpolate(fr, [0, 20], [0, 1], clamp);
  const a = spring({ frame: fr - 10, fps, config: { damping: 15, stiffness: 120 } });
  const b = spring({ frame: fr - 22, fps, config: { damping: 15, stiffness: 120 } });
  const glow = 0.5 + 0.5 * Math.sin(fr / 9);
  return (
    <AbsoluteFill>
      <AbsoluteFill style={{ backdropFilter: `blur(${dim * 14}px)`, background: `rgba(0,0,0,${0.55 * dim})` }} />
      <AbsoluteFill style={{ flexDirection: "row", alignItems: "center", justifyContent: "center", gap: 90 }}>
        <div style={{ transform: `translateX(${(1 - a) * -80}px)`, opacity: a, maxWidth: 720 }}>
          <div style={{ fontFamily: INTER, fontWeight: 900, fontSize: 40, letterSpacing: 10, color: accent2 }}>WATCH NEXT</div>
          <div style={{ fontFamily: ANTON, fontSize: 92, lineHeight: 1.05, color: "#fff", marginTop: 10, textShadow: "0 8px 30px #000" }}>{e.next.toUpperCase()}</div>
          <div style={{ display: "inline-block", marginTop: 34, padding: "16px 40px", background: "#FF0033", borderRadius: 12,
            fontFamily: INTER, fontWeight: 900, fontSize: 40, letterSpacing: 3, color: "#fff", transform: `scale(${0.95 + 0.05 * glow})` }}>SUBSCRIBE</div>
        </div>
        <div style={{ width: 800, height: 450, borderRadius: 22, border: `5px solid ${accent}`, transform: `scale(${0.85 + 0.15 * b})`, opacity: b,
          boxShadow: `0 0 ${30 + 30 * glow}px ${accent}`, background: "rgba(255,255,255,0.04)" }} />
      </AbsoluteFill>
    </AbsoluteFill>
  );
};

export const FactsVideo = (p) => {
  useFonts();
  const { shots, captions, cards, stats, intro, comment, end, tracker, flashes, accent, accent2, total } = p;
  return (
    <AbsoluteFill style={{ backgroundColor: "#000" }}>
      {shots.map((s, i) => (
        <Sequence key={"s" + i} from={s.from} durationInFrames={s.dur} premountFor={20}><Shot s={s} /></Sequence>
      ))}
      <Grade />
      {flashes.map((f, i) => <Sequence key={"f" + i} from={f} durationInFrames={10}><Flash /></Sequence>)}
      {stats.map((s, i) => <Sequence key={"st" + i} from={s.from} durationInFrames={s.dur}><Stat s={s} accent={accent} accent2={accent2} /></Sequence>)}
      {captions.map((c, i) => <Sequence key={"c" + i} from={c.from} durationInFrames={c.dur}><Caption c={c} accent={accent} /></Sequence>)}
      {cards.map((c, i) => <Sequence key={"k" + i} from={c.from} durationInFrames={c.dur}><Card c={c} accent={accent} accent2={accent2} /></Sequence>)}
      {intro && <Sequence from={intro.from} durationInFrames={intro.dur}><Intro it={intro} accent={accent} accent2={accent2} /></Sequence>}
      {comment && <Sequence from={comment.from} durationInFrames={comment.dur}><Comment c={comment} accent={accent} /></Sequence>}
      {end && <Sequence from={end.from} durationInFrames={end.dur}><End e={end} accent={accent} accent2={accent2} /></Sequence>}
      <Tracker tracker={tracker} total={total} accent={accent} />
    </AbsoluteFill>
  );
};
