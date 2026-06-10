import React, { useMemo, useRef, useEffect } from "react";
import { useCurrentFrame, useVideoConfig, interpolate } from "remotion";
import { loadFont } from "@remotion/google-fonts/Outfit";
import { videoScript } from "../data/videoScript";

// Load Outfit font
export const { fontFamily } = loadFont("normal", {
  weights: ["300", "400", "500", "600", "700"],
  subsets: ["latin"],
});

// Deterministic random generator based on a seed
const pseudoRandom = (seed: number) => {
  const x = Math.sin(seed++) * 10000;
  return x - Math.floor(x);
};

// High-speed Canvas-based data network background
export const DataNetworkBackground: React.FC = () => {
  const frame = useCurrentFrame();
  const { width, height } = useVideoConfig();
  const canvasRef = useRef<HTMLCanvasElement>(null);

  // Define 24 nodes deterministically (reduced from 35 to speed up rendering while retaining density)
  const nodes = useMemo(() => {
    const arr = [];
    for (let i = 0; i < 24; i++) {
      const xSeed = i * 13.5 + 4.1;
      const ySeed = i * 47.9 + 1.7;
      const speedSeed = i * 2.3 + 9.8;
      arr.push({
        baseX: pseudoRandom(xSeed) * width,
        baseY: pseudoRandom(ySeed) * height,
        vx: (pseudoRandom(speedSeed) - 0.5) * 1.5,
        vy: (pseudoRandom(speedSeed + 1.2) - 0.5) * 1.5,
        size: pseudoRandom(speedSeed + 2.5) * 4 + 3,
        color: pseudoRandom(speedSeed + 3.1) > 0.6 ? "#00f2fe" : "#4facfe",
      });
    }
    return arr;
  }, [width, height]);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    // Clear canvas
    ctx.clearRect(0, 0, width, height);

    // Draw dark background gradient
    const grad = ctx.createRadialGradient(
      width / 2,
      height / 2,
      50,
      width / 2,
      height / 2,
      Math.max(width, height) * 0.8
    );
    grad.addColorStop(0, "#0e172a"); // Slate 900
    grad.addColorStop(1, "#060913"); // Deep dark
    ctx.fillStyle = grad;
    ctx.fillRect(0, 0, width, height);

    // Calculate node coordinates for this frame
    const positions = nodes.map((node) => ({
      x: (node.baseX + node.vx * frame + width) % width,
      y: (node.baseY + node.vy * frame + height) % height,
      size: node.size,
      color: node.color,
    }));

    // Draw connection lines
    ctx.lineWidth = 1;
    for (let i = 0; i < positions.length; i++) {
      const p1 = positions[i];
      for (let j = i + 1; j < positions.length; j++) {
        const p2 = positions[j];
        const dist = Math.hypot(p2.x - p1.x, p2.y - p1.y);
        
        if (dist < 280) {
          const alpha = interpolate(dist, [120, 280], [0.35, 0], {
            extrapolateRight: "clamp",
          });
          if (alpha > 0) {
            ctx.strokeStyle = `rgba(0, 242, 254, ${alpha})`;
            ctx.beginPath();
            ctx.moveTo(p1.x, p1.y);
            ctx.lineTo(p2.x, p2.y);
            ctx.stroke();
          }
        }
      }
    }

    // Draw nodes
    for (let i = 0; i < positions.length; i++) {
      const p = positions[i];
      ctx.fillStyle = p.color;
      ctx.beginPath();
      ctx.arc(p.x, p.y, p.size, 0, Math.PI * 2);
      ctx.fill();
    }
  }, [frame, nodes, width, height]);

  return (
    <canvas
      ref={canvasRef}
      width={width}
      height={height}
      style={{
        position: "absolute",
        top: 0,
        left: 0,
        width: "100%",
        height: "100%",
        zIndex: 0,
        pointerEvents: "none",
      }}
    />
  );
};

// Premium Glassmorphic Card Container
export const GlassCard: React.FC<{
  children: React.ReactNode;
  style?: React.CSSProperties;
}> = ({ children, style }) => {
  return (
    <div
      style={{
        background: "rgba(11, 20, 38, 0.92)",
        backdropFilter: "blur(4px) saturate(120%)",
        border: "1px solid rgba(255, 255, 255, 0.08)",
        borderRadius: "24px",
        boxShadow: "0 20px 50px rgba(0, 0, 0, 0.3), inset 0 1px 1px rgba(255, 255, 255, 0.1)",
        padding: "40px",
        fontFamily,
        color: "#f8fafc",
        ...style,
      }}
    >
      {children}
    </div>
  );
};

// Global Progress Bar
export const ProgressBar: React.FC = () => {
  const frame = useCurrentFrame();
  const { durationInFrames } = useVideoConfig();

  const progress = frame / durationInFrames;

  return (
    <div
      style={{
        position: "absolute",
        top: 0,
        left: 0,
        width: "100%",
        height: "6px",
        background: "rgba(255, 255, 255, 0.05)",
        zIndex: 100,
      }}
    >
      <div
        style={{
          width: `${progress * 100}%`,
          height: "100%",
          background: "linear-gradient(90deg, #00f2fe 0%, #4facfe 100%)",
          boxShadow: "0 0 10px rgba(0, 242, 254, 0.8)",
        }}
      />
    </div>
  );
};

// Subtitle Box
export const SubtitleBox: React.FC = () => {
  const frame = useCurrentFrame();
  
  // Find current scene and subtitle text
  const currentScene = videoScript.find(
    (scene) => frame >= scene.startFrame && frame < scene.endFrame
  ) || videoScript[videoScript.length - 1];

  const localFrame = frame - currentScene.startFrame;

  // Fade in / out subtitle on transition
  const opacity = interpolate(
    localFrame,
    [0, 15, currentScene.durationFrames - 15, currentScene.durationFrames],
    [0, 1, 1, 0],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
  );

  // Split narration into sentences or small phrases to make it highly readable
  const words = currentScene.narration.split(" ");
  const totalWords = words.length;
  
  // Distribute words over the scene duration
  // We want to highlight or reveal words progressively
  const wordsToShow = Math.floor(
    interpolate(localFrame, [10, currentScene.durationFrames - 20], [1, totalWords], {
      extrapolateLeft: "clamp",
      extrapolateRight: "clamp",
    })
  );

  const visibleText = words.slice(0, wordsToShow).join(" ");
  const remainingText = words.slice(wordsToShow).join(" ");

  return (
    <div
      style={{
        position: "absolute",
        bottom: "60px",
        left: "5%",
        width: "90%",
        display: "flex",
        justifyContent: "center",
        zIndex: 50,
        opacity,
        fontFamily,
      }}
    >
      <div
        style={{
          background: "rgba(6, 9, 19, 0.85)",
          border: "1px solid rgba(0, 242, 254, 0.15)",
          borderRadius: "16px",
          padding: "24px 48px",
          maxWidth: "1200px",
          boxShadow: "0 10px 30px rgba(0, 0, 0, 0.5)",
          textAlign: "center",
          fontSize: "26px",
          fontWeight: 400,
          lineHeight: "1.5",
          letterSpacing: "0.5px",
        }}
      >
        <span style={{ color: "#f8fafc" }}>{visibleText}</span>
        <span style={{ color: "rgba(148, 163, 184, 0.25)" }}> {remainingText}</span>
      </div>
    </div>
  );
};
