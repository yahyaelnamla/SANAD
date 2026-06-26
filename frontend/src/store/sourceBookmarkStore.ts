"use client";

import { create } from "zustand";
import { persist } from "zustand/middleware";

const SOURCE_BOOKMARK_KEY = "sanad-source-bookmarks";

export interface SourceBookmark {
  sourceId: string;
  title: string;
  author: string;
  type: string;
  citation: string;
  savedAt: string;
}

interface SourceBookmarkState {
  bookmarks: SourceBookmark[];
  toggleSourceBookmark: (source: {
    source_id: string;
    title: string;
    author: string;
    type: string;
    citation: string;
  }) => void;
  isSourceBookmarked: (sourceId: string) => boolean;
}

export const useSourceBookmarkStore = create<SourceBookmarkState>()(
  persist(
    (set, get) => ({
      bookmarks: [],
      toggleSourceBookmark: (source) =>
        set((state) => {
          const exists = state.bookmarks.some((item) => item.sourceId === source.source_id);
          if (exists) {
            return {
              bookmarks: state.bookmarks.filter((item) => item.sourceId !== source.source_id),
            };
          }
          return {
            bookmarks: [
              {
                sourceId: source.source_id,
                title: source.title,
                author: source.author,
                type: source.type,
                citation: source.citation,
                savedAt: new Date().toISOString(),
              },
              ...state.bookmarks,
            ],
          };
        }),
      isSourceBookmarked: (sourceId) => get().bookmarks.some((item) => item.sourceId === sourceId),
    }),
    { name: SOURCE_BOOKMARK_KEY },
  ),
);
