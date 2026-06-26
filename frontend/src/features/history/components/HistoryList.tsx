"use client";

import Link from "next/link";
import { Pin, PinOff, Search, Trash2, X } from "lucide-react";
import { useCallback, useMemo, useState } from "react";

import { PageLayout } from "@/components/PageGuide";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { HistoryQueryActions } from "@/features/history/components/HistoryQueryActions";
import { useAuth } from "@/hooks/useAuth";
import { useConversationHistory } from "@/hooks/useConversationHistory";
import { useTranslations } from "@/hooks/useTranslations";
import { cn, formatDate } from "@/lib/utils";
import { ApiClientError } from "@/services/apiClient";
import { deleteQuery } from "@/services/queryService";
import { useConversationStore } from "@/store/conversationStore";
import { queryDisplayTitle, type QueryListItem } from "@/types/query";

type HistoryFilter = "all" | "completed" | "refused" | "pinned" | "archived";

const HISTORY_PAGE_SIZE = 30;

function matchesFilter(item: QueryListItem, filter: HistoryFilter, pinnedIds: Set<string>): boolean {
  if (filter === "archived") return Boolean(item.archived);
  if (item.archived) return false;
  if (filter === "pinned") return pinnedIds.has(item.query_id);
  if (filter === "completed") return !item.refused;
  if (filter === "refused") return item.refused;
  return true;
}

