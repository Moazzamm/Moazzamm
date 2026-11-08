import React from "react";
import { AbsoluteFill, interpolate, useCurrentFrame } from "remotion";
import { geoAlbersUsa, geoOrthographic } from "d3-geo";
import { SceneShell } from "../components/Shell";
import { Center, Chip, Counter, Headline, Layer, Panel, Penny, Photo, Sfx, Stamp } from "../components/core";
import { GeoMap } from "../components/geo";
import { Flag50 } from "../components/Flag";
import { BODY, C, HEAD as HF } from "../lib/theme";
import { cue, sceneFrames, voEnd } from "../lib/timeline";
import { lerp, pop, ramp } from "../lib/anim";

/* =============================== INTRO =============================== */
export const Intro: React.FC = () => {
  const f = useCurrentFrame();
  const id = "intro";
  const c = (p: string, n = 0) => cue(id, p, n);
  const end = sceneFrames(id);
  const t1 = c("Hawaii"), t2 = c("and one American"), t3 = c("These are"), t4 = c("and number one");
  const rot = lerp(f, [t2, t3], [-118, -132]);
  return (
    <SceneShell id={id} label="10 USA FACTS">
      <Layer a={0} b={t1 + 6} fade={6}>
        <Photo src="rushmore.jpg" dur={t1} zoom={[1.0, 1.35]} pan={["0px 0px", "-120px -40px"]} />
        <AbsoluteFill style={{ alignItems: "center", paddingTop: 170 }}>
          <Headline text="A *secret* room?" at={8} size={150} />
        </AbsoluteFill>
        <svg width={1920} height={1080} style={{ position: "absolute" }}>
          <circle cx={1180} cy={520} r={150 + 12 * Math.sin(f / 4)} fill="none" stroke={C.red} strokeWidth={10} strokeDasharray="30 18" opacity={ramp(f, 20, 10)} />
        </svg>
      </Layer>
      <Layer a={t1} b={t2 + 6} fade={6}>
        <Photo src="lava.jpg" from={t1} dur={t2 - t1} zoom={[1.15, 1.0]} />
        <Center>
          <Headline text="Hawaii is *moving*" at={t1 + 2} size={140} />
          <Headline text="toward Japan" at={t1 + 14} size={100} color={C.gold} />
        </Center>
      </Layer>
      <Layer a={t2} b={t3 + 6} fade={6}>
        <GeoMap
          projection={geoOrthographic().rotate([-rot, -55]).scale(1150).translate([960, 620])}
          sphere
          graticule
          stateFill={(n) => (n === "Alaska" ? C.gold : n === "Hawaii" ? C.land : C.land)}
        />
        <div style={{ position: "absolute", left: 1180, top: 260, display: "flex", flexDirection: "column", gap: 26 }}>
          <Chip at={c("north")} color={C.blue}>Farthest north ✓</Chip>
          <Chip at={c("west")} color={C.blue}>Farthest west ✓</Chip>
          <Chip at={c("east")} color={C.red}>Farthest east ?!</Chip>
        </div>
        <Sfx src="pop.wav" at={c("north")} />
        <Sfx src="pop.wav" at={c("west")} />
        <Sfx src="pop.wav" at={c("east")} volume={0.7} />
      </Layer>
      <Layer a={t3} b={t4 + 6} fade={6}>
        <Photo src="flag.jpg" from={t3} dur={t4 - t3} dim={0.65} zoom={[1.1, 1.2]} />
        <Center style={{ gap: 10 }}>
          <Headline text="10 USA facts" at={t3} size={190} />
          <Headline text="that sound *fake*" at={t3 + 10} size={120} hi={C.red} />
          <div style={{ marginTop: 30 }}>
            <Stamp text="100% true" at={c("true")} color={C.green} size={110} />
          </div>
        </Center>
        <Sfx src="stamp.wav" at={c("true")} volume={0.8} />
      </Layer>
      <Layer a={t4} b={end} fade={6} style={{ background: `radial-gradient(circle, ${C.bg2}, ${C.bg})` }}>
        <Center style={{ gap: 20 }}>
          <div style={{ fontFamily: HF, fontSize: 300, color: C.gold, scale: String(pop(f, t4, 10)), textShadow: `0 0 80px ${C.red}` }}>#1</div>
          <Headline text="breaks a rule from *school*" at={c("breaks")} size={90} />
        </Center>
        <Sfx src="riser.wav" at={t4} volume={0.4} />
      </Layer>
    </SceneShell>
  );
};

