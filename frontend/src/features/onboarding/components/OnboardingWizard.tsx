"use client";

import { motion } from "framer-motion";
import { ArrowLeft, ArrowRight, CheckCircle2 } from "lucide-react";
import { useRouter } from "next/navigation";
import { useState } from "react";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { useAuth } from "@/hooks/useAuth";
import { useTranslations } from "@/hooks/useTranslations";
import * as saasService from "@/services/saasService";
import type { MadhhabChoice } from "@/services/preferencesService";
import type { UseCaseChoice } from "@/types/auth";
import { useSettingsStore } from "@/store/settingsStore";

const MADHHABS: MadhhabChoice[] = ["general", "hanafi", "maliki", "shafii", "hanbali"];
const USE_CASES: UseCaseChoice[] = ["personal", "student", "professional", "institution"];

export function OnboardingWizard() {
  const { t, locale } = useTranslations();
  const setLocale = useSettingsStore((s) => s.setLocale);
  const { accessToken, hydrateProfile } = useAuth();
  const router = useRouter();
  const [step, setStep] = useState(0);
  const [displayName, setDisplayName] = useState("");
  const [madhhab, setMadhhab] = useState<MadhhabChoice>("general");
  const [scholars, setScholars] = useState("");
  const [useCase, setUseCase] = useState<UseCaseChoice>("personal");
  const [saving, setSaving] = useState(false);

  const steps = [
    t("onboarding.stepWelcome"),
    t("onboarding.stepPreferences"),
    t("onboarding.stepUseCase"),
  ];

  const finish = async () => {
    if (!accessToken) return;
    setSaving(true);
    try {
      await saasService.updateOnboarding(accessToken, {
        display_name: displayName.trim() || undefined,
        locale,
        preferred_madhhab: madhhab,
        favorite_scholars: scholars
          .split(",")
          .map((s) => s.trim())
          .filter(Boolean)
          .slice(0, 20),
        use_case: useCase,
        completed: true,
      });
      await hydrateProfile();
      router.replace("/chat");
    } finally {
      setSaving(false);
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      className="mx-auto w-full max-w-xl"
    >
      <Card className="glass-card border-border/50 shadow-lg">
        <CardHeader>
          <p className="text-xs font-medium uppercase tracking-widest text-cyan-400">
            {t("onboarding.badge")}
          </p>
          <CardTitle>{t("onboarding.title")}</CardTitle>
          <p className="text-sm text-muted-foreground">{t("onboarding.subtitle")}</p>
          <div className="flex gap-2 pt-2">
            {steps.map((label, index) => (
              <div
                key={label}
                className={`h-1.5 flex-1 rounded-full ${
                  index <= step ? "bg-cyan-400" : "bg-muted"
                }`}
                aria-label={label}
              />
            ))}
          </div>
        </CardHeader>
        <CardContent className="space-y-6">
          {step === 0 && (
            <div className="space-y-4">
              <p className="text-sm text-muted-foreground">{t("onboarding.welcomeBody")}</p>
              <div className="space-y-2">
                <p className="text-sm font-medium">{t("onboarding.displayName")}</p>
                <Input
                  value={displayName}
                  onChange={(e) => setDisplayName(e.target.value)}
                  placeholder={t("onboarding.displayNamePlaceholder")}
                  maxLength={80}
                />
                <p className="text-xs text-muted-foreground">{t("onboarding.displayNameHint")}</p>
              </div>
              <div className="grid grid-cols-2 gap-2">
                <Button
                  type="button"
                  variant={locale === "ar" ? "default" : "outline"}
                  onClick={() => {
                    setLocale("ar");
                  }}
                >
                  {t("onboarding.languageArabic")}
                </Button>
                <Button
                  type="button"
                  variant={locale === "en" ? "default" : "outline"}
                  onClick={() => {
                    setLocale("en");
                  }}
                >
                  {t("onboarding.languageEnglish")}
                </Button>
              </div>
            </div>
          )}

          {step === 1 && (
            <div className="space-y-4">
              <div className="space-y-2">
                <p className="text-sm font-medium">{t("settings.preferredMadhhab")}</p>
                <select
                  value={madhhab}
                  onChange={(e) => setMadhhab(e.target.value as MadhhabChoice)}
                  className="h-10 w-full rounded-xl border border-border/50 bg-background/60 px-3 text-sm"
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
                <Input
                  value={scholars}
                  onChange={(e) => setScholars(e.target.value)}
                  placeholder={t("settings.favoriteScholarsPlaceholder")}
                />
              </div>
            </div>
          )}

          {step === 2 && (
            <div className="space-y-3">
              <p className="text-sm text-muted-foreground">{t("onboarding.useCaseHint")}</p>
              <div className="grid gap-2 sm:grid-cols-2">
                {USE_CASES.map((value) => (
                  <button
                    key={value}
                    type="button"
                    onClick={() => setUseCase(value)}
                    className={`rounded-xl border p-4 text-start transition ${
                      useCase === value
                        ? "border-cyan-500/40 bg-cyan-500/10"
                        : "border-border/50 hover:border-border"
                    }`}
                  >
                    <p className="text-sm font-medium">{t(`onboarding.useCase.${value}.title`)}</p>
                    <p className="mt-1 text-xs text-muted-foreground">
                      {t(`onboarding.useCase.${value}.description`)}
                    </p>
                  </button>
                ))}
              </div>
            </div>
          )}

          <div className="flex items-center justify-between gap-3 pt-2">
            <Button
              type="button"
              variant="ghost"
              disabled={step === 0 || saving}
              onClick={() => setStep((s) => Math.max(0, s - 1))}
            >
              <ArrowLeft className="me-1 h-4 w-4" />
              {t("onboarding.back")}
            </Button>
            {step < steps.length - 1 ? (
              <Button type="button" onClick={() => setStep((s) => s + 1)}>
                {t("onboarding.next")}
                <ArrowRight className="ms-1 h-4 w-4" />
              </Button>
            ) : (
              <Button type="button" disabled={saving} onClick={() => void finish()}>
                <CheckCircle2 className="me-1 h-4 w-4" />
                {t("onboarding.finish")}
              </Button>
            )}
          </div>
        </CardContent>
      </Card>
    </motion.div>
  );
}
