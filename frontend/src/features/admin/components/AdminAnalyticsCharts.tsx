"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { useTranslations } from "@/hooks/useTranslations";
import type { AdminAnalytics } from "@/types/source";

interface AdminAnalyticsChartsProps {
  analytics: AdminAnalytics;
}

function BarChart({
  data,
  label,
  maxValue,
}: {
  data: Array<{ label: string; value: number }>;
  label: string;
  maxValue?: number;
}) {
  const peak = maxValue ?? Math.max(1, ...data.map((d) => d.value));

  return (
    <div role="img" aria-label={label}>
      <div className="flex h-36 items-end gap-2">
        {data.map((item) => (
          <div key={item.label} className="flex flex-1 flex-col items-center gap-1">
            <div
              className="w-full rounded-t-md bg-gradient-to-t from-cyan-600 to-cyan-400 transition-all"
              style={{ height: `${Math.max(8, (item.value / peak) * 100)}%` }}
              title={`${item.label}: ${item.value}`}
            />
            <span className="max-w-full truncate text-[10px] text-muted-foreground">{item.label}</span>
          </div>
        ))}
      </div>
    </div>
  );
}

export function AdminAnalyticsCharts({ analytics }: AdminAnalyticsChartsProps) {
  const { t } = useTranslations();

  const dailyData = analytics.queries_by_day.map((row) => ({
    label: row.date.slice(5),
    value: row.count,
  }));

  const modelData = analytics.model_usage.map((row) => ({
    label: row.model.replace("Fanar-", "").slice(0, 12),
    value: row.count,
  }));

  return (
    <div className="grid gap-4 lg:grid-cols-2">
      <Card className="glass-card">
        <CardHeader className="pb-2">
          <CardTitle className="text-sm font-medium">{t("admin.queryVolume")}</CardTitle>
        </CardHeader>
        <CardContent>
          <BarChart data={dailyData} label={t("admin.queryVolume")} />
          <div className="mt-4 grid grid-cols-2 gap-2 text-xs sm:grid-cols-4">
            <div>
              <p className="text-muted-foreground">{t("admin.totalQueries")}</p>
              <p className="text-lg font-semibold">{analytics.total_queries}</p>
            </div>
            <div>
              <p className="text-muted-foreground">{t("admin.completedQueries")}</p>
              <p className="text-lg font-semibold text-emerald-400">{analytics.completed_queries}</p>
            </div>
            <div>
              <p className="text-muted-foreground">{t("admin.refusalRate")}</p>
              <p className="text-lg font-semibold">{Math.round(analytics.refusal_rate * 100)}%</p>
            </div>
            <div>
              <p className="text-muted-foreground">{t("admin.avgLatency")}</p>
              <p className="text-lg font-semibold">
                {analytics.average_latency_ms != null
                  ? `${Math.round(analytics.average_latency_ms)} ms`
                  : "—"}
              </p>
            </div>
          </div>
        </CardContent>
      </Card>

      <Card className="glass-card">
        <CardHeader className="pb-2">
          <CardTitle className="text-sm font-medium">{t("admin.modelUsage")}</CardTitle>
        </CardHeader>
        <CardContent>
          {modelData.length === 0 ? (
            <p className="text-sm text-muted-foreground">{t("admin.noModelData")}</p>
          ) : (
            <BarChart data={modelData} label={t("admin.modelUsage")} />
          )}
        </CardContent>
      </Card>
    </div>
  );
}
