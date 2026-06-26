"use client";

import { useMemo } from "react";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { useTranslations } from "@/hooks/useTranslations";
import { buildConfidenceRadar } from "@/features/evaluation/utils/visualizationHelpers";
import type { QueryResult } from "@/types/query";

interface ConfidenceRadarChartProps {
  result: QueryResult;
}

const SIZE = 220;
const CENTER = SIZE / 2;
const RADIUS = 78;

function polarPoint(index: number, total: number, value: number): { x: number; y: number } {
  const angle = (Math.PI * 2 * index) / total - Math.PI / 2;
  const r = RADIUS * value;
  return {
    x: CENTER + r * Math.cos(angle),
    y: CENTER + r * Math.sin(angle),
  };
}

export function ConfidenceRadarChart({ result }: ConfidenceRadarChartProps) {
  const { t } = useTranslations();

  const axes = useMemo(
    () =>
      buildConfidenceRadar(result.confidence_breakdown, {
        retrieval: t("explainability.factorRetrieval"),
        grounding: t("explainability.factorGrounding"),
        model: t("explainability.factorModel"),
        guard: t("explainability.factorGuard"),
        verification: t("explainability.factorVerification"),
        scholarly_coverage: t("explainability.factorScholarly"),
      }),
    [result.confidence_breakdown, t],
  );

  if (axes.every((a) => a.value === 0)) {
    return (
      <p className="text-sm text-muted-foreground">{t("evaluation.noConfidenceData")}</p>
    );
  }

  const polygon = axes
    .map((axis, i) => {
      const { x, y } = polarPoint(i, axes.length, axis.value);
      return `${x},${y}`;
    })
    .join(" ");

  const gridLevels = [0.25, 0.5, 0.75, 1];

  return (
    <Card className="glass-card border-border/50">
      <CardHeader className="pb-2">
        <CardTitle className="text-sm font-semibold">{t("evaluation.confidenceRadar")}</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="flex flex-col items-center gap-4 lg:flex-row lg:items-start">
          <svg
            viewBox={`0 0 ${SIZE} ${SIZE}`}
            className="h-[220px] w-[220px] shrink-0"
            role="img"
            aria-label={t("evaluation.confidenceRadar")}
          >
            {gridLevels.map((level) => (
              <polygon
                key={level}
                points={axes
                  .map((_, i) => {
                    const { x, y } = polarPoint(i, axes.length, level);
                    return `${x},${y}`;
                  })
                  .join(" ")}
                fill="none"
                stroke="currentColor"
                strokeOpacity={0.12}
                className="text-foreground"
              />
            ))}
            {axes.map((axis, i) => {
              const outer = polarPoint(i, axes.length, 1);
              return (
                <line
                  key={axis.key}
                  x1={CENTER}
                  y1={CENTER}
                  x2={outer.x}
                  y2={outer.y}
                  stroke="currentColor"
                  strokeOpacity={0.15}
                  className="text-foreground"
                />
              );
            })}
            <polygon
              points={polygon}
              fill="rgba(0,229,255,0.25)"
              stroke="#00E5FF"
              strokeWidth={2}
            />
            {axes.map((axis, i) => {
              const { x, y } = polarPoint(i, axes.length, axis.value);
              return <circle key={`dot-${axis.key}`} cx={x} cy={y} r={3} fill="#00E5FF" />;
            })}
          </svg>
          <ul className="grid flex-1 gap-2 text-xs sm:grid-cols-2">
            {axes.map((axis) => (
              <li key={axis.key} className="flex items-center justify-between gap-2 rounded-lg bg-muted/20 px-2 py-1.5">
                <span className="text-muted-foreground">{axis.label}</span>
                <span className="font-mono text-cyan-400">{Math.round(axis.value * 100)}%</span>
              </li>
            ))}
          </ul>
        </div>
      </CardContent>
    </Card>
  );
}
