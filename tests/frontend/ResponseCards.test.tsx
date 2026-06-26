import { render, screen } from "@testing-library/react";
import { beforeEach, describe, expect, it } from "vitest";

import { ResponseCards } from "@/features/chat/components/ResponseCards";
import { useSettingsStore } from "@/store/settingsStore";
import type { QueryResult } from "@/types/query";

const mockResult: QueryResult = {
  query_id: "q-1",
  status: "completed",
  question: "Is riba prohibited?",
  language: "en",
  summary: "Riba is categorically prohibited.",
  evidence: [
    {
      text: "Riba is prohibited in Islamic law.",
      source_id: "s1",
      chunk_id: "c1",
      citation: "Scholars. Majallah.",
      source_title: "Majallah",
      source_author: "Scholars",
      source_type: "classical",
      language: "en",
      score: 0.9,
    },
  ],
  principles: [
    {
      name: "Prohibition of Riba",
      description: "Guaranteed increase on loans is prohibited.",
      citation: "Scholars. Majallah.",
    },
  ],
  reasoning: "Based on authenticated evidence, riba is haram.",
  opinions: [
    {
      scholar: "Classical Consensus",
      position: "Riba is prohibited.",
      citations: ["Scholars. Majallah."],
    },
  ],
  sources: [
    {
      source_id: "s1",
      title: "Majallah",
      author: "Scholars",
      type: "classical",
      citation: "Scholars. Majallah.",
    },
  ],
  confidence: 0.92,
  refused: false,
  refusal_reason: null,
  created_at: "2026-01-01T00:00:00Z",
};

describe("ResponseCards", () => {
  beforeEach(() => {
    useSettingsStore.setState({ locale: "en" });
  });

  it("renders structured response cards", () => {
    render(<ResponseCards result={mockResult} />);
    expect(screen.getByText("Riba is categorically prohibited.")).toBeInTheDocument();
    expect(screen.getAllByText("Riba is prohibited in Islamic law.").length).toBeGreaterThan(0);
    expect(screen.getByText("Prohibition of Riba")).toBeInTheDocument();
    expect(screen.getByText("Classical Consensus")).toBeInTheDocument();
  });
});