/* =============================== #10 PENNY =============================== */
const Bar: React.FC<{ label: string; value: string; w: number; at: number; color: string }> = ({ label, value, w, at, color }) => {
  const f = useCurrentFrame();
  const p = ramp(f, at, 30);
  return (
    <div style={{ marginBottom: 34, opacity: ramp(f, at, 8) }}>
      <div style={{ fontFamily: BODY, fontWeight: 900, fontSize: 34, color: C.dim, letterSpacing: 3, marginBottom: 10 }}>{label}</div>
      <div style={{ display: "flex", alignItems: "center", gap: 24 }}>
        <div style={{ height: 70, width: w * p, background: color, borderRadius: 14, boxShadow: `0 0 40px ${color}55` }} />
        <div style={{ fontFamily: HF, fontSize: 80, color: "#fff" }}>{value}</div>
      </div>
    </div>
  );
};

export const F10: React.FC = () => {
  const f = useCurrentFrame();
  const id = "f10";
  const c = (p: string, n = 0) => cue(id, p, n);
  const end = sceneFrames(id);
  const tNov = c("On November"), tWhy = c("Why"), tLegal = c("Pennies are"), tBridge = c("And if you");
  return (
    <SceneShell id={id} n={10}>
      <Layer a={0} b={tNov + 6} fade={6}>
        <Photo src="pennies.jpg" dur={tNov} zoom={[1.2, 1.05]} />
        <AbsoluteFill style={{ alignItems: "center", paddingTop: 230 }}>
          <Headline text="America *stopped*" at={c("America")} size={150} />
          <Headline text="making the penny" at={c("America") + 8} size={150} />
        </AbsoluteFill>
      </Layer>
      <Layer a={tNov} b={tWhy + 6} fade={6} style={{ background: `radial-gradient(circle at 30% 40%, ${C.bg2}, ${C.bg})` }}>
        <div style={{ position: "absolute", left: 150, top: 210 }}>
          <Panel at={tNov}>
            <div style={{ fontFamily: BODY, fontWeight: 900, color: C.red, fontSize: 36, letterSpacing: 6 }}>FINAL PENNY STRUCK</div>
            <div style={{ fontFamily: HF, color: "#fff", fontSize: 130, lineHeight: 1.05 }}>NOV 12, 2025</div>
            <div style={{ fontFamily: BODY, fontWeight: 700, color: C.dim, fontSize: 38 }}>U.S. Mint · Philadelphia</div>
          </Panel>
        </div>
        <div style={{ position: "absolute", left: 150, top: 500, width: 1620, opacity: ramp(f, c("ending"), 10) }}>
          <div style={{ display: "flex", justifyContent: "space-between", fontFamily: HF, fontSize: 60, color: "#fff" }}>
            <span>1793</span>
            <span>2025</span>
          </div>
          <div style={{ height: 18, borderRadius: 9, background: "rgba(255,255,255,.12)", marginTop: 8 }}>
            <div style={{ height: 18, borderRadius: 9, width: `${100 * ramp(f, c("ending"), 40)}%`, background: `linear-gradient(90deg, ${C.copper}, ${C.gold})` }} />
          </div>
          <div style={{ display: "flex", alignItems: "baseline", gap: 24, marginTop: 20 }}>
            <Counter from={0} to={232} at={c("232")} dur={30} size={140} color={C.gold} comma={false} />
            <div style={{ fontFamily: HF, fontSize: 80, color: "#fff", opacity: ramp(f, c("232"), 10) }}>YEARS OF PENNIES</div>
          </div>
        </div>
        <div style={{ position: "absolute", right: 170, top: 190 }}>
          <Penny at={tNov + 6} size={300} />
        </div>
      </Layer>
      <Layer a={tWhy} b={tLegal + 6} fade={6} style={{ background: `radial-gradient(circle at 70% 40%, ${C.bg2}, ${C.bg})` }}>
        <div style={{ position: "absolute", left: 140, top: 250 }}>
          <Penny at={tWhy} size={380} />
        </div>
        <div style={{ position: "absolute", left: 640, top: 230, width: 1150 }}>
          <Bar label="FACE VALUE" value="1¢" w={230} at={tWhy + 6} color={C.green} />
          <Bar label="COST TO MAKE ONE" value="3.7¢" w={850} at={c("3.7")} color={C.red} />
          <div style={{ marginTop: 10 }}>
            <Chip at={c("The government")} color={C.red} size={46}>
              −2.7¢ lost on every penny
            </Chip>
          </div>
        </div>
        <Sfx src="pop.wav" at={c("3.7")} />
        <Sfx src="stamp.wav" at={c("The government")} volume={0.5} />
      </Layer>
      <Layer a={tLegal} b={tBridge + 6} fade={6}>
        <Photo src="pennies.jpg" from={tLegal} dur={tBridge - tLegal} dim={0.7} zoom={[1.05, 1.15]} />
        <Center style={{ gap: 40 }}>
          <Chip at={tLegal + 4} color={C.green} size={64}>✓ Still legal tender</Chip>
          <Chip at={c("but no new")} color={C.red} size={64}>✕ No new pennies</Chip>
        </Center>
        <Sfx src="ding.wav" at={tLegal + 4} volume={0.3} />
        <Sfx src="stamp.wav" at={c("but no new")} volume={0.6} />
      </Layer>
      <Layer a={tBridge} b={end} fade={6}>
        <Photo src="flag.jpg" from={tBridge} dur={end - tBridge} dim={0.55} />
        <Center>
          <Headline text="Who designed *the flag?*" at={c("who designed")} size={130} />
        </Center>
      </Layer>
    </SceneShell>
  );
};

