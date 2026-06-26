"use client";

import { motion } from "framer-motion";
import {
  ArrowRight,
  Cpu,
  Gauge,
  Layers,
  Mic,
  Shield,
  Sparkles,
  Zap,
} from "lucide-react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useCallback, useEffect, useState } from "react";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { useAuth } from "@/hooks/useAuth";
import { useTranslations } from "@/hooks/useTranslations";
import {
  localizeEvalFuture,
  localizeEvalLimitation,
  localizeEvaluationDemo,
  localizeFanarCapability,
  localizeFanarImprovement,
  localizeFeatureMatrix,
  localizeHarnessCategory,
  localizeHarnessQuestion,
  localizePipelineDepth,
} from "@/lib/domainLocalizations";
import { ApiClientError } from "@/services/apiClient";
import {
  getEvaluationDashboard,
  getEvaluationHarness,
  type EvaluationDashboard,
  type EvaluationHarness,
} from "@/services/evaluationService";

const FANAR_ICONS: Record<string, typeof Sparkles> = {
  "Fanar-Sadiq": Sparkles,
  "Fanar-Sadiq-Agentic": Sparkles,
  "Fanar-C-2-27B": Cpu,
  "Fanar-Guard-2": Shield,
  "Fanar-Aura-STT-1": Mic,
  "Fanar-Aura-STT": Mic,
  "Fanar-Oryx-IVU-2": Layers,
  "Fanar-Oryx-IVU": Layers,
  "Fanar-Shaheen-MT-1": Zap,
};

function formatLatency(ms: number | null | undefined): string {
  if (ms == null) return "—";
  if (ms < 1000) return `${Math.round(ms)} ms`;
  return `${(ms / 1000).toFixed(1)} s`;
}

