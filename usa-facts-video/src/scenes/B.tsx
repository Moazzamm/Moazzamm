import React from "react";
import { AbsoluteFill, interpolate, useCurrentFrame } from "remotion";
import { geoAlbers, geoPath, GeoProjection } from "d3-geo";
import type { Feature, Geometry } from "geojson";
import { SceneShell } from "../components/Shell";
import { Center, Chip, Counter, Headline, Layer, Panel, Penny, Photo, Sfx, Stamp } from "../components/core";
import { GeoMap, LOWER48 } from "../components/geo";
import { BODY, C, HEAD as HF } from "../lib/theme";
import { cue, sceneFrames } from "../lib/timeline";
import { EASE, lerp, pop, ramp } from "../lib/anim";

const bg = (x = 50, y = 45) => ({ background: `radial-gradient(circle at ${x}% ${y}%, ${C.bg2}, ${C.bg})` });

/* =============================== #8 POINT ROBERTS =============================== */
const BORDER_Y = 500;
const CANADA_D =
  "M0,0 H1920 V500 H1090 C1050,470 1010,425 940,405 C860,385 790,380 745,405 C720,450 715,560 690,640 C660,700 520,700 455,640 C420,600 400,470 360,420 C300,380 150,370 0,365 Z";
const US_MAIN_D = "M1090,500 H1920 V1080 H1000 C1030,930 1010,760 1040,640 C1060,570 1075,530 1090,500 Z";

