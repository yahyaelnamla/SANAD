"use client";

import { X } from "lucide-react";
import { useEffect } from "react";

import { Button } from "@/components/ui/button";
import { SourcesEvidencePanel } from "@/features/chat/components/SourcesEvidencePanel";
import { useTranslations } from "@/hooks/useTranslations";
import { cn } from "@/lib/utils";
import type { QueryResult } from "@/types/query";

interface SourcesSidePanelProps {
  open: boolean;
  onClose: () => void;
  result: QueryResult;
}

export function SourcesSidePanel({ open, onClose, result }: SourcesSidePanelProps) {
  const { t } = useTranslations();

  useEffect(() => {
    if (!open) return;
    const onKeyDown = (event: KeyboardEvent) => {
      if (event.key === "Escape") onClose();
    };
    window.addEventListener("keydown", onKeyDown);
    return () => window.removeEventListener("keydown", onKeyDown);
  }, [open, onClose]);

  if (!open) return null;

  return (
    <>
      <button
        type="button"
        aria-label={t("sourceCards.closePanel")}
        className="fixed inset-0 z-40 bg-black/50 backdrop-blur-[1px]"
        onClick={onClose}
      />
      <aside
        role="dialog"
        aria-modal="true"
        aria-label={t("sourceCards.panelTitle")}
        className={cn(
          "fixed inset-y-0 end-0 z-50 flex w-full max-w-md flex-col border-s border-border/60 bg-card shadow-2xl",
          "animate-in slide-in-from-end duration-200",
        )}
      >
        <header className="flex items-center justify-between border-b border-border/50 px-4 py-3">
          <h2 className="text-sm font-semibold">{t("sourceCards.panelTitle")}</h2>
          <Button type="button" variant="ghost" size="icon" className="h-8 w-8" onClick={onClose}>
            <X className="h-4 w-4" />
          </Button>
        </header>
        <div className="flex-1 overflow-y-auto px-4 py-4">
          <SourcesEvidencePanel result={result} />
        </div>
      </aside>
    </>
  );
}
