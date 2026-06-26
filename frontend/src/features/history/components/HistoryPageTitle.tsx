"use client";

import { useTranslations } from "@/hooks/useTranslations";

export function HistoryPageTitle() {
  const { t } = useTranslations();
  return <h1 className="text-center text-2xl font-bold">{t("history.title")}</h1>;
}
