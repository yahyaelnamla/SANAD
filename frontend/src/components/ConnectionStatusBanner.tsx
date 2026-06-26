"use client";

import { AlertTriangle, RefreshCw, WifiOff } from "lucide-react";

import { Button } from "@/components/ui/button";
import { useHealthCheck, type HealthState } from "@/hooks/useHealthCheck";
import { useTranslations } from "@/hooks/useTranslations";

function statusMessage(health: HealthState, t: (key: string) => string): string {
  switch (health) {
    case "degraded":
      return t("connection.degraded");
    case "offline":
      return t("connection.offline");
    default:
      return "";
  }
}

export function ConnectionStatusBanner() {
  const { t } = useTranslations();
  const { health, refresh } = useHealthCheck({ poll: true });

  if (health === "healthy" || health === "checking") return null;

  const message = statusMessage(health, t);
  const isOffline = health === "offline";

  return (
    <div
      role="status"
      className={`flex flex-wrap items-center justify-center gap-2 border-b px-4 py-2 text-xs ${
        isOffline
          ? "border-destructive/30 bg-destructive/10 text-destructive"
          : "border-amber-500/30 bg-amber-500/10 text-amber-200"
      }`}
    >
      {isOffline ? (
        <WifiOff className="h-3.5 w-3.5 shrink-0" aria-hidden />
      ) : (
        <AlertTriangle className="h-3.5 w-3.5 shrink-0" aria-hidden />
      )}
      <span>{message}</span>
      <Button
        type="button"
        variant="ghost"
        size="sm"
        className="h-7 gap-1 px-2 text-inherit hover:bg-white/10"
        onClick={() => void refresh()}
      >
        <RefreshCw className="h-3 w-3" />
        {t("connection.retry")}
      </Button>
    </div>
  );
}