export function FanarJudgeDashboard() {
  const { t, locale } = useTranslations();
  const router = useRouter();
  const { accessToken } = useAuth();
  const [data, setData] = useState<EvaluationDashboard | null>(null);
  const [harness, setHarness] = useState<EvaluationHarness | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    if (!accessToken) {
      setLoading(false);
      return;
    }
    setLoading(true);
    setError(null);
    try {
      const [dashboard, harnessData] = await Promise.all([
        getEvaluationDashboard(accessToken),
        getEvaluationHarness(accessToken),
      ]);
      setData(dashboard);
      setHarness(harnessData);
    } catch (err) {
      setError(err instanceof ApiClientError ? err.message : t("errors.generic"));
    } finally {
      setLoading(false);
    }
  }, [accessToken, t]);

  useEffect(() => {
    void load();
  }, [load]);

  const runDemo = (route: string, question: string | null) => {
    const normalizedRoute = route === "/" ? "/chat" : route;
    if (question && normalizedRoute === "/chat") {
      router.push(`/chat?q=${encodeURIComponent(question)}`);
      return;
    }
    router.push(normalizedRoute);
  };

  if (loading) {
    return <p className="text-center text-muted-foreground">{t("evaluation.loading")}</p>;
  }

  if (error || !data) {
    return <p className="text-center text-destructive">{error ?? t("errors.generic")}</p>;
  }

  const { stats } = data;

  return (
    <div className="mx-auto flex w-full max-w-6xl flex-col gap-6">
      <div>
        <div className="flex flex-wrap items-center gap-2">
          <Gauge className="h-6 w-6 text-cyan-400" />
          <h1 className="text-2xl font-bold tracking-tight">{t("evaluation.title")}</h1>
          <Badge variant="secondary" className="border-cyan-500/30 text-cyan-400">
            {t("evaluation.badge")}
          </Badge>
        </div>
        <p className="mt-1 text-sm text-muted-foreground">{t("evaluation.subtitle")}</p>
        <p className="mt-1 text-xs text-cyan-400/80">{t("evaluation.liveStatsNote")}</p>
      </div>

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-5">
        {[
          { label: t("evaluation.statQueries"), value: stats.total_completed_queries },
          {
            label: t("evaluation.statLatency"),
            value: formatLatency(stats.average_latency_ms),
          },
          {
            label: t("evaluation.statTokensTotal"),
            value:
              stats.total_tokens_estimate != null
                ? stats.total_tokens_estimate.toLocaleString()
                : stats.average_tokens_estimate != null
                  ? `~${Math.round(stats.average_tokens_estimate)}`
                  : "—",
          },
          {
            label: t("evaluation.statGuard"),
            value:
              stats.guard_pass_rate != null
                ? `${Math.round(stats.guard_pass_rate * 100)}%`
                : "—",
          },
          {
            label: t("evaluation.statModels"),
            value: stats.unique_models_used.length,
          },
        ].map((item, i) => (
          <motion.div
            key={item.label}
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: i * 0.05 }}
          >
            <Card className="glass-card border-cyan-500/15">
              <CardContent className="pt-5">
                <p className="text-xs text-muted-foreground">{item.label}</p>
                <p className="mt-1 text-2xl font-semibold text-cyan-400">{item.value}</p>
              </CardContent>
            </Card>
          </motion.div>
        ))}
      </div>

      <Card className="glass-card border-border/50">
        <CardHeader>
          <CardTitle className="text-base">{t("evaluation.fanarStrengths")}</CardTitle>
        </CardHeader>
        <CardContent className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
          {Object.entries(data.fanar_capabilities).map(([name, role]) => {
            const Icon = FANAR_ICONS[name] ?? Sparkles;
            const improvement = data.fanar_capability_improvements?.[name];
            return (
              <div
                key={name}
                className="rounded-xl border border-border/40 bg-muted/10 p-4 transition-colors hover:border-cyan-500/30"
              >
                <div className="mb-2 flex items-center gap-2">
                  <Icon className="h-4 w-4 text-cyan-400" />
                  <p className="text-sm font-semibold">{name}</p>
                </div>
                <p className="text-xs leading-relaxed text-muted-foreground">
                  {localizeFanarCapability(name, locale, role)}
                </p>
                {improvement && (
                  <p className="mt-2 border-t border-border/30 pt-2 text-[10px] leading-relaxed text-cyan-400/70">
                    <span className="font-medium">{t("evaluation.colImprovement")}: </span>
                    {localizeFanarImprovement(name, locale, improvement)}
                  </p>
                )}
              </div>
            );
          })}
        </CardContent>
      </Card>

      <Card className="glass-card border-border/50">
        <CardHeader>
          <CardTitle className="text-base">{t("evaluation.demoPrompts")}</CardTitle>
        </CardHeader>
        <CardContent className="grid gap-3 md:grid-cols-2">
          {data.demo_prompts.map((prompt) => (
            <div
              key={prompt.id}
              className="flex flex-col justify-between rounded-xl border border-border/40 bg-muted/10 p-4"
            >
              <div>
                <div className="mb-2 flex flex-wrap items-center gap-2">
                  <p className="text-sm font-medium">
                    {localizeEvaluationDemo(prompt.id, "title", locale, prompt.title)}
                  </p>
                  <Badge variant="outline" className="text-[10px]">
                    {prompt.fanar_product}
                  </Badge>
                </div>
                <p className="text-xs text-muted-foreground">
                  {localizeEvaluationDemo(prompt.id, "description", locale, prompt.description)}
                </p>
              </div>
              <Button
                type="button"
                size="sm"
                variant="secondary"
                className="mt-3 w-fit gap-1"
                onClick={() => runDemo(prompt.route, prompt.question)}
              >
                {t("evaluation.tryDemo")}
                <ArrowRight className="h-3.5 w-3.5" />
              </Button>
            </div>
          ))}
        </CardContent>
      </Card>

      <Card className="glass-card border-border/50">
        <CardHeader>
          <CardTitle className="text-base">{t("evaluation.featureMatrix")}</CardTitle>
        </CardHeader>
        <CardContent className="overflow-x-auto">
          <table className="w-full min-w-[560px] text-sm">
            <thead>
              <tr className="border-b border-border/40 text-start text-xs text-muted-foreground">
                <th className="pb-2 pe-4 font-medium">{t("evaluation.colFeature")}</th>
                <th className="pb-2 pe-4 font-medium">{t("evaluation.colFanar")}</th>
                <th className="pb-2 font-medium">{t("evaluation.colDescription")}</th>
              </tr>
            </thead>
            <tbody>
              {data.feature_matrix.map((row) => (
                <tr key={row.id ?? row.feature} className="border-b border-border/20 last:border-0">
                  <td className="py-3 pe-4 font-medium">
                    {localizeFeatureMatrix(row.id ?? row.feature, "feature", locale, row.feature)}
                  </td>
                  <td className="py-3 pe-4">
                    <div className="flex flex-wrap gap-1">
                      {row.fanar_products.map((p) => (
                        <Badge key={p} variant="outline" className="text-[10px]">
                          {p}
                        </Badge>
                      ))}
                    </div>
                  </td>
                  <td className="py-3 text-muted-foreground">
                    {localizeFeatureMatrix(row.id ?? row.feature, "description", locale, row.description)}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </CardContent>
      </Card>

      {data.recent_queries.length > 0 && (
        <Card className="glass-card border-border/50">
          <CardHeader>
            <CardTitle className="text-base">{t("evaluation.recentQueries")}</CardTitle>
          </CardHeader>
          <CardContent className="space-y-2">
            {data.recent_queries.map((row) => (
              <Link
                key={row.query_id}
                href={`/history/${row.query_id}`}
                className="flex flex-wrap items-center justify-between gap-2 rounded-lg border border-border/30 bg-muted/10 px-3 py-2 text-sm transition-colors hover:border-cyan-500/30"
              >
                <span className="line-clamp-1 flex-1">{row.question}</span>
                <div className="flex flex-wrap gap-1">
                  {row.pipeline_depth && (
                    <Badge variant="secondary" className="text-[10px]">
                      {localizePipelineDepth(row.pipeline_depth, locale)}
                    </Badge>
                  )}
                  {row.latency_ms != null && (
                    <Badge variant="outline" className="text-[10px]">
                      {formatLatency(row.latency_ms)}
                    </Badge>
                  )}
                </div>
              </Link>
            ))}
          </CardContent>
        </Card>
      )}

      {harness && (
        <Card className="glass-card border-border/50">
          <CardHeader className="pb-2">
            <CardTitle className="text-base">{t("evaluation.harnessTitle")}</CardTitle>
            <p className="text-xs text-muted-foreground">{t("evaluation.harnessSubtitle")}</p>
          </CardHeader>
          <CardContent className="space-y-3">
            <ul className="list-disc space-y-1 ps-4 text-xs text-muted-foreground">
              {harness.scoring_notes.map((note) => (
                <li key={note}>{note}</li>
              ))}
            </ul>
            <div className="space-y-2">
              {harness.cases.map((testCase) => (
                <div
                  key={testCase.id}
                  className="rounded-lg border border-border/30 bg-muted/10 p-3 text-sm"
                >
                  <div className="flex flex-wrap items-start justify-between gap-2">
                    <div className="min-w-0 flex-1">
                      <p className="font-medium">
                        {localizeHarnessQuestion(testCase.id, locale, testCase.question)}
                      </p>
                      <p className="mt-1 text-xs text-muted-foreground">
                        {t("evaluation.harnessCategory")}:{" "}
                        {localizeHarnessCategory(testCase.category, locale)}
                      </p>
                    </div>
                    <Button
                      type="button"
                      size="sm"
                      variant="secondary"
                      className="shrink-0"
                      onClick={() => runDemo("/chat", testCase.question)}
                    >
                      {t("evaluation.harnessRun")}
                    </Button>
                  </div>
                  {testCase.rubric.length > 0 && (
                    <ul className="mt-2 list-disc space-y-0.5 ps-4 text-xs text-muted-foreground">
                      {testCase.rubric.map((item) => (
                        <li key={item}>{item}</li>
                      ))}
                    </ul>
                  )}
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      <div className="grid gap-4 lg:grid-cols-2">
        <Card className="glass-card border-border/50">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm">{t("evaluation.limitations")}</CardTitle>
          </CardHeader>
          <CardContent>
            <ul className="list-disc space-y-1 ps-4 text-xs text-muted-foreground">
              {data.limitations.map((item, index) => (
                <li key={item}>{localizeEvalLimitation(index, locale, item)}</li>
              ))}
            </ul>
          </CardContent>
        </Card>
        <Card className="glass-card border-border/50">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm">{t("evaluation.futureFanar")}</CardTitle>
          </CardHeader>
          <CardContent>
            <ul className="list-disc space-y-1 ps-4 text-xs text-muted-foreground">
              {data.future_fanar_suggestions.map((item, index) => (
                <li key={item}>{localizeEvalFuture(index, locale, item)}</li>
              ))}
            </ul>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
