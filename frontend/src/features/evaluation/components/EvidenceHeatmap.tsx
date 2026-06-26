"use client";

import { Fragment, useMemo } from "react";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { useTranslations } from "@/hooks/useTranslations";
import {
  buildEvidenceHeatmap,
  heatmapIntensity,
} from "@/features/evaluation/utils/visualizationHelpers";
import { cn } from "@/lib/utils";
import type { Evidence } from "@/types/query";

interface EvidenceHeatmapProps {
  evidence: Evidence[];
}

const BUCKET_LABELS = ["0–20%", "20–40%", "40–60%", "60–80%", "80–100%"];

export function EvidenceHeatmap({ evidence }: EvidenceHeatmapProps) {
  const { t } = useTranslations();

  const cells = useMemo(() => buildEvidenceHeatmap(evidence), [evidence]);
  const types = ["quran", "hadith", "fiqh", "fatwa", "standard"] as const;

  if (evidence.length === 0) {
    return (
      <p className="text-sm text-muted-foreground">{t("evaluation.noEvidenceData")}</p>
    );
  }

  return (
    <Card className="glass-card border-border/50">
      <CardHeader className="pb-2">
        <CardTitle className="text-sm font-semibold">{t("evaluation.evidenceHeatmap")}</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="overflow-x-auto">
          <div
            className="inline-grid min-w-[320px] gap-1"
            style={{ gridTemplateColumns: `auto repeat(5, minmax(3rem, 1fr))` }}
            role="grid"
            aria-label={t("evaluation.evidenceHeatmap")}
          >
            <div />
            {BUCKET_LABELS.map((label) => (
              <div key={label} className="px-1 text-center text-[10px] text-muted-foreground">
                {label}
              </div>
            ))}
            {types.map((type) => (
              <Fragment key={type}>
                <div className="flex items-center pe-2 text-xs text-muted-foreground">
                  {t(`explainability.kind.${type}` as "explainability.kind.quran")}
                </div>
                {[0, 1, 2, 3, 4].map((bucket) => {
                  const cell = cells.find((c) => c.type === type && c.bucket === bucket);
                  const intensity = heatmapIntensity(cell?.count ?? 0, cell?.maxScore ?? 0);
                  return (
                    <div
                      key={`${type}-${bucket}`}
                      role="gridcell"
                      title={
                        cell?.count
                          ? `${cell.count} · max ${Math.round((cell.maxScore ?? 0) * 100)}%`
                          : t("evaluation.heatmapEmpty")
                      }
                      className={cn(
                        "flex h-10 items-center justify-center rounded-md border border-border/30 text-[10px] font-medium transition-colors",
                        intensity === 0 && "bg-muted/10 text-muted-foreground/40",
                      )}
                      style={
                        intensity > 0
                          ? {
                              backgroundColor: `rgba(0, 229, 255, ${intensity * 0.55})`,
                              color: intensity > 0.5 ? "#08111F" : undefined,
                            }
                          : undefined
                      }
                    >
                      {cell?.count ? cell.count : "·"}
                    </div>
                  );
                })}
              </Fragment>
            ))}
          </div>
        </div>
        <p className="mt-3 text-xs text-muted-foreground">{t("evaluation.heatmapHint")}</p>
      </CardContent>
    </Card>
  );
}
