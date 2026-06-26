"use client";

import { useMemo } from "react";
import { Scale } from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  alignmentStyle,
  buildFatwaComparisonRows,
} from "@/features/scholars/utils/opinionUtils";
import { useTranslations } from "@/hooks/useTranslations";
import { cn } from "@/lib/utils";
import type { QueryResult } from "@/types/query";

interface FatwaComparisonPanelProps {
  result: QueryResult;
}

const ALIGNMENT_CLASSES: Record<string, string> = {
  agree: "bg-emerald-500/10 text-emerald-400 border-emerald-500/30",
  disagree: "bg-destructive/10 text-destructive border-destructive/30",
  mixed: "bg-amber-500/10 text-amber-400 border-amber-500/30",
  neutral: "bg-muted/20 text-muted-foreground border-border/40",
};

export function FatwaComparisonPanel({ result }: FatwaComparisonPanelProps) {
  const { t } = useTranslations();

  const rows = useMemo(
    () => buildFatwaComparisonRows(result.opinions, result.madhhab_matrix ?? []),
    [result.opinions, result.madhhab_matrix],
  );

  if (rows.length < 2) {
    return (
      <p className="text-sm text-muted-foreground">{t("scholars.compareNeedMore")}</p>
    );
  }

  return (
    <Card className="glass-card border-violet-500/20">
      <CardHeader className="pb-2">
        <CardTitle className="flex items-center gap-2 text-sm font-semibold text-violet-300">
          <Scale className="h-4 w-4" />
          {t("scholars.fatwaComparison")}
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="grid gap-3 md:grid-cols-2">
          {rows.map((row) => {
            const alignKey = alignmentStyle(row.alignment);
            return (
              <div
                key={row.id}
                className="rounded-xl border border-border/40 bg-muted/10 p-4"
              >
                <div className="mb-2 flex flex-wrap items-center gap-2">
                  <p className="text-sm font-semibold">{row.label}</p>
                  <Badge variant="outline" className="text-[10px]">
                    {row.kind === "madhhab" ? t("scholars.madhhab") : t("scholars.scholar")}
                  </Badge>
                  {row.alignment && (
                    <Badge className={cn("text-[10px]", ALIGNMENT_CLASSES[alignKey])}>
                      {row.alignment}
                    </Badge>
                  )}
                </div>
                {row.institution && (
                  <p className="mb-2 text-xs text-muted-foreground">{row.institution}</p>
                )}
                <p className="text-sm leading-relaxed">{row.position}</p>
                {row.source && (
                  <p className="mt-2 text-xs text-primary">{row.source}</p>
                )}
              </div>
            );
          })}
        </div>
        <p className="mt-3 text-xs text-muted-foreground">{t("scholars.compareHint")}</p>
      </CardContent>
    </Card>
  );
}