export const F8: React.FC = () => {
  const f = useCurrentFrame();
  const id = "f8";
  const c = (p: string, n = 0) => cue(id, p, n);
  const end = sceneFrames(id);
  const t1846 = c("In 1846"), tSliced = c("sliced"), tDrive = c("To drive"), tCan = c("cross into Canada"), tBack = c("then back"), tKids = c("Older kids");
  const tipUS = f < t1846 ? 1 : ramp(f, tSliced, 12);
  const route = ramp(f, tDrive, tBack + 30 - tDrive, EASE);
  const crossings = f >= tBack ? 2 : f >= tCan ? 1 : 0;
  const zoom = lerp(f, [0, 60], [1.25, 1]);
  return (
    <SceneShell id={id} n={8}>
      <AbsoluteFill style={{ background: "#0f2f57", scale: String(zoom) }}>
        <svg width={1920} height={1080}>
          <defs>
            <clipPath id="belowBorder">
              <rect x={0} y={BORDER_Y} width={1920} height={1080} />
            </clipPath>
            <pattern id="waves" width="60" height="30" patternUnits="userSpaceOnUse">
              <path d="M0,15 Q15,5 30,15 T60,15" fill="none" stroke="rgba(255,255,255,.06)" strokeWidth="3" />
            </pattern>
          </defs>
          <rect width={1920} height={1080} fill="url(#waves)" />
          <path d={CANADA_D} fill="#2b3550" stroke="rgba(255,255,255,.25)" strokeWidth={3} />
          <path d={US_MAIN_D} fill="#2c5aa0" stroke="rgba(255,255,255,.25)" strokeWidth={3} />
          {/* Point Roberts = Canada-shaped peninsula clipped below the border */}
          <path d={CANADA_D} fill="#2c5aa0" clipPath="url(#belowBorder)" opacity={tipUS} />
          <path d={CANADA_D} fill="none" stroke={C.gold} strokeWidth={6} clipPath="url(#belowBorder)" opacity={tipUS * (0.6 + 0.4 * Math.sin(f / 5))} />
          {/* 49th parallel */}
          <line x1={0} y1={BORDER_Y} x2={1920 * (f < t1846 ? 1 : ramp(f, c("49th"), 30))} y2={BORDER_Y} stroke={C.red} strokeWidth={6} strokeDasharray="26 16" />
          {/* drive route */}
          <path
            d="M560,600 C575,520 590,420 640,360 C760,300 1000,300 1120,360 C1150,420 1160,480 1170,570"
            fill="none"
            stroke={C.gold}
            strokeWidth={9}
            strokeLinecap="round"
            strokeDasharray="1400"
            strokeDashoffset={1400 * (1 - route)}
          />
          <circle cx={1170} cy={575} r={14} fill="#fff" opacity={ramp(f, tDrive, 10)} />
          {crossings >= 1 && <circle cx={590} cy={BORDER_Y} r={26 * pop(f, tCan, 10)} fill="none" stroke="#fff" strokeWidth={6} />}
          {crossings >= 2 && <circle cx={1158} cy={BORDER_Y} r={26 * pop(f, tBack + 18, 10)} fill="none" stroke="#fff" strokeWidth={6} />}
        </svg>
        <Label x={820} y={200} at={c("This is")} size={70} color="#cfd8ea">CANADA</Label>
        <Label x={1500} y={760} at={c("This is")} size={70} color="#cfe0ff">USA</Label>
        <Label x={300} y={700} at={c("This is")} size={40} color={C.gold}>POINT ROBERTS, WA (USA)</Label>
        <Label x={1205} y={600} at={tDrive} size={36} color="#fff">BLAINE, WA</Label>
        <Label x={1250} y={455} at={c("49th")} size={34} color={C.red}>49TH PARALLEL · BORDER</Label>
        <Label x={770} y={720} at={c("This is")} size={30} color="rgba(255,255,255,.45)">Boundary Bay</Label>
      </AbsoluteFill>
      <div style={{ position: "absolute", left: 70, bottom: 28, fontFamily: BODY, fontWeight: 700, fontSize: 22, color: "rgba(255,255,255,.55)" }}>Simplified map · not to scale</div>
      <Layer a={0} b={c("This is") + 4} fade={6}>
        <AbsoluteFill style={{ alignItems: "center", paddingTop: 200 }}>
          <Headline text="You can't drive here" at={c("There's")} size={120} />
          <Headline text="without *leaving the U.S.*" at={c("without")} size={96} hi={C.red} />
        </AbsoluteFill>
      </Layer>
      <Layer a={t1846} b={tDrive} fade={8}>
        <div style={{ position: "absolute", left: 1280, top: 170 }}>
          <Panel at={t1846}>
            <div style={{ fontFamily: HF, fontSize: 110, color: "#fff", lineHeight: 1 }}>1846</div>
            <div style={{ fontFamily: BODY, fontWeight: 900, fontSize: 32, color: C.dim, letterSpacing: 3 }}>BORDER DRAWN ON THE 49TH</div>
          </Panel>
        </div>
      </Layer>
      <Layer a={tDrive} b={end} fade={8}>
        <div style={{ position: "absolute", left: 1330, top: 160 }}>
          <Panel at={tDrive} from="right">
            <div style={{ fontFamily: BODY, fontWeight: 900, fontSize: 30, color: C.dim, letterSpacing: 3 }}>BORDER CROSSINGS</div>
            <div style={{ fontFamily: HF, fontSize: 150, color: f >= tKids ? C.gold : "#fff", lineHeight: 1 }}>{f >= c("four times") ? 4 : crossings}</div>
            {f >= tKids && <div style={{ fontFamily: BODY, fontWeight: 900, fontSize: 30, color: C.gold }}>EVERY SCHOOL DAY</div>}
          </Panel>
        </div>
      </Layer>
      <Sfx src="pop.wav" at={tCan} />
      <Sfx src="pop.wav" at={tBack + 18} />
      <Sfx src="ding.wav" at={c("four times")} volume={0.4} />
      <Sfx src="whoosh.wav" at={c("49th")} volume={0.4} />
    </SceneShell>
  );
};

const Label: React.FC<{ x: number; y: number; at: number; size: number; color: string; children: React.ReactNode }> = ({ x, y, at, size, color, children }) => {
  const f = useCurrentFrame();
  const p = pop(f, at, 14);
  return (
    <div style={{ position: "absolute", left: x, top: y, fontFamily: HF, fontSize: size, color, opacity: Math.min(1, p * 1.5), translate: `0px ${(1 - p) * 30}px`, letterSpacing: 2, textShadow: "0 4px 16px rgba(0,0,0,.7)" }}>
      {children}
    </div>
  );
};

/* =============================== #7 STATUE OF LIBERTY =============================== */
const BROWN = "sepia(1) saturate(2.7) hue-rotate(-14deg) brightness(.9) contrast(1.06)";

