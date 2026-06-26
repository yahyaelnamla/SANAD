"use client";

import { Calculator, Loader2, Plus, RefreshCw, Sparkles, Trash2 } from "lucide-react";
import { useCallback, useState } from "react";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { useAuth } from "@/hooks/useAuth";
import { useTranslations } from "@/hooks/useTranslations";
import { cn } from "@/lib/utils";
import { ApiClientError } from "@/services/apiClient";
import {
  calculateZakat,
  fetchZakatPrices,
  type ZakatHoldingPayload,
  type ZakatResult,
} from "@/services/featuresService";

const CURRENCIES = ["USD", "EUR", "GBP", "SAR", "AED", "EGP", "QAR", "KWD", "BHD", "OMR", "PKR", "MYR", "TRY"] as const;

interface ZakatFormState {
  cash: number;
  cashCurrency: string;
  goldGrams: number;
  goldPriceCurrency: string;
  goldPriceOverride: number | null;
  stockHoldings: ZakatHoldingPayload[];
  cryptoHoldings: ZakatHoldingPayload[];
  debts: number;
  debtCurrency: string;
  outputCurrency: string;
  fetchLivePrices: boolean;
  includeAiGuidance: boolean;
}

const DEFAULT_FORM: ZakatFormState = {
  cash: 10000,
  cashCurrency: "USD",
  goldGrams: 50,
  goldPriceCurrency: "USD",
  goldPriceOverride: null,
  stockHoldings: [{ symbol: "AAPL", quantity: 10, asset_type: "stock" }],
  cryptoHoldings: [{ symbol: "BTC", quantity: 0.25, asset_type: "crypto" }],
  debts: 2000,
  debtCurrency: "USD",
  outputCurrency: "USD",
  fetchLivePrices: true,
  includeAiGuidance: true,
};

function CurrencySelect({
  value,
  onChange,
  className,
}: {
  value: string;
  onChange: (value: string) => void;
  className?: string;
}) {
  return (
    <select
      value={value}
      onChange={(e) => onChange(e.target.value)}
      className={cn(
        "h-10 rounded-md border border-input bg-background px-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring",
        className,
      )}
    >
      {CURRENCIES.map((code) => (
        <option key={code} value={code}>
          {code}
        </option>
      ))}
    </select>
  );
}

