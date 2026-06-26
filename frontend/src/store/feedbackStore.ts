"use client";

import { create } from "zustand";
import { persist } from "zustand/middleware";

import { FEEDBACK_STORAGE_KEY } from "@/lib/constants";

export type FeedbackRating = "up" | "down";

interface FeedbackState {
  ratings: Record<string, FeedbackRating>;
  setFeedback: (queryId: string, rating: FeedbackRating) => void;
  getFeedback: (queryId: string) => FeedbackRating | undefined;
}

export const useFeedbackStore = create<FeedbackState>()(
  persist(
    (set, get) => ({
      ratings: {},
      setFeedback: (queryId, rating) =>
        set((state) => ({
          ratings: { ...state.ratings, [queryId]: rating },
        })),
      getFeedback: (queryId) => get().ratings[queryId],
    }),
    { name: FEEDBACK_STORAGE_KEY },
  ),
);
