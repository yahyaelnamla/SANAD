"use client";

import { motion } from "framer-motion";
import { AlertTriangle, BarChart3 } from "lucide-react";

import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion";
import { ExecutionMetricsPanel } from "@/features/chat/components/ExecutionMetricsPanel";
import { useTranslations } from "@/hooks/useTranslations";
import { cn } from "@/lib/utils";
import type { QueryResult } from "@/types/query";

interface ExplainabilityPanelProps {
  result: QueryResult;
  className?: string;
}

export function ExplainabilityPanel({
  result,
  className,
}: ExplainabilityPanelProps) {
  const { t } = useTranslations();

  if (result.refused) {
    return (
      <motion.div
        initial={{ opacity: 0, y: 8 }}
        animate={{ opacity: 1, y: 0 }}
        className={cn("rounded-xl border border-destructive/30 bg-destructive/5 p-4", className)}
      >
        <div className="flex items-start gap-3">
          <AlertTriangle className="mt-0.5 h-5 w-5 text-destructive" />
          <div>
            <p className="font-semibold text-destructive">{t("explainability.refusalTitle")}</p>
            <p className="mt-1 text-sm text-muted-foreground">
              {result.refusal_reason ?? t("explainability.noEvidence")}
            </p>
          </div>
        </div>
      </motion.div>
    );
  }

  const hasMetrics = Boolean(result.agent_trace && result.agent_trace.length > 0);

  if (!hasMetrics) return null;

  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.25 }}
      className={cn("pt-2", className)}
    >
      <Accordion type="multiple" defaultValue={["metrics"]} className="space-y-2">
        <AccordionItem
          value="metrics"
          className="rounded-xl border border-nexus-cyan/20 bg-card/30 px-1"
        >
          <AccordionTrigger className="gap-2 px-3 py-2.5 text-sm font-medium hover:no-underline">
            <BarChart3 className="h-4 w-4 shrink-0 text-nexus-cyan" />
            {t("explainability.viewExecutionTrace")}
          </AccordionTrigger>
          <AccordionContent className="px-3 pb-3">
            <ExecutionMetricsPanel
              steps={result.agent_trace!}
              metrics={result.execution_metrics}
            />
          </AccordionContent>
        </AccordionItem>
      </Accordion>
    </motion.div>
  );
}
