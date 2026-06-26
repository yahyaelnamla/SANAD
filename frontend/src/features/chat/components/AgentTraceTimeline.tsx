"use client";

import { motion } from "framer-motion";
import { CheckCircle2, Circle, Loader2, XCircle } from "lucide-react";

import { useTranslations } from "@/hooks/useTranslations";
import { localizeAgentStep, localizeTraceStatus } from "@/lib/domainLocalizations";
import { cn } from "@/lib/utils";
import type { AgentTraceStep } from "@/types/query";

interface AgentTraceTimelineProps {
  steps: AgentTraceStep[];
  activeModel?: string | null;
  className?: string;
  compact?: boolean;
  showLatency?: boolean;
}

function statusIcon(status: string) {
  if (status === "running") return <Loader2 className="h-3.5 w-3.5 animate-spin text-cyan-400" />;
  if (status === "completed") return <CheckCircle2 className="h-3.5 w-3.5 text-emerald-400" />;
  if (status === "rejected") return <XCircle className="h-3.5 w-3.5 text-destructive" />;
  return <Circle className="h-3.5 w-3.5 text-muted-foreground" />;
}

export function AgentTraceTimeline({
  steps,
  activeModel,
  className,
  compact = false,
  showLatency = false,
}: AgentTraceTimelineProps) {
  const { locale } = useTranslations();

  if (steps.length === 0 && !activeModel) return null;

  return (
    <div className={cn("space-y-1.5", className)}>
      {steps.map((step, index) => (
        <motion.div
          key={`${step.agent}-${index}`}
          initial={{ opacity: 0, x: locale === "ar" ? 6 : -6 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: index * 0.04 }}
          className={cn(
            "flex items-center gap-2.5 rounded-lg border border-border/40 bg-background/50 px-3 py-2",
            compact && "py-1.5",
          )}
        >
          {statusIcon(step.status)}
          <div className="min-w-0 flex-1">
            <p className="truncate text-xs font-medium">
              {localizeAgentStep(step.agent, locale)}
            </p>
            {!compact && (
              <p className="truncate text-[10px] text-muted-foreground">{step.model}</p>
            )}
          </div>
          {showLatency && step.latency_ms != null && (
            <span className="text-[10px] text-muted-foreground">{step.latency_ms}ms</span>
          )}
          <span
            className={cn(
              "rounded-full px-2 py-0.5 text-[10px]",
              step.status === "completed" && "bg-emerald-500/10 text-emerald-400",
              step.status === "running" && "bg-cyan-500/10 text-cyan-400",
              step.status === "rejected" && "bg-destructive/10 text-destructive",
              step.status !== "completed" &&
                step.status !== "running" &&
                step.status !== "rejected" &&
                "bg-muted text-muted-foreground",
            )}
          >
            {localizeTraceStatus(step.status, locale)}
          </span>
        </motion.div>
      ))}
      {activeModel && steps.every((s) => s.status !== "running") && (
        <div className="flex items-center gap-2 rounded-lg border border-cyan-500/20 bg-cyan-500/5 px-3 py-2">
          <Loader2 className="h-3.5 w-3.5 animate-spin text-cyan-400" />
          <p className="truncate text-xs text-cyan-300">{activeModel}</p>
        </div>
      )}
    </div>
  );
}