export function ZakatCalculatorPanel() {
  const { t, locale } = useTranslations();
  const { accessToken } = useAuth();
  const [form, setForm] = useState<ZakatFormState>(DEFAULT_FORM);
  const [result, setResult] = useState<ZakatResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [priceLoading, setPriceLoading] = useState(false);
  const [priceHint, setPriceHint] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const buildPayload = useCallback(
    () => ({
      cash: form.cash,
      cash_currency: form.cashCurrency,
      gold_grams: form.goldGrams,
      gold_price_currency: form.goldPriceCurrency,
      gold_price_per_gram: form.goldPriceOverride,
      stock_holdings: form.stockHoldings.filter((h) => h.symbol.trim() && h.quantity > 0),
      crypto_holdings: form.cryptoHoldings.filter((h) => h.symbol.trim() && h.quantity > 0),
      debts: form.debts,
      debt_currency: form.debtCurrency,
      output_currency: form.outputCurrency,
      fetch_live_prices: form.fetchLivePrices,
      include_ai_guidance: form.includeAiGuidance,
      language: locale,
    }),
    [form, locale],
  );

  const handleFetchPrices = async () => {
    if (!accessToken) return;
    setPriceLoading(true);
    setError(null);
    try {
      const prices = await fetchZakatPrices(accessToken, {
        output_currency: form.outputCurrency,
        gold_currency: form.goldPriceCurrency,
        stock_symbols: form.stockHoldings.map((h) => h.symbol).filter(Boolean),
        crypto_symbols: form.cryptoHoldings.map((h) => h.symbol).filter(Boolean),
      });
      setForm((prev) => ({ ...prev, goldPriceOverride: prices.gold_price_per_gram }));
      const stockHints = Object.entries(prices.stocks)
        .map(([sym, row]) => `${sym}: ${row.unit_price_converted.toLocaleString()} ${form.outputCurrency}`)
        .join(" · ");
      const cryptoHints = Object.entries(prices.crypto)
        .map(([sym, row]) => `${sym}: ${row.unit_price_converted.toLocaleString()} ${form.outputCurrency}`)
        .join(" · ");
      setPriceHint(
        [
          `${t("zakat.goldPrice")}: ${prices.gold_price_per_gram.toLocaleString()} ${prices.gold_price_currency}/g`,
          stockHints,
          cryptoHints,
        ]
          .filter(Boolean)
          .join(" · "),
      );
    } catch (err) {
      setError(err instanceof ApiClientError ? err.message : t("errors.generic"));
    } finally {
      setPriceLoading(false);
    }
  };

  const handleCalculate = async () => {
    if (!accessToken) return;
    setLoading(true);
    setError(null);
    try {
      setResult(await calculateZakat(accessToken, buildPayload()));
    } catch (err) {
      setError(err instanceof ApiClientError ? err.message : t("errors.generic"));
    } finally {
      setLoading(false);
    }
  };

  const updateHolding = (
    type: "stock" | "crypto",
    index: number,
    patch: Partial<ZakatHoldingPayload>,
  ) => {
    const key = type === "stock" ? "stockHoldings" : "cryptoHoldings";
    setForm((prev) => ({
      ...prev,
      [key]: prev[key].map((item, i) => (i === index ? { ...item, ...patch } : item)),
    }));
  };

  return (
    <div className="mx-auto max-w-3xl space-y-6">
      <Card className="glass-card border-cyan-500/20">
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-lg">
            <Calculator className="h-5 w-5 text-cyan-400" />
            {t("zakat.title")}
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="flex flex-wrap items-end gap-3">
            <label className="space-y-2 text-sm">
              <span className="text-muted-foreground">{t("zakat.outputCurrency")}</span>
              <CurrencySelect
                value={form.outputCurrency}
                onChange={(value) => setForm((prev) => ({ ...prev, outputCurrency: value }))}
              />
            </label>
            <Button
              variant="outline"
              size="sm"
              className="gap-2"
              disabled={priceLoading || !accessToken}
              onClick={() => void handleFetchPrices()}
            >
              {priceLoading ? <Loader2 className="h-4 w-4 animate-spin" /> : <RefreshCw className="h-4 w-4" />}
              {t("zakat.fetchPrices")}
            </Button>
          </div>

          {priceHint && <p className="text-xs text-cyan-400/90">{priceHint}</p>}

          <div className="grid gap-4 sm:grid-cols-2">
            <label className="space-y-2 text-sm">
              <span className="text-muted-foreground">{t("zakat.cash")}</span>
              <div className="flex gap-2">
                <Input
                  type="number"
                  min={0}
                  value={form.cash}
                  onChange={(e) => setForm((prev) => ({ ...prev, cash: Number(e.target.value) || 0 }))}
                />
                <CurrencySelect
                  value={form.cashCurrency}
                  onChange={(value) => setForm((prev) => ({ ...prev, cashCurrency: value }))}
                  className="w-24 shrink-0"
                />
              </div>
            </label>

            <label className="space-y-2 text-sm">
              <span className="text-muted-foreground">{t("zakat.gold")}</span>
              <div className="relative">
                <Input
                  type="number"
                  min={0}
                  step="any"
                  value={form.goldGrams}
                  className="pe-12"
                  onChange={(e) => setForm((prev) => ({ ...prev, goldGrams: Number(e.target.value) || 0 }))}
                />
                <span className="pointer-events-none absolute inset-y-0 end-3 flex items-center text-xs text-muted-foreground">
                  {t("zakat.gramsUnit")}
                </span>
              </div>
            </label>

            <label className="space-y-2 text-sm sm:col-span-2">
              <span className="text-muted-foreground">{t("zakat.goldPrice")}</span>
              <div className="flex gap-2">
                <div className="relative flex-1">
                  <Input
                    type="number"
                    min={0}
                    placeholder={t("zakat.goldPriceAuto")}
                    value={form.goldPriceOverride ?? ""}
                    className="pe-10"
                    onChange={(e) =>
                      setForm((prev) => ({
                        ...prev,
                        goldPriceOverride: e.target.value ? Number(e.target.value) : null,
                      }))
                    }
                  />
                  <span className="pointer-events-none absolute inset-y-0 end-3 flex items-center text-xs text-muted-foreground">
                    /{t("zakat.gramsUnit")}
                  </span>
                </div>
                <CurrencySelect
                  value={form.goldPriceCurrency}
                  onChange={(value) => setForm((prev) => ({ ...prev, goldPriceCurrency: value }))}
                  className="w-24 shrink-0"
                />
              </div>
            </label>

            <label className="space-y-2 text-sm sm:col-span-2">
              <span className="text-muted-foreground">{t("zakat.debts")}</span>
              <div className="flex gap-2">
                <Input
                  type="number"
                  min={0}
                  value={form.debts}
                  onChange={(e) => setForm((prev) => ({ ...prev, debts: Number(e.target.value) || 0 }))}
                />
                <CurrencySelect
                  value={form.debtCurrency}
                  onChange={(value) => setForm((prev) => ({ ...prev, debtCurrency: value }))}
                  className="w-24 shrink-0"
                />
              </div>
            </label>
          </div>

          <div className="space-y-3">
            <p className="text-sm font-medium text-muted-foreground">{t("zakat.stocks")}</p>
            {form.stockHoldings.map((holding, index) => (
              <div key={`stock-${index}`} className="grid gap-2 sm:grid-cols-[1fr_120px_40px]">
                <Input
                  value={holding.symbol}
                  placeholder={t("zakat.symbolPlaceholder")}
                  onChange={(e) => updateHolding("stock", index, { symbol: e.target.value.toUpperCase() })}
                />
                <div className="relative">
                  <Input
                    type="number"
                    min={0}
                    step="any"
                    placeholder={t("zakat.shares")}
                    value={holding.quantity}
                    className="pe-14"
                    onChange={(e) => updateHolding("stock", index, { quantity: Number(e.target.value) || 0 })}
                  />
                  <span className="pointer-events-none absolute inset-y-0 end-2 flex items-center text-[10px] text-muted-foreground">
                    {t("zakat.sharesUnit")}
                  </span>
                </div>
                <Button
                  variant="ghost"
                  size="icon"
                  onClick={() =>
                    setForm((prev) => ({
                      ...prev,
                      stockHoldings: prev.stockHoldings.filter((_, i) => i !== index),
                    }))
                  }
                >
                  <Trash2 className="h-4 w-4" />
                </Button>
              </div>
            ))}
            <Button
              variant="outline"
              size="sm"
              onClick={() =>
                setForm((prev) => ({
                  ...prev,
                  stockHoldings: [...prev.stockHoldings, { symbol: "", quantity: 0, asset_type: "stock" }],
                }))
              }
            >
              <Plus className="h-4 w-4" />
              {t("zakat.addStock")}
            </Button>
          </div>

          <div className="space-y-3">
            <p className="text-sm font-medium text-muted-foreground">{t("zakat.crypto")}</p>
            {form.cryptoHoldings.map((holding, index) => (
              <div key={`crypto-${index}`} className="grid gap-2 sm:grid-cols-[1fr_120px_40px]">
                <Input
                  value={holding.symbol}
                  placeholder="BTC"
                  onChange={(e) => updateHolding("crypto", index, { symbol: e.target.value.toUpperCase() })}
                />
                <div className="relative">
                  <Input
                    type="number"
                    min={0}
                    step="any"
                    placeholder={t("zakat.amount")}
                    value={holding.quantity}
                    className="pe-14"
                    onChange={(e) => updateHolding("crypto", index, { quantity: Number(e.target.value) || 0 })}
                  />
                  <span className="pointer-events-none absolute inset-y-0 end-2 flex max-w-[40px] truncate items-center text-[10px] text-muted-foreground">
                    {holding.symbol.trim() || t("zakat.coinsUnit")}
                  </span>
                </div>
                <Button
                  variant="ghost"
                  size="icon"
                  onClick={() =>
                    setForm((prev) => ({
                      ...prev,
                      cryptoHoldings: prev.cryptoHoldings.filter((_, i) => i !== index),
                    }))
                  }
                >
                  <Trash2 className="h-4 w-4" />
                </Button>
              </div>
            ))}
            <Button
              variant="outline"
              size="sm"
              onClick={() =>
                setForm((prev) => ({
                  ...prev,
                  cryptoHoldings: [...prev.cryptoHoldings, { symbol: "", quantity: 0, asset_type: "crypto" }],
                }))
              }
            >
              <Plus className="h-4 w-4" />
              {t("zakat.addCrypto")}
            </Button>
          </div>

          <label className="flex items-center gap-2 text-sm text-muted-foreground">
            <input
              type="checkbox"
              checked={form.includeAiGuidance}
              onChange={(e) => setForm((prev) => ({ ...prev, includeAiGuidance: e.target.checked }))}
              className="rounded border-border"
            />
            <Sparkles className="h-4 w-4 text-cyan-400" />
            {t("zakat.aiGuidance")}
          </label>

          <Button
            onClick={() => void handleCalculate()}
            disabled={loading || !accessToken}
            className="w-full bg-gradient-to-r from-cyan-500 to-teal-500 text-slate-950"
          >
            {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : t("zakat.calculate")}
          </Button>
        </CardContent>
      </Card>

      {error && <p className="text-center text-sm text-destructive">{error}</p>}

      {result && (
        <div className="grid gap-4 sm:grid-cols-2">
          <Card className="glass-card">
            <CardContent className="space-y-2 pt-6">
              <p className="text-xs text-muted-foreground">{t("zakat.netWealth")}</p>
              <p className="text-2xl font-bold">
                {result.net_wealth.toLocaleString()} {result.output_currency}
              </p>
            </CardContent>
          </Card>
          <Card className="glass-card border-emerald-500/30">
            <CardContent className="space-y-2 pt-6">
              <p className="text-xs text-muted-foreground">{t("zakat.due")}</p>
              <p className="text-2xl font-bold text-emerald-400">
                {result.zakat_due.toLocaleString()} {result.output_currency}
              </p>
            </CardContent>
          </Card>

          {result.asset_breakdown.length > 0 && (
            <Card className="glass-card sm:col-span-2">
              <CardContent className="space-y-2 pt-6">
                <p className="text-xs font-medium text-muted-foreground">{t("zakat.breakdown")}</p>
                <div className="responsive-table-wrap safe-scroll-x">
                  <table className="w-full min-w-[480px] text-left text-sm">
                    <thead>
                      <tr className="border-b border-border/40 text-xs text-muted-foreground">
                        <th className="pb-2 pe-2">{t("zakat.asset")}</th>
                        <th className="pb-2 pe-2">{t("zakat.quantity")}</th>
                        <th className="pb-2 pe-2">{t("zakat.unitPrice")}</th>
                        <th className="pb-2">{t("zakat.value")}</th>
                      </tr>
                    </thead>
                    <tbody>
                      {result.asset_breakdown.map((row) => (
                        <tr key={`${row.category}-${row.label}`} className="border-b border-border/20">
                          <td className="py-2 pe-2">{row.label}</td>
                          <td className="py-2 pe-2">{row.quantity_display ?? "—"}</td>
                          <td className="py-2 pe-2">{row.unit_price_display ?? "—"}</td>
                          <td className="py-2">
                            {row.value_in_output_currency.toLocaleString()} {result.output_currency}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </CardContent>
            </Card>
          )}

          {result.ai_guidance && (
            <Card className="glass-card border-cyan-500/20 sm:col-span-2">
              <CardContent className="space-y-2 pt-6 text-sm">
                <p className="flex items-center gap-2 font-medium text-cyan-300">
                  <Sparkles className="h-4 w-4" />
                  {t("zakat.aiInsight")}
                </p>
                <p className="whitespace-pre-wrap text-muted-foreground">{result.ai_guidance}</p>
              </CardContent>
            </Card>
          )}

          <Card className="glass-card sm:col-span-2">
            <CardContent className="space-y-2 pt-6 text-sm text-muted-foreground">
              {result.notes.map((note) => (
                <p key={note}>• {note}</p>
              ))}
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  );
}
