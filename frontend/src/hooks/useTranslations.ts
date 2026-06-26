"use client";

import { useCallback } from "react";

import { translate } from "@/lib/i18n";
import { useSettingsStore } from "@/store/settingsStore";
import type { Locale } from "@/types/common";

export function useTranslations() {
  const locale = useSettingsStore((s) => s.locale);
  const t = useCallback((key: string) => translate(locale, key), [locale]);
  return { locale, t };
}

export function useLocale(): Locale {
  return useSettingsStore((s) => s.locale);
}
