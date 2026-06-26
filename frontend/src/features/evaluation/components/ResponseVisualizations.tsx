"use client";

import { ConfidenceRadarChart } from "@/features/evaluation/components/ConfidenceRadarChart";
import { EvidenceHeatmap } from "@/features/evaluation/components/EvidenceHeatmap";
import { SourceTimeline } from "@/features/evaluation/components/SourceTimeline";
import type { QueryResult } from "@/types/query";

interface ResponseVisualizationsProps {
  result: QueryResult;
}

export function ResponseVisualizations({ result }: ResponseVisualizationsProps) {
  if (result.refused) return null;

  return (
    <div className="space-y-4">
      <div className="grid gap-4 lg:grid-cols-2">
        <EvidenceHeatmap evidence={result.evidence} />
        <ConfidenceRadarChart result={result} />
      </div>
      <SourceTimeline result={result} />
    </div>
  );
}
