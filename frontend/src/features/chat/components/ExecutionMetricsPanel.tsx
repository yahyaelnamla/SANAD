"use client";

import { AgentTraceTimeline } from "@/features/chat/components/AgentTraceTimeline";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { useTranslations } from "@/hooks/useTranslations";
import type { AgentTraceStep, ExecutionMetrics } from "@/types/query";

interface ExecutionMetricsPanelProps {
  steps: AgentTraceStep[];
  metrics?: ExecutionMetrics | null;
}

function formatLatency(ms: number | null | undefined): string {
  if (ms == null) return "—";
  if (ms < 1000) return `${ms} ms`;
  return `${(ms / 1000).toFixed(1)} s`;
}

function estimateCostUsd(tokens: number): string {
  const usd = (tokens / 1_000_000) * 2.5;
  if (usd < 0.01) return "< $0.01";
  return `$${usd.toFixed(3)}`;
}

export function ExecutionMetricsPanel({ steps, metrics }: ExecutionMetricsPanelProps) {
  const { t } = useTranslations();

  const settledSteps = steps.filter((step) => step.status !== "running");
  const completedCount = settledSteps.filter((step) => step.status === "completed").length;
  const total = settledSteps.length;

  const models = [
    ...new Set(
      settledSteps
        .filter((step) => step.status === "completed" && step.model)
        .map((step) => step.model as string),
    ),
  ];

  const totalLatency =
    metrics?.total_latency_ms ??
    settledSteps.reduce((sum, step) => sum + (step.latency_ms ?? 0), 0);

  return (
    <div className="space-y-4">
      <Card className="glass-card border-border/50">
        <CardHeader className="pb-2">
          <CardTitle className="text-sm font-semibold">{t("explainability.executionMetrics")}</CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          <div className="flex flex-wrap gap-2 text-xs">
            <Badge variant="secondary">
              {t("explainability.stepsCompleted")}: {completedCount}/{total}
            </Badge>
            <Badge variant="outline">
              {t("explainability.totalLatency")}: {formatLatency(totalLatency)}
            </Badge>
            {(metrics?.tokens_total ?? metrics?.tokens_estimate) != null && (
              <>
                <Badge variant="outline">
                  {t("explainability.tokensEstimate")}:{" "}
                  {(metrics?.tokens_total ?? metrics?.tokens_estimate ?? 0).toLocaleString()}
                </Badge>
                <Badge variant="outline">
                  {t("explainability.costEstimate")}:{" "}
                  {estimateCostUsd(metrics?.tokens_total ?? metrics?.tokens_estimate ?? 0)}
                </Badge>
              </>
            )}
            {metrics?.fanar_model_preference && metrics.fanar_model_preference !== "auto" && (
              <Badge variant="outline">
                {t("chat.modelLabel")}: {metrics.fanar_model_preference}
              </Badge>
            )}
            {metrics?.pipeline_depth && (
              <Badge variant="secondary">
                {t("explainability.pipelineDepth")}:{" "}
                {metrics.pipeline_depth === "fast"
                  ? t("chat.pipelineFast")
                  : metrics.pipeline_depth === "standard"
                    ? t("chat.pipelineStandard")
                    : t("chat.pipelineDeep")}
              </Badge>
            )}
            {metrics?.auto_mode && (
              <Badge variant="secondary">
                {t("explainability.autoMode")}: {t(`autoMode.${metrics.auto_mode}` as "autoMode.fast")}
              </Badge>
            )}
            {metrics?.document_context_used && (
              <Badge variant="outline">{t("explainability.documentMemoryUsed")}</Badge>
            )}
            {metrics?.conversation_memory_used && (
              <Badge variant="outline">{t("explainability.conversationMemoryUsed")}</Badge>
            )}
          </div>

          <AgentTraceTimeline steps={settledSteps} compact showLatency />
        </CardContent>
      </Card>

      {models.length > 0 && (
        <Card className="glass-card border-border/50">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-semibold">{t("explainability.modelsUsed")}</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex flex-wrap gap-2">
              {models.map((model) => (
                <Badge key={model} variant="outline" className="font-mono text-[11px]">
                  {model}
                </Badge>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
