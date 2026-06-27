import { render, screen } from "@testing-library/react";
import { beforeEach, describe, expect, it } from "vitest";

import { ExplainabilityPanel } from "@/features/chat/components/ExplainabilityPanel";
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
  opinions: [],
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
  agent_trace: [
    {
      agent: "knowledge",
      model: "fanar-1",
      status: "completed",
      latency_ms: 1200,
    },
  ],
};

describe("ExplainabilityPanel", () => {
  beforeEach(() => {
    useSettingsStore.setState({ locale: "en" });
  });

  it("renders sources and execution metrics accordions", () => {
    render(<ExplainabilityPanel result={mockResult} />);
    expect(screen.getByText("View Execution Trace")).toBeInTheDocument();
    expect(screen.getByText("Execution Metrics")).toBeInTheDocument();
  });

  it("renders refusal message when refused", () => {
    render(
      <ExplainabilityPanel
        result={{
          ...mockResult,
          refused: true,
          refusal_reason: "No authenticated sources found.",
          summary: null,
          evidence: [],
          agent_trace: [],
        }}
      />,
    );
    expect(screen.getByText(/No authenticated sources found/)).toBeInTheDocument();
  });
});
