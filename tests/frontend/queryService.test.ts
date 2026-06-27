import { afterEach, describe, expect, it, vi } from "vitest";

import { submitQuery } from "@/services/queryService";

const makeStreamResponse = (data: object) => {
  const payload = `event: complete\ndata: ${JSON.stringify(data)}\n\n`;
  const encoded = new TextEncoder().encode(payload);
  let consumed = false;
  return {
    ok: true,
    status: 200,
    body: {
      getReader: () => ({
        read: async () => {
          if (!consumed) { consumed = true; return { done: false, value: encoded }; }
          return { done: true, value: undefined };
        },
        releaseLock: () => {},
      }),
    },
  };
};

describe("queryService", () => {
  afterEach(() => {
    vi.restoreAllMocks();
  });

  it("submits query and polls until completed", async () => {
    const mockResult = {
      query_id: "123", status: "completed", question: "Is riba haram?",
      language: "en", summary: "Riba is prohibited.", evidence: [],
      principles: [], reasoning: "Analysis", opinions: [], sources: [],
      confidence: 0.9, refused: false, refusal_reason: null,
      created_at: "2026-01-01T00:00:00Z",
    };

    vi.stubGlobal("fetch", vi.fn()
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({ ...mockResult, status: "processing", summary: null }),
      })
      .mockResolvedValueOnce(makeStreamResponse(mockResult)),
    );

    const result = await submitQuery(
      { question: "Is riba haram?", language: "en" },
      "jwt-token-abc",
    );

    expect(result.summary).toBe("Riba is prohibited.");
  });

  it("returns refused result when polling finds failed status", async () => {
    const refusedResult = {
      query_id: "123", status: "failed", question: "Unknown topic",
      language: "en", summary: null, evidence: [], principles: [],
      reasoning: null, opinions: [], sources: [], confidence: 0,
      refused: true, refusal_reason: "No authenticated sources found.",
      created_at: "2026-01-01T00:00:00Z",
    };

    vi.stubGlobal("fetch", vi.fn()
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({ ...refusedResult, status: "processing" }),
      })
      .mockResolvedValueOnce(makeStreamResponse(refusedResult)),
    );

    const result = await submitQuery({ question: "Unknown topic" }, "jwt-token-abc");
    expect(result.refused).toBe(true);
    expect(result.refusal_reason).toContain("authenticated");
  });
});