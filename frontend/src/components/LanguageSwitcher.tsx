"use client";

import { Languages } from "lucide-react";

import { Button } from "@/components/ui/button";
import { useTranslations } from "@/hooks/useTranslations";
import { useSettingsStore } from "@/store/settingsStore";
import type { Locale } from "@/types/common";

export function LanguageSwitcher() {
  const { locale, t } = useTranslations();
  const setLocale = useSettingsStore((s) => s.setLocale);

  const toggle = () => {
    const next: Locale = locale === "ar" ? "en" : "ar";
    setLocale(next);
  };

  return (
    <Button
      variant="ghost"
      size="icon"
      onClick={toggle}
      className="inline-flex h-9 w-9 items-center justify-center"
      aria-label={t("settings.language")}
      title={locale === "ar" ? "English" : "العربية"}
    >
      <Languages className="h-4 w-4" />
    </Button>
  );
}
