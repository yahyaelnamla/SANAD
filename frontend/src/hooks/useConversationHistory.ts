"use client";

import { useCallback, useEffect, useMemo, useRef, useState } from "react";

import { useAuth } from "@/hooks/useAuth";
import { useLocale } from "@/hooks/useTranslations";
import { translate } from "@/lib/i18n";
import { ApiClientError } from "@/services/apiClient";
import { listQueries } from "@/services/queryService";
import { useAuthStore } from "@/store/authStore";
import { useConversationStore } from "@/store/conversationStore";
import type { QueryListItem } from "@/types/query";

const RECENT_LIMIT = 8;
const AUTO_RETRY_MS = 5000;
const MAX_AUTO_RETRIES = 3;

function matchesSearch(item: QueryListItem, query: string): boolean {
  const needle = query.trim().toLowerCase();
  if (!needle) return true;
  return (
    item.question.toLowerCase().includes(needle) ||
    (item.display_title?.toLowerCase().includes(needle) ?? false) ||
    (item.summary?.toLowerCase().includes(needle) ?? false) ||
    (item.folder?.toLowerCase().includes(needle) ?? false) ||
    (item.tags?.some((tag) => tag.toLowerCase().includes(needle)) ?? false)
  );
}

export function useConversationHistory(
  searchQuery = "",
  options?: { fullList?: boolean; deferMs?: number; includeArchived?: boolean },
) {
  const { accessToken } = useAuth();
  const locale = useLocale();
  const pinnedQueryIds = useConversationStore((s) => s.pinnedQueryIds);
  const historyVersion = useConversationStore((s) => s.historyVersion);
  const togglePin = useConversationStore((s) => s.togglePin);
  const isPinned = useConversationStore((s) => s.isPinned);
  const [items, setItems] = useState<QueryListItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const itemsRef = useRef(items);
  const refreshInFlightRef = useRef(false);
  const retryTimerRef = useRef<number | null>(null);
  const retryCountRef = useRef(0);
  itemsRef.current = items;

  const fullList = options?.fullList ?? false;
  const includeArchived = options?.includeArchived ?? false;
  const deferMs = options?.deferMs ?? 400;

  const refresh = useCallback(async () => {
    if (!accessToken) {
      setItems([]);
      setLoading(false);
      setRefreshing(false);
      return;
    }
    if (refreshInFlightRef.current) return;
    refreshInFlightRef.current = true;
    setError(null);
    const isInitialLoad = itemsRef.current.length === 0;
    if (isInitialLoad) {
      setLoading(true);
    } else {
      setRefreshing(true);
    }
    try {
      const response = await listQueries(
        accessToken,
        fullList ? 100 : 50,
        0,
        includeArchived,
      );
      setItems(response.items);
      retryCountRef.current = 0;
    } catch (err) {
      if (err instanceof ApiClientError) {
        if (err.status === 401 || err.code === "UNAUTHORIZED") {
          useAuthStore.getState().logout();
          setItems([]);
          setError(null);
          return;
        }
        if (err.status === 0 || err.code === "NETWORK_ERROR") {
          setError(translate(locale, "sidebar.historyUnavailable"));
          if (retryCountRef.current < MAX_AUTO_RETRIES) {
            retryCountRef.current += 1;
            retryTimerRef.current = window.setTimeout(() => {
              refreshInFlightRef.current = false;
              void refresh();
            }, AUTO_RETRY_MS);
            return;
          }
        } else {
          setError(translate(locale, "sidebar.historyError"));
        }
      } else {
        setError(translate(locale, "sidebar.historyError"));
      }
    } finally {
      refreshInFlightRef.current = false;
      setLoading(false);
      setRefreshing(false);
    }
  }, [accessToken, fullList, includeArchived, locale]);

  useEffect(() => {
    if (!accessToken) {
      setItems([]);
      setLoading(false);
      return;
    }

    let cancelled = false;
    const timer = window.setTimeout(() => {
      if (!cancelled) void refresh();
    }, deferMs);

    return () => {
      cancelled = true;
      window.clearTimeout(timer);
      if (retryTimerRef.current != null) {
        window.clearTimeout(retryTimerRef.current);
        retryTimerRef.current = null;
      }
    };
  }, [refresh, accessToken, deferMs, historyVersion]);

  const filtered = useMemo(
    () => items.filter((item) => matchesSearch(item, searchQuery)),
    [items, searchQuery],
  );

  const pinned = useMemo(
    () =>
      filtered
        .filter((item) => pinnedQueryIds.includes(item.query_id))
        .sort(
          (a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime(),
        ),
    [filtered, pinnedQueryIds],
  );

  const recent = useMemo(() => {
    const sorted = filtered
      .filter((item) => !pinnedQueryIds.includes(item.query_id))
      .sort(
        (a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime(),
      );
    return fullList ? sorted : sorted.slice(0, RECENT_LIMIT);
  }, [filtered, pinnedQueryIds, fullList]);

  return {
    pinned,
    recent,
    loading,
    refreshing,
    error,
    refresh,
    togglePin,
    isPinned,
  };
}
