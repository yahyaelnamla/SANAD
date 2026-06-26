"use client";

import { motion } from "framer-motion";

import { cn, formatConfidence } from "@/lib/utils";

interface ConfidenceMeterProps {
  value: number;
  locale: string;
  breakdown?: {
    retrieval?: number;
    grounding?: number;
    model?: number;
    guard?: number;
    verification?: number;
    scholarly_coverage?: number;
  } | null;
  labels?: Record<string, string>;
  className?: string;
}

function confidenceColor(value: number): string {
  if (value >= 0.75) return "stroke-cyan-400";
  if (value >= 0.5) return "stroke-amber-400";
  return "stroke-orange-500";
}

export function ConfidenceMeter({
  value,
  locale,
  breakdown,
  labels,
  className,
}: ConfidenceMeterProps) {
  const pct = Math.round(Math.min(Math.max(value, 0), 1) * 100);
  const radius = 36;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference - (value * circumference);

  const factors = breakdown
    ? [
        { key: "retrieval", value: breakdown.retrieval ?? 0 },
        { key: "grounding", value: breakdown.grounding ?? 0 },
        { key: "guard", value: breakdown.guard ?? 0 },
        { key: "verification", value: breakdown.verification ?? 0 },
      ]
    : [];

  return (
    <div className={cn("flex flex-col items-center gap-3 sm:flex-row sm:items-start", className)}>
      <div className="relative flex h-24 w-24 shrink-0 items-center justify-center">
        <svg className="-rotate-90" width="96" height="96" viewBox="0 0 96 96">
          <circle cx="48" cy="48" r={radius} fill="none" stroke="currentColor" strokeWidth="6" className="text-muted/30" />
          <motion.circle
            cx="48"
            cy="48"
            r={radius}
            fill="none"
            strokeWidth="6"
            strokeLinecap="round"
            className={confidenceColor(value)}
            initial={{ strokeDashoffset: circumference }}
            animate={{ strokeDashoffset: offset }}
            transition={{ duration: 1.2, ease: "easeOut" }}
            strokeDasharray={circumference}
          />
        </svg>
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <span className="text-xl font-bold tabular-nums">{pct}%</span>
          <span className="text-[10px] text-muted-foreground">{formatConfidence(value, locale)}</span>
        </div>
      </div>

      {factors.length > 0 && labels && (
        <div className="grid flex-1 grid-cols-2 gap-2 text-xs">
          {factors.map(({ key, value: factorValue }) => (
            <div key={key} className="rounded-lg border bg-muted/20 px-2 py-1.5">
              <div className="flex justify-between gap-2">
                <span className="text-muted-foreground">{labels[key] ?? key}</span>
                <span className="font-mono font-medium">{Math.round(factorValue * 100)}%</span>
              </div>
              <div className="mt-1 h-1 overflow-hidden rounded-full bg-muted">
                <motion.div
                  className="h-full rounded-full bg-cyan-500/80"
                  initial={{ width: 0 }}
                  animate={{ width: `${factorValue * 100}%` }}
                  transition={{ duration: 0.8, delay: 0.2 }}
                />
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
