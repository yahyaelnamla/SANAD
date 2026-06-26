import { describe, expect, it } from "vitest";

import { useConversationStore } from "@/store/conversationStore";

describe("conversationStore", () => {
  it("pins and unpins query ids", () => {
    useConversationStore.setState({ pinnedQueryIds: [] });
    useConversationStore.getState().togglePin("q-1");
    expect(useConversationStore.getState().isPinned("q-1")).toBe(true);
    useConversationStore.getState().togglePin("q-1");
    expect(useConversationStore.getState().isPinned("q-1")).toBe(false);
  });
});
