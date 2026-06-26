"use client";

import Link from "next/link";
import {
  Loader2,
  PieChart,
  Plus,
  RefreshCw,
  Sparkles,
  Trash2,
  TrendingDown,
  TrendingUp,
} from "lucide-react";
import { useCallback, useEffect, useMemo, useState } from "react";

import { PageLayout } from "@/components/PageGuide";
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { ExecutionMetricsPanel } from "@/features/chat/components/ExecutionMetricsPanel";
import { FanarModelSelector } from "@/features/chat/components/FanarModelSelector";
import { ReasoningProcessAccordion } from "@/features/chat/components/ReasoningProcessAccordion";
import { useAuth } from "@/hooks/useAuth";
import { useTranslations } from "@/hooks/useTranslations";
import { useUserPreferences } from "@/hooks/useUserPreferences";
import { cn } from "@/lib/utils";
import { ApiClientError } from "@/services/apiClient";
import {
  fetchZakatPrices,
  scanPortfolio,
  type AllocationSlice,
  type PortfolioHoldingPayload,
  type PortfolioScanResult,
} from "@/services/featuresService";
import type { SavedPortfolioProfile } from "@/services/preferencesService";
import { useSettingsStore } from "@/store/settingsStore";

type HoldingForm = PortfolioHoldingPayload & {
  id: string;
  marketPricePreview: number | null;
  priceLoading: boolean;
  priceError: string | null;
};

const ASSET_TYPES: HoldingForm["asset_type"][] = ["stock", "etf", "reit", "fund", "crypto"];

const STATUS_STYLES: Record<string, string> = {
  green: "bg-emerald-500/15 text-emerald-600 dark:text-emerald-400 border-emerald-500/30",
  yellow: "bg-amber-500/15 text-amber-700 dark:text-amber-400 border-amber-500/30",
  red: "bg-destructive/15 text-destructive border-destructive/30",
};

const ALLOCATION_COLORS = [
  "bg-cyan-500",
  "bg-violet-500",
  "bg-emerald-500",
  "bg-amber-500",
  "bg-rose-500",
  "bg-sky-500",
  "bg-orange-500",
];

function newHolding(): HoldingForm {
  return {
    id: crypto.randomUUID(),
    symbol: "",
    quantity: 1,
    asset_type: "stock",
    use_market_price: true,
    marketPricePreview: null,
    priceLoading: false,
    priceError: null,
  };
}

function formatMoney(value: number | null | undefined, currency = "USD"): string {
  if (value == null) return "—";
  return `${value.toLocaleString(undefined, { maximumFractionDigits: 2 })} ${currency}`;
}

function formatPct(value: number | null | undefined): string {
  if (value == null) return "—";
  const sign = value > 0 ? "+" : "";
  return `${sign}${Math.round(value * 10) / 10}%`;
}