/* =============================== #9 FLAG =============================== */
const GradeCard: React.FC<{ at: number; aAt: number }> = ({ at, aAt }) => {
  const f = useCurrentFrame();
  const strike = ramp(f, aAt - 6, 10);
  return (
    <Panel at={at} style={{ background: "#f6f1e3", border: "none", width: 520, padding: 36, rotate: "3deg" }}>
      <div style={{ fontFamily: BODY, fontWeight: 900, color: "#555", fontSize: 28, letterSpacing: 3 }}>AMERICAN HISTORY · 1958</div>
      <div style={{ fontFamily: BODY, fontWeight: 700, color: "#333", fontSize: 34, marginTop: 8 }}>Project: 50-star flag</div>
      <div style={{ position: "relative", height: 210, marginTop: 10 }}>
        <div style={{ position: "absolute", left: 20, top: 10, fontFamily: HF, fontSize: 190, color: C.red, lineHeight: 1, opacity: ramp(f, at + 6, 6), rotate: "-8deg" }}>
          B−
          <div style={{ position: "absolute", left: -10, top: 95, height: 14, width: 230 * strike, background: "#222", rotate: "-12deg" }} />
        </div>
        <div style={{ position: "absolute", left: 260, top: 0 }}>
          <Stamp text="A" at={aAt} color="#1a9c5a" size={170} rotate={10} />
        </div>
      </div>
    </Panel>
  );
};

