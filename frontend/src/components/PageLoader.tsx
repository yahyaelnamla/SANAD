"use client";

import { Loader2 } from "lucide-react";

import { useTranslations } from "@/hooks/useTranslations";

export function PageLoader() {
  const { t } = useTranslations();

  return (
    <div className="flex min-h-[50vh] flex-col items-center justify-center gap-4 px-6">
      <div className="flex h-14 w-14 items-center justify-center rounded-2xl bg-cyan-500/10 ring-1 ring-cyan-500/20">
        <Loader2 className="h-7 w-7 animate-spin text-cyan-400" />
      </div>
      <p className="text-sm text-muted-foreground">{t("common.loading")}</p>
      <div className="flex w-full max-w-xs flex-col gap-2">
        <div className="h-2 w-full rounded-md shimmer" />
        <div className="h-2 w-4/5 rounded-md shimmer" />
      </div>
    </div>
  );
}
