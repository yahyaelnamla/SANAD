"use client";

import { Download, X } from "lucide-react";
import { useEffect, useState } from "react";

import { Button } from "@/components/ui/button";
import { useTranslations } from "@/hooks/useTranslations";

interface BeforeInstallPromptEvent extends Event {
  prompt: () => Promise<void>;
  userChoice: Promise<{ outcome: "accepted" | "dismissed" }>;
}

export function PwaInstallPrompt() {
  const { t } = useTranslations();
  const [deferred, setDeferred] = useState<BeforeInstallPromptEvent | null>(null);
  const [dismissed, setDismissed] = useState(false);

  useEffect(() => {
    if (typeof window === "undefined") return;
    const dismissedKey = "sanad-pwa-install-dismissed";
    if (localStorage.getItem(dismissedKey) === "1") {
      setDismissed(true);
      return;
    }

    const handler = (event: Event) => {
      event.preventDefault();
      setDeferred(event as BeforeInstallPromptEvent);
    };

    window.addEventListener("beforeinstallprompt", handler);
    return () => window.removeEventListener("beforeinstallprompt", handler);
  }, []);

  if (!deferred || dismissed) return null;

  const handleInstall = async () => {
    await deferred.prompt();
    await deferred.userChoice;
    setDeferred(null);
    localStorage.setItem("sanad-pwa-install-dismissed", "1");
  };

  const handleDismiss = () => {
    setDismissed(true);
    setDeferred(null);
    localStorage.setItem("sanad-pwa-install-dismissed", "1");
  };

  return (
    <div className="fixed bottom-4 start-4 end-4 z-50 mx-auto max-w-md rounded-xl border border-cyan-500/30 bg-card/95 p-4 shadow-xl backdrop-blur-md sm:start-auto sm:end-4">
      <div className="flex items-start gap-3">
        <div className="flex-1">
          <p className="text-sm font-semibold">{t("pwa.installTitle")}</p>
          <p className="mt-1 text-xs text-muted-foreground">{t("pwa.installHint")}</p>
        </div>
        <button
          type="button"
          onClick={handleDismiss}
          className="touch-target rounded-lg p-1 text-muted-foreground hover:bg-muted/40"
          aria-label={t("pwa.dismiss")}
        >
          <X className="h-4 w-4" />
        </button>
      </div>
      <Button type="button" size="sm" className="mt-3 w-full gap-2 sm:w-auto" onClick={() => void handleInstall()}>
        <Download className="h-4 w-4" />
        {t("pwa.installAction")}
      </Button>
    </div>
  );
}
