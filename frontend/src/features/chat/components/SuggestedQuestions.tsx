"use client";

import { motion } from "framer-motion";

import { useTranslations } from "@/hooks/useTranslations";
import { cn } from "@/lib/utils";

interface SuggestedQuestionsProps {
  questions: string[];
  onSelect: (question: string) => void;
  className?: string;
}

export function SuggestedQuestions({ questions, onSelect, className }: SuggestedQuestionsProps) {
  const { t } = useTranslations();

  if (!questions.length) return null;

  return (
    <div className={cn("mt-3 space-y-2", className)}>
      <p className="text-xs font-medium text-muted-foreground">{t("chat.suggestedFollowUps")}</p>
      <div className="flex flex-wrap gap-2">
        {questions.map((question) => (
          <motion.button
            key={question}
            type="button"
            initial={{ opacity: 0, y: 4 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.2 }}
            className="touch-target rounded-full border border-cyan-500/25 bg-cyan-500/5 px-3 py-1.5 text-start text-xs text-cyan-200 transition-colors hover:border-cyan-400/50 hover:bg-cyan-500/15 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-cyan-400/50"
            onClick={() => onSelect(question)}
          >
            {question}
          </motion.button>
        ))}
      </div>
    </div>
  );
}
