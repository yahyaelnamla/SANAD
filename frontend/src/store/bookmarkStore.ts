"use client";

import { create } from "zustand";
import { persist } from "zustand/middleware";

import { BOOKMARK_STORAGE_KEY } from "@/lib/constants";
import type { SavedBookmark } from "@/services/preferencesService";
import type { QueryResult } from "@/types/query";

export interface BookmarkEntry {
  queryId: string;
  question: string;
  summary: string | null;
  savedAt: string;
  note?: string | null;
  folder?: string | null;
  isFavorite?: boolean;
}

interface BookmarkState {
  bookmarks: BookmarkEntry[];
  toggleBookmark: (result: QueryResult) => void;
  toggleFavorite: (queryId: string) => void;
  updateNote: (queryId: string, note: string) => void;
  updateFolder: (queryId: string, folder: string) => void;
  isBookmarked: (queryId: string) => boolean;
  isFavorite: (queryId: string) => boolean;
  removeBookmark: (queryId: string) => void;
  hydrateFromServer: (items: SavedBookmark[]) => void;
  toServerPayload: () => SavedBookmark[];
}

function toEntry(item: SavedBookmark): BookmarkEntry {
  return {
    queryId: item.query_id,
    question: item.question,
    summary: item.summary ?? null,
    savedAt: item.saved_at ?? new Date().toISOString(),
    note: item.note ?? null,
    folder: item.folder ?? null,
    isFavorite: item.is_favorite ?? false,
  };
}

export const useBookmarkStore = create<BookmarkState>()(
  persist(
    (set, get) => ({
      bookmarks: [],
      toggleBookmark: (result) =>
        set((state) => {
          const exists = state.bookmarks.some((b) => b.queryId === result.query_id);
          if (exists) {
            return {
              bookmarks: state.bookmarks.filter((b) => b.queryId !== result.query_id),
            };
          }
          return {
            bookmarks: [
              {
                queryId: result.query_id,
                question: result.question,
                summary: result.summary,
                savedAt: new Date().toISOString(),
                note: null,
                folder: null,
                isFavorite: false,
              },
              ...state.bookmarks,
            ],
          };
        }),
      toggleFavorite: (queryId) =>
        set((state) => ({
          bookmarks: state.bookmarks.map((b) =>
            b.queryId === queryId ? { ...b, isFavorite: !b.isFavorite } : b,
          ),
        })),
      updateNote: (queryId, note) =>
        set((state) => ({
          bookmarks: state.bookmarks.map((b) => (b.queryId === queryId ? { ...b, note } : b)),
        })),
      updateFolder: (queryId, folder) =>
        set((state) => ({
          bookmarks: state.bookmarks.map((b) =>
            b.queryId === queryId ? { ...b, folder: folder.trim() || null } : b,
          ),
        })),
      isBookmarked: (queryId) => get().bookmarks.some((b) => b.queryId === queryId),
      isFavorite: (queryId) => get().bookmarks.some((b) => b.queryId === queryId && b.isFavorite),
      removeBookmark: (queryId) =>
        set((state) => ({
          bookmarks: state.bookmarks.filter((b) => b.queryId !== queryId),
        })),
      hydrateFromServer: (items) => {
        if (!items.length) return;
        set((state) => {
          const merged = new Map(state.bookmarks.map((b) => [b.queryId, b]));
          for (const item of items.map(toEntry)) {
            const existing = merged.get(item.queryId);
            merged.set(item.queryId, existing ? { ...existing, ...item } : item);
          }
          return { bookmarks: Array.from(merged.values()) };
        });
      },
      toServerPayload: () =>
        get().bookmarks.map((b) => ({
          query_id: b.queryId,
          question: b.question,
          summary: b.summary,
          note: b.note ?? null,
          folder: b.folder ?? null,
          is_favorite: Boolean(b.isFavorite),
          saved_at: b.savedAt,
        })),
    }),
    { name: BOOKMARK_STORAGE_KEY },
  ),
);
