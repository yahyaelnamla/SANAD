"use client";

import { motion } from "framer-motion";
import {
  BookmarkPlus,
  Building2,
  Loader2,
  Search,
  Sparkles,
  TrendingDown,
  TrendingUp,
} from "lucide-react";
import Image from "next/image";
import { useSearchParams } from "next/navigation";
import { useEffect, useState } from "react";

import { PageLayout } from "@/components/PageGuide";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { ExecutionMetricsPanel } from "@/features/chat/components/ExecutionMetricsPanel";
import { FanarModelSelector } from "@/features/chat/components/FanarModelSelector";
import { ReasoningProcessAccordion } from "@/features/chat/components/ReasoningProcessAccordion";
import { useAuth } from "@/hooks/useAuth";
import { useTranslations } from "@/hooks/useTranslations";
import { useUserPreferences } from "@/hooks/useUserPreferences";
import { cn } from "@/lib/utils";
import { ApiClientError } from "@/services/apiClient";
import { scanCompany, type CompanyScanResult } from "@/services/featuresService";
import { useSettingsStore } from "@/store/settingsStore";

const STATUS_STYLES: Record<string, string> = {
  green: "bg-emerald-500/15 text-emerald-600 dark:text-emerald-400 border-emerald-500/30",
  yellow: "bg-amber-500/15 text-amber-700 dark:text-amber-400 border-amber-500/30",
  red: "bg-destructive/15 text-destructive border-destructive/30",
};

const VERDICT_STYLES: Record<string, string> = {
  halal: "border-emerald-500/40 bg-emerald-500/10 text-emerald-700 dark:text-emerald-300",
  haram: "border-destructive/40 bg-destructive/10 text-destructive",
  doubtful: "border-amber-500/40 bg-amber-500/10 text-amber-800 dark:text-amber-200",
};

function formatPct(value: number | null | undefined): string {
  if (value == null) return "—";
  return `${Math.round(value * 1000) / 10}%`;
}

function formatMetric(value: number | null | undefined, suffix = ""): string {
  if (value == null) return "—";
  const rounded = Math.round(value * 100) / 100;
  return `${rounded.toLocaleString()}${suffix}`;
}

function RatioBar({
  label,
  value,
  threshold,
  overIsBad = true,
}: {
  label: string;
  value: number | null | undefined;
  threshold: number;
  overIsBad?: boolean;
}) {
  const pct = value != null ? Math.min(100, Math.round(value * 100)) : 0;
  const over = value != null && value > threshold;
  const bad = overIsBad ? over : !over && value != null;
  return (
    <div className="space-y-1">
      <div className="flex justify-between text-xs text-muted-foreground">
        <span>{label}</span>
        <span>{formatPct(value)}</span>
      </div>
      <div className="h-2 overflow-hidden rounded-full bg-muted/40">
        <div
          className={cn("h-full rounded-full transition-all", bad ? "bg-red-400" : "bg-cyan-400")}
          style={{ width: `${pct}%` }}
        />
      </div>
      <p className="text-[10px] text-muted-foreground">
        {overIsBad ? `< ${Math.round(threshold * 100)}%` : `≥ ${Math.round(threshold * 100)}%`}
      </p>
    </div>
  );
}

function MetricGrid({ result }: { result: CompanyScanResult }) {
  const { t } = useTranslations();
  const m = result.financial_metrics;
  const items = [
    { label: t("scanner.peRatio"), value: formatMetric(m?.pe_ratio) },
    { label: t("scanner.pbRatio"), value: formatMetric(m?.pb_ratio) },
    { label: t("scanner.pegRatio"), value: formatMetric(m?.peg_ratio) },
    { label: t("scanner.grossMargin"), value: formatPct(m?.gross_profit_margin) },
    { label: t("scanner.netMargin"), value: formatPct(m?.net_profit_margin) },
    { label: t("scanner.roe"), value: formatPct(m?.roe) },
    { label: t("scanner.currentRatio"), value: formatMetric(m?.current_ratio) },
    { label: t("scanner.debtToEquity"), value: formatMetric(m?.debt_to_equity) },
  ];
  return (
    <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
      {items.map((item) => (
        <div key={item.label} className="rounded-lg border border-border/40 bg-muted/10 p-3">
          <p className="text-xs text-muted-foreground">{item.label}</p>
          <p className="mt-1 font-semibold">{item.value}</p>
        </div>
      ))}
    </div>
  );
}

