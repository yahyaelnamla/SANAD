"use client";

import { useMemo } from "react";
import { BookOpen } from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { useTranslations } from "@/hooks/useTranslations";
import { buildSourceTimeline } from "@/features/evaluation/utils/visualizationHelpers";
import { sourceTypeEmoji } from "@/lib/sourceIcons";
import type { QueryResult } from "@/types/query";

interface SourceTimelineProps {
  result: QueryResult;
}

export function SourceTimeline({ result }: SourceTimelineProps) {
  const { t, locale } = useTranslations();

  const entries = useMemo(
    () => buildSourceTimeline(result, locale),
    [result, locale],
  );

  if (entries.length === 0) {
    return (
      <p className="text-sm text-muted-foreground">{t("evaluation.noTimelineData")}</p>
    );
  }

  return (
    <Card className="glass-card border-border/50">
      <CardHeader className="pb-2">
        <CardTitle className="text-sm font-semibold">{t("evaluation.sourceTimeline")}</CardTitle>
      </CardHeader>
      <CardContent>
        <ol className="relative space-y-0 border-s border-cyan-500/20 ps-4">
          {entries.map((entry, index) => (
            <li key={`${entry.id}-${index}`} className="relative pb-5 last:pb-0">
              <span
                className="absolute -start-[1.35rem] top-1 flex h-5 w-5 items-center justify-center rounded-full border border-cyan-500/40 bg-card text-[10px]"
                aria-hidden
              >
                {sourceTypeEmoji(entry.type) || "📖"}
              </span>
              <div className="rounded-lg border border-border/40 bg-muted/10 p-3">
                <div className="flex flex-wrap items-start justify-between gap-2">
                  <div className="min-w-0 flex-1">
                    <p className="text-sm font-medium leading-snug">{entry.title}</p>
                    <p className="mt-0.5 text-xs text-muted-foreground">{entry.author}</p>
                  </div>
                  <Badge variant="outline" className="shrink-0 text-[10px]">
                    {entry.era}
                  </Badge>
                </div>
                {entry.citation && (
                  <p className="mt-2 flex items-start gap-1.5 text-xs text-muted-foreground">
                    <BookOpen className="mt-0.5 h-3 w-3 shrink-0 text-cyan-400" />
                    <span className="line-clamp-2">{entry.citation}</span>
                  </p>
                )}
              </div>
            </li>
          ))}
        </ol>
      </CardContent>
    </Card>
  );
}
