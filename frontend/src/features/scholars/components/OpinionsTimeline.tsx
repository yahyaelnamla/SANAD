"use client";

import { useMemo } from "react";
import { Clock } from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { buildOpinionsTimeline } from "@/features/scholars/utils/opinionUtils";
import { useTranslations } from "@/hooks/useTranslations";
import type { Opinion } from "@/types/query";

interface OpinionsTimelineProps {
  opinions: Opinion[];
}

export function OpinionsTimeline({ opinions }: OpinionsTimelineProps) {
  const { t } = useTranslations();

  const entries = useMemo(() => buildOpinionsTimeline(opinions), [opinions]);

  if (entries.length === 0) {
    return (
      <p className="text-sm text-muted-foreground">{t("scholars.noOpinionsTimeline")}</p>
    );
  }

  return (
    <Card className="glass-card border-border/50">
      <CardHeader className="pb-2">
        <CardTitle className="flex items-center gap-2 text-sm font-semibold">
          <Clock className="h-4 w-4 text-cyan-400" />
          {t("scholars.opinionsTimeline")}
        </CardTitle>
      </CardHeader>
      <CardContent>
        <ol className="relative space-y-0 border-s border-violet-500/20 ps-4">
          {entries.map((entry, index) => (
            <li key={entry.id} className="relative pb-5 last:pb-0">
              <span
                className="absolute -start-[1.35rem] top-1 flex h-5 w-5 items-center justify-center rounded-full border border-violet-500/40 bg-card text-[9px] font-bold text-violet-300"
                aria-hidden
              >
                {index + 1}
              </span>
              <div className="rounded-lg border border-border/40 bg-muted/10 p-3">
                <div className="flex flex-wrap items-start justify-between gap-2">
                  <div>
                    <p className="text-sm font-medium text-violet-300">{entry.scholar}</p>
                    {entry.institution && (
                      <p className="text-xs text-muted-foreground">{entry.institution}</p>
                    )}
                  </div>
                  {entry.date && (
                    <Badge variant="outline" className="text-[10px]">
                      {entry.date}
                    </Badge>
                  )}
                </div>
                <p className="mt-2 text-sm leading-relaxed">{entry.position}</p>
                {entry.citations.length > 0 && (
                  <p className="mt-2 text-xs text-primary">{entry.citations.join(" · ")}</p>
                )}
              </div>
            </li>
          ))}
        </ol>
      </CardContent>
    </Card>
  );
}