function AllocationChart({
  title,
  slices,
  currency,
}: {
  title: string;
  slices: AllocationSlice[];
  currency: string;
}) {
  if (slices.length === 0) {
    return (
      <div className="rounded-lg border border-border/40 p-4">
        <p className="text-sm font-medium">{title}</p>
        <p className="mt-2 text-xs text-muted-foreground">—</p>
      </div>
    );
  }

  return (
    <div className="rounded-lg border border-border/40 p-4 space-y-3">
      <p className="text-sm font-medium">{title}</p>
      <div className="flex h-3 overflow-hidden rounded-full">
        {slices.map((slice, index) => (
          <div
            key={slice.label}
            className={ALLOCATION_COLORS[index % ALLOCATION_COLORS.length]}
            style={{ width: `${slice.weight_pct}%` }}
            title={`${slice.label} ${slice.weight_pct}%`}
          />
        ))}
      </div>
      <div className="space-y-1">
        {slices.slice(0, 6).map((slice, index) => (
          <div key={slice.label} className="flex items-center justify-between text-xs">
            <span className="flex items-center gap-2 text-muted-foreground">
              <span
                className={cn("inline-block h-2 w-2 rounded-full", ALLOCATION_COLORS[index % ALLOCATION_COLORS.length])}
              />
              {slice.label}
            </span>
            <span>
              {slice.weight_pct}% · {formatMoney(slice.value, currency)}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}

export function PortfolioScannerPanel() {
  const { t, locale } = useTranslations();
  const { accessToken } = useAuth();
  const { save, preferences } = useUserPreferences();
  const fanarModel = useSettingsStore((s) => s.fanarModelPreference);
  const [holdings, setHoldings] = useState<HoldingForm[]>([newHolding()]);
  const [result, setResult] = useState<PortfolioScanResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [saved, setSaved] = useState(false);
  const [portfolioName, setPortfolioName] = useState("My Portfolio");

  const savedProfiles = preferences?.saved_portfolio_profiles ?? [];

  const fetchMarketPreview = useCallback(
    async (symbol: string, assetType: HoldingForm["asset_type"], holdingId: string) => {
      if (!accessToken || !symbol.trim()) return;
      setHoldings((prev) =>
        prev.map((h) =>
          h.id === holdingId ? { ...h, priceLoading: true, priceError: null } : h,
        ),
      );
      try {
        const stockSymbols = assetType === "crypto" ? [] : [symbol.trim().toUpperCase()];
        const cryptoSymbols = assetType === "crypto" ? [symbol.trim().toUpperCase()] : [];
        const prices = await fetchZakatPrices(accessToken, { stock_symbols: stockSymbols, crypto_symbols: cryptoSymbols });
        const key = symbol.trim().toUpperCase();
        const quote = assetType === "crypto" ? prices.crypto[key] : prices.stocks[key];
        const unitPrice =
          assetType === "crypto"
            ? (quote && "unit_price_usd" in quote ? quote.unit_price_converted ?? quote.unit_price_usd : null)
            : (quote && "unit_price" in quote ? quote.unit_price_converted ?? quote.unit_price : null);
        setHoldings((prev) =>
          prev.map((h) =>
            h.id === holdingId
              ? {
                  ...h,
                  priceLoading: false,
                  marketPricePreview: unitPrice,
                  priceError: unitPrice == null ? t("scanner.priceUnavailable") : null,
                }
              : h,
          ),
        );
      } catch {
        setHoldings((prev) =>
          prev.map((h) =>
            h.id === holdingId
              ? { ...h, priceLoading: false, marketPricePreview: null, priceError: t("scanner.priceUnavailable") }
              : h,
          ),
        );
      }
    },
    [accessToken, t],
  );

  useEffect(() => {
    const timers: ReturnType<typeof setTimeout>[] = [];
    for (const holding of holdings) {
      if (!holding.use_market_price || !holding.symbol.trim()) continue;
      timers.push(
        setTimeout(() => {
          void fetchMarketPreview(holding.symbol, holding.asset_type, holding.id);
        }, 600),
      );
    }
    return () => timers.forEach(clearTimeout);
    // eslint-disable-next-line react-hooks/exhaustive-deps -- refetch only when symbol/pricing mode changes
  }, [
    accessToken,
    holdings.map((h) => `${h.id}:${h.symbol}:${h.asset_type}:${h.use_market_price}`).join("|"),
    fetchMarketPreview,
  ]);

  const payloadHoldings = useMemo(
    (): PortfolioHoldingPayload[] =>
      holdings
        .filter((h) => h.symbol.trim() && h.quantity > 0)
        .map(({ id: _id, marketPricePreview: _p, priceLoading: _l, priceError: _e, ...rest }) => rest),
    [holdings],
  );

  const handleScan = async () => {
    if (!accessToken || payloadHoldings.length === 0) return;
    setLoading(true);
    setError(null);
    setSaved(false);
    try {
      setResult(
        await scanPortfolio(accessToken, payloadHoldings, {
          language: locale === "ar" ? "ar" : "en",
          fanar_model: fanarModel,
          include_ai: true,
        }),
      );
    } catch (err) {
      setError(err instanceof ApiClientError ? err.message : t("errors.generic"));
    } finally {
      setLoading(false);
    }
  };

  const handleSavePortfolio = async () => {
    if (!result || payloadHoldings.length === 0) return;
    const name = portfolioName.trim() || payloadHoldings.map((h) => h.symbol).join(", ");
    const profile: SavedPortfolioProfile = {
      id: crypto.randomUUID(),
      name,
      holdings: payloadHoldings.map((h) => ({
        symbol: h.symbol,
        quantity: h.quantity,
        asset_type: h.asset_type ?? "stock",
        purchase_price: h.purchase_price,
        manual_price: h.manual_price,
        use_market_price: h.use_market_price ?? true,
      })),
      created_at: new Date().toISOString(),
      last_scanned_at: result.scanned_at,
    };
    const existing = savedProfiles.filter((p) => p.name !== name);
    await save({ saved_portfolio_profiles: [...existing, profile] });
    setSaved(true);
  };

  const loadProfile = (profile: SavedPortfolioProfile) => {
    setPortfolioName(profile.name);
    setHoldings(
      profile.holdings.map((h) => ({
        ...newHolding(),
        symbol: h.symbol,
        quantity: h.quantity,
        asset_type: h.asset_type,
        purchase_price: h.purchase_price ?? undefined,
        manual_price: h.manual_price ?? undefined,
        use_market_price: h.use_market_price ?? true,
      })),
    );
    setResult(null);
    setSaved(false);
  };

  const updateHolding = (id: string, patch: Partial<HoldingForm>) => {
    setHoldings((prev) => prev.map((h) => (h.id === id ? { ...h, ...patch } : h)));
  };

  return (
    <PageLayout guideKey="portfolioScanner" className="mx-auto max-w-5xl space-y-6">
      <Card className="glass-card border-cyan-500/20">
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-lg">
            <PieChart className="h-5 w-5 text-cyan-400" />
            {t("pages.portfolioScanner.title")}
          </CardTitle>
          <p className="text-sm text-muted-foreground">{t("pages.portfolioScanner.description")}</p>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex flex-col gap-3 sm:flex-row sm:items-end">
            <div className="flex-1 space-y-1">
              <label className="text-xs text-muted-foreground">{t("scanner.portfolioName")}</label>
              <Input value={portfolioName} onChange={(e) => setPortfolioName(e.target.value)} />
            </div>
            {savedProfiles.length > 0 && (
              <div className="flex flex-wrap gap-2">
                {savedProfiles.map((profile) => (
                  <Button key={profile.id} variant="outline" size="sm" onClick={() => loadProfile(profile)}>
                    {t("scanner.loadPortfolio")}: {profile.name}
                  </Button>
                ))}
              </div>
            )}
          </div>

          {holdings.map((holding) => (
            <div
              key={holding.id}
              className="rounded-lg border border-border/40 bg-muted/5 p-3 space-y-3"
            >
              <div className="grid gap-2 sm:grid-cols-2 lg:grid-cols-4">
                <Input
                  value={holding.symbol}
                  onChange={(e) => updateHolding(holding.id, { symbol: e.target.value.toUpperCase() })}
                  placeholder={t("scanner.symbol")}
                />
                <Input
                  type="number"
                  min={0}
                  step="any"
                  value={holding.quantity}
                  onChange={(e) => updateHolding(holding.id, { quantity: Number(e.target.value) || 0 })}
                  placeholder={t("scanner.quantity")}
                />
                <select
                  className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                  value={holding.asset_type ?? "stock"}
                  onChange={(e) =>
                    updateHolding(holding.id, {
                      asset_type: e.target.value as HoldingForm["asset_type"],
                    })
                  }
                >
                  {ASSET_TYPES.map((type) => (
                    <option key={type} value={type}>
                      {t(`scanner.${type}` as "scanner.stock")}
                    </option>
                  ))}
                </select>
                <Input
                  type="number"
                  min={0}
                  step="any"
                  value={holding.purchase_price ?? ""}
                  onChange={(e) =>
                    updateHolding(holding.id, {
                      purchase_price: e.target.value ? Number(e.target.value) : undefined,
                    })
                  }
                  placeholder={t("scanner.purchasePrice")}
                />
              </div>

              <div className="flex flex-wrap items-center gap-3">
                <label className="flex items-center gap-2 text-sm">
                  <input
                    type="checkbox"
                    checked={holding.use_market_price ?? true}
                    onChange={(e) =>
                      updateHolding(holding.id, {
                        use_market_price: e.target.checked,
                        manual_price: e.target.checked ? undefined : holding.manual_price,
                      })
                    }
                  />
                  {t("scanner.useMarketPrice")}
                </label>

                {holding.use_market_price ? (
                  <span className="text-xs text-muted-foreground">
                    {holding.priceLoading ? (
                      <span className="inline-flex items-center gap-1">
                        <Loader2 className="h-3 w-3 animate-spin" />
                        {t("scanner.fetchingPrice")}
                      </span>
                    ) : holding.marketPricePreview != null ? (
                      <>
                        {t("scanner.marketPrice")}: {formatMoney(holding.marketPricePreview)}
                      </>
                    ) : holding.symbol ? (
                      holding.priceError ?? t("scanner.priceUnavailable")
                    ) : null}
                  </span>
                ) : (
                  <div className="flex items-center gap-2">
                    <Input
                      type="number"
                      min={0}
                      step="any"
                      className="h-8 w-32"
                      value={holding.manual_price ?? ""}
                      onChange={(e) =>
                        updateHolding(holding.id, {
                          manual_price: e.target.value ? Number(e.target.value) : undefined,
                        })
                      }
                      placeholder={t("scanner.manualPrice")}
                    />
                    <Badge variant="outline">{t("scanner.manualPriceBadge")}</Badge>
                  </div>
                )}

                <Button
                  variant="ghost"
                  size="icon"
                  className="ms-auto"
                  onClick={() => setHoldings((prev) => prev.filter((h) => h.id !== holding.id))}
                  disabled={holdings.length <= 1}
                >
                  <Trash2 className="h-4 w-4" />
                </Button>
              </div>
            </div>
          ))}

          <div className="flex flex-wrap items-center gap-3">
            <Button variant="outline" size="sm" onClick={() => setHoldings((prev) => [...prev, newHolding()])}>
              <Plus className="h-4 w-4" />
              {t("scanner.addHolding")}
            </Button>
            <FanarModelSelector />
            <Button
              onClick={() => void handleScan()}
              disabled={loading || !accessToken || payloadHoldings.length === 0}
            >
              {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : t("scanner.scanPortfolio")}
            </Button>
          </div>
        </CardContent>
      </Card>

      {error && <p className="text-center text-sm text-destructive">{error}</p>}

      {loading && (
        <Card className="glass-card">
          <CardContent className="flex items-center justify-center gap-3 py-10 text-sm text-muted-foreground">
            <Loader2 className="h-5 w-5 animate-spin text-cyan-400" />
            {t("scanner.fetchingPrice")} · Fanar…
          </CardContent>
        </Card>
      )}

      {result && !loading && (
        <div className="space-y-4">
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
            <Card className="glass-card">
              <CardContent className="pt-6">
                <p className="text-xs text-muted-foreground">{t("scanner.totalValue")}</p>
                <p className="text-2xl font-bold">{formatMoney(result.total_value, result.output_currency)}</p>
              </CardContent>
            </Card>
            <Card className="glass-card">
              <CardContent className="pt-6">
                <p className="text-xs text-muted-foreground">{t("scanner.weightedCompliance")}</p>
                <p className="text-2xl font-bold text-cyan-400">{Math.round(result.halal_score * 100)}%</p>
              </CardContent>
            </Card>
            <Card className="glass-card">
              <CardContent className="pt-6">
                <p className="text-xs text-muted-foreground">{t("scanner.diversification")}</p>
                <p className="text-2xl font-bold">{Math.round(result.diversification_score * 100)}%</p>
              </CardContent>
            </Card>
            <Card className="glass-card">
              <CardContent className="pt-6">
                <p className="text-xs text-muted-foreground">{t("scanner.purification")}</p>
                <p className="text-2xl font-bold">{formatMoney(result.purification_amount, result.output_currency)}</p>
              </CardContent>
            </Card>
          </div>

          <Card className="glass-card border-cyan-500/20">
            <CardContent className="space-y-2 pt-6">
              <p className="text-xs font-medium uppercase tracking-wide text-muted-foreground">
                {t("scanner.portfolioAssessment")}
              </p>
              <p className="text-lg font-semibold capitalize">{result.portfolio_assessment.replace(/_/g, " ")}</p>
              <p className="text-sm text-muted-foreground">{result.portfolio_assessment_detail}</p>
              <div className="grid gap-2 pt-2 sm:grid-cols-2 lg:grid-cols-4 text-sm">
                <div>
                  <span className="text-muted-foreground">{t("scanner.holdingsCount")}: </span>
                  {result.insights.holdings_count}
                </div>
                <div>
                  <span className="text-muted-foreground">{t("scanner.largestPosition")}: </span>
                  {result.insights.largest_position ?? "—"}
                </div>
                <div>
                  <span className="text-muted-foreground">{t("scanner.dailyChange")}: </span>
                  {result.insights.daily_change_pct != null ? (
                    <span
                      className={cn(
                        "inline-flex items-center gap-0.5",
                        result.insights.daily_change_pct >= 0 ? "text-emerald-500" : "text-destructive",
                      )}
                    >
                      {result.insights.daily_change_pct >= 0 ? (
                        <TrendingUp className="h-3 w-3" />
                      ) : (
                        <TrendingDown className="h-3 w-3" />
                      )}
                      {formatPct(result.insights.daily_change_pct)}
                    </span>
                  ) : (
                    t("scanner.dataUnavailable")
                  )}
                </div>
                <div>
                  <span className="text-muted-foreground">{t("scanner.unrealizedGainLoss")}: </span>
                  {result.insights.unrealized_gain_loss != null
                    ? `${formatMoney(result.insights.unrealized_gain_loss, result.output_currency)} (${formatPct(result.insights.unrealized_gain_loss_pct)})`
                    : t("scanner.dataUnavailable")}
                </div>
              </div>
            </CardContent>
          </Card>

          <div className="grid gap-4 lg:grid-cols-2">
            <AllocationChart
              title={t("scanner.sectorAllocation")}
              slices={result.sector_allocation}
              currency={result.output_currency}
            />
            <AllocationChart
              title={t("scanner.countryAllocation")}
              slices={result.country_allocation}
              currency={result.output_currency}
            />
            <AllocationChart
              title={t("scanner.currencyAllocation")}
              slices={result.currency_allocation}
              currency={result.output_currency}
            />
            <AllocationChart
              title={t("scanner.assetAllocation")}
              slices={result.asset_type_allocation}
              currency={result.output_currency}
            />
          </div>

          {result.ai_analysis && (
            <Card className="glass-card border-violet-500/20">
              <CardHeader>
                <CardTitle className="flex items-center gap-2 text-base">
                  <Sparkles className="h-4 w-4 text-violet-400" />
                  {t("scanner.fanarPortfolioAnalysis")}
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-3 text-sm">
                <p>{result.ai_analysis}</p>
                {result.ai_observations.length > 0 && (
                  <ul className="space-y-1 text-muted-foreground">
                    {result.ai_observations.map((item) => (
                      <li key={item}>• {item}</li>
                    ))}
                  </ul>
                )}
                {result.ai_limitations.length > 0 && (
                  <div className="rounded-md border border-amber-500/30 bg-amber-500/5 p-3 text-xs">
                    <p className="font-medium">{t("scanner.dataGaps")}</p>
                    {result.ai_limitations.map((item) => (
                      <p key={item} className="mt-1 text-muted-foreground">
                        • {item}
                      </p>
                    ))}
                  </div>
                )}
              </CardContent>
            </Card>
          )}

          <Accordion type="single" collapsible className="glass-card rounded-lg border px-4">
            <AccordionItem value="methodology">
              <AccordionTrigger>{t("scanner.shariahMethodology")}</AccordionTrigger>
              <AccordionContent className="space-y-3 text-sm text-muted-foreground pb-4">
                <div>
                  <p className="font-medium text-foreground">{t("scanner.standardsUsed")}</p>
                  <ul className="mt-1 list-inside list-disc">
                    {result.shariah_methodology.standards_used.map((s) => (
                      <li key={s}>{s}</li>
                    ))}
                  </ul>
                </div>
                <div>
                  <p className="font-medium text-foreground">{t("scanner.screeningMethod")}</p>
                  <p>{result.shariah_methodology.screening_methodology}</p>
                </div>
                <div>
                  <p className="font-medium text-foreground">{t("scanner.financialRatioMethod")}</p>
                  <p>{result.shariah_methodology.financial_ratio_methodology}</p>
                </div>
                <div>
                  <p className="font-medium text-foreground">{t("scanner.businessActivityMethod")}</p>
                  <p>{result.shariah_methodology.business_activity_methodology}</p>
                </div>
                <div>
                  <p className="font-medium text-foreground">{t("scanner.purificationMethod")}</p>
                  <p>{result.shariah_methodology.purification_methodology}</p>
                </div>
                <div>
                  <p className="font-medium text-foreground">{t("scanner.aggregationMethod")}</p>
                  <p>{result.shariah_methodology.aggregation_methodology}</p>
                </div>
              </AccordionContent>
            </AccordionItem>
          </Accordion>

          <Card className="glass-card">
            <CardHeader>
              <CardTitle className="text-base">{t("scanner.allocation")}</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              {result.holdings.map((holding) => (
                <Accordion key={holding.symbol} type="single" collapsible>
                  <AccordionItem value={holding.symbol} className="border-border/40">
                    <AccordionTrigger className="hover:no-underline py-3">
                      <div className="flex flex-1 flex-wrap items-center gap-2 text-left">
                        <span className="font-semibold">{holding.symbol}</span>
                        <span className="text-xs text-muted-foreground">{holding.name}</span>
                        <Badge variant="outline" className={STATUS_STYLES[holding.status] ?? ""}>
                          {t(`scanner.complianceBadge.${holding.status}` as "scanner.complianceBadge.green")}
                        </Badge>
                        {holding.price_source === "manual" && (
                          <Badge variant="secondary">{t("scanner.manualPriceBadge")}</Badge>
                        )}
                        <span className="ms-auto text-sm">
                          {holding.weight_pct}% · {formatMoney(holding.value, result.output_currency)}
                        </span>
                      </div>
                    </AccordionTrigger>
                    <AccordionContent className="space-y-3 pb-4 text-sm">
                      <div className="grid gap-2 sm:grid-cols-2 lg:grid-cols-3 text-xs text-muted-foreground">
                        <p>
                          {t("scanner.marketPrice")}:{" "}
                          {holding.current_price != null
                            ? formatMoney(holding.current_price, holding.currency ?? result.output_currency)
                            : t("scanner.dataUnavailable")}
                        </p>
                        <p>{t("scanner.quantity")}: {holding.quantity}</p>
                        <p>
                          {t("scanner.sectorAllocation")}: {holding.sector ?? t("scanner.dataUnavailable")}
                        </p>
                        <p>
                          {t("scanner.countryAllocation")}: {holding.country ?? t("scanner.dataUnavailable")}
                        </p>
                        <p>
                          {t("scanner.dailyChange")}: {formatPct(holding.daily_change_pct)}
                        </p>
                        <p>
                          {t("scanner.complianceScore")}: {Math.round(holding.compliance_score * 100)}%
                        </p>
                      </div>
                      <p className="rounded-md bg-muted/20 p-3 text-xs leading-relaxed">
                        {holding.compliance_explanation}
                      </p>
                      {holding.data_unavailable.length > 0 && (
                        <p className="text-xs text-amber-600 dark:text-amber-400">
                          {holding.data_unavailable.join(" · ")}
                        </p>
                      )}
                      <Link
                        href={`/scanner/company?q=${encodeURIComponent(holding.symbol)}`}
                        className="inline-flex text-xs text-cyan-500 hover:underline"
                      >
                        {t("scanner.viewCompanyScan")} →
                      </Link>
                    </AccordionContent>
                  </AccordionItem>
                </Accordion>
              ))}
            </CardContent>
          </Card>

          {result.violations.length > 0 && (
            <Card className="glass-card border-destructive/20">
              <CardContent className="space-y-2 pt-6 text-sm">
                {result.violations.map((item) => (
                  <p key={item}>• {item}</p>
                ))}
              </CardContent>
            </Card>
          )}

          {result.recommendations.length > 0 && (
            <Card className="glass-card">
              <CardContent className="space-y-2 pt-6 text-sm text-muted-foreground">
                {result.recommendations.map((item) => (
                  <p key={item}>• {item}</p>
                ))}
              </CardContent>
            </Card>
          )}

          {result.data_gaps.length > 0 && (
            <Card className="glass-card border-amber-500/20">
              <CardContent className="space-y-2 pt-6 text-sm">
                <p className="font-medium">{t("scanner.dataGaps")}</p>
                {result.data_gaps.map((item) => (
                  <p key={item} className="text-muted-foreground">
                    • {item}
                  </p>
                ))}
              </CardContent>
            </Card>
          )}

          {result.agent_trace.length > 0 && (
            <ReasoningProcessAccordion steps={result.agent_trace} defaultOpen={false} />
          )}
          {result.execution_metrics && result.agent_trace.length > 0 && (
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
          )}

          <div className="flex justify-end gap-2">
            <Button variant="outline" size="sm" onClick={() => void handleScan()} disabled={loading}>
              <RefreshCw className="h-4 w-4" />
              {t("scanner.scanPortfolio")}
            </Button>
            <Button variant="outline" size="sm" disabled={saved} onClick={() => void handleSavePortfolio()}>
              {saved ? t("scanner.savedPortfolio") : t("scanner.savePortfolio")}
            </Button>
          </div>
        </div>
      )}
    </PageLayout>
  );
}
