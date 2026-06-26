"use client";

import { FlaskConical, Sparkles } from "lucide-react";

import { useTranslations } from "@/hooks/useTranslations";
import { cn } from "@/lib/utils";
import { useSettingsStore } from "@/store/settingsStore";

export function ChatModeToggle() {
  const { t } = useTranslations();
  const advanced = useSettingsStore((s) => s.advancedAnalysisMode);
  const setAdvanced = useSettingsStore((s) => s.setAdvancedAnalysisMode);

  return (
    <div className="theme-segment" role="group" aria-label={t("chat.modeLabel")}>
      <button
        type="button"
        onClick={() => setAdvanced(false)}
        className={cn("theme-segment-item", !advanced && "theme-segment-item-active")}
        aria-pressed={!advanced}
      >
        <Sparkles className="h-3.5 w-3.5 shrink-0" />
        {t("chat.modeStandard")}
      </button>
      <button
        type="button"
        onClick={() => setAdvanced(true)}
        className={cn("theme-segment-item", advanced && "theme-segment-item-active")}
        aria-pressed={advanced}
        title={t("settings.advancedAnalysisHint")}
      >
        <FlaskConical className="h-3.5 w-3.5 shrink-0" />
        {t("chat.modeAdvanced")}
      </button>
    </div>
  );
}
