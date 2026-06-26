"use client";

import { memo } from "react";

import { sanitizeUserFacingText } from "@/lib/sanitizeResponse";
import { cn } from "@/lib/utils";

interface SafeTextProps {
  text: string | null | undefined;
  className?: string;
  as?: "p" | "span" | "div";
}

export const SafeText = memo(function SafeText({ text, className, as: Tag = "span" }: SafeTextProps) {
  const safe = sanitizeUserFacingText(text);
  if (!safe) return null;
  return <Tag className={cn("break-words [overflow-wrap:anywhere]", className)}>{safe}</Tag>;
});
