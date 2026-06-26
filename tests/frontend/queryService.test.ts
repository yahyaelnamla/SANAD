import { afterEach, describe, expect, it, vi } from "vitest";

import { submitQuery } from "@/services/queryService";

describe("queryService", () => {
  afterEach(() => {
    vi.restoreAllMocks();
  });

  it("submits query and polls until completed", async () => {
    const mockResult = {
      query_id: "123",
      status: "completed",
      question: "Is riba haram?",
      language: "en",
      summary: "Riba is prohibited.",
      evidence: [],
      principles: [],
      reasoning: "Analysis",
      opinions: [],
      sources: [],
      confidence: 0.9,
      refused: false,
      refusal_reason: null,
      created_at: "2026-01-01T00:00:00Z",
    };

    vi.stubGlobal(
      "fetch",
      vi
        .fn()
        .mockResolvedValueOnce({
          ok: true,
          json: async () => ({ ...mockResult, status: "processing", summary: null }),
        })
        .mockResolvedValueOnce({
          ok: false,
          status: 404,
          statusText: "Not Found",
          json: async () => ({ code: "NOT_FOUND", message: "Stream unavailable" }),
        })
        .mockResolvedValueOnce({
          ok: true,
          json: async () => mockResult,
        }),
    );

    const result = await submitQuery(
      { question: "Is riba haram?", language: "en" },
      "jwt-token-abc",
    );

    expect(result.summary).toBe("Riba is prohibited.");
    expect(fetch).toHaveBeenCalledTimes(3);
  });

  it("returns refused result when polling finds failed status", async () => {
    vi.stubGlobal(
      "fetch",
      vi
        .fn()
        .mockResolvedValueOnce({
          ok: true,
          json: async () => ({
            query_id: "123",
            status: "processing",
            question: "Unknown topic",
            language: "en",
            created_at: "2026-01-01T00:00:00Z",
          }),
        })
        .mockResolvedValueOnce({
          ok: false,
          status: 404,
          statusText: "Not Found",
          json: async () => ({ code: "NOT_FOUND", message: "Stream unavailable" }),
        })
        .mockResolvedValueOnce({
          ok: true,
          json: async () => ({
            query_id: "123",
            status: "failed",
            question: "Unknown topic",
            language: "en",
            summary: null,
            evidence: [],
            principles: [],
            reasoning: null,
            opinions: [],
            sources: [],
            confidence: 0,
            refused: true,
            refusal_reason: "No authenticated sources found.",
            created_at: "2026-01-01T00:00:00Z",
          }),
        }),
    );

    const result = await submitQuery({ question: "Unknown topic" }, "jwt-token-abc");
    expect(result.refused).toBe(true);
    expect(result.refusal_reason).toContain("authenticated");
  });
});
