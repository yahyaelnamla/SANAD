"use client";

import { useEffect, useState } from "react";

const DEFAULT_SECTIONS = [
  "summary",
  "evidence",
  "analysis",
  "opinions",
  "madhhab",
  "financial",
  "sources",
] as const;

export type RevealSection = (typeof DEFAULT_SECTIONS)[number];

export function useProgressiveReveal(enabled: boolean, intervalMs = 280) {
  const [visibleCount, setVisibleCount] = useState(enabled ? 0 : DEFAULT_SECTIONS.length);

  useEffect(() => {
    if (!enabled) {
      setVisibleCount(DEFAULT_SECTIONS.length);
      return;
    }

    setVisibleCount(0);
    let index = 0;
    const timer = window.setInterval(() => {
      index += 1;
      setVisibleCount(index);
      if (index >= DEFAULT_SECTIONS.length) {
        window.clearInterval(timer);
      }
    }, intervalMs);

    return () => window.clearInterval(timer);
  }, [enabled, intervalMs]);

  const isVisible = (section: RevealSection) => {
    const sectionIndex = DEFAULT_SECTIONS.indexOf(section);
    return sectionIndex <= visibleCount - 1;
  };

  const isComplete = visibleCount >= DEFAULT_SECTIONS.length;

  return { isVisible, isComplete, visibleCount };
}
