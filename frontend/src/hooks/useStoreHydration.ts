"use client";

import { useEffect, useState } from "react";

import { useAuthStore } from "@/store/authStore";
import { useSettingsStore } from "@/store/settingsStore";

export function useStoreHydration(): boolean {
  const [hydrated, setHydrated] = useState(false);

  useEffect(() => {
    const stores = [useAuthStore, useSettingsStore];

    const markHydrated = () => {
      if (stores.every((store) => store.persist.hasHydrated())) {
        setHydrated(true);
      }
    };

    if (stores.every((store) => store.persist.hasHydrated())) {
      setHydrated(true);
      return;
    }

    const unsubscribers = stores.map((store) => store.persist.onFinishHydration(markHydrated));

    return () => {
      unsubscribers.forEach((unsubscribe) => unsubscribe());
    };
  }, []);

  return hydrated;
}
