"use client";

import { useUserPreferences } from "@/hooks/useUserPreferences";

/** Loads server-side user preferences once authenticated. */
export function PreferencesBootstrap() {
  useUserPreferences();
  return null;
}
