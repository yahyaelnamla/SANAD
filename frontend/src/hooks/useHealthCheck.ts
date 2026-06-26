"use client";

import { useCallback, useEffect, useState } from "react";

import { API_BASE_URL, API_PREFIX } from "@/lib/constants";

export type HealthState = "checking" | "healthy" | "degraded" | "offline";

const POLL_INTERVAL_MS = 30_000;

export function useHealthCheck(options?: { poll?: boolean }) {
  const [health, setHealth] = useState<HealthState>("checking");
  const [version, setVersion] = useState<string | null>(null);

  const check = useCallback(async () => {
    try {
      const [healthRes, versionRes] = await Promise.all([
        fetch(`${API_BASE_URL}${API_PREFIX}/health`, { cache: "no-store" }),
        fetch(`${API_BASE_URL}${API_PREFIX}/version`, { cache: "no-store" }),
      ]);
      setHealth(healthRes.ok ? "healthy" : "degraded");
      if (versionRes.ok) {
        const data = (await versionRes.json()) as { version?: string };
        setVersion(data.version ?? null);
      }
    } catch {
      setHealth("offline");
    }
  }, []);

  useEffect(() => {
    let cancelled = false;

    const run = async () => {
      await check();
    };

    void run();

    if (!options?.poll) {
      return () => {
        cancelled = true;
      };
    }

    const interval = window.setInterval(() => {
      if (!cancelled) void check();
    }, POLL_INTERVAL_MS);

    return () => {
      cancelled = true;
      window.clearInterval(interval);
    };
  }, [check, options?.poll]);

  return { health, version, refresh: check };
}
