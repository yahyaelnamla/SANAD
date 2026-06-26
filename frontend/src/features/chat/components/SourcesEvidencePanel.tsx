"use client";

import { useState } from "react";

import { SourceCardsSection } from "@/features/chat/components/SourceCardsSection";
import { useTranslations } from "@/hooks/useTranslations";
import type { QueryResult } from "@/types/query";

interface SourcesEvidencePanelProps {
  result: QueryResult;
}

export function SourcesEvidencePanel({ result }: SourcesEvidencePanelProps) {
  const { t } = useTranslations();
  const [openSourceIds, setOpenSourceIds] = useState<string[]>([]);

  const hasContent = result.sources.length > 0 || result.evidence.length > 0;

  if (!hasContent) {
    return (
      <p className="py-4 text-center text-sm text-muted-foreground">{t("explainability.noEvidence")}</p>
    );
  }

  return (
    <SourceCardsSection
      result={result}
      openSourceIds={openSourceIds}
      onOpenSource={(sourceId) => {
        setOpenSourceIds((prev) => (prev.includes(sourceId) ? prev : [...prev, sourceId]));
        window.setTimeout(() => {
          document
            .getElementById(`source-panel-${sourceId}`)
            ?.scrollIntoView({ behavior: "smooth", block: "nearest" });
        }, 80);
      }}
      onOpenSourceIdsChange={setOpenSourceIds}
    />
  );
}
