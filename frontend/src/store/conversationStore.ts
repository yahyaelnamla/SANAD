"use client";

import { create } from "zustand";
import { persist } from "zustand/middleware";

import { CONVERSATION_STORAGE_KEY } from "@/lib/constants";
import type { ChatMessage } from "@/types/query";

interface ConversationState {
  pinnedQueryIds: string[];
  historyVersion: number;
  sessionId: string;
  ownerUserId: string | null;
  sessionMessages: Record<string, ChatMessage[]>;
  togglePin: (queryId: string) => void;
  isPinned: (queryId: string) => boolean;
  removePinned: (queryIds: string[]) => void;
  bumpHistory: () => void;
  resetSession: () => void;
  clearForUserChange: () => void;
  bindSessionToUser: (userId: string) => void;
  setSessionId: (sessionId: string) => void;
  setSessionMessages: (sessionId: string, messages: ChatMessage[]) => void;
  getSessionMessages: (sessionId: string) => ChatMessage[];
}

function createSessionId() {
  return `sess-${Date.now()}-${Math.random().toString(36).slice(2, 9)}`;
}

export const useConversationStore = create<ConversationState>()(
  persist(
    (set, get) => ({
      pinnedQueryIds: [],
      historyVersion: 0,
      sessionId: createSessionId(),
      ownerUserId: null,
      sessionMessages: {},
      togglePin: (queryId) =>
        set((state) => ({
          pinnedQueryIds: state.pinnedQueryIds.includes(queryId)
            ? state.pinnedQueryIds.filter((id) => id !== queryId)
            : [...state.pinnedQueryIds, queryId],
        })),
      isPinned: (queryId) => get().pinnedQueryIds.includes(queryId),
      removePinned: (queryIds) =>
        set((state) => {
          const remove = new Set(queryIds);
          return {
            pinnedQueryIds: state.pinnedQueryIds.filter((id) => !remove.has(id)),
          };
        }),
      bumpHistory: () => set((state) => ({ historyVersion: state.historyVersion + 1 })),
      clearForUserChange: () =>
        set({
          sessionId: createSessionId(),
          ownerUserId: null,
          sessionMessages: {},
          pinnedQueryIds: [],
        }),
      bindSessionToUser: (userId) => {
        const state = get();
        const legacyCache =
          !state.ownerUserId && Object.keys(state.sessionMessages).length > 0;
        if (state.ownerUserId !== userId || legacyCache) {
          set({
            sessionId: createSessionId(),
            ownerUserId: userId,
            sessionMessages: {},
            pinnedQueryIds: [],
          });
        }
      },
      resetSession: () =>
        set({
          sessionId: createSessionId(),
          sessionMessages: {},
        }),
      setSessionId: (sessionId) => set({ sessionId }),
      setSessionMessages: (sessionId, messages) =>
        set((state) => ({
          sessionMessages: {
            ...state.sessionMessages,
            [sessionId]: messages.filter((message) => !message.loading && !message.error),
          },
        })),
      getSessionMessages: (sessionId) => get().sessionMessages[sessionId] ?? [],
    }),
    {
      name: CONVERSATION_STORAGE_KEY,
      partialize: (state) => ({
        pinnedQueryIds: state.pinnedQueryIds,
        sessionId: state.sessionId,
        ownerUserId: state.ownerUserId,
        sessionMessages: state.sessionMessages,
      }),
    },
  ),
);
