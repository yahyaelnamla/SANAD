import { afterEach, describe, expect, it, vi } from "vitest";

import * as authService from "@/services/authService";

describe("authService", () => {
  afterEach(() => {
    vi.restoreAllMocks();
  });

  it("registers a user", async () => {
    const profile = {
      id: "user-1",
      email: "user@example.com",
      role: "user",
      locale: "en",
      created_at: "2026-01-01T00:00:00Z",
    };

    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({
        ok: true,
        json: async () => profile,
      }),
    );

    const result = await authService.register({
      email: "user@example.com",
      password: "password123",
      locale: "en",
    });

    expect(result.email).toBe("user@example.com");
    expect(fetch).toHaveBeenCalledWith(
      expect.stringContaining("/api/v1/auth/register"),
      expect.objectContaining({ method: "POST" }),
    );
  });

  it("logs in and returns token", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({
        ok: true,
        json: async () => ({
          access_token: "jwt-token",
          token_type: "bearer",
        }),
      }),
    );

    const result = await authService.login({
      email: "user@example.com",
      password: "password123",
    });

    expect(result.access_token).toBe("jwt-token");
    expect(fetch).toHaveBeenCalledWith(
      expect.stringContaining("/api/v1/auth/login"),
      expect.objectContaining({ method: "POST" }),
    );
  });

  it("fetches profile with Bearer token", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({
        ok: true,
        json: async () => ({
          id: "user-1",
          email: "user@example.com",
          role: "user",
          locale: "en",
          created_at: "2026-01-01T00:00:00Z",
        }),
      }),
    );

    const result = await authService.getProfile("jwt-token");

    expect(result.email).toBe("user@example.com");
    expect(fetch).toHaveBeenCalledWith(
      expect.stringContaining("/api/v1/auth/me"),
      expect.objectContaining({
        headers: expect.objectContaining({ Authorization: "Bearer jwt-token" }),
      }),
    );
  });
});
