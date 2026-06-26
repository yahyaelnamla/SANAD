import { afterEach, describe, expect, it, vi } from "vitest";

import { ApiClientError, apiRequest } from "@/services/apiClient";

describe("apiClient", () => {
  afterEach(() => {
    vi.restoreAllMocks();
  });

  it("returns parsed JSON on success", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({
        ok: true,
        status: 200,
        json: async () => ({ status: "ok" }),
      }),
    );

    const result = await apiRequest<{ status: string }>("/health");
    expect(result.status).toBe("ok");
  });

  it("handles 204 No Content responses", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({
        ok: true,
        status: 204,
      }),
    );

    const result = await apiRequest<void>("/sources/1", { method: "DELETE" });
    expect(result).toBeUndefined();
  });

  it("throws ApiClientError with server error body", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({
        ok: false,
        status: 403,
        statusText: "Forbidden",
        json: async () => ({ code: "FORBIDDEN", message: "Insufficient permissions" }),
      }),
    );

    await expect(apiRequest("/sources")).rejects.toMatchObject({
      name: "ApiClientError",
      status: 403,
      code: "FORBIDDEN",
    } satisfies Partial<ApiClientError>);
  });
});
