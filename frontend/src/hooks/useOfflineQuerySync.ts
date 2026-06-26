"use client";

import { useEffect, useRef } from "react";

import { useAuth } from "@/hooks/useAuth";
import { useOnlineStatus } from "@/hooks/useOnlineStatus";
import { submitQuery } from "@/services/queryService";
import { useConversationStore } from "@/store/conversationStore";
import { useOfflineQueryStore } from "@/store/offlineQueryStore";

// Flush queued chat questions when connectivity returns.
export function useOfflineQuerySync() {
  const online = useOnlineStatus();
  const { accessToken } = useAuth();
  const queue = useOfflineQueryStore((state) => state.queue);
  const dequeue = useOfflineQueryStore((state) => state.dequeue);
  const syncingRef = useRef(false);

  useEffect(() => {
    if (!online || !accessToken || queue.length === 0 || syncingRef.current) return;

    syncingRef.current = true;

    void (async () => {
      const pending = [...useOfflineQueryStore.getState().queue];
      for (const item of pending) {
        try {
          await submitQuery(
            {
              question: item.question,
              language: item.language,
              session_id: item.session_id,
              conversation_history: item.conversation_history,
              advanced_analysis: item.advanced_analysis,
            },
            accessToken,
          );
          dequeue(item.id);
          useConversationStore.getState().bumpHistory();
        } catch {
          break;
        }
      }
    })().finally(() => {
      syncingRef.current = false;
    });
  }, [online, accessToken, queue.length, dequeue]);
}
