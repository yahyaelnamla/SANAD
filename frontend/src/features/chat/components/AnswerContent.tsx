"use client";

import { memo } from "react";
import { BookOpen, ScrollText } from "lucide-react";

import { SafeText } from "@/components/SafeText";
import {
  parseAnswerParagraphs,
  splitAnswerSections,
  stripInlineCitations,
} from "@/lib/formatAnswer";
import { sanitizeUserFacingText } from "@/lib/sanitizeResponse";
import { cn } from "@/lib/utils";

interface AnswerContentProps {
  text: string;
  isStreaming?: boolean;
  arabic?: boolean;
  className?: string;
}

const PARAGRAPH_STYLES: Record<string, string> = {
  text: "whitespace-pre-wrap text-[15px] leading-[1.8] text-foreground/95",
  "section-label": "text-sm font-semibold text-cyan-700 dark:text-cyan-300/90 pt-2",
  quran:
    "my-2 rounded-xl border border-emerald-600/30 bg-emerald-500/10 px-4 py-3.5 text-[15px] leading-[2] text-emerald-950 dark:text-emerald-50/95",
  hadith:
    "my-2 rounded-xl border border-amber-600/30 bg-amber-500/10 px-4 py-3.5 text-[15px] leading-[2] text-amber-950 dark:text-amber-50/95",
};

function ParagraphBlock({
  kind,
  text,
  arabic,
}: {
  kind: string;
  text: string;
  arabic?: boolean;
}) {
  const Icon = kind === "quran" ? BookOpen : kind === "hadith" ? ScrollText : null;

  return (
    <div className={cn(PARAGRAPH_STYLES[kind] ?? PARAGRAPH_STYLES.text, arabic && "font-arabic")}>
      {Icon && (
        <div className="mb-2 flex items-center gap-1.5 text-xs font-medium opacity-70">
          <Icon className="h-3.5 w-3.5" />
        </div>
      )}
      <SafeText text={text} as="span" />
    </div>
  );
}

export const AnswerContent = memo(function AnswerContent({
  text,
  isStreaming = false,
  arabic,
  className,
}: AnswerContentProps) {
  const cleaned = sanitizeUserFacingText(text);
  if (!cleaned && !isStreaming) return null;

  const { body, summary } = splitAnswerSections(cleaned);
  const paragraphs = parseAnswerParagraphs(cleaned);
  const displaySummary = summary ? stripInlineCitations(summary) : null;

  if (isStreaming) {
    return (
      <div
        dir={arabic ? "rtl" : "ltr"}
        className={cn("space-y-4", arabic && "font-arabic text-right", className)}
      >
        <p
          className={cn(
            "whitespace-pre-wrap break-words text-[15px] leading-[1.75] [overflow-wrap:anywhere]",
            arabic && "font-arabic",
          )}
        >
          <SafeText text={stripInlineCitations(cleaned)} as="span" />
          <span
            className="ms-0.5 inline-block h-4 w-0.5 animate-pulse bg-cyan-400 align-middle"
            aria-hidden
          />
        </p>
      </div>
    );
  }

  return (
    <div
      dir={arabic ? "rtl" : "ltr"}
      className={cn("space-y-4", arabic && "font-arabic text-right", className)}
    >
      {paragraphs.length > 0 ? (
        paragraphs.map((para, index) => (
          <ParagraphBlock key={index} kind={para.kind} text={para.text} arabic={arabic} />
        ))
      ) : (
        body && (
          <p className={cn("text-[15px] leading-[1.75]", arabic && "font-arabic")}>
            <SafeText text={stripInlineCitations(body)} as="span" />
          </p>
        )
      )}

      {displaySummary && (
        <div className="mt-2 border-t border-border/40 pt-4">
          <p className="mb-2 text-xs font-semibold uppercase tracking-wide text-muted-foreground">
            {arabic ? "خلاصة" : "In short"}
          </p>
          <p
            className={cn(
              "rounded-lg bg-muted/20 px-3 py-2.5 text-sm leading-relaxed text-foreground/90",
              arabic && "font-arabic",
            )}
          >
            <SafeText text={displaySummary} as="span" />
          </p>
        </div>
      )}
    </div>
  );
});
