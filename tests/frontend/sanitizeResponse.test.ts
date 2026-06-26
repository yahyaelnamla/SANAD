import { describe, expect, it } from "vitest";

import {
  escapeHtml,
  sanitizeReasoningForDisplay,
  sanitizeUserFacingText,
} from "@/lib/sanitizeResponse";

describe("sanitizeReasoningForDisplay", () => {
  it("strips thinking tags", () => {
    const input = "<thinking>hidden</thinking>Public analysis text.";
    expect(sanitizeReasoningForDisplay(input)).toBe("Public analysis text.");
  });

  it("strips model tags", () => {
    const input = "<assistant>Public analysis text.</assistant>";
    expect(sanitizeUserFacingText(input)).toBe("Public analysis text.");
  });

  it("returns empty for nullish values", () => {
    expect(sanitizeReasoningForDisplay(null)).toBe("");
    expect(sanitizeReasoningForDisplay(undefined)).toBe("");
  });
});

describe("escapeHtml", () => {
  it("escapes script tags", () => {
    expect(escapeHtml('<script>alert("x")</script>')).not.toContain("<script>");
  });
});

describe("sanitizeUserFacingText html", () => {
  it("strips HTML tags", () => {
    expect(sanitizeUserFacingText('<b onclick="x">bold</b> text')).toBe("bold text");
  });
});
