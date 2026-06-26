/** Detect whether answer text is primarily Arabic or English. */

export function detectContentLanguage(text: string, fallback = "ar"): string {
  if (!text.trim()) return fallback;
  const arabic = (text.match(/[\u0600-\u06FF]/g) ?? []).length;
  const latin = (text.match(/[A-Za-z]/g) ?? []).length;
  if (arabic > latin) return "ar";
  if (latin > 0) return "en";
  return fallback;
}
