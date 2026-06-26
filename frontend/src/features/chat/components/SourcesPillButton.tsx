"use client";

import { useMemo } from "react";

import { Button } from "@/components/ui/button";
import { buildUnifiedSources } from "@/features/chat/components/sourceUtils";
import { useTranslations } from "@/hooks/useTranslations";
import { cn } from "@/lib/utils";
import type { QueryResult } from "@/types/query";

interface SourcesPillButtonProps {
  result: QueryResult;
  onClick: () => void;
  className?: string;
}

function faviconUrl(sourceUrl?: string): string | null {
  if (!sourceUrl) return null;
  try {
    const hostname = new URL(sourceUrl).hostname.replace(/^www\./, "");
    return `https://www.google.com/s2/favicons?domain=${hostname}&sz=32`;
  } catch {
    return null;
  }
}

export function SourcesPillButton({ result, onClick, className }: SourcesPillButtonProps) {
  const { locale } = useTranslations();
  const unified = useMemo(() => buildUnifiedSources(result), [result]);

  if (unified.length === 0) return null;

  const preview = unified.slice(0, 4);

  return (
    <Button
      type="button"
      variant="outline"
      size="sm"
      className={cn(
        "h-8 gap-2 rounded-full border-border/60 bg-background/60 px-3 text-xs font-medium",
        className,
      )}
      onClick={onClick}
    >
      <span className="flex -space-x-1.5 rtl:space-x-reverse">
        {preview.map(({ source }) => {
          const icon = faviconUrl(source.source_url ?? undefined);
          return (
            <span
              key={source.source_id}
              className="inline-flex h-5 w-5 items-center justify-center overflow-hidden rounded-full border border-border/60 bg-muted"
            >
              {icon ? (
                // eslint-disable-next-line @next/next/no-img-element
                <img src={icon} alt="" className="h-3.5 w-3.5" />
              ) : (
                <span className="text-[9px] font-bold text-muted-foreground">
                  {(source.author || source.title || "?").slice(0, 1)}
                </span>
              )}
            </span>
          );
        })}
      </span>
      {locale === "ar" ? `${unified.length} مصادر` : `${unified.length} Sources`}
    </Button>
  );
}