export function CompanyScannerPanel() {
  const { t, locale } = useTranslations();
  const { accessToken } = useAuth();
  const { preferences, save } = useUserPreferences();
  const fanarModel = useSettingsStore((s) => s.fanarModelPreference);
  const searchParams = useSearchParams();
  const [company, setCompany] = useState("Tesla");
  const [result, setResult] = useState<CompanyScanResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [saved, setSaved] = useState(false);

  useEffect(() => {
    const preset = searchParams.get("q");
    if (preset?.trim()) {
      setCompany(preset.trim());
    }
  }, [searchParams]);

  useEffect(() => {
    setSaved(false);
  }, [company, result?.company_name]);

  const handleScan = async () => {
    if (!accessToken || !company.trim()) return;
    setLoading(true);
    setError(null);
    try {
      setResult(
        await scanCompany(accessToken, company.trim(), {
          language: locale === "ar" ? "ar" : "en",
          fanar_model: fanarModel,
        }),
      );
    } catch (err) {
      if (err instanceof ApiClientError) {
        if (err.status === 401) {
          setError(t("errors.unauthorized"));
        } else if (err.status === 0) {
          setError(t("errors.network"));
        } else {
          setError(err.message || t("errors.generic"));
        }
      } else {
        setError(t("errors.generic"));
      }
    } finally {
      setLoading(false);
    }
  };

  const handleSaveCompany = async () => {
    if (!result) return;
    const name = result.company_name.trim();
    const existing = preferences?.saved_companies ?? [];
    if (existing.includes(name)) {
      setSaved(true);
      return;
    }
    await save({ saved_companies: [...existing, name] });
    setSaved(true);
  };

  const isCompanySaved =
    saved ||
    (result != null && (preferences?.saved_companies ?? []).includes(result.company_name.trim()));

  const ratios = result?.aaoifi_ratios;

  return (
    <PageLayout guideKey="companyScanner" className="mx-auto max-w-4xl space-y-6">
      <Card className="glass-card border-cyan-500/20">
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-lg">
            <Building2 className="h-5 w-5 text-cyan-400" />
            {t("pages.companyScanner.title")}
          </CardTitle>
          <p className="text-sm text-muted-foreground">{t("pages.companyScanner.description")}</p>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex flex-col gap-3 sm:flex-row">
            <Input
              value={company}
              onChange={(e) => setCompany(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && void handleScan()}
              placeholder={t("scanner.companyPlaceholder")}
              className="flex-1"
            />
            <Button onClick={() => void handleScan()} disabled={loading || !accessToken} className="gap-2">
              {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : <Search className="h-4 w-4" />}
              {t("scanner.scan")}
            </Button>
          </div>
          <div className="flex flex-wrap items-center justify-between gap-2">
            <span className="text-xs text-muted-foreground">{t("scanner.fanarModelHint")}</span>
            <FanarModelSelector />
          </div>
        </CardContent>
      </Card>

      {loading && (
        <div className="space-y-4">
          {[1, 2, 3].map((i) => (
            <div key={i} className="h-32 animate-pulse rounded-xl bg-muted/30" />
          ))}
        </div>
      )}

      {error && <p className="text-center text-sm text-destructive">{error}</p>}

      {result && !loading && (
        <motion.div
          initial={{ opacity: 0, y: 12 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.35 }}
          className="space-y-4"
        >
          <Card className="glass-card overflow-hidden border-cyan-500/20">
            <CardContent className="flex flex-col gap-4 p-5 sm:flex-row sm:items-center sm:justify-between">
              <div className="flex items-center gap-4">
                {result.logo_url ? (
                  <Image
                    src={result.logo_url}
                    alt=""
                    width={48}
                    height={48}
                    className="rounded-lg bg-white/10 object-contain p-1"
                    unoptimized
                    onError={(e) => {
                      (e.target as HTMLImageElement).style.display = "none";
                    }}
                  />
                ) : (
                  <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-cyan-500/10">
                    <Building2 className="h-6 w-6 text-cyan-400" />
                  </div>
                )}
                <div>
                  <h2 className="text-xl font-bold">{result.company_name}</h2>
                  <p className="text-sm text-muted-foreground">
                    {result.symbol ?? "—"}
                    {result.sector ? ` · ${result.sector}` : ""}
                    {result.industry ? ` · ${result.industry}` : ""}
                  </p>
                </div>
              </div>
              <div className="flex flex-wrap items-center gap-3">
                {result.market_price != null && (
                  <div className="text-end">
                    <p className="text-2xl font-bold">
                      {result.market_price.toLocaleString()} {result.currency ?? "USD"}
                    </p>
                    {result.price_change_percent != null && (
                      <p
                        className={cn(
                          "flex items-center justify-end gap-1 text-sm",
                          result.price_change_percent >= 0 ? "text-emerald-500" : "text-red-400",
                        )}
                      >
                        {result.price_change_percent >= 0 ? (
                          <TrendingUp className="h-3.5 w-3.5" />
                        ) : (
                          <TrendingDown className="h-3.5 w-3.5" />
                        )}
                        {result.price_change_percent >= 0 ? "+" : ""}
                        {result.price_change_percent.toFixed(2)}%
                      </p>
                    )}
                  </div>
                )}
                <Badge variant="outline" className={cn("capitalize", STATUS_STYLES[result.status])}>
                  {t(`scanner.complianceBadge.${result.status}`)}
                </Badge>
                <Button
                  variant="outline"
                  size="sm"
                  className="gap-1"
                  disabled={isCompanySaved}
                  onClick={() => void handleSaveCompany()}
                >
                  <BookmarkPlus className="h-3.5 w-3.5" />
                  {isCompanySaved ? t("scanner.savedCompany") : t("scanner.saveCompany")}
                </Button>
              </div>
            </CardContent>
          </Card>

          <div
            className={cn(
              "rounded-2xl border-2 p-5 text-center",
              VERDICT_STYLES[result.verdict] ?? VERDICT_STYLES.doubtful,
            )}
          >
            <p className="text-xs font-medium uppercase tracking-wider opacity-80">
              {t("scanner.shariahVerdict")}
            </p>
            <p className="mt-1 text-2xl font-bold md:text-3xl">{t(`scanner.verdict.${result.verdict}`)}</p>
            <p className="mt-2 text-sm opacity-90">{result.verdict_reason}</p>
          </div>

          {result.ai_summary && (
            <Card className="glass-card border-cyan-500/15">
              <CardHeader>
                <CardTitle className="flex items-center gap-2 text-base">
                  <Sparkles className="h-4 w-4 text-cyan-400" />
                  {t("scanner.aiSummary")}
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-3 text-sm">
                <p className="leading-relaxed">{result.ai_summary}</p>
                {result.key_takeaways.length > 0 && (
                  <ul className="space-y-1.5 text-muted-foreground">
                    {result.key_takeaways.map((item) => (
                      <li key={item} className="flex gap-2">
                        <span className="text-cyan-400">•</span>
                        <span>{item}</span>
                      </li>
                    ))}
                  </ul>
                )}
              </CardContent>
            </Card>
          )}

          <Card className="glass-card">
            <CardHeader>
              <CardTitle>{t("scanner.shariahCompliance")}</CardTitle>
            </CardHeader>
            <CardContent className="space-y-5 text-sm">
              {result.qualitative_screening && (
                <div className="rounded-xl border border-border/50 bg-muted/10 p-4">
                  <div className="flex items-center justify-between gap-2">
                    <p className="font-medium">{t("scanner.qualitativeScreening")}</p>
                    <Badge
                      variant="outline"
                      className={cn(
                        result.qualitative_screening.status === "pass"
                          ? "border-emerald-500/40 text-emerald-500"
                          : "border-destructive/40 text-destructive",
                      )}
                    >
                      {result.qualitative_screening.status === "pass"
                        ? t("scanner.pass")
                        : t("scanner.fail")}
                    </Badge>
                  </div>
                  <p className="mt-2 text-muted-foreground">{result.qualitative_screening.analysis}</p>
                </div>
              )}

              <div className="grid gap-4 sm:grid-cols-2">
                <RatioBar
                  label={t("scanner.nonPermissibleIncome")}
                  value={ratios?.non_permissible_income_ratio ?? null}
                  threshold={ratios?.income_threshold ?? 0.05}
                />
                <RatioBar
                  label={t("scanner.debtRatio")}
                  value={ratios?.interest_bearing_debt_ratio ?? result.debt_ratio}
                  threshold={ratios?.debt_threshold ?? 0.3}
                />
                <RatioBar
                  label={t("scanner.interestInvestments")}
                  value={ratios?.interest_earning_investments_ratio ?? result.interest_income_ratio}
                  threshold={ratios?.investments_threshold ?? 0.3}
                />
                <RatioBar
                  label={t("scanner.purificationRatio")}
                  value={ratios?.dividend_purification_ratio ?? null}
                  threshold={0.05}
                />
              </div>

              <div className="grid gap-3 sm:grid-cols-3">
                <div>
                  <p className="text-muted-foreground">{t("scanner.complianceScore")}</p>
                  <p className="text-xl font-semibold">{Math.round(result.compliance_score * 100)}%</p>
                </div>
                <div>
                  <p className="text-muted-foreground">{t("scanner.riskLevel")}</p>
                  <p className="font-medium capitalize">{result.risk_level}</p>
                </div>
                <div>
                  <p className="text-muted-foreground">{t("scanner.purificationEstimate")}</p>
                  <p>{result.purification_estimate?.toLocaleString() ?? "—"}</p>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card className="glass-card">
            <CardHeader>
              <CardTitle>{t("scanner.financialHealth")}</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4 text-sm">
              <MetricGrid result={result} />
              {result.ai_financial_assessment && (
                <p className="rounded-xl border border-border/40 bg-muted/10 p-4 leading-relaxed text-muted-foreground">
                  {result.ai_financial_assessment}
                </p>
              )}
              <div className="rounded-xl border border-border/50 bg-muted/20 p-4">
                <p className="text-xs font-medium text-muted-foreground">{t("scanner.investmentOutlook")}</p>
                <p className="mt-1 flex items-center gap-2 font-semibold">
                  {result.investment_favorable ? (
                    <TrendingUp className="h-4 w-4 text-emerald-500" />
                  ) : (
                    <TrendingDown className="h-4 w-4 text-amber-500" />
                  )}
                  {result.investment_favorable
                    ? t("scanner.investmentFavorable")
                    : t("scanner.investmentUnfavorable")}
                </p>
                <p className="mt-2 text-xs leading-relaxed text-muted-foreground">{result.investment_outlook}</p>
              </div>
            </CardContent>
          </Card>

          {(result.agent_trace.length > 0 || result.sources.length > 0) && (
            <Card className="glass-card">
              <CardHeader>
                <CardTitle>{t("explainability.title")}</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                {result.agent_trace.length > 0 && (
                  <ReasoningProcessAccordion steps={result.agent_trace} />
                )}
                <Tabs defaultValue="sources">
                  <TabsList className="mb-3 flex h-auto flex-wrap gap-1 bg-muted/30 p-1">
                    <TabsTrigger value="sources" className="text-xs">
                      {t("explainability.sources")}
                    </TabsTrigger>
                    {result.execution_metrics && (
                      <TabsTrigger value="metrics" className="text-xs">
                        {t("explainability.executionMetrics")}
                      </TabsTrigger>
                    )}
                  </TabsList>
                  <TabsContent value="sources" className="space-y-2">
                    {result.sources.map((source) => (
                      <div
                        key={`${source.title}-${source.citation}`}
                        className="rounded-lg border border-border/40 bg-muted/10 p-3 text-sm"
                      >
                        <p className="font-medium">{source.title}</p>
                        <p className="text-muted-foreground">{source.citation}</p>
                        {source.source_url && (
                          <a
                            href={source.source_url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="mt-1 inline-block text-xs text-cyan-400 hover:underline"
                          >
                            {source.source_url}
                          </a>
                        )}
                      </div>
                    ))}
                  </TabsContent>
                  {result.execution_metrics && result.agent_trace.length > 0 && (
                    <TabsContent value="metrics">
                      <ExecutionMetricsPanel
                        steps={result.agent_trace}
                        metrics={{
                          total_latency_ms: result.execution_metrics.total_latency_ms,
                          steps_completed: result.execution_metrics.steps_completed,
                          steps_total: result.execution_metrics.steps_total,
                          models_used: result.execution_metrics.models_used,
                          tokens_total: result.execution_metrics.tokens_total,
                          fanar_model_preference: result.execution_metrics.fanar_model_preference,
                        }}
                      />
                    </TabsContent>
                  )}
                </Tabs>
              </CardContent>
            </Card>
          )}

          {result.peer_comparison.length > 0 && (
            <Card className="glass-card">
              <CardHeader>
                <CardTitle className="text-base">{t("scanner.peerComparison")}</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="responsive-table-wrap safe-scroll-x">
                  <table className="w-full min-w-[320px] text-left text-xs">
                    <thead>
                      <tr className="border-b border-border/40 text-muted-foreground">
                        <th className="pb-2 pe-2">{t("scanner.peerCompany")}</th>
                        <th className="pb-2 pe-2">{t("scanner.complianceScore")}</th>
                        <th className="pb-2">{t("scanner.status")}</th>
                      </tr>
                    </thead>
                    <tbody>
                      {result.peer_comparison.map((peer) => (
                        <tr key={peer.company_name} className="border-b border-border/20">
                          <td className="py-2 pe-2">{peer.company_name}</td>
                          <td className="py-2 pe-2">{Math.round(peer.compliance_score * 100)}%</td>
                          <td className="py-2 capitalize">{peer.status}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </CardContent>
            </Card>
          )}
        </motion.div>
      )}
    </PageLayout>
  );
}
