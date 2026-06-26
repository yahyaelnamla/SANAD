"use client";

import { AgentTraceTimeline } from "@/features/chat/components/AgentTraceTimeline";
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion";
import { useTranslations } from "@/hooks/useTranslations";
import type { AgentTraceStep } from "@/types/query";

interface ReasoningProcessAccordionProps {
  steps: AgentTraceStep[];
  defaultOpen?: boolean;
}

export function ReasoningProcessAccordion({
  steps,
  defaultOpen = false,
}: ReasoningProcessAccordionProps) {
  const { t } = useTranslations();

  if (!steps.length) return null;

  return (
    <Accordion
      type="single"
      collapsible
      defaultValue={defaultOpen ? "reasoning-process" : undefined}
      className="rounded-xl border border-border/50 bg-card/40"
    >
      <AccordionItem value="reasoning-process" className="border-none">
        <AccordionTrigger className="px-4 py-3 text-sm font-medium hover:no-underline">
          {t("explainability.reasoningProcess")}
        </AccordionTrigger>
        <AccordionContent className="px-2 pb-3">
          <AgentTraceTimeline steps={steps} compact />
        </AccordionContent>
      </AccordionItem>
    </Accordion>
  );
}
