import { describe, expect, it } from "vitest";

import { buildMarkdownExport } from "@/lib/exportResponse";
import type { QueryResult } from "@/types/query";

const mockResult: QueryResult = {
  query_id: "q-export",
  status: "completed",
  question: "Is Tesla halal?",
  language: "en",
  summary: "Requires screening.",
  evidence: [],
  principles: [],
  reasoning: null,
  opinions: [],
  sources: [],
  confidence: 0.8,
  refused: false,
  refusal_reason: null,
  madhhab_matrix: [{ school: "Hanafi", position: "Screen first", alignment: "mixed" }],
  financial_context: {
    entities: ["Tesla"],
    screening_notes: ["Check debt ratio"],
    market_quotes: [{ symbol: "TSLA", price: 250, currency: "USD" }],
  },
  created_at: "2026-01-01T00:00:00Z",
};

describe("exportResponse", () => {
  it("builds markdown with structured sections", () => {
    const markdown = buildMarkdownExport(mockResult);
    expect(markdown).toContain("# SANAD — Is Tesla halal?");
    expect(markdown).toContain("## Summary");
    expect(markdown).toContain("## Madhhab Matrix");
    expect(markdown).toContain("Hanafi");
    expect(markdown).toContain("## Financial Screening");
    expect(markdown).toContain("Check debt ratio");
  });
});
