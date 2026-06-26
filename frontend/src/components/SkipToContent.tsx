"use client";

import { useTranslations } from "@/hooks/useTranslations";

export function SkipToContent() {
  const { t } = useTranslations();

  return (
    <a
      href="#main-content"
      className="sr-only focus:not-sr-only focus:fixed focus:start-4 focus:top-4 focus:z-[200] focus:rounded-lg focus:bg-primary focus:px-4 focus:py-2 focus:text-primary-foreground focus:outline-none focus:ring-2 focus:ring-ring"
    >
      {t("accessibility.skipToContent")}
    </a>
  );
}
