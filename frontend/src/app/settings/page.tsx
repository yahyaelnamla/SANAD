"use client";

import { AuthGuard } from "@/features/auth/components/AuthGuard";
import { BillingSettings } from "@/features/billing/components/BillingSettings";
import { PageLayout } from "@/components/PageGuide";
import { UserPreferencesSettings } from "@/features/settings/components/UserPreferencesSettings";
import { LanguageSwitcher } from "@/components/LanguageSwitcher";
import { ThemeSelector } from "@/components/ThemeSelector";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Switch } from "@/components/ui/switch";
import { useTranslations } from "@/hooks/useTranslations";
import { useUserPreferences } from "@/hooks/useUserPreferences";
import { useSettingsStore } from "@/store/settingsStore";

export default function SettingsPage() {
  return (
    <AuthGuard>
      <SettingsContent />
    </AuthGuard>
  );
}

function SettingsContent() {
  const { t } = useTranslations();
  const { preferences } = useUserPreferences();
  const showAdvancedMetrics = useSettingsStore((s) => s.showAdvancedMetrics);
  const setShowAdvancedMetrics = useSettingsStore((s) => s.setShowAdvancedMetrics);
  const advancedAnalysisMode = useSettingsStore((s) => s.advancedAnalysisMode);
  const setAdvancedAnalysisMode = useSettingsStore((s) => s.setAdvancedAnalysisMode);

  return (
    <PageLayout guideKey="settings" className="page-shell space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">{t("pages.settings.title")}</h1>
        <p className="mt-1 text-sm text-muted-foreground">{t("pages.settings.description")}</p>
      </div>

      <Card className="glass-card border-border/50">
        <CardHeader>
          <CardTitle className="text-base">{t("pages.settings.preferences")}</CardTitle>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
            <div>
              <p className="text-sm font-medium">{t("settings.language")}</p>
              <p className="text-xs text-muted-foreground">{t("pages.settings.languageHint")}</p>
            </div>
            <LanguageSwitcher />
          </div>
          <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
            <div>
              <p className="text-sm font-medium">{t("settings.theme")}</p>
              <p className="text-xs text-muted-foreground">{t("pages.settings.themeHint")}</p>
            </div>
            <ThemeSelector variant="segmented" />
          </div>
          <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
            <div>
              <p className="text-sm font-medium">{t("settings.advancedMetrics")}</p>
              <p className="text-xs text-muted-foreground">{t("settings.advancedMetricsHint")}</p>
            </div>
            <Switch
              checked={showAdvancedMetrics}
              onCheckedChange={setShowAdvancedMetrics}
              aria-label={t("settings.advancedMetrics")}
            />
          </div>
          <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
            <div>
              <p className="text-sm font-medium">{t("settings.advancedAnalysis")}</p>
              <p className="text-xs text-muted-foreground">{t("settings.advancedAnalysisHint")}</p>
            </div>
            <Switch
              checked={advancedAnalysisMode}
              onCheckedChange={setAdvancedAnalysisMode}
              aria-label={t("settings.advancedAnalysis")}
            />
          </div>
          <UserPreferencesSettings />
        </CardContent>
      </Card>

      <BillingSettings />

      {preferences?.recent_topics && preferences.recent_topics.length > 0 && (
        <Card className="glass-card border-border/50">
          <CardHeader>
            <CardTitle className="text-base">{t("settings.recentTopics")}</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex flex-wrap gap-2">
              {preferences.recent_topics.slice(0, 10).map((topic) => (
                <span
                  key={topic}
                  className="rounded-full border border-border/50 bg-muted/30 px-3 py-1 text-xs text-muted-foreground"
                >
                  {topic}
                </span>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
    </PageLayout>
  );
}