export const F9: React.FC = () => {
  const f = useCurrentFrame();
  const id = "f9";
  const c = (p: string, n = 0) => cue(id, p, n);
  const end = sceneFrames(id);
  const t1958 = c("In 1958"), tSent = c("Bob sent"), tChange = c("His teacher changed"), tLong = c("That flag has");
  const flagW = interpolate(f, [tSent - 8, tSent + 10], [1100, 760], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  return (
    <SceneShell id={id} n={9}>
      <Layer a={0} b={t1958 + 6} fade={6}>
        <Photo src="flag.jpg" dur={t1958} zoom={[1.0, 1.15]} dim={0.5} />
        <AbsoluteFill style={{ alignItems: "center", paddingTop: 230 }}>
          <Headline text="Designed by a" at={c("The flag")} size={110} />
          <Headline text="*17-year-old*" at={c("17")} size={190} hi={C.gold} />
          <div style={{ marginTop: 30 }}>
            <Chip at={c("school project")} color={C.blue} size={50}>for a school project</Chip>
          </div>
        </AbsoluteFill>
      </Layer>
      <Layer a={t1958} b={tChange + 6} fade={6} style={{ background: `radial-gradient(circle at 40% 45%, ${C.bg2}, ${C.bg})` }}>
        <div style={{ position: "absolute", left: 120, top: 200 }}>
          <Flag50 width={flagW} at={c("sewed")} starsAt={c("sewed") + 10} starsDur={45} />
          <div style={{ marginTop: 26, display: "flex", gap: 18 }}>
            <Chip at={t1958} color={C.red} size={38}>1958 · Ohio</Chip>
            <Chip at={c("Bob Heft")} color={C.blue} size={38}>Bob Heft, age 17</Chip>
          </div>
        </div>
        <Layer a={c("His teacher gave")} b={tSent + 4} fade={6}>
          <div style={{ position: "absolute", right: 140, top: 240 }}>
            <GradeCard at={c("His teacher gave")} aAt={99999} />
          </div>
        </Layer>
        <Sfx src="stamp.wav" at={c("His teacher gave") + 6} volume={0.6} />
        <Layer a={tSent} b={tChange + 6} fade={8}>
          <div style={{ position: "absolute", right: 60, top: 170, width: 980, height: 580 }}>
            <GeoMap
              w={980}
              h={580}
              projection={geoAlbersUsa().scale(1150).translate([490, 290])}
              showWorld={false}
              stateFill={(n) => (n === "Alaska" && f >= c("Alaska") ? C.gold : n === "Hawaii" && f >= c("Hawaii") ? C.gold : C.landHi)}
            />
          </div>
          <div style={{ position: "absolute", right: 150, top: 760, display: "flex", gap: 16 }}>
            <Chip at={c("Alaska")} color={C.gold} size={34} style={{ color: "#1a1a1a" }}>49 · Alaska</Chip>
            <Chip at={c("Hawaii")} color={C.gold} size={34} style={{ color: "#1a1a1a" }}>50 · Hawaii</Chip>
          </div>
          <div style={{ position: "absolute", right: 260, top: 150 }}>
            <Stamp text="Official · 1960" at={c("picked")} color={C.green} size={70} rotate={-6} />
          </div>
          <Sfx src="pop.wav" at={c("Alaska")} />
          <Sfx src="pop.wav" at={c("Hawaii")} />
          <Sfx src="stamp.wav" at={c("picked")} volume={0.6} />
        </Layer>
      </Layer>
      <Layer a={tChange} b={tLong + 6} fade={6} style={{ background: `radial-gradient(circle, ${C.bg2}, ${C.bg})` }}>
        <Center style={{ scale: "1.45", paddingBottom: 120 }}>
          <GradeCard at={tChange - 4} aAt={c("an A")} />
        </Center>
        <Sfx src="ding.wav" at={c("an A")} volume={0.5} />
        <Sfx src="stamp.wav" at={c("an A")} volume={0.6} />
      </Layer>
      <Layer a={tLong} b={end} fade={6} style={{ background: `radial-gradient(circle, ${C.bg2}, ${C.bg})` }}>
        <div style={{ position: "absolute", left: 160, top: 230, width: 1600 }}>
          <Headline text="Longest-serving *U.S. flag*" at={tLong} size={96} align="left" />
          <div style={{ marginTop: 50 }}>
            <Bar label="48 STARS · 1912–1959" value="47 yrs" w={47 * 17} at={tLong + 10} color={C.dim} />
            <Bar label="50 STARS · 1960–TODAY" value="66 yrs+" w={66 * 17} at={c("longer")} color={C.red} />
          </div>
        </div>
      </Layer>
    </SceneShell>
  );
};

export { voEnd };
