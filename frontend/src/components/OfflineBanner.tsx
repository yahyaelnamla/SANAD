"use client";

import { Clock, WifiOff } from "lucide-react";

import { useOnlineStatus } from "@/hooks/useOnlineStatus";
import { useTranslations } from "@/hooks/useTranslations";
import { useOfflineQueryStore } from "@/store/offlineQueryStore";

export function OfflineBanner() {
  const online = useOnlineStatus();
  const { t } = useTranslations();
  const queueLength = useOfflineQueryStore((state) => state.queue.length);

  if (online && queueLength === 0) return null;

  return (
    <div
      role="status"
      className="flex flex-wrap items-center justify-center gap-2 border-b border-amber-500/30 bg-amber-500/10 px-4 py-2 text-xs text-amber-200"
    >
      {!online && (
        <>
          <WifiOff className="h-3.5 w-3.5 shrink-0" aria-hidden />
          <span>{t("errors.offline")}</span>
        </>
      )}
      {queueLength > 0 && (
        <>
          <Clock className="h-3.5 w-3.5 shrink-0" aria-hidden />
          <span>
            {queueLength} {t("errors.offlineQueuePending")}
          </span>
        </>
      )}
    </div>
  );
}
