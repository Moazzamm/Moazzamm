import React, { useMemo } from "react";
import { ThreeCanvas } from "@remotion/three";
import { useCurrentFrame, interpolate } from "remotion";
import * as THREE from "three";
import { W, H } from "../lib/theme";
import { lerp } from "../lib/anim";

/* ================= Grand Canyon rock layers ================= */
const LAYERS = [
  { name: "Kaibab", c: "#e9d6a6", h: 0.35 },
  { name: "Toroweap", c: "#d9b98a", h: 0.3 },
  { name: "Coconino", c: "#f2e3c4", h: 0.4 },
  { name: "Hermit", c: "#b5523b", h: 0.45 },
  { name: "Supai", c: "#c4633f", h: 0.6 },
  { name: "Redwall", c: "#9e3d2c", h: 0.55 },
  { name: "Muav", c: "#8c7a6b", h: 0.35 },
  { name: "Bright Angel", c: "#6f8a73", h: 0.45 },
  { name: "Tapeats", c: "#7a5b45", h: 0.3 },
  { name: "Vishnu", c: "#2e2a33", h: 0.9 },
];
export const CANYON_DEPTH = LAYERS.reduce((a, l) => a + l.h, 0);

/** Builds a slab with a V-shaped canyon carved through it (extruded profile). */
const slabShape = (top: number, bottom: number, wTop: number, wBot: number, half = 5) => {
  // cross-section in XY: outer block minus canyon notch whose width shrinks with depth
  const s = new THREE.Shape();
  s.moveTo(-half, bottom);
  s.lineTo(-wBot, bottom);
  s.lineTo(-wTop, top);
  s.lineTo(-half, top);
  s.lineTo(-half, bottom);
  const r = new THREE.Shape();
  r.moveTo(half, bottom);
  r.lineTo(half, top);
  r.lineTo(wTop, top);
  r.lineTo(wBot, bottom);
  r.lineTo(half, bottom);
  return [s, r];
};

export const CanyonScene: React.FC<{ marker: number; reveal: number; river: number; orbit?: number }> = ({ marker, reveal, river, orbit = 0 }) => {
  const f = useCurrentFrame();
  const geoms = useMemo(() => {
    let y = 0;
    return LAYERS.map((l) => {
      const top = -y;
      const bottom = -(y + l.h);
      y += l.h;
      // canyon walls step inward deeper down (wider at the rim)
      const wTop = 3.2 - (Math.abs(top) / CANYON_DEPTH) * 2.8;
      const wBot = 3.2 - (Math.abs(bottom) / CANYON_DEPTH) * 2.8;
      const shapes = slabShape(top, bottom, Math.max(0.35, wTop), Math.max(0.35, wBot));
      return shapes.map((sh) => new THREE.ExtrudeGeometry(sh, { depth: 6, bevelEnabled: false }));
    });
  }, []);
  const ang = -0.45 + orbit + Math.sin(f / 90) * 0.06;
  const cam = new THREE.Vector3(Math.sin(ang) * 15, 5.5, Math.cos(ang) * 15 + 3);
  const yM = -marker * CANYON_DEPTH;
  const xM = Math.max(0.35, 3.2 - marker * 2.8) * -1 + 0.15;
  return (
    <ThreeCanvas width={W} height={H} camera={{ position: [cam.x, cam.y, cam.z], fov: 36 }} onCreated={({ camera }) => camera.lookAt(0, -1.2, 3)}>
      <ambientLight intensity={0.55} />
      <directionalLight position={[5, 8, 6]} intensity={1.6} />
      <directionalLight position={[-6, 2, -4]} intensity={0.4} color="#88aaff" />
      <group position={[0, 1.4, 0]} scale={[1, interpolate(reveal, [0, 1], [0.001, 1]), 1]}>
        {geoms.map((pair, i) => (
          <group key={i}>
            {pair.map((g, k) => (
              <mesh key={k} geometry={g}>
                <meshStandardMaterial color={LAYERS[i].c} roughness={0.9} side={THREE.DoubleSide} />
              </mesh>
            ))}
          </group>
        ))}
        {/* river */}
        <mesh position={[0, -CANYON_DEPTH + 0.02, 3]} rotation={[-Math.PI / 2, 0, 0]} scale={[1, river, 1]}>
          <planeGeometry args={[0.7, 6]} />
          <meshStandardMaterial color="#3d8bff" emissive="#1d4fa8" emissiveIntensity={0.6} />
        </mesh>
        {/* hiker marker */}
        <mesh position={[xM, yM + 0.12, 5.6]}>
          <sphereGeometry args={[0.16, 24, 24]} />
          <meshStandardMaterial color="#ffc93c" emissive="#ffb000" emissiveIntensity={1.2} />
        </mesh>
      </group>
    </ThreeCanvas>
  );
};

