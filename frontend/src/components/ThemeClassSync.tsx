"use client";

import { useTheme } from "next-themes";
import { useEffect } from "react";

import { isDarkTheme, normalizeTheme } from "@/lib/themes";

/**
 * Keeps Tailwind `dark:` variants in sync with multi-theme class names.
 * next-themes sets `night-blue` / `dark-gray`; Tailwind expects `.dark`.
 */
export function ThemeClassSync() {
  const { resolvedTheme } = useTheme();

  useEffect(() => {
    const normalized = normalizeTheme(resolvedTheme);
    const root = document.documentElement;
    root.classList.toggle("dark", isDarkTheme(normalized));
  }, [resolvedTheme]);

  return null;
}