const Rain: React.FC<{ at: number; b: number }> = ({ at, b }) => {
  const f = useCurrentFrame();
  const o = ramp(f, at, 15) * (1 - ramp(f, b - 15, 15));
  return (
    <svg width={1920} height={1080} style={{ position: "absolute", opacity: o * 0.55 }}>
      {Array.from({ length: 90 }, (_, i) => {
        const x = (i * 211) % 1920;
        const y = ((i * 97 + f * 38) % 1250) - 120;
        return <line key={i} x1={x} y1={y} x2={x - 18} y2={y + 70} stroke="#cfe3ff" strokeWidth={2.5} />;
      })}
    </svg>
  );
};

export const F7: React.FC = () => {
  const f = useCurrentFrame();
  const id = "f7";
  const c = (p: string, n = 0) => cue(id, p, n);
  const end = sceneFrames(id);
  const tUnv = c("When she was"), tSkin = c("Her skin"), tOver = c("Over the next"), tTwist = c("And here's"), tFam = c("The most famous");
  const brown = f < tUnv ? 0 : f < tOver ? 1 : 1 - ramp(f, tOver + 10, c("patina") - tOver, EASE);
  const year = Math.round(lerp(f, [tOver + 10, c("patina")], [1886, 1906]));
  return (
    <SceneShell id={id} n={7}>
      <Layer a={0} b={tSkin + 6} fade={6}>
        <Photo src="statue_green.jpg" dur={tSkin} zoom={[1.0, 1.2]} origin="25% 40%" />
        <AbsoluteFill style={{ opacity: brown }}>
          <Photo src="statue_green.jpg" dur={tSkin} zoom={[1.0, 1.2]} origin="25% 40%" filter={BROWN} />
        </AbsoluteFill>
        <AbsoluteFill style={{ alignItems: "flex-end", paddingRight: 140, paddingTop: 220 }}>
          <Headline text="Wasn't always *green*" at={c("always")} size={120} hi={C.patina} out={tUnv} />
        </AbsoluteFill>
        <Layer a={tUnv} b={tSkin + 6}>
          <div style={{ position: "absolute", right: 150, top: 200, display: "flex", flexDirection: "column", alignItems: "flex-end", gap: 24 }}>
            <Chip at={c("1886")} color={C.copper} size={56}>1886</Chip>
            <Headline text="Shiny *reddish-brown*" at={c("reddish")} size={100} hi="#ff9a5a" align="left" />
            <div style={{ display: "flex", alignItems: "center", gap: 30, marginTop: 20 }}>
              <div style={{ fontFamily: HF, fontSize: 60, color: "#fff", opacity: ramp(f, c("the color of"), 10) }}>= A NEW PENNY</div>
              <Penny at={c("the color of")} size={220} />
            </div>
          </div>
        </Layer>
        <AbsoluteFill style={{ background: "#fff", opacity: interpolate(f, [tUnv, tUnv + 3, tUnv + 10], [0, 0.7, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" }) }} />
      </Layer>
      <Layer a={tSkin} b={tOver + 6} fade={6} style={bg(50, 40)}>
        <AbsoluteFill style={{ alignItems: "center", paddingTop: 190 }}>
          <Headline text="Her skin: *copper*" at={tSkin} size={110} hi="#ff9a5a" />
        </AbsoluteFill>
        <div style={{ position: "absolute", left: 360, top: 430, display: "flex", alignItems: "center", gap: 90 }}>
          <div style={{ display: "flex", flexDirection: "column", gap: 8, opacity: ramp(f, c("two pennies"), 10) }}>
            {[0, 1].map((k) => (
              <div key={k} style={{ width: 420, height: 64, borderRadius: 32, background: "linear-gradient(#e7a06a,#a8562a 60%,#6b3115)", boxShadow: "0 10px 20px rgba(0,0,0,.4)", translate: `0px ${(1 - pop(f, c("two pennies") + k * 6, 12)) * -200}px` }} />
            ))}
            <div style={{ fontFamily: BODY, fontWeight: 900, fontSize: 30, color: C.dim, textAlign: "center", marginTop: 10, letterSpacing: 3 }}>2 PENNIES STACKED</div>
          </div>
          <div style={{ fontFamily: HF, fontSize: 120, color: "#fff", opacity: ramp(f, c("two pennies") + 10, 10) }}>≈</div>
          <div style={{ display: "flex", flexDirection: "column", alignItems: "center" }}>
            <Counter from={0} to={2.4} decimals={1} suffix=" mm" at={c("two pennies") + 12} size={170} color={C.gold} />
            <div style={{ fontFamily: BODY, fontWeight: 900, fontSize: 30, color: C.dim, letterSpacing: 3 }}>COPPER SKIN THICKNESS</div>
          </div>
        </div>
      </Layer>
      <Layer a={tOver} b={tTwist + 6} fade={6}>
        <Photo src="statue_green.jpg" from={tOver} dur={tTwist - tOver} zoom={[1.15, 1.3]} origin="25% 35%" />
        <AbsoluteFill style={{ opacity: brown }}>
          <Photo src="statue_green.jpg" from={tOver} dur={tTwist - tOver} zoom={[1.15, 1.3]} origin="25% 35%" filter={BROWN} />
        </AbsoluteFill>
        <Rain at={c("rain")} b={tTwist} />
        <div style={{ position: "absolute", right: 140, top: 190, display: "flex", flexDirection: "column", alignItems: "flex-end", gap: 22 }}>
          <div style={{ fontFamily: HF, fontSize: 170, color: "#fff", lineHeight: 1, textShadow: "0 8px 30px rgba(0,0,0,.6)" }}>{year}</div>
          <Chip at={c("rain")} color={C.blue} size={40}>Rain</Chip>
          <Chip at={c("wind")} color={C.blue} size={40}>Wind</Chip>
          <Chip at={c("salty")} color={C.blue} size={40}>Salty sea air</Chip>
          <div style={{ marginTop: 10 }}>
            <Stamp text="Patina" at={c("patina")} color={C.patina} size={100} rotate={-6} />
          </div>
        </div>
        <Sfx src="pop.wav" at={c("rain")} />
        <Sfx src="pop.wav" at={c("wind")} />
        <Sfx src="pop.wav" at={c("salty")} />
        <Sfx src="stamp.wav" at={c("patina")} volume={0.6} />
      </Layer>
      <Layer a={tTwist} b={tFam + 6} fade={6} style={bg(50, 50)}>
        <AbsoluteFill style={{ alignItems: "center", paddingTop: 170 }}>
          <div style={{ display: "flex", gap: 40, alignItems: "center" }}>
            <div style={{ fontFamily: HF, fontSize: 90, color: "#fff", opacity: ramp(f, c("isn't damage"), 8), textDecoration: f >= c("it's a shield") ? "line-through" : "none", textDecorationColor: C.red }}>DAMAGE?</div>
            <div style={{ fontFamily: HF, fontSize: 110, color: C.green, opacity: ramp(f, c("it's a shield"), 8) }}>A SHIELD</div>
          </div>
        </AbsoluteFill>
        <svg width={1920} height={1080} style={{ position: "absolute" }}>
          {/* cross-section: copper below, patina on top */}
          <rect x={460} y={560} width={1000} height={170} rx={20} fill="#b2602f" />
          <text x={960} y={665} textAnchor="middle" fontFamily={HF} fontSize={54} fill="rgba(255,255,255,.85)">COPPER</text>
          <rect x={460} y={560 - 70 * ramp(f, tTwist + 6, 20)} width={1000} height={70 * ramp(f, tTwist + 6, 20)} rx={14} fill={C.patina} />
          <text x={960} y={540} textAnchor="middle" fontFamily={HF} fontSize={44} fill="#0b2a22" opacity={ramp(f, tTwist + 20, 10)}>PATINA</text>
          {Array.from({ length: 7 }, (_, i) => {
            const t = ((f - tTwist + i * 9) % 40) / 40;
            const x = 520 + i * 140;
            const y = t < 0.5 ? 330 + t * 2 * 150 : 480 - (t - 0.5) * 2 * 120;
            return <circle key={i} cx={x + (t > 0.5 ? (t - 0.5) * 80 : 0)} cy={y} r={12} fill="#9fd0ff" opacity={f > tTwist + 10 ? 0.9 : 0} />;
          })}
        </svg>
        <Sfx src="ding.wav" at={c("it's a shield")} volume={0.35} />
      </Layer>
      <Layer a={tFam} b={end} fade={6}>
        <Photo src="statue_green.jpg" from={tFam} dur={end - tFam} zoom={[1.1, 1.3]} origin="25% 35%" />
        <AbsoluteFill style={{ alignItems: "flex-end", paddingRight: 140, paddingTop: 250 }}>
          <Headline text="Armor made from" at={c("wearing armor")} size={100} align="left" />
          <Headline text="her own *corrosion*" at={c("her own")} size={100} hi={C.patina} align="left" />
        </AbsoluteFill>
      </Layer>
    </SceneShell>
  );
};

/* =============================== #6 GREAT LAKES =============================== */
const Donut: React.FC<{ at: number; pct: number }> = ({ at, pct }) => {
  const f = useCurrentFrame();
  const p = ramp(f, at, 40) * pct;
  const r = 200, cx = 260, cy = 260, L = 2 * Math.PI * r;
  return (
    <svg width={520} height={520} style={{ overflow: "visible", opacity: ramp(f, at - 6, 8) }}>
      <circle cx={cx} cy={cy} r={r} fill="none" stroke="rgba(255,255,255,.15)" strokeWidth={60} />
      <circle cx={cx} cy={cy} r={r} fill="none" stroke={C.water} strokeWidth={60} strokeDasharray={`${L * p} ${L}`} transform={`rotate(-90 ${cx} ${cy})`} strokeLinecap="round" />
    </svg>
  );
};

export const F6: React.FC = () => {
  const f = useCurrentFrame();
  const id = "f6";
  const c = (p: string, n = 0) => cue(id, p, n);
  const end = sceneFrames(id);
  const tHow = c("How much"), tSup = c("And Lake Superior");
  const level = ramp(f, c("poured"), c("nine and") + 20 - c("poured"), EASE); // 0..1 of 9.5 ft
  const proj = geoAlbers().scale(1500).translate([620, 560]);
  const GH = 520; // gauge height in px for 10 ft
  return (
    <SceneShell id={id} n={6}>
      <Layer a={0} b={tHow + 6} fade={6}>
        <Photo src="superior.jpg" dur={tHow} zoom={[1.05, 1.2]} dim={0.6} />
        <div style={{ position: "absolute", left: 150, top: 250, width: 900 }}>
          <Headline text="The Great Lakes hold" at={c("The Great")} size={92} align="left" />
          <Headline text="*21%* of Earth's" at={c("21")} size={130} align="left" hi={C.gold} />
          <Headline text="fresh surface water" at={c("21") + 10} size={92} align="left" />
          <div style={{ marginTop: 30 }}>
            <Chip at={c("five lakes")} color={C.blue} size={44}>1/5 of the world · just 5 lakes</Chip>
          </div>
        </div>
        <div style={{ position: "absolute", right: 170, top: 230 }}>
          <Donut at={c("21")} pct={0.21} />
          <div style={{ position: "absolute", inset: 0, display: "flex", alignItems: "center", justifyContent: "center" }}>
            <Counter from={0} to={21} suffix="%" at={c("21")} dur={40} size={150} />
          </div>
        </div>
      </Layer>
      <Layer a={tHow} b={tSup + 6} fade={6} style={bg(35, 55)}>
        <svg width={1920} height={1080} style={{ position: "absolute" }}>
          <defs>
            <clipPath id="usClip">
              {LOWER48.map((s, i) => (
                <path key={i} d={geoPathStr(proj, s)} />
              ))}
            </clipPath>
          </defs>
        </svg>
        <GeoMap projection={proj} states={LOWER48} showWorld={false} stateFill={() => C.landHi} />
        <svg width={1920} height={1080} style={{ position: "absolute" }}>
          <g clipPath="url(#usClip)">
            <rect x={0} y={1000 - 760 * level} width={1300} height={1080} fill={C.water} opacity={0.85} />
            <path d={`M0,${1000 - 760 * level} ${Array.from({ length: 27 }, (_, i) => `Q${i * 50 + 25},${1000 - 760 * level + (i % 2 ? -12 : 12) * Math.sin(f / 6)} ${i * 50 + 50},${1000 - 760 * level}`).join(" ")}`} stroke="#9fd0ff" strokeWidth={4} fill="none" />
          </g>
        </svg>
        {/* depth gauge */}
        <div style={{ position: "absolute", left: 1380, top: 250, width: 420, height: GH + 40, opacity: ramp(f, c("poured"), 10) }}>
          <svg width={420} height={GH + 40} style={{ overflow: "visible" }}>
            {Array.from({ length: 11 }, (_, i) => (
              <g key={i}>
                <line x1={40} x2={i % 5 === 0 ? 80 : 64} y1={GH - (i * GH) / 10} y2={GH - (i * GH) / 10} stroke="#fff" strokeWidth={3} />
                {i % 5 === 0 && (
                  <text x={0} y={GH - (i * GH) / 10 + 10} fill="#fff" fontFamily={BODY} fontWeight={900} fontSize={26}>{i}ft</text>
                )}
              </g>
            ))}
            {/* person 6ft */}
            <g transform={`translate(150, ${GH - (6 * GH) / 10})`} fill="#e9eef7">
              <circle cx={30} cy={22} r={22} />
              <rect x={8} y={48} width={44} height={(6 * GH) / 10 - 50} rx={18} />
            </g>
            {/* hoop at 10 ft */}
            <g transform={`translate(260, 0)`}>
              <rect x={60} y={0} width={10} height={GH} fill="#9aa6bd" />
              <rect x={20} y={-40} width={90} height={60} fill="none" stroke="#fff" strokeWidth={4} />
              <ellipse cx={20} cy={20} rx={34} ry={8} fill="none" stroke={f >= c("basketball") ? C.red : "#ff8a3c"} strokeWidth={6} />
            </g>
            <rect x={90} y={GH - (9.5 * GH * level) / 10} width={320} height={(9.5 * GH * level) / 10} fill={C.water} opacity={0.55} />
            <line x1={90} x2={410} y1={GH - (9.5 * GH * level) / 10} y2={GH - (9.5 * GH * level) / 10} stroke="#9fd0ff" strokeWidth={4} />
          </svg>
        </div>
        <div style={{ position: "absolute", left: 1390, top: 140 }}>
          <Counter from={0} to={9.5} decimals={1} suffix=" FT DEEP" at={c("poured")} dur={c("nine and") + 20 - c("poured")} size={84} color={C.gold} />
        </div>
        <AbsoluteFill style={{ alignItems: "flex-start", paddingLeft: 150, paddingTop: 160 }}>
          <Headline text="Pour it over the *lower 48*" at={c("If you poured")} size={70} align="left" />
        </AbsoluteFill>
        <Sfx src="riser.wav" at={c("poured")} volume={0.25} />
        <Sfx src="ding.wav" at={c("basketball")} volume={0.35} />
      </Layer>
      <Layer a={tSup} b={end} fade={6} style={bg(50, 45)}>
        <div style={{ position: "absolute", left: 200, top: 230, width: 1520 }}>
          <Headline text="Lake Superior *alone*" at={tSup} size={96} align="left" />
          <div style={{ marginTop: 50, fontFamily: BODY, fontWeight: 900, fontSize: 30, color: C.dim, letterSpacing: 3 }}>SUPERIOR · 12,100 km³</div>
          <div style={{ height: 80, width: 1500 * ramp(f, tSup + 6, 25), background: C.water, borderRadius: 14, marginTop: 10 }} />
          <div style={{ marginTop: 40, fontFamily: BODY, fontWeight: 900, fontSize: 30, color: C.dim, letterSpacing: 3 }}>MICHIGAN + HURON + ONTARIO + ERIE + 3 MORE ERIES</div>
          <div style={{ display: "flex", gap: 4, marginTop: 10 }}>
            {[
              [610, "#5aa0ff", "MICHIGAN"], [439, "#3d8bff", "HURON"], [203, "#2c6fd6", "ONT."], [60, C.gold, ""], [60, C.gold, ""], [60, C.gold, ""], [60, C.gold, ""],
            ].map(([w, col, name], i) => {
              const at = c("could hold") + i * 5 + (i >= 4 ? c("three more") - c("could hold") - 10 : 0);
              const p = pop(f, at, 14);
              return (
                <div key={i} style={{ height: 80, width: Number(w) * p, background: String(col), borderRadius: 10, overflow: "hidden", fontFamily: BODY, fontWeight: 900, fontSize: 24, color: "#fff", display: "flex", alignItems: "center", paddingLeft: 12, whiteSpace: "nowrap" }}>
                  {String(name)}
                </div>
              );
            })}
          </div>
          <div style={{ marginTop: 34 }}>
            <Chip at={c("three more") + 18} color={C.green} size={44}>Still fits ✓</Chip>
          </div>
        </div>
        <Sfx src="pop.wav" at={c("three more")} />
        <Sfx src="ding.wav" at={c("three more") + 18} volume={0.35} />
      </Layer>
    </SceneShell>
  );
};

const geoPathStr = (p: GeoProjection, s: Feature<Geometry>) => geoPath(p)(s) ?? "";

/* =============================== MYTH BUSTER =============================== */
const Plane: React.FC<{ at: number; b: number }> = ({ at, b }) => {
  const f = useCurrentFrame();
  const t = ramp(f, at, b - at, EASE);
  const x = interpolate(t, [0, 1], [-300, 1100]);
  const y = interpolate(t, [0, 1], [180, 520]);
  return (
    <svg width={1920} height={1080} style={{ position: "absolute" }}>
      <g transform={`translate(${x},${y}) rotate(14) scale(1.6)`} opacity={f >= at ? 1 : 0}>
        <path d="M0,20 L120,14 L170,0 L182,6 L150,22 L182,38 L170,44 L120,30 L0,24 Z" fill="#fff" />
        <path d="M70,20 L40,-30 L60,-30 L110,18 Z M70,24 L40,74 L60,74 L110,26 Z" fill="#dfe7f5" />
      </g>
    </svg>
  );
};

export const Myth: React.FC = () => {
  const f = useCurrentFrame();
  const id = "myth";
  const c = (p: string, n = 0) => cue(id, p, n);
  const end = sceneFrames(id);
  const tFalse = c("completely false"), tFed = c("The Federal"), tOk = c("Okay");
  const glitch = f < 20 ? Math.round(Math.sin(f * 3) * 8) : 0;
  return (
    <SceneShell id={id} label="MYTH BUSTER">
      <Layer a={0} b={tOk + 6} fade={6}>
        <Photo src="highway.jpg" dur={tOk} zoom={[1.0, 1.25]} dim={f >= tFalse ? 0.75 : 0.45} filter={f >= tFalse ? "grayscale(.8)" : undefined} />
        <AbsoluteFill style={{ alignItems: "center", paddingTop: 170 }}>
          <div style={{ translate: `${glitch}px 0px` }}>
            <Chip at={2} color={C.gold} size={58} style={{ color: "#1a1a1a" }}>Myth buster</Chip>
          </div>
          <div style={{ marginTop: 40 }}>
            <Headline text="1 in 5 interstate miles" at={c("one out of")} size={100} />
            <Headline text="must be *straight*?" at={c("perfectly")} size={100} />
          </div>
        </AbsoluteFill>
        <Plane at={c("so planes")} b={tFalse} />
        <Center>
          <div style={{ marginTop: 300 }}>
            <Stamp text="False" at={tFalse} color={C.red} size={230} rotate={-10} />
          </div>
        </Center>
        <Layer a={tFed} b={tOk + 6}>
          <AbsoluteFill style={{ background: "rgba(5,8,16,.6)", justifyContent: "center", alignItems: "center" }}>
            <Panel at={tFed} style={{ maxWidth: 1300 }}>
              <div style={{ fontFamily: HF, fontSize: 84, color: "#fff", lineHeight: 1.1 }}>“NO LAW, RULE OR POLICY HAS EVER REQUIRED IT.”</div>
              <div style={{ fontFamily: BODY, fontWeight: 900, fontSize: 34, color: C.dim, marginTop: 20, letterSpacing: 2 }}>— FEDERAL HIGHWAY ADMINISTRATION (PARAPHRASED)</div>
            </Panel>
          </AbsoluteFill>
        </Layer>
        <Sfx src="whoosh.wav" at={c("so planes")} volume={0.5} />
        <Sfx src="boom.wav" at={tFalse} volume={0.7} />
        <Sfx src="stamp.wav" at={tFalse} volume={0.8} />
      </Layer>
      <Layer a={tOk} b={end} fade={6} style={{ background: `radial-gradient(circle, #2a0d14, ${C.bg})` }}>
        <Center>
          <div style={{ fontFamily: BODY, fontWeight: 900, fontSize: 60, color: C.gold, letterSpacing: 20, opacity: ramp(f, tOk, 10) }}>NOW…</div>
          <div style={{ fontFamily: HF, fontSize: 320, color: "#fff", lineHeight: 1, scale: String(pop(f, c("the top"), 9)), textShadow: `0 0 80px ${C.red}` }}>THE TOP 5</div>
        </Center>
        <Sfx src="riser.wav" at={tOk - 10} volume={0.5} />
        <Sfx src="boom.wav" at={c("the top")} volume={0.6} />
      </Layer>
    </SceneShell>
  );
};
