import type { Locale } from "@/types/common";

interface ScholarNameFields {
  name: string;
  name_ar?: string | null;
  name_en?: string | null;
}

/** Bilingual scholar display: primary name for locale + optional secondary line. */
export function scholarDisplayName(
  scholar: ScholarNameFields,
  locale: Locale,
): { primary: string; secondary: string | null } {
  const en = scholar.name_en ?? scholar.name;
  const ar = scholar.name_ar ?? null;

  if (locale === "ar") {
    return {
      primary: ar ?? en,
      secondary: null,
    };
  }
  return {
    primary: en,
    secondary: ar,
  };
}
