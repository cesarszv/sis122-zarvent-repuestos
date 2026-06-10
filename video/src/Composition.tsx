import { AbsoluteFill, Sequence, staticFile } from "remotion";
import { Audio } from "@remotion/media";
import { DataNetworkBackground, ProgressBar, SubtitleBox } from "./components/UI";
import {
  Scene1Apertura,
  Scene2Problema,
  Scene3Actores,
  Scene4Erd,
  Scene5Integridad,
  Scene6Demo,
  Scene7Alcance,
  Scene8Cierre,
} from "./components/Scenes";

export const MyComposition = () => {
  const logoUrl = staticFile("logo.png");

  return (
    <AbsoluteFill style={{ backgroundColor: "#060913", overflow: "hidden" }}>
      {/* Background audio track */}
      <Audio src={staticFile("music.mp3")} volume={0.4} />

      {/* Global Animated Network Grid */}
      <DataNetworkBackground />

      {/* Top progress indicator */}
      <ProgressBar />

      {/* Timeline Scenes */}
      {/* 1. Apertura: 0 - 300f (0-10s) */}
      <Sequence durationInFrames={300}>
        <Scene1Apertura logoUrl={logoUrl} />
      </Sequence>

      {/* 2. Problema: 300 - 750f (10-25s) */}
      <Sequence from={300} durationInFrames={450}>
        <Scene2Problema />
      </Sequence>

      {/* 3. Actores: 750 - 1260f (25-42s) */}
      <Sequence from={750} durationInFrames={510}>
        <Scene3Actores />
      </Sequence>

      {/* 4. ERD: 1260 - 1950f (42-65s) */}
      <Sequence from={1260} durationInFrames={690}>
        <Scene4Erd />
      </Sequence>

      {/* 5. Integridad y precio histórico: 1950 - 2700f (65-90s) */}
      <Sequence from={1950} durationInFrames={750}>
        <Scene5Integridad />
      </Sequence>

      {/* 6. Demo visual: 2700 - 3540f (90-118s) */}
      <Sequence from={2700} durationInFrames={840}>
        <Scene6Demo />
      </Sequence>

      {/* 7. Alcance honesto: 3540 - 4110f (118-137s) */}
      <Sequence from={3540} durationInFrames={570}>
        <Scene7Alcance />
      </Sequence>

      {/* 8. Cierre académico: 4110 - 4500f (137-150s) */}
      <Sequence from={4110} durationInFrames={390}>
        <Scene8Cierre logoUrl={logoUrl} />
      </Sequence>

      {/* Dynamic Subtitles Overlay */}
      <SubtitleBox />
    </AbsoluteFill>
  );
};
