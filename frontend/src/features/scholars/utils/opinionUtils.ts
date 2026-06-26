import type { MadhhabPosition, Opinion } from "@/types/query";

export interface OpinionTimelineEntry {
  id: string;
  scholar: string;
  institution: string | null;
  position: string;
  date: string | null;
  sortKey: number;
  citations: string[];
  strength: string | null;
}

function parseYear(value: string | null | undefined): number | null {
  if (!value) return null;
  const match = value.match(/\b(1[0-9]{3}|20[0-9]{2})\b/);
  return match ? Number.parseInt(match[1], 10) : null;
}

export function buildOpinionsTimeline(opinions: Opinion[]): OpinionTimelineEntry[] {
  return opinions
    .map((opinion, index) => {
      const year = parseYear(opinion.date);
      return {
        id: `opinion-${index}-${opinion.scholar}`,
        scholar: opinion.scholar,
        institution: opinion.institution ?? null,
        position: opinion.position,
        date: opinion.date ?? null,
        sortKey: year ?? 2000 + index,
        citations: opinion.citations,
        strength: opinion.strength ?? null,
      };
    })
    .sort((a, b) => a.sortKey - b.sortKey);
}

export interface ComparisonRow {
  id: string;
  label: string;
  kind: "opinion" | "madhhab";
  position: string;
  alignment: string | null;
  institution: string | null;
  source: string | null;
  strength: string | null;
}

export function buildFatwaComparisonRows(
  opinions: Opinion[],
  madhhabMatrix: MadhhabPosition[],
): ComparisonRow[] {
  const rows: ComparisonRow[] = opinions.map((opinion, index) => ({
    id: `op-${index}`,
    label: opinion.scholar,
    kind: "opinion",
    position: opinion.position,
    alignment: opinion.strength ?? null,
    institution: opinion.institution ?? null,
    source: opinion.citations.join(" · ") || null,
    strength: opinion.strength ?? null,
  }));

  for (const entry of madhhabMatrix) {
    rows.push({
      id: `madhhab-${entry.school}`,
      label: entry.school,
      kind: "madhhab",
      position: entry.position,
      alignment: entry.alignment,
      institution: null,
      source: entry.source ?? null,
      strength: null,
    });
  }

  return rows;
}

export function alignmentStyle(alignment: string | null): string {
  const value = (alignment ?? "").toLowerCase();
  if (value.includes("agree") && !value.includes("dis")) return "agree";
  if (value.includes("disagree")) return "disagree";
  if (value.includes("mixed")) return "mixed";
  return "neutral";
}
