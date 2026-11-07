import React from "react";
import { Composition } from "remotion";
import { FactsVideo } from "./Video";
import "@fontsource/anton/400.css";
import "@fontsource/inter/600.css";
import "@fontsource/inter/800.css";
import "@fontsource/inter/900.css";
export const Root = () => (
  <Composition id="Facts" component={FactsVideo} width={1920} height={1080} fps={30} durationInFrames={300}
    defaultProps={{ shots: [], captions: [], cards: [], stats: [], tracker: [], flashes: [], accent: "#FF3D6E", accent2: "#FFD23F", total: 12 }}
    calculateMetadata={({ props }) => ({ durationInFrames: props.durationInFrames || 300 })} />
);
