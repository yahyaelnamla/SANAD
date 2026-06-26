"use client";

import { useCallback, useEffect, useState } from "react";

import { useAuth } from "@/hooks/useAuth";
import {
  getUserPreferences,
  updateUserPreferences,
  type UserPreferences,
  type UserPreferencesUpdate,
} from "@/services/preferencesService";
import { useBookmarkStore } from "@/store/bookmarkStore";

export function useUserPreferences() {
  const { accessToken } = useAuth();
  const [preferences, setPreferences] = useState<UserPreferences | null>(null);
  const [loading, setLoading] = useState(false);
  const hydrateBookmarks = useBookmarkStore((s) => s.hydrateFromServer);

  const load = useCallback(async () => {
    if (!accessToken) return;
    setLoading(true);
    try {
      const prefs = await getUserPreferences(accessToken);
      setPreferences(prefs);
      hydrateBookmarks(prefs.bookmarks);
    } finally {
      setLoading(false);
    }
  }, [accessToken, hydrateBookmarks]);

  useEffect(() => {
    void load();
  }, [load]);

  const save = useCallback(
    async (patch: UserPreferencesUpdate) => {
      if (!accessToken) return;
      const updated = await updateUserPreferences(accessToken, patch);
      setPreferences(updated);
      if (updated.bookmarks) {
        hydrateBookmarks(updated.bookmarks);
      }
      return updated;
    },
    [accessToken, hydrateBookmarks],
  );

  return { preferences, loading, load, save };
}
