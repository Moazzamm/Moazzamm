import React from "react";
import { AbsoluteFill, staticFile, useCurrentFrame } from "remotion";
import { Audio } from "@remotion/media";
import { TransitionSeries, linearTiming } from "@remotion/transitions";
import { fade } from "@remotion/transitions/fade";
import { slide } from "@remotion/transitions/slide";
import { ORDER, SceneId, TRANSITION, sceneFrames, sceneStart, totalFrames, voEnd } from "./lib/timeline";
import { ProgressBar } from "./components/overlay";
import { Intro, F10, F9 } from "./scenes/A";
import { F8, F7, F6, Myth } from "./scenes/B";
import { F5, F4, F3, F2, F1, Outro } from "./scenes/C";
import { C } from "./lib/theme";

export const SCENES: Record<SceneId, React.FC> = {
  intro: Intro, f10: F10, f9: F9, f8: F8, f7: F7, f6: F6, myth: Myth, f5: F5, f4: F4, f3: F3, f2: F2, f1: F1, outro: Outro,
};

export const USAFacts: React.FC = () => {
  const total = totalFrames();
  const endScreen = sceneStart("outro") + voEnd("outro");
  return (
    <AbsoluteFill style={{ backgroundColor: C.bg }}>
      <TransitionSeries>
        {ORDER.map((id, i) => {
          const Scene = SCENES[id];
          return (
            <React.Fragment key={id}>
              {i > 0 && (
                <TransitionSeries.Transition
                  presentation={i % 3 === 0 ? slide({ direction: "from-right" }) : fade()}
                  timing={linearTiming({ durationInFrames: TRANSITION })}
                />
              )}
              <TransitionSeries.Sequence name={id} durationInFrames={sceneFrames(id)}>
                <Scene />
              </TransitionSeries.Sequence>
            </React.Fragment>
          );
        })}
      </TransitionSeries>
      <Audio
        src={staticFile("audio/music.mp3")}
        volume={(f: number) => (f > endScreen ? 0.32 : f < 20 ? 0.05 + (f / 20) * 0.08 : 0.13)}
      />
      <ProgressBar total={total} />
      <FrameCounterGuard />
    </AbsoluteFill>
  );
};

const FrameCounterGuard: React.FC = () => {
  useCurrentFrame();
  return null;
};
