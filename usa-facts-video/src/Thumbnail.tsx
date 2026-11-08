import React from "react";
import { AbsoluteFill, Img, staticFile } from "remotion";
import { BODY, C, HEAD } from "./lib/theme";

const stroke: React.CSSProperties = { WebkitTextStroke: "6px #000", paintOrder: "stroke fill", textShadow: "0 10px 30px rgba(0,0,0,.6)" };

export const ThumbStatue: React.FC = () => (
  <AbsoluteFill style={{ background: C.bg }}>
    <div style={{ position: "absolute", left: 0, top: 0, width: 640, height: 720, overflow: "hidden" }}>
      <Img src={staticFile("img/statue_green.jpg")} style={{ position: "absolute", height: 720, left: -40, filter: "sepia(1) saturate(3) hue-rotate(-16deg) brightness(.95) contrast(1.1)" }} />
    </div>
    <div style={{ position: "absolute", left: 640, top: 0, width: 640, height: 720, overflow: "hidden" }}>
      <Img src={staticFile("img/statue_green.jpg")} style={{ position: "absolute", height: 720, left: -680, filter: "saturate(1.4) contrast(1.1)" }} />
    </div>
    <div style={{ position: "absolute", left: 632, top: 0, width: 16, height: 720, background: "#fff" }} />
    <div style={{ position: "absolute", left: 40, top: 40, fontFamily: HEAD, fontSize: 92, color: "#ffb37a", ...stroke }}>1886</div>
    <div style={{ position: "absolute", right: 40, top: 40, fontFamily: HEAD, fontSize: 92, color: "#7fe0c4", ...stroke }}>TODAY</div>
    <div style={{ position: "absolute", left: 0, right: 0, bottom: 60, textAlign: "center", fontFamily: HEAD, fontSize: 150, color: "#fff", lineHeight: 0.95, ...stroke }}>
      SHE WAS <span style={{ color: C.gold }}>BROWN?!</span>
    </div>
    <div style={{ position: "absolute", left: 470, top: 250, background: C.red, color: "#fff", fontFamily: BODY, fontWeight: 900, fontSize: 40, padding: "10px 26px", borderRadius: 14, rotate: "-6deg", boxShadow: "0 10px 30px rgba(0,0,0,.5)" }}>
      USA FACTS
    </div>
  </AbsoluteFill>
);

export const ThumbRushmore: React.FC = () => (
  <AbsoluteFill style={{ background: C.bg }}>
    <Img src={staticFile("img/rushmore.jpg")} style={{ position: "absolute", width: 1280, height: 720, objectFit: "cover", filter: "contrast(1.15) saturate(1.2) brightness(.9)" }} />
    <AbsoluteFill style={{ background: "linear-gradient(90deg, rgba(0,0,0,.75), rgba(0,0,0,0) 60%)" }} />
    <svg width={1280} height={720} style={{ position: "absolute" }}>
      <circle cx={900} cy={330} r={150} fill="none" stroke={C.red} strokeWidth={14} />
      <path d="M560,520 C640,500 700,460 760,410" stroke={C.red} strokeWidth={16} fill="none" strokeLinecap="round" />
      <path d="M735,395 L790,385 L770,440 Z" fill={C.red} />
    </svg>
    <div style={{ position: "absolute", left: 50, top: 70, fontFamily: HEAD, fontSize: 150, color: "#fff", lineHeight: 0.92, ...stroke }}>
      SECRET
      <br />
      <span style={{ color: C.gold }}>ROOM?!</span>
    </div>
    <div style={{ position: "absolute", left: 50, bottom: 60, background: C.red, color: "#fff", fontFamily: BODY, fontWeight: 900, fontSize: 40, padding: "10px 26px", borderRadius: 14 }}>
      10 USA FACTS THAT SOUND FAKE
    </div>
  </AbsoluteFill>
);
