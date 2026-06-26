"use client";

import { motion, useReducedMotion } from "framer-motion";
import {
  ArrowLeft,
  ArrowRight,
  Building2,
  Calculator,
  Check,
  FileText,
  Mail,
  Mic,
  Network,
  Scale,
  Shield,
  Sparkles,
  Zap,
} from "lucide-react";
import { useRouter } from "next/navigation";
import Link from "next/link";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { useTranslations } from "@/hooks/useTranslations";
import { cn } from "@/lib/utils";

const ENTERPRISE_EMAIL = "enterprise@sanad.qa";

const fadeUp = (delay: number, reduced: boolean) =>
  reduced
    ? { initial: { opacity: 1 }, animate: { opacity: 1 } }
    : {
        initial: { opacity: 0, y: 22 },
        animate: { opacity: 1, y: 0 },
        transition: { duration: 0.55, delay, ease: [0.22, 1, 0.36, 1] },
      };

export function LandingPage() {
  const { t, locale } = useTranslations();
  const router = useRouter();
  const reducedMotion = useReducedMotion();
  const isRtl = locale === "ar";

  const features = [
    { key: "chat", icon: Sparkles },
    { key: "evidence", icon: Scale },
    { key: "scanner", icon: Building2 },
    { key: "documents", icon: FileText },
    { key: "voice", icon: Mic },
    { key: "zakat", icon: Calculator },
  ] as const;

  const tiers = ["free", "enterprise"] as const;
  const heroDelay = reducedMotion ? 0 : 0.08;
  const featureBaseDelay = reducedMotion ? 0 : 0.55;

  const sampleQueryKeys = ["riba", "tesla", "bitcoin", "zakat", "etf"] as const;
  const whyWinsKeys = ["agents", "evidence", "fanar", "tools"] as const;
  const whyWinsIcons = { agents: Network, evidence: Scale, fanar: Sparkles, tools: Zap };

  const launchSample = (question: string) => {
    router.push(`/chat?q=${encodeURIComponent(question)}`);
  };

  return (
    <div className="landing-page -mx-3 -mt-6 sm:-mx-4 sm:-mt-8">
      <section className="landing-hero px-4 py-10 md:py-14" aria-label="Hero">
        <div className="relative z-10 mx-auto max-w-6xl text-center">
          <motion.p
            {...fadeUp(0, !!reducedMotion)}
            className="landing-hero-badge mb-4 text-sm font-medium uppercase tracking-[0.2em]"
          >
            {t("landing.badge")}
          </motion.p>

          <motion.h1
            {...fadeUp(heroDelay, !!reducedMotion)}
            className="landing-hero-title mx-auto max-w-4xl text-3xl font-bold leading-tight tracking-tight md:text-5xl md:leading-[1.15]"
          >
            {t("landing.heroTitleLead")}
            <span className="nexus-gradient-text">{t("landing.heroTitleAccent")}</span>
            {t("landing.heroTitleEnd")}
          </motion.h1>

          <motion.p
            {...fadeUp(heroDelay * 2, !!reducedMotion)}
            className="landing-hero-subtitle mx-auto mt-5 max-w-2xl text-base font-normal leading-relaxed text-muted-foreground md:text-lg md:leading-8"
          >
            {t("landing.heroSubtitle")}
          </motion.p>

          <motion.div
            {...fadeUp(heroDelay * 3, !!reducedMotion)}
            className="mt-9 flex flex-wrap items-center justify-center gap-3"
          >
            <Button
              size="lg"
              asChild
              className={cn(
                "group fanar-btn-primary h-12 min-w-[168px] gap-2 rounded-xl px-6 text-base font-semibold",
                "nexus-glow transition-all duration-300 hover:opacity-95",
              )}
            >
              <Link href="/register">
                {t("landing.ctaStart")}
                {isRtl ? (
                  <ArrowLeft
                    className="h-4 w-4 shrink-0 transition-transform duration-300 group-hover:-translate-x-1"
                    aria-hidden
                  />
                ) : (
                  <ArrowRight
                    className="h-4 w-4 shrink-0 transition-transform duration-300 group-hover:translate-x-1"
                    aria-hidden
                  />
                )}
              </Link>
            </Button>

            <Button
              size="lg"
              variant="outline"
              asChild
              className="landing-hero-btn-outline h-12 min-w-[168px] rounded-xl px-6 text-base font-medium transition-colors"
            >
              <Link href="/login">{t("landing.ctaSignIn")}</Link>
            </Button>
          </motion.div>

          <motion.div
            {...fadeUp(heroDelay * 4, !!reducedMotion)}
            className="landing-hero-trust mx-auto mt-12 flex max-w-2xl flex-wrap items-center justify-center gap-x-6 gap-y-3 text-sm md:mt-16"
          >
            <span className="inline-flex items-center gap-2">
              <Shield className="h-4 w-4 shrink-0 text-brand-accent" aria-hidden />
              {t("landing.trustGuard")}
            </span>
            <span className="inline-flex items-center gap-2">
              <Scale className="h-4 w-4 shrink-0 text-brand-accent" aria-hidden />
              {t("landing.trustEvidence")}
            </span>
          </motion.div>
        </div>
      </section>

      <section className="landing-problem px-4 py-12 md:py-16" id="problem">
        <div className="mx-auto max-w-4xl">
          <motion.div {...fadeUp(featureBaseDelay, !!reducedMotion)}>
            <p className="mb-2 text-center text-xs font-semibold uppercase tracking-[0.2em] text-nexus-cyan">
              {t("landing.problemTitle")}
            </p>
            <Card className="glass-card border-nexus-cyan/20 bg-card/60">
              <CardContent className="space-y-4 pt-6 text-[15px] leading-relaxed text-muted-foreground">
                <p>{t("landing.problemStatement")}</p>
                <p className="border-s-2 border-nexus-cyan/60 ps-4 font-medium text-foreground">
                  {t("landing.problemSolution")}
                </p>
              </CardContent>
            </Card>
          </motion.div>
        </div>
      </section>

      <section className="landing-samples px-4 pb-12 md:pb-16" id="demo">
        <div className="mx-auto max-w-4xl text-center">
          <motion.h2
            {...fadeUp(featureBaseDelay + 0.1, !!reducedMotion)}
            className="text-xl font-bold md:text-2xl"
          >
            {t("landing.sampleQueriesTitle")}
          </motion.h2>
          <motion.p
            {...fadeUp(featureBaseDelay + 0.15, !!reducedMotion)}
            className="mt-2 text-sm text-muted-foreground"
          >
            {t("landing.sampleQueriesSubtitle")}
          </motion.p>
          <motion.div
            {...fadeUp(featureBaseDelay + 0.2, !!reducedMotion)}
            className="mt-6 flex flex-wrap justify-center gap-2"
          >
            {sampleQueryKeys.map((key) => (
              <Button
                key={key}
                type="button"
                variant="outline"
                size="sm"
                className="rounded-full border-nexus-cyan/30 bg-background/40 text-sm hover:border-nexus-cyan/60 hover:bg-nexus-cyan/5"
                onClick={() => launchSample(t(`landing.sampleQueries.${key}`))}
              >
                {t(`landing.sampleQueries.${key}`)}
              </Button>
            ))}
          </motion.div>
        </div>
      </section>

      <section className="landing-why-wins px-4 pb-12 md:pb-16" id="why-sanad">
        <div className="mx-auto max-w-6xl">
          <motion.div {...fadeUp(featureBaseDelay + 0.25, !!reducedMotion)} className="mb-8 text-center">
            <h2 className="text-2xl font-bold md:text-3xl">{t("landing.whyWinsTitle")}</h2>
            <p className="mt-2 text-sm text-muted-foreground">{t("landing.whyWinsSubtitle")}</p>
          </motion.div>
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
            {whyWinsKeys.map((key, index) => {
              const Icon = whyWinsIcons[key];
              return (
                <motion.div key={key} {...fadeUp(featureBaseDelay + 0.3 + index * 0.06, !!reducedMotion)}>
                  <Card className="glass-card h-full border-nexus-cyan/15 transition-colors hover:border-nexus-cyan/35">
                    <CardContent className="pt-6">
                      <Icon className="mb-3 h-6 w-6 text-nexus-cyan" aria-hidden />
                      <p className="font-semibold">{t(`landing.whyWins.${key}.title`)}</p>
                      <p className="mt-2 text-sm leading-relaxed text-muted-foreground">
                        {t(`landing.whyWins.${key}.description`)}
                      </p>
                    </CardContent>
                  </Card>
                </motion.div>
              );
            })}
          </div>
        </div>
      </section>

      <section className="landing-features px-4 py-16 md:py-20">
        <div className="mx-auto max-w-6xl space-y-20 md:space-y-24">
          <section id="features" className="scroll-mt-20">
            <motion.h2
              {...fadeUp(featureBaseDelay, !!reducedMotion)}
              className="mb-8 text-center text-2xl font-bold text-foreground md:text-3xl"
            >
              {t("landing.featuresTitle")}
            </motion.h2>

            <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
              {features.map(({ key, icon: Icon }, index) => (
                <motion.div
                  key={key}
                  {...fadeUp(featureBaseDelay + index * 0.07, !!reducedMotion)}
                >
                  <Card className="glass-card h-full border-border/40 transition-colors hover:border-brand-accent/25">
                    <CardContent className="pt-6">
                      <Icon className="mb-3 h-6 w-6 text-brand-accent" aria-hidden />
                      <p className="text-base font-semibold text-foreground">
                        {t(`landing.features.${key}.title`)}
                      </p>
                      <p className="mt-2.5 text-[15px] leading-relaxed text-muted-foreground">
                        {t(`landing.features.${key}.description`)}
                      </p>
                    </CardContent>
                  </Card>
                </motion.div>
              ))}
            </div>
          </section>

          <section id="pricing" className="scroll-mt-20 pb-4">
            <motion.h2
              {...fadeUp(featureBaseDelay + 0.35, !!reducedMotion)}
              className="mb-2 text-center text-2xl font-bold text-foreground md:text-3xl"
            >
              {t("landing.pricingTitle")}
            </motion.h2>
            <motion.p
              {...fadeUp(featureBaseDelay + 0.42, !!reducedMotion)}
              className="mb-10 text-center text-sm text-muted-foreground"
            >
              {t("landing.pricingSubtitle")}
            </motion.p>

            <div className="mx-auto grid max-w-3xl gap-5 md:grid-cols-2 md:items-stretch">
              {tiers.map((tier, index) => (
                <motion.div
                  key={tier}
                  {...fadeUp(featureBaseDelay + 0.5 + index * 0.08, !!reducedMotion)}
                  className="h-full"
                >
                  <Card
                    className={cn(
                      "glass-card flex h-full flex-col border-border/40",
                      tier === "free"
                        ? "border-brand-accent/40 ring-1 ring-brand-accent/20"
                        : "border-border/50",
                    )}
                  >
                    <CardHeader className="pb-4">
                      <CardTitle className="text-lg text-foreground">
                        {t(`landing.pricing.${tier}.name`)}
                      </CardTitle>
                      <p className="text-2xl font-bold text-brand-accent">
                        {t(`landing.pricing.${tier}.price`)}
                      </p>
                    </CardHeader>

                    <CardContent className="flex flex-1 flex-col pt-0">
                      <ul className="flex-1 space-y-3">
                        {(t(`landing.pricing.${tier}.features`) as string)
                          .split("|")
                          .map((item) => (
                            <li
                              key={item}
                              className="flex items-start gap-3 text-start text-[15px] leading-relaxed text-muted-foreground"
                            >
                              <span
                                className="mt-0.5 flex h-5 w-5 shrink-0 items-center justify-center text-brand-accent"
                                aria-hidden
                              >
                                <Check className="h-4 w-4 stroke-[2.5]" />
                              </span>
                              <span className="flex-1">{item}</span>
                            </li>
                          ))}
                      </ul>

                      <div className="mt-6 shrink-0">
                        {tier === "enterprise" ? (
                          <Button
                            variant="outline"
                            asChild
                            className="flex h-11 w-full items-center justify-center gap-2 rounded-xl border-brand-accent/40 bg-transparent px-4 py-0 text-sm font-medium leading-none text-foreground hover:bg-brand-accent/10"
                          >
                            <a href={`mailto:${ENTERPRISE_EMAIL}`}>
                              <Mail className="h-4 w-4 shrink-0" aria-hidden />
                              <span>{t("landing.contactUs")}</span>
                            </a>
                          </Button>
                        ) : (
                          <Button
                            asChild
                            className="flex h-11 w-full items-center justify-center rounded-xl bg-brand-accent px-4 py-0 text-sm font-semibold leading-none text-primary-foreground hover:opacity-90"
                          >
                            <Link href="/register">{t("landing.pricing.cta")}</Link>
                          </Button>
                        )}
                      </div>
                    </CardContent>
                  </Card>
                </motion.div>
              ))}
            </div>
          </section>
        </div>
      </section>
    </div>
  );
}
