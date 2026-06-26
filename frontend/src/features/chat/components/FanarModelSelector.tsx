"use client";

import { Bot, Cpu, Sparkles, Zap } from "lucide-react";

import { useTranslations } from "@/hooks/useTranslations";
import { cn } from "@/lib/utils";
import { useSettingsStore, type FanarModelPreference } from "@/store/settingsStore";

const MODEL_OPTIONS: Array<{
  id: FanarModelPreference;
  icon: typeof Sparkles;
  labelKey: string;
  hintKey: string;
}> = [
  { id: "auto", icon: Zap, labelKey: "chat.modelAuto", hintKey: "chat.modelAutoHint" },
  { id: "sadiq", icon: Sparkles, labelKey: "chat.modelSadiq", hintKey: "chat.modelSadiqHint" },
  { id: "c2", icon: Cpu, labelKey: "chat.modelC2", hintKey: "chat.modelC2Hint" },
  { id: "guard", icon: Bot, labelKey: "chat.modelGuard", hintKey: "chat.modelGuardHint" },
];

export function FanarModelSelector() {
  const { t } = useTranslations();
  const model = useSettingsStore((s) => s.fanarModelPreference);
  const setModel = useSettingsStore((s) => s.setFanarModelPreference);

  return (
    <div
      className="theme-segment max-w-full flex-wrap"
      role="group"
      aria-label={t("chat.modelLabel")}
    >
      {MODEL_OPTIONS.map(({ id, icon: Icon, labelKey, hintKey }) => (
        <button
          key={id}
          type="button"
          title={t(hintKey)}
          onClick={() => setModel(id)}
          className={cn(
            "theme-segment-item px-2 py-1.5 text-[11px]",
            model === id && "theme-segment-item-active",
          )}
          aria-pressed={model === id}
        >
          <Icon className="h-3 w-3 shrink-0" />
          {t(labelKey)}
        </button>
      ))}
    </div>
  );
}