/* ================= Hawaii hotspot conveyor belt ================= */
const ISLANDS = [
  { name: "Kauai", born: 0.0, r: 0.55 },
  { name: "Oahu", born: 0.22, r: 0.6 },
  { name: "Maui", born: 0.45, r: 0.65 },
  { name: "Big Island", born: 0.68, r: 0.95 },
];

/** progress 0..1 drives the plate sliding left over a fixed hotspot. */
export const HotspotScene: React.FC<{ progress: number; glow: number }> = ({ progress, glow }) => {
  const f = useCurrentFrame();
  const plateX = -progress * 9; // plate moves left (north-west)
  const flicker = 0.85 + 0.15 * Math.sin(f / 3) * Math.sin(f / 7);
  return (
    <ThreeCanvas width={W} height={H} camera={{ position: [0, 3.2, 12.5], fov: 40 }} onCreated={({ camera }) => camera.lookAt(0, -0.5, 0)}>
      <ambientLight intensity={0.5} />
      <directionalLight position={[4, 7, 5]} intensity={1.4} />
      {/* mantle */}
      <mesh position={[0, -2.75, 0]}>
        <boxGeometry args={[44, 4, 4.4]} />
        <meshStandardMaterial color="#5a1a0a" emissive="#3a0c02" emissiveIntensity={0.5} />
      </mesh>
      {/* hotspot plume (fixed) */}
      <mesh position={[2.2, -1.55, 1.5]}>
        <cylinderGeometry args={[0.45, 1.3, 2.4, 32]} />
        <meshStandardMaterial color="#ff7a1a" emissive="#ff4500" emissiveIntensity={1.6 * glow * flicker} transparent opacity={0.92} />
      </mesh>
      <pointLight position={[2.2, -0.2, 3.0]} intensity={6 * glow * flicker} color="#ff6a00" distance={6} />
      {/* plate */}
      <group position={[plateX, 0, 0]}>
        <mesh position={[6, -0.38, 0]}>
          <boxGeometry args={[42, 0.75, 4.4]} />
          <meshStandardMaterial color="#26476b" roughness={0.8} />
        </mesh>
        {/* ocean surface */}
        <mesh position={[6, 0.02, 0]} rotation={[-Math.PI / 2, 0, 0]}>
          <planeGeometry args={[42, 4.4]} />
          <meshStandardMaterial color="#1d6fd6" transparent opacity={0.85} />
        </mesh>
        {ISLANDS.map((isl, i) => {
          // island i is born when the hotspot passes under its future position
          const local = progress - isl.born;
          const grow = interpolate(local, [0, 0.12], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
          const age = Math.max(0, local);
          const erode = interpolate(age, [0.3, 1], [1, 0.55], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
          const x = 2.2 + isl.born * 9;
          const active = grow > 0 && age < 0.25;
          return (
            <mesh key={i} position={[x, Math.max(0.001, grow * erode * isl.r * 1.9) / 2, 1.5]} scale={[isl.r * 1.3, Math.max(0.001, grow * erode * isl.r * 1.9), isl.r * 1.3]}>
              <coneGeometry args={[1, 1, 40]} />
              <meshStandardMaterial color={active ? "#5c3a2a" : "#2f7d4a"} emissive={active ? "#ff3d00" : "#000000"} emissiveIntensity={active ? 0.8 * flicker : 0} />
            </mesh>
          );
        })}
      </group>
    </ThreeCanvas>
  );
};

export const islandScreenX = (i: number, progress: number) => {
  // approximate screen x of island i for labels (camera at z=10.5, fov 40)
  const worldX = 2.2 + ISLANDS[i].born * 9 - progress * 9;
  return 960 + worldX * 134;
};
export const ISLAND_NAMES = ISLANDS.map((i) => i.name);
export { lerp };
