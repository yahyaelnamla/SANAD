import { describe, expect, it } from "vitest";

import {
  buildConfidenceRadar,
  buildEvidenceHeatmap,
  buildSourceTimeline,
  heatmapIntensity,
} from "@/features/evaluation/utils/visualizationHelpers";
import type { QueryResult } from "@/types/query";

const baseResult: QueryResult = {
  query_id: "1",
  status: "completed",
  question: "Test",
  language: "en",
  summary: "Summary",
  evidence: [
    {
      text: "Trade is permitted",
      source_id: "s1",
      chunk_id: "c1",
      citation: "2:275",
      source_title: "Al-Baqarah",
      source_author: "Quran",
      source_type: "quran",
      language: "en",
      score: 0.92,
    },
    {
      text: "Hadith text",
      source_id: "s2",
      chunk_id: "c2",
      citation: "Bukhari",
      source_title: "Sahih Bukhari",
      source_author: "Al-Bukhari",
      source_type: "hadith",
      language: "en",
      score: 0.71,
    },
  ],
  principles: [],
  reasoning: null,
  opinions: [
    {
      scholar: "Ibn Taymiyyah",
      position: "Riba is prohibited",
      citations: ["1"],
      institution: "Dar al-Ifta",
      date: "1328",
    },
  ],
  sources: [],
  confidence: 0.8,
  confidence_breakdown: {
    retrieval: 0.9,
    grounding: 0.85,
    model: 0.7,
    guard: 1,
    verification: 0.95,
    scholarly_coverage: 0.6,
  },
  refused: false,
  refusal_reason: null,
  created_at: new Date().toISOString(),
};

describe("visualizationHelpers", () => {
  it("builds source timeline sorted by era", () => {
    const entries = buildSourceTimeline(baseResult, "en");
    expect(entries.length).toBeGreaterThanOrEqual(3);
    expect(entries[0].type).toBe("quran");
  });

  it("builds evidence heatmap cells", () => {
    const cells = buildEvidenceHeatmap(baseResult.evidence);
    const quranHigh = cells.find((c) => c.type === "quran" && c.bucket === 4);
    expect(quranHigh?.count).toBe(1);
  });

  it("builds confidence radar axes", () => {
    const axes = buildConfidenceRadar(baseResult.confidence_breakdown, {
      retrieval: "Retrieval",
      grounding: "Grounding",
      model: "Model",
      guard: "Guard",
      verification: "Verification",
      scholarly_coverage: "Scholarly",
    });
    expect(axes).toHaveLength(6);
    expect(axes[0].value).toBe(0.9);
  });

  it("computes heatmap intensity", () => {
    expect(heatmapIntensity(0, 0)).toBe(0);
    expect(heatmapIntensity(2, 0.8)).toBeGreaterThan(0.5);
  });
});
