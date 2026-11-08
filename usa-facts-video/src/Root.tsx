import React from "react";
import { Composition, Folder, Still } from "remotion";
import { USAFacts, SCENES } from "./USAFacts";
import { ThumbRushmore, ThumbStatue } from "./Thumbnail";
import { ORDER, sceneFrames, totalFrames } from "./lib/timeline";
import { FPS, H, W } from "./lib/theme";

export const RemotionRoot: React.FC = () => (
  <>
    <Composition id="USAFacts" component={USAFacts} width={W} height={H} fps={FPS} durationInFrames={totalFrames()} />
    <Folder name="Scenes">
      {ORDER.map((id) => (
        <Composition key={id} id={`Scene-${id}`} component={SCENES[id]} width={W} height={H} fps={FPS} durationInFrames={sceneFrames(id)} />
      ))}
    </Folder>
    <Folder name="Thumbnails">
      <Still id="ThumbStatue" component={ThumbStatue} width={1280} height={720} />
      <Still id="ThumbRushmore" component={ThumbRushmore} width={1280} height={720} />
    </Folder>
  </>
);
