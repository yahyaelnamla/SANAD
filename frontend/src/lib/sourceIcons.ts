/** Source type icons — clean emoji affordances replacing raw URLs. */

export function sourceTypeEmoji(type?: string): string {
  const normalized = (type ?? "").toLowerCase();
  if (normalized.includes("quran") || normalized === "classical") return "📖";
  if (normalized.includes("hadith")) return "📜";
  if (normalized.includes("fatwa")) return "📑";
  if (normalized.includes("book")) return "📚";
  if (normalized.includes("standard") || normalized.includes("aaoifi")) return "🏛";
  if (normalized.includes("institution") || normalized.includes("academy")) return "🏛";
  if (normalized.includes("http") || normalized.includes("website") || normalized.includes("web"))
    return "🌐";
  return "📖";
}

export function sourceTypeLabel(type?: string, fallback = "Source"): string {
  const emoji = sourceTypeEmoji(type);
  return `${emoji} ${fallback}`;
}
