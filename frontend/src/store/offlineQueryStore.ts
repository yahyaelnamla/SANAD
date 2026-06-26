"use client";

import { create } from "zustand";
import { persist } from "zustand/middleware";

import { OFFLINE_QUEUE_STORAGE_KEY } from "@/lib/constants";
import type { QueryCreatePayload } from "@/types/query";

export interface QueuedQuery extends QueryCreatePayload {
  id: string;
  queuedAt: string;
}

interface OfflineQueryState {
  queue: QueuedQuery[];
  enqueue: (payload: QueryCreatePayload) => QueuedQuery;
  dequeue: (id: string) => void;
  clear: () => void;
}

export const useOfflineQueryStore = create<OfflineQueryState>()(
  persist(
    (set, get) => ({
      queue: [],
      enqueue: (payload) => {
        const item: QueuedQuery = {
          ...payload,
          id: `${Date.now()}-${Math.random().toString(36).slice(2, 9)}`,
          queuedAt: new Date().toISOString(),
        };
        set({ queue: [...get().queue, item] });
        return item;
      },
      dequeue: (id) => set({ queue: get().queue.filter((item) => item.id !== id) }),
      clear: () => set({ queue: [] }),
    }),
    { name: OFFLINE_QUEUE_STORAGE_KEY },
  ),
);
