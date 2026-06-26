"use client";

import Link from "next/link";
import { useEffect, useState } from "react";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Switch } from "@/components/ui/switch";
import { useTranslations } from "@/hooks/useTranslations";
import { useUserPreferences } from "@/hooks/useUserPreferences";
import type { MadhhabChoice } from "@/services/preferencesService";
import { useSettingsStore } from "@/store/settingsStore";

const MADHHABS: MadhhabChoice[] = ["general", "hanafi", "maliki", "shafii", "hanbali"];

export function UserPreferencesSettings() {
  const { t } = useTranslations();
  const { preferences, save, loading } = useUserPreferences();
  const evaluationMode = useSettingsStore((s) => s.evaluationMode);
  const setEvaluationMode = useSettingsStore((s) => s.setEvaluationMode);
  const [madhhab, setMadhhab] = useState<MadhhabChoice>("general");
  const [displayName, setDisplayName] = useState("");
  const [scholars, setScholars] = useState("");
  const [saved, setSaved] = useState(false);

  useEffect(() => {
    if (!preferences) return;
    setMadhhab(preferences.preferred_madhhab ?? "general");
    setDisplayName(preferences.display_name ?? "");
    setScholars(preferences.favorite_scholars.join(", "));
  }, [preferences]);

  const handleSave = async () => {
    await save({
      display_name: displayName.trim() || null,
      preferred_madhhab: madhhab,
      favorite_scholars: scholars
        .split(",")
        .map((s) => s.trim())
        .filter(Boolean)
        .slice(0, 20),
    });
    setSaved(true);
    window.setTimeout(() => setSaved(false), 2000);
  };

  return (
    <div className="space-y-6">
      <div className="space-y-2">
        <p className="text-sm font-medium">{t("settings.displayName")}</p>
        <p className="text-xs text-muted-foreground">{t("settings.displayNameHint")}</p>
        <Input
          value={displayName}
          onChange={(e) => setDisplayName(e.target.value)}
          placeholder={t("settings.displayNamePlaceholder")}
          maxLength={80}
        />
      </div>

      <div className="space-y-2">
        <p className="text-sm font-medium">{t("settings.preferredMadhhab")}</p>
        <p className="text-xs text-muted-foreground">{t("settings.preferredMadhhabHint")}</p>
        <select
          value={madhhab}
          onChange={(e) => setMadhhab(e.target.value as MadhhabChoice)}
          className="h-10 w-full rounded-xl border border-border/50 bg-background/60 px-3 text-sm"
          aria-label={t("settings.preferredMadhhab")}
        >
          {MADHHABS.map((value) => (
            <option key={value} value={value}>
              {t(`settings.madhhab.${value}`)}
            </option>
          ))}
        </select>
      </div>

      <div className="space-y-2">
        <p className="text-sm font-medium">{t("settings.favoriteScholars")}</p>
        <p className="text-xs text-muted-foreground">{t("settings.favoriteScholarsHint")}</p>
        <Input
          value={scholars}
          onChange={(e) => setScholars(e.target.value)}
          placeholder={t("settings.favoriteScholarsPlaceholder")}
        />
      </div>

      <Button type="button" onClick={() => void handleSave()} disabled={loading}>
        {saved ? t("settings.saved") : t("settings.savePreferences")}
      </Button>

      <div className="flex flex-col gap-3 border-t border-border/40 pt-6 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <p className="text-sm font-medium">{t("settings.evaluationMode")}</p>
          <p className="text-xs text-muted-foreground">{t("settings.evaluationModeHint")}</p>
        </div>
        <Switch
          checked={evaluationMode}
          onCheckedChange={setEvaluationMode}
          aria-label={t("settings.evaluationMode")}
        />
      </div>

      {evaluationMode && (
        <div className="rounded-xl border border-cyan-500/20 bg-cyan-500/5 p-4">
          <p className="text-sm font-medium">{t("evaluation.judgeDashboardLink")}</p>
          <p className="mt-1 text-xs text-muted-foreground">{t("evaluation.judgeDashboardHint")}</p>
          <Button type="button" variant="secondary" size="sm" className="mt-3" asChild>
            <Link href="/evaluation">{t("evaluation.openDashboard")}</Link>
          </Button>
        </div>
      )}
    </div>
  );
}
