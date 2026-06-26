/** Empty string = same-origin (Next.js rewrites proxy /api → backend). */
const configuredApiUrl = process.env.NEXT_PUBLIC_API_URL?.trim();
export const API_BASE_URL =
  configuredApiUrl && configuredApiUrl.length > 0
    ? configuredApiUrl.replace(/\/$/, "")
    : "";

export const API_PREFIX = "/api/v1";

export const SETTINGS_STORAGE_KEY = "sanad-settings";

export const CONVERSATION_STORAGE_KEY = "sanad-conversations";

export const BOOKMARK_STORAGE_KEY = "sanad-bookmarks";

export const FEEDBACK_STORAGE_KEY = "sanad-feedback";

export const OFFLINE_QUEUE_STORAGE_KEY = "sanad-offline-queue";

export const AUTH_TOKEN_STORAGE_KEY = "sanad-access-token";

export const DEFAULT_LOCALE = "ar" as const;

export const SUPPORTED_LOCALES = ["ar", "en"] as const;
