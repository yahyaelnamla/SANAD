"use client";

import { motion, useReducedMotion } from "framer-motion";
import { Bitcoin, ChartCandlestick, TrendingUp } from "lucide-react";
import type { ReactNode } from "react";
import { useMemo } from "react";

type MotifKind = "arabic" | "star" | "chart" | "candle" | "btc" | "eth";

interface FloatingMotif {
  id: number;
  kind: MotifKind;
  glyph?: string;
  left: string;
  top: string;
  size: number;
  duration: number;
  delay: number;
  driftX: number;
  driftY: number;
  rotation: number;
}

const ARABIC_GLYPHS = ["س", "ن", "د", "أ", "م", "ر", "ب", "ح"];

function StarMotif({ size }: { size: number }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" aria-hidden>
      <path
        d="M12 2L13.8 8.2L20 10L13.8 11.8L12 18L10.2 11.8L4 10L10.2 8.2L12 2Z"
        stroke="currentColor"
        strokeWidth="0.75"
      />
      <path
        d="M12 6L12.9 9.1L16 10L12.9 10.9L12 14L11.1 10.9L8 10L11.1 9.1L12 6Z"
        stroke="currentColor"
        strokeWidth="0.5"
        opacity="0.7"
      />
    </svg>
  );
}

function EthMotif({ size }: { size: number }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" aria-hidden>
      <path d="M12 2L5 12L12 16L19 12L12 2Z" stroke="currentColor" strokeWidth="0.85" />
      <path d="M5 13.5L12 22L19 13.5L12 17L5 13.5Z" stroke="currentColor" strokeWidth="0.85" />
    </svg>
  );
}

function MotifContent({ motif }: { motif: FloatingMotif }) {
  const iconClass = "h-full w-full";

  switch (motif.kind) {
    case "arabic":
      return (
        <span
          className="font-arabic font-medium leading-none"
          style={{ fontSize: motif.size }}
          aria-hidden
        >
          {motif.glyph}
        </span>
      );
    case "star":
      return <StarMotif size={motif.size} />;
    case "chart":
      return <TrendingUp className={iconClass} strokeWidth={1.25} aria-hidden />;
    case "candle":
      return <ChartCandlestick className={iconClass} strokeWidth={1.25} aria-hidden />;
    case "btc":
      return <Bitcoin className={iconClass} strokeWidth={1.25} aria-hidden />;
    case "eth":
      return <EthMotif size={motif.size} />;
    default:
      return null;
  }
}

function buildMotifs(): FloatingMotif[] {
  const kinds: MotifKind[] = ["arabic", "star", "chart", "candle", "btc", "eth"];
  const count = 28;

  return Array.from({ length: count }, (_, i) => {
    const kind = kinds[i % kinds.length];
    return {
      id: i,
      kind,
      glyph: kind === "arabic" ? ARABIC_GLYPHS[i % ARABIC_GLYPHS.length] : undefined,
      left: `${4 + ((i * 17) % 88)}%`,
      top: `${3 + ((i * 23) % 90)}%`,
      size: 14 + (i % 5) * 6,
      duration: 22 + (i % 7) * 4,
      delay: (i % 6) * 1.2,
      driftX: 12 + (i % 5) * 6,
      driftY: 10 + (i % 4) * 8,
      rotation: (i % 3) * 8 - 8,
    };
  });
}

export function GlobalBackground({ children }: { children?: ReactNode }) {
  const reducedMotion = useReducedMotion();
  const motifs = useMemo(() => buildMotifs(), []);

  return (
    <div className="pointer-events-none fixed inset-0 -z-10 overflow-hidden" aria-hidden>
      <div
        className="absolute inset-0 bg-background"
        style={{
          backgroundImage:
            "radial-gradient(circle at 50% 0%, hsl(var(--brand-accent) / 0.04), transparent 42%)",
        }}
      />

      <div className="bg-motif-layer absolute inset-0 text-brand-accent opacity-[0.05] dark:opacity-[0.06]">
        {motifs.map((motif) => {
          const style = {
            left: motif.left,
            top: motif.top,
            width: motif.size,
            height: motif.size,
          };

          if (reducedMotion) {
            return (
              <div key={motif.id} className="absolute" style={style}>
                <MotifContent motif={motif} />
              </div>
            );
          }

          return (
            <motion.div
              key={motif.id}
              className="absolute"
              style={style}
              initial={{ opacity: 0.04, x: 0, y: 0, rotate: 0 }}
              animate={{
                opacity: [0.04, 0.07, 0.05, 0.04],
                x: [0, motif.driftX, -motif.driftX * 0.6, 0],
                y: [0, -motif.driftY, motif.driftY * 0.5, 0],
                rotate: [0, motif.rotation, -motif.rotation * 0.5, 0],
              }}
              transition={{
                duration: motif.duration,
                delay: motif.delay,
                repeat: Infinity,
                ease: "easeInOut",
              }}
            >
              <MotifContent motif={motif} />
            </motion.div>
          );
        })}
      </div>

      {children}
    </div>
  );
}

export function GlobalBackgroundMount() {
  return <GlobalBackground />;
}
