"use client";

import Link from "next/link";
import { useMemo, useState } from "react";
import { Bookmark, Search, Star, Trash2 } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { useAuth } from "@/hooks/useAuth";
import { useTranslations } from "@/hooks/useTranslations";
import { useUserPreferences } from "@/hooks/useUserPreferences";
import { formatDate } from "@/lib/utils";
import { useBookmarkStore } from "@/store/bookmarkStore";

function useSyncBookmarks() {
  const { accessToken } = useAuth();
  const { save } = useUserPreferences();
  const toServerPayload = useBookmarkStore((s) => s.toServerPayload);

  return async () => {
    if (!accessToken) return;
    await save({ bookmarks: toServerPayload() });
  };
}

export function BookmarksPanel() {
  const { t } = useTranslations();
  const { locale } = useTranslations();
  const bookmarks = useBookmarkStore((state) => state.bookmarks);
  const removeBookmark = useBookmarkStore((state) => state.removeBookmark);
  const updateNote = useBookmarkStore((state) => state.updateNote);
  const toggleFavorite = useBookmarkStore((state) => state.toggleFavorite);
  const syncBookmarks = useSyncBookmarks();
  const [search, setSearch] = useState("");

  const filtered = useMemo(() => {
    const q = search.trim().toLowerCase();
    if (!q) return bookmarks;
    return bookmarks.filter(
      (item) =>
        item.question.toLowerCase().includes(q) ||
        item.summary?.toLowerCase().includes(q) ||
        item.note?.toLowerCase().includes(q) ||
        item.folder?.toLowerCase().includes(q),
    );
  }, [bookmarks, search]);

  if (bookmarks.length === 0) {
    return <p className="py-20 text-center text-muted-foreground">{t("bookmarks.empty")}</p>;
  }

  return (
    <div className="mx-auto max-w-4xl space-y-4">
      <div className="relative">
        <Search className="pointer-events-none absolute start-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
        <Input
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          placeholder={t("bookmarks.search")}
          className="ps-9"
        />
      </div>

      <div className="grid gap-3">
        {filtered.map((item) => (
          <Card key={item.queryId} className="glass-card">
            <CardHeader className="flex flex-row items-start justify-between gap-3 pb-2">
              <CardTitle className="text-base">
                <Link href={`/history/${item.queryId}`} className="hover:text-primary hover:underline">
                  {item.question}
                </Link>
              </CardTitle>
              <div className="flex gap-1">
                <Button
                  variant="ghost"
                  size="icon"
                  className={item.isFavorite ? "text-amber-400" : undefined}
                  aria-label={t("bookmarks.favorite")}
                  onClick={() => {
                    toggleFavorite(item.queryId);
                    void syncBookmarks();
                  }}
                >
                  <Star className="h-4 w-4" />
                </Button>
                <Button
                  variant="ghost"
                  size="icon"
                  onClick={() => {
                    removeBookmark(item.queryId);
                    void syncBookmarks();
                  }}
                >
                  <Trash2 className="h-4 w-4" />
                </Button>
              </div>
            </CardHeader>
            <CardContent className="space-y-3 text-sm text-muted-foreground">
              {item.summary && <p>{item.summary}</p>}
              {item.folder && (
                <p className="text-xs text-cyan-300/80">
                  {t("bookmarks.folder")}: {item.folder}
                </p>
              )}
              <Textarea
                value={item.note ?? ""}
                onChange={(e) => updateNote(item.queryId, e.target.value)}
                onBlur={() => void syncBookmarks()}
                placeholder={t("bookmarks.notePlaceholder")}
                className="min-h-[72px] text-sm"
              />
              <p>{formatDate(item.savedAt, locale)}</p>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}

export function FavoritesPanel() {
  const { t, locale } = useTranslations();
  const bookmarks = useBookmarkStore((state) => state.bookmarks);
  const favorites = bookmarks.filter((b) => b.isFavorite);

  if (favorites.length === 0) {
    return <p className="py-20 text-center text-muted-foreground">{t("favorites.empty")}</p>;
  }

  return (
    <div className="mx-auto grid max-w-4xl gap-3">
      {favorites.map((item) => (
        <Card key={item.queryId} className="glass-card border-amber-500/20">
          <CardHeader className="pb-2">
            <CardTitle className="flex items-center gap-2 text-base">
              <Bookmark className="h-4 w-4 text-amber-400" />
              <Link href={`/history/${item.queryId}`} className="hover:text-primary hover:underline">
                {item.question}
              </Link>
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-2 text-sm text-muted-foreground">
            {item.note && <p className="italic text-foreground/80">{item.note}</p>}
            <p>
              {item.summary ?? t("favorites.noSummary")} · {formatDate(item.savedAt, locale)}
            </p>
          </CardContent>
        </Card>
      ))}
    </div>
  );
}
