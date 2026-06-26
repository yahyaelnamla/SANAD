"use client";

import { useState } from "react";

import { cn } from "@/lib/utils";

interface CitationChipProps {
  citation: string;
  sourceId?: string;
  sourceTitle?: string;
  sourceAuthor?: string;
  snippet?: string;
  url?: string | null;
  onOpenSource?: (sourceId: string) => void;
  className?: string;
}

export function CitationChip({
  citation,
  sourceId,
  sourceTitle,
  sourceAuthor,
  snippet,
  url,
  onOpenSource,
  className,
}: CitationChipProps) {
  const [previewOpen, setPreviewOpen] = useState(false);
  const externalUrl = url?.startsWith("http") ? url : null;

  const handleClick = () => {
    if (externalUrl) {
      window.open(externalUrl, "_blank", "noopener,noreferrer");
      return;
    }
    if (sourceId && onOpenSource) {
      onOpenSource(sourceId);
    }
  };

  return (
    <span
      className={cn("relative inline-flex", className)}
      onMouseEnter={() => setPreviewOpen(true)}
      onMouseLeave={() => setPreviewOpen(false)}
    >
      <button
        type="button"
        onClick={handleClick}
        className="inline-flex max-w-full items-center rounded-md border border-cyan-500/30 bg-cyan-500/10 px-1.5 py-0.5 text-[11px] font-medium text-cyan-300 transition-colors hover:bg-cyan-500/20 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-cyan-400/50"
        aria-label={citation}
      >
        <span className="truncate">{citation}</span>
      </button>

      {previewOpen && (sourceTitle || snippet) && (
        <div
          role="tooltip"
          className="absolute bottom-full start-0 z-50 mb-2 w-72 rounded-xl border border-border/60 bg-card p-3 text-start shadow-xl"
        >
          <p className="text-xs font-semibold text-foreground">
            {sourceAuthor}
            {sourceTitle && sourceTitle !== sourceAuthor ? ` · ${sourceTitle}` : ""}
          </p>
          {snippet && (
            <p className="mt-2 line-clamp-4 text-xs leading-relaxed text-muted-foreground">{snippet}</p>
          )}
          {externalUrl && (
            <p className="mt-2 text-[10px] text-cyan-400">{externalUrl}</p>
          )}
        </div>
      )}
    </span>
  );
}
