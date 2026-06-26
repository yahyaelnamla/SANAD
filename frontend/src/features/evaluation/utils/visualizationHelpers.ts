import type { Evidence, Opinion, QueryResult, SourceReference } from "@/types/query";

export interface TimelineEntry {
  id: string;
  title: string;
  author: string;
  type: string;
  era: string;
  sortKey: number;
  citation?: string;
}

const TYPE_SORT_BASE: Record<string, number> = {
  quran: 100,
  hadith: 200,
  fiqh: 400,
  fatwa: 600,
  standard: 800,
};

const ERA_LABELS: Record<string, { en: string; ar: string }> = {
  quran: { en: "Quranic revelation", ar: "عصر الوحي" },
  hadith: { en: "Prophetic era", ar: "العصر النبوي" },
  fiqh: { en: "Classical fiqh", ar: "الفقه الكلاسيكي" },
  fatwa: { en: "Contemporary scholarship", ar: "الفتاوى المعاصرة" },
  standard: { en: "Modern standards", ar: "المعايير الحديثة" },
};

function normalizeType(raw: string): string {
  const lower = raw.toLowerCase();
  if (lower.includes("quran") || lower.includes("qur")) return "quran";
  if (lower.includes("hadith") || lower.includes("sunna")) return "hadith";
  if (lower.includes("fatwa")) return "fatwa";
  if (lower.includes("standard") || lower.includes("aaoifi")) return "standard";
  if (lower.includes("fiqh") || lower.includes("book")) return "fiqh";
  return "fiqh";
}

function parseYear(value: string | null | undefined): number | null {
  if (!value) return null;
  const match = value.match(/\b(1[0-9]{3}|20[0-9]{2})\b/);
  return match ? Number.parseInt(match[1], 10) : null;
}

function sortKeyForEntry(type: string, year: number | null): number {
  const base = TYPE_SORT_BASE[type] ?? 500;
  if (year != null) return year;
  return base;
}

function eraLabel(type: string, locale: "ar" | "en"): string {
  const labels = ERA_LABELS[type] ?? ERA_LABELS.fiqh;
  return locale === "ar" ? labels.ar : labels.en;
}

export function buildSourceTimeline(
  result: QueryResult,
  locale: "ar" | "en",
): TimelineEntry[] {
  const seen = new Set<string>();
  const entries: TimelineEntry[] = [];

  const push = (
    id: string,
    title: string,
    author: string,
    type: string,
    citation: string | undefined,
    year: number | null,
  ) => {
    const key = `${id}-${title}`;
    if (seen.has(key)) return;
    seen.add(key);
    entries.push({
      id,
      title,
      author: author || "—",
      type,
      era: eraLabel(type, locale),
      sortKey: sortKeyForEntry(type, year),
      citation,
    });
  };

  for (const ev of result.evidence as Evidence[]) {
    const type = normalizeType(ev.source_type || "");
    const year = parseYear(String(ev.metadata?.date ?? ev.metadata?.year ?? ""));
    push(ev.source_id || ev.chunk_id, ev.source_title, ev.source_author, type, ev.citation, year);
  }

  for (const src of result.sources as SourceReference[]) {
    const type = normalizeType(src.type || "");
    push(src.source_id, src.title, src.author, type, src.citation, null);
  }

  for (const op of result.opinions as Opinion[]) {
    const year = parseYear(op.date);
    push(
      `opinion-${op.scholar}`,
      op.scholar,
      op.institution || op.book || "—",
      "fatwa",
      op.fatwa || op.position.slice(0, 80),
      year,
    );
  }

  return entries.sort((a, b) => a.sortKey - b.sortKey);
}

export interface HeatmapCell {
  type: string;
  bucket: number;
  count: number;
  maxScore: number;
}

const HEATMAP_TYPES = ["quran", "hadith", "fiqh", "fatwa", "standard"] as const;

export function buildEvidenceHeatmap(evidence: Evidence[]): HeatmapCell[] {
  const grid = new Map<string, { count: number; maxScore: number }>();

  for (const item of evidence) {
    const type = normalizeType(item.source_type || "");
    if (!HEATMAP_TYPES.includes(type as (typeof HEATMAP_TYPES)[number])) continue;
    const score = Math.min(1, Math.max(0, item.score ?? 0));
    const bucket = Math.min(4, Math.floor(score * 5));
    const key = `${type}-${bucket}`;
    const prev = grid.get(key) ?? { count: 0, maxScore: 0 };
    grid.set(key, {
      count: prev.count + 1,
      maxScore: Math.max(prev.maxScore, score),
    });
  }

  const cells: HeatmapCell[] = [];
  for (const type of HEATMAP_TYPES) {
    for (let bucket = 0; bucket < 5; bucket += 1) {
      const data = grid.get(`${type}-${bucket}`);
      cells.push({
        type,
        bucket,
        count: data?.count ?? 0,
        maxScore: data?.maxScore ?? 0,
      });
    }
  }
  return cells;
}

export interface RadarAxis {
  key: string;
  label: string;
  value: number;
}

export function buildConfidenceRadar(
  breakdown: QueryResult["confidence_breakdown"],
  labels: Record<string, string>,
): RadarAxis[] {
  const keys = [
    "retrieval",
    "grounding",
    "model",
    "guard",
    "verification",
    "scholarly_coverage",
  ] as const;

  return keys.map((key) => ({
    key,
    label: labels[key] ?? key,
    value: Math.min(1, Math.max(0, breakdown?.[key] ?? 0)),
  }));
}

export function heatmapIntensity(count: number, maxScore: number): number {
  if (count === 0) return 0;
  return Math.min(1, 0.35 + count * 0.15 + maxScore * 0.35);
}
