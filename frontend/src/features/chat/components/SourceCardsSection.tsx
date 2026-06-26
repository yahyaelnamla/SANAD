"use client";

import { useMemo, useState } from "react";

import { Bookmark, BookmarkCheck, Search } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { CitationChip } from "@/features/chat/components/CitationChip";
import { buildUnifiedSources } from "@/features/chat/components/sourceUtils";
import { useTranslations } from "@/hooks/useTranslations";
import { cn } from "@/lib/utils";
import { useSourceBookmarkStore } from "@/store/sourceBookmarkStore";
import type { QueryResult } from "@/types/query";

interface SourceCardsSectionProps {
  result: QueryResult;
  openSourceIds: string[];
  onOpenSource: (sourceId: string) => void;
  onOpenSourceIdsChange: (ids: string[]) => void;
}

function matchesFilter(entry: ReturnType<typeof buildUnifiedSources>[number], query: string): boolean {
  if (!query) return true;
  const haystack = [
    entry.source.title,
    entry.source.author,
    entry.source.citation,
    ...entry.excerpts,
  ]
    .join(" ")
    .toLowerCase();
  return haystack.includes(query);
}

function primaryExcerpt(entry: ReturnType<typeof buildUnifiedSources>[number]): string {
  return entry.excerpts[0] ?? "";
}

export function SourceCardsSection({
  result,
  openSourceIds,
  onOpenSource,
  onOpenSourceIdsChange,
}: SourceCardsSectionProps) {
  const { t, locale } = useTranslations();
  const isArabic = locale === "ar";
  const [filter, setFilter] = useState("");
  const { toggleSourceBookmark, isSourceBookmarked } = useSourceBookmarkStore();

  const unifiedSources = useMemo(() => buildUnifiedSources(result), [result]);

  const filteredSources = useMemo(() => {
    const query = filter.trim().toLowerCase();
    return unifiedSources.filter((entry) => matchesFilter(entry, query));
  }, [filter, unifiedSources]);

  if (unifiedSources.length === 0) return null;

  return (
    <div className="space-y-3">
      <div className="relative">
        <Search className="pointer-events-none absolute start-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
        <Input
          value={filter}
          onChange={(e) => setFilter(e.target.value)}
          placeholder={t("sourceCards.search")}
          className="border-border/50 bg-background/60 ps-9"
        />
      </div>

      <div className="space-y-3">
        {filteredSources.map(({ source, excerpts }) => {
          const excerpt = primaryExcerpt({ source, excerpts });
          const expanded = openSourceIds.includes(source.source_id);
          const bookmarked = isSourceBookmarked(source.source_id);
          const showSubtitle = source.title.trim() && source.title.trim() !== source.author.trim();

          return (
            <div
              key={source.source_id}
              id={`source-panel-${source.source_id}`}
              className="rounded-xl border border-border/50 bg-card/40 p-4"
            >
              <div className="min-w-0">
                <p className="font-semibold leading-snug">{source.author || source.title}</p>
                {showSubtitle && (
                  <p className="mt-0.5 text-sm text-muted-foreground">{source.title}</p>
                )}
              </div>

              {excerpt && (
                <p className={cn("mt-3 text-sm leading-relaxed text-muted-foreground", isArabic && "font-arabic")}>
                  {expanded ? excerpt : `${excerpt.slice(0, 320)}${excerpt.length > 320 ? "…" : ""}`}
                </p>
              )}

              {expanded && excerpts.length > 1 && (
                <div className="mt-3 space-y-2 border-t border-border/30 pt-3">
                  {excerpts.slice(1).map((text, index) => (
                    <p
                      key={`${source.source_id}-excerpt-${index}`}
                      className={cn("text-sm leading-relaxed text-muted-foreground", isArabic && "font-arabic")}
                    >
                      {text}
                    </p>
                  ))}
                </div>
              )}

              <div className="mt-3 flex flex-wrap items-center gap-2">
                <CitationChip
                  citation={source.citation}
                  sourceId={source.source_url ? undefined : source.source_id}
                  sourceTitle={source.title}
                  sourceAuthor={source.author}
                  snippet={excerpt}
                  url={source.source_url}
                  onOpenSource={source.source_url ? undefined : onOpenSource}
                />
                {excerpt.length > 320 && (
                  <Button
                    type="button"
                    variant="ghost"
                    size="sm"
                    className="h-8 px-2 text-xs"
                    onClick={() =>
                      onOpenSourceIdsChange(
                        expanded
                          ? openSourceIds.filter((id) => id !== source.source_id)
                          : [...openSourceIds, source.source_id],
                      )
                    }
                  >
                    {expanded ? t("sourceCards.collapse") : t("sourceCards.expand")}
                  </Button>
                )}
                <Button
                  type="button"
                  variant="ghost"
                  size="sm"
                  className={cn("h-8 gap-1 px-2 text-xs", bookmarked && "text-cyan-400")}
                  onClick={() => toggleSourceBookmark(source)}
                >
                  {bookmarked ? <BookmarkCheck className="h-3 w-3" /> : <Bookmark className="h-3 w-3" />}
                  {bookmarked ? t("sourceCards.bookmarked") : t("sourceCards.bookmark")}
                </Button>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