export function HistoryList() {
  const { t, locale } = useTranslations();
  const { accessToken } = useAuth();
  const [searchQuery, setSearchQuery] = useState("");
  const [filter, setFilter] = useState<HistoryFilter>("all");
  const [visibleCount, setVisibleCount] = useState(HISTORY_PAGE_SIZE);
  const [selectedIds, setSelectedIds] = useState<Set<string>>(new Set());
  const [bulkDeleting, setBulkDeleting] = useState(false);
  const [bulkError, setBulkError] = useState<string | null>(null);
  const pinnedQueryIds = useConversationStore((s) => s.pinnedQueryIds);
  const bumpHistory = useConversationStore((s) => s.bumpHistory);
  const removePinned = useConversationStore((s) => s.removePinned);
  const pinnedIdSet = useMemo(() => new Set(pinnedQueryIds), [pinnedQueryIds]);
  const { pinned, recent, loading, error, refresh, togglePin, isPinned } = useConversationHistory(searchQuery, {
    fullList: true,
    includeArchived: filter === "archived",
  });

  const handleUpdated = useCallback(() => {
    void refresh();
  }, [refresh]);

  const allItems = useMemo(() => {
    const merged = [...pinned, ...recent];
    const seen = new Set<string>();
    return merged.filter((item) => {
      if (seen.has(item.query_id)) return false;
      seen.add(item.query_id);
      return true;
    });
  }, [pinned, recent]);

  const filteredItems = useMemo(
    () => allItems.filter((item) => matchesFilter(item, filter, pinnedIdSet)),
    [allItems, filter, pinnedIdSet],
  );

  const visibleItems = useMemo(
    () => filteredItems.slice(0, visibleCount),
    [filteredItems, visibleCount],
  );

  const hasMore = filteredItems.length > visibleItems.length;
  const allVisibleSelected =
    visibleItems.length > 0 && visibleItems.every((item) => selectedIds.has(item.query_id));

  const filters: { id: HistoryFilter; label: string }[] = [
    { id: "all", label: t("history.filterAll") },
    { id: "pinned", label: t("history.filterPinned") },
    { id: "completed", label: t("history.filterCompleted") },
    { id: "refused", label: t("history.filterRefused") },
    { id: "archived", label: t("history.filterArchived") },
  ];

  const toggleSelected = (queryId: string) => {
    setSelectedIds((prev) => {
      const next = new Set(prev);
      if (next.has(queryId)) next.delete(queryId);
      else next.add(queryId);
      return next;
    });
  };

  const toggleSelectAllVisible = () => {
    if (allVisibleSelected) {
      setSelectedIds((prev) => {
        const next = new Set(prev);
        visibleItems.forEach((item) => next.delete(item.query_id));
        return next;
      });
      return;
    }
    setSelectedIds((prev) => {
      const next = new Set(prev);
      visibleItems.forEach((item) => next.add(item.query_id));
      return next;
    });
  };

  const runBulkDelete = async (ids: string[], confirmMessage: string) => {
    if (!accessToken || ids.length === 0) return;
    if (!window.confirm(confirmMessage)) return;
    setBulkDeleting(true);
    setBulkError(null);
    const failed: string[] = [];
    try {
      for (const id of ids) {
        try {
          await deleteQuery(id, accessToken);
        } catch {
          failed.push(id);
        }
      }
      const deleted = ids.filter((id) => !failed.includes(id));
      if (deleted.length > 0) {
        removePinned(deleted);
        setSelectedIds((prev) => {
          const next = new Set(prev);
          deleted.forEach((id) => next.delete(id));
          return next;
        });
        bumpHistory();
        await refresh();
      }
      if (failed.length > 0) {
        setBulkError(t("history.deletePartialError").replace("{count}", String(failed.length)));
      }
    } catch (err) {
      setBulkError(err instanceof ApiClientError ? err.message : t("errors.generic"));
    } finally {
      setBulkDeleting(false);
    }
  };

  const handleDeleteSelected = () => {
    void runBulkDelete(Array.from(selectedIds), t("history.deleteSelectedConfirm"));
  };

  const handleDeleteAll = () => {
    void runBulkDelete(
      filteredItems.map((item) => item.query_id),
      t("history.deleteAllConfirm"),
    );
  };

  if (loading && allItems.length === 0) {
    return (
      <div className="mx-auto w-full max-w-4xl space-y-3 px-2">
        {Array.from({ length: 4 }).map((_, index) => (
          <div key={index} className="h-24 rounded-2xl skeleton-block" />
        ))}
      </div>
    );
  }

  if (error && allItems.length === 0) {
    return <p className="text-center text-destructive">{error}</p>;
  }

  return (
    <PageLayout guideKey="history" className="page-shell space-y-4">
      <div className="glass-card space-y-3 rounded-2xl border border-border/50 p-4">
        <div className="relative">
          <Search className="pointer-events-none absolute start-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
          <Input
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder={t("history.searchPlaceholder")}
            className="border-border/50 bg-background/60 ps-9 pe-9"
            aria-label={t("history.searchPlaceholder")}
          />
          {searchQuery && (
            <Button
              type="button"
              variant="ghost"
              size="icon"
              className="absolute end-1 top-1/2 h-7 w-7 -translate-y-1/2"
              onClick={() => setSearchQuery("")}
              aria-label={t("chat.clearSearch")}
            >
              <X className="h-3.5 w-3.5" />
            </Button>
          )}
        </div>

        <div className="flex flex-wrap gap-2">
          {filters.map((item) => (
            <Button
              key={item.id}
              type="button"
              size="sm"
              variant={filter === item.id ? "default" : "outline"}
              className="h-8 rounded-full px-3 text-xs"
              onClick={() => {
                setFilter(item.id);
                setVisibleCount(HISTORY_PAGE_SIZE);
                setSelectedIds(new Set());
              }}
            >
              {item.label}
            </Button>
          ))}
        </div>

        {filteredItems.length > 0 && (
          <div className="flex flex-wrap items-center gap-2 border-t border-border/40 pt-3">
            <Button
              type="button"
              size="sm"
              variant="outline"
              className="h-8 text-xs"
              onClick={toggleSelectAllVisible}
              disabled={bulkDeleting}
            >
              {allVisibleSelected ? t("history.deselectAll") : t("history.selectAll")}
            </Button>
            {selectedIds.size > 0 && (
              <Button
                type="button"
                size="sm"
                variant="destructive"
                className="h-8 gap-1.5 text-xs"
                onClick={() => void handleDeleteSelected()}
                disabled={bulkDeleting}
              >
                <Trash2 className="h-3.5 w-3.5" />
                {bulkDeleting ? t("common.loading") : `${t("history.deleteSelected")} (${selectedIds.size})`}
              </Button>
            )}
            <Button
              type="button"
              size="sm"
              variant="ghost"
              className="h-8 text-xs text-destructive hover:text-destructive"
              onClick={() => void handleDeleteAll()}
              disabled={bulkDeleting}
            >
              {t("history.deleteAll")}
            </Button>
          </div>
        )}

        {bulkError && <p className="text-sm text-destructive">{bulkError}</p>}
      </div>

      {allItems.length === 0 ? (
        <p className="text-center text-muted-foreground">
          {t("history.empty")}{" "}
          <Link href="/chat" className="text-primary underline">
            {t("nav.chat")}
          </Link>
        </p>
      ) : filteredItems.length === 0 ? (
        <p className="text-center text-muted-foreground">{t("history.noResults")}</p>
      ) : (
        <div className="grid gap-3">
          {bulkDeleting && (
            <p className="text-center text-sm text-muted-foreground">{t("history.deleting")}</p>
          )}
          {visibleItems.map((item) => (
            <Card key={item.query_id} className={cnCard(item.archived, selectedIds.has(item.query_id))}>
              <CardHeader className="pb-2">
                <div className="flex flex-wrap items-start justify-between gap-2">
                  <div className="flex min-w-0 flex-1 items-start gap-3">
                    <input
                      type="checkbox"
                      checked={selectedIds.has(item.query_id)}
                      onChange={() => toggleSelected(item.query_id)}
                      disabled={bulkDeleting}
                      className="mt-1 h-4 w-4 shrink-0 rounded border-border accent-cyan-500"
                      aria-label={t("history.selectAll")}
                    />
                    <CardTitle className="min-w-0 flex-1 text-base font-medium">
                      <Link
                        href={
                          item.session_id
                            ? `/chat?session=${encodeURIComponent(item.session_id)}`
                            : `/history/${item.query_id}`
                        }
                        className="hover:text-primary hover:underline"
                      >
                        {queryDisplayTitle(item)}
                      </Link>
                      {item.session_id && item.turn_count && item.turn_count > 1 && (
                        <p className="mt-1 text-xs font-normal text-muted-foreground">
                          {item.turn_count} {locale === "ar" ? "رسائل" : "turns"}
                        </p>
                      )}
                    </CardTitle>
                  </div>
                  <div className="flex items-center gap-2">
                    {item.archived && (
                      <Badge variant="outline">{t("history.archivedBadge")}</Badge>
                    )}
                    {isPinned(item.query_id) && (
                      <Badge variant="outline" className="text-cyan-400">
                        {t("sidebar.pinned")}
                      </Badge>
                    )}
                    <Badge variant={item.refused ? "destructive" : "secondary"}>
                      {item.refused ? t("history.refused") : t("history.completed")}
                    </Badge>
                    <Button
                      type="button"
                      variant="ghost"
                      size="icon"
                      className="h-8 w-8"
                      onClick={() => togglePin(item.query_id)}
                      disabled={bulkDeleting}
                      aria-label={isPinned(item.query_id) ? t("history.unpin") : t("history.pin")}
                    >
                      {isPinned(item.query_id) ? (
                        <PinOff className="h-4 w-4" />
                      ) : (
                        <Pin className="h-4 w-4" />
                      )}
                    </Button>
                  </div>
                </div>
              </CardHeader>
              <CardContent className="space-y-2 text-sm text-muted-foreground">
                {item.display_title && item.display_title !== item.question && (
                  <p className="line-clamp-1 text-xs opacity-70">{item.question}</p>
                )}
                {item.summary && <p className="line-clamp-2">{item.summary}</p>}
                <p>{formatDate(item.created_at, locale)}</p>
                <HistoryQueryActions item={item} onUpdated={handleUpdated} />
              </CardContent>
            </Card>
          ))}
          {hasMore && (
            <Button
              type="button"
              variant="outline"
              className="touch-target w-full"
              onClick={() => setVisibleCount((count) => count + HISTORY_PAGE_SIZE)}
              disabled={bulkDeleting}
            >
              {t("history.loadMore")} ({filteredItems.length - visibleItems.length})
            </Button>
          )}
        </div>
      )}
    </PageLayout>
  );
}

function cnCard(archived?: boolean, selected?: boolean) {
  const base = "transition-shadow hover:shadow-md";
  if (selected) return `${base} border-cyan-500/40 ring-1 ring-cyan-500/20`;
  if (archived) return `${base} border-border/40 opacity-80`;
  return base;
}
