import { describe, expect, it } from "vitest";

import {
  alignmentStyle,
  buildFatwaComparisonRows,
  buildOpinionsTimeline,
} from "@/features/scholars/utils/opinionUtils";
import type { MadhhabPosition, Opinion } from "@/types/query";

const opinions: Opinion[] = [
  {
    scholar: "Scholar A",
    position: "Permitted with conditions",
    citations: ["1"],
    date: "2010",
    institution: "Inst A",
  },
  {
    scholar: "Scholar B",
    position: "Not permitted",
    citations: ["2"],
    date: "2020",
    institution: "Inst B",
    strength: "strong",
  },
];

const madhhab: MadhhabPosition[] = [
  {
    school: "Hanafi",
    position: "Conditional",
    alignment: "mixed",
    source: "Ref 1",
  },
];

describe("opinionUtils", () => {
  it("sorts opinions timeline by date", () => {
    const entries = buildOpinionsTimeline(opinions);
    expect(entries[0].scholar).toBe("Scholar A");
    expect(entries[1].scholar).toBe("Scholar B");
  });

  it("builds comparison rows from opinions and madhhab", () => {
    const rows = buildFatwaComparisonRows(opinions, madhhab);
    expect(rows).toHaveLength(3);
    expect(rows[2].kind).toBe("madhhab");
  });

  it("detects alignment styles", () => {
    expect(alignmentStyle("agree")).toBe("agree");
    expect(alignmentStyle("disagree")).toBe("disagree");
    expect(alignmentStyle("mixed")).toBe("mixed");
  });
});
