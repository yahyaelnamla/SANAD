import { describe, expect, it } from "vitest";

import {
  parseAnswerParagraphs,
  splitAnswerSections,
  stripInlineCitations,
} from "@/lib/formatAnswer";

describe("formatAnswer", () => {
  it("splits body and summary at separator", () => {
    const text = "Full analysis here.\n\n━━━\nخلاصة\nBrief conclusion.";
    const { body, summary } = splitAnswerSections(text);
    expect(body).toBe("Full analysis here.");
    expect(summary).toBe("Brief conclusion.");
  });

  it("extracts quran verse blocks", () => {
    const paragraphs = parseAnswerParagraphs("\uFD3F\u064A\u0627 \u0623\u064A\u0651\u0647\u0627 \u0627\u0644\u0651\u0630\u064A\u0646 \u0622\u0645\u0646\u0648\u0627\uFD3E");
    expect(paragraphs.some((p) => p.kind === "quran")).toBe(true);
  });

  it("strips inline URLs, citations, and nbs artifacts", () => {
    const cleaned = stripInlineCitations(
      "Ruling is clear [1]. See https://example.com (Bukhari 1234) nbs text",
    );
    expect(cleaned).not.toContain("https://");
    expect(cleaned).not.toContain("Bukhari");
    expect(cleaned).not.toContain("[1]");
    expect(cleaned).not.toContain("nbs");
  });

  it("preserves paragraph breaks when stripping citations", () => {
    const cleaned = stripInlineCitations("First paragraph [1].\n\nSecond paragraph [2].");
    expect(cleaned).toContain("\n\n");
  });
});
