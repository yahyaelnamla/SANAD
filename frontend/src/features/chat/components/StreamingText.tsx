"use client";

import { memo } from "react";

import { SafeText } from "@/components/SafeText";
import { sanitizeUserFacingText } from "@/lib/sanitizeResponse";
import { cn } from "@/lib/utils";

interface StreamingTextProps {
  text: string;
  isStreaming?: boolean;
  className?: string;
  arabic?: boolean;
}

export const StreamingText = memo(function StreamingText({
  text,
  isStreaming = false,
  className,
  arabic,
}: StreamingTextProps) {
  const cleaned = sanitizeUserFacingText(text);
  if (!cleaned && !isStreaming) return null;

  return (
    <p className={cn("break-words leading-relaxed [overflow-wrap:anywhere]", arabic && "font-arabic", className)}>
      <SafeText text={cleaned} as="span" />
      {isStreaming && (
        <span
          className="ms-0.5 inline-block h-4 w-0.5 animate-pulse bg-cyan-400 align-middle"
          aria-hidden
        />
      )}
    </p>
  );
});
