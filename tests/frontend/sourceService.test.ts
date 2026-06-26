import { afterEach, describe, expect, it, vi } from "vitest";

import * as sourceService from "@/services/sourceService";

describe("sourceService", () => {
  afterEach(() => {
    vi.restoreAllMocks();
  });

  it("lists sources with Bearer token", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({
        ok: true,
        json: async () => ({
          items: [
            {
              id: "source-1",
              title: "AAOIFI Standard",
              author: "AAOIFI",
              source_type: "standard",
              language: "en",
              url: null,
              is_authenticated: true,
              created_at: "2026-01-01T00:00:00Z",
            },
          ],
          total: 1,
        }),
      }),
    );

    const result = await sourceService.listSources("jwt-token");

    expect(result.total).toBe(1);
    expect(fetch).toHaveBeenCalledWith(
      expect.stringContaining("/api/v1/sources"),
      expect.objectContaining({
        headers: expect.objectContaining({ Authorization: "Bearer jwt-token" }),
      }),
    );
  });

  it("creates a source", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({
        ok: true,
        json: async () => ({
          id: "source-2",
          title: "New Source",
          author: "Scholar",
          source_type: "classical",
          language: "ar",
          url: null,
          is_authenticated: false,
          created_at: "2026-01-01T00:00:00Z",
        }),
      }),
    );

    const result = await sourceService.createSource("jwt-token", {
      title: "New Source",
      author: "Scholar",
      source_type: "classical",
      language: "ar",
    });

    expect(result.is_authenticated).toBe(false);
    expect(fetch).toHaveBeenCalledWith(
      expect.stringContaining("/api/v1/sources"),
      expect.objectContaining({ method: "POST" }),
    );
  });

  it("fetches admin stats", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({
        ok: true,
        json: async () => ({
          total_sources: 3,
          authenticated_sources: 2,
          pending_sources: 1,
        }),
      }),
    );

    const result = await sourceService.getAdminStats("jwt-token");

    expect(result.pending_sources).toBe(1);
    expect(fetch).toHaveBeenCalledWith(
      expect.stringContaining("/api/v1/admin/stats"),
      expect.objectContaining({
        headers: expect.objectContaining({ Authorization: "Bearer jwt-token" }),
      }),
    );
  });
});
