import React from "react";
import { AbsoluteFill, Sequence, staticFile } from "remotion";
import { Audio } from "@remotion/media";
import { C } from "../lib/theme";
import { HEAD, SceneId } from "../lib/timeline";
import { Captions, Hud } from "./overlay";
import { Sfx, Stinger } from "./core";

export const SceneShell: React.FC<{ id: SceneId; n?: number; children: React.ReactNode; hud?: boolean; captions?: boolean; label?: string }> = ({
  id, n, children, hud = true, captions = true, label,
}) => (
  <AbsoluteFill style={{ backgroundColor: C.bg, overflow: "hidden" }}>
    {children}
    {n !== undefined && (
      <>
        <Stinger n={n} dur={HEAD + 26} />
        <Sfx src="boom.wav" at={2} volume={0.55} />
      </>
    )}
    <Sfx src="whoosh.wav" at={0} volume={0.45} />
    {hud && <Hud n={n} label={label} />}
    {captions && <Captions id={id} />}
    <Sequence from={HEAD} layout="none">
      <Audio src={staticFile(`audio/${id}.mp3`)} volume={1} />
    </Sequence>
  </AbsoluteFill>
);
