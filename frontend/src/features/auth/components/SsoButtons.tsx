"use client";

import { useState } from "react";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { useAuth } from "@/hooks/useAuth";
import { useTranslations } from "@/hooks/useTranslations";
import * as saasService from "@/services/saasService";

interface SsoButtonsProps {
  onSuccess?: (needsOnboarding: boolean) => void;
}

export function SsoButtons({ onSuccess }: SsoButtonsProps) {
  const { t } = useTranslations();
  const { completeSso, isLoading } = useAuth();
  const [demoEmail, setDemoEmail] = useState("");
  const [pendingProvider, setPendingProvider] = useState<"google" | "microsoft" | null>(null);
  const [pendingSessionId, setPendingSessionId] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleProviderClick = async (provider: "google" | "microsoft") => {
    setError(null);
    try {
      const start = await saasService.startSso(provider);
      if (start.mode === "oauth" && start.authorization_url) {
        window.location.href = start.authorization_url;
        return;
      }
      setPendingProvider(provider);
      setPendingSessionId(start.session_id);
    } catch {
      setError(t("auth.ssoFailed"));
    }
  };

  const handleDemoComplete = async () => {
    if (!pendingProvider || !pendingSessionId || !demoEmail.trim()) return;
    setError(null);
    try {
      const needsOnboarding = await completeSso({
        provider: pendingProvider,
        session_id: pendingSessionId,
        email: demoEmail.trim(),
      });
      onSuccess?.(needsOnboarding);
    } catch {
      setError(t("auth.ssoFailed"));
    }
  };

  return (
    <div className="space-y-3">
      <div className="relative py-2 text-center text-xs text-muted-foreground">
        <span className="bg-card px-2">{t("auth.orContinueWith")}</span>
        <div className="absolute inset-x-0 top-1/2 -z-10 border-t border-border/50" />
      </div>
      <div className="grid grid-cols-2 gap-2">
        <Button
          type="button"
          variant="outline"
          disabled={isLoading}
          onClick={() => void handleProviderClick("google")}
        >
          {t("auth.ssoGoogle")}
        </Button>
        <Button
          type="button"
          variant="outline"
          disabled={isLoading}
          onClick={() => void handleProviderClick("microsoft")}
        >
          {t("auth.ssoMicrosoft")}
        </Button>
      </div>
      {pendingSessionId && (
        <div className="space-y-2 rounded-xl border border-cyan-500/20 bg-cyan-500/5 p-3">
          <p className="text-xs text-muted-foreground">{t("auth.ssoDemoHint")}</p>
          <Input
            type="email"
            value={demoEmail}
            onChange={(e) => setDemoEmail(e.target.value)}
            placeholder={t("auth.email")}
          />
          <Button type="button" className="w-full" disabled={isLoading} onClick={() => void handleDemoComplete()}>
            {t("auth.ssoDemoContinue")}
          </Button>
        </div>
      )}
      {error && <p className="text-sm text-destructive">{error}</p>}
    </div>
  );
}
