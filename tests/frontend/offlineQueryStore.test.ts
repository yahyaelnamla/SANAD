import { describe, expect, it } from "vitest";

import { useOfflineQueryStore } from "@/store/offlineQueryStore";

describe("offlineQueryStore", () => {
  it("enqueues and dequeues questions", () => {
    useOfflineQueryStore.setState({ queue: [] });
    const item = useOfflineQueryStore.getState().enqueue({
      question: "Is riba haram?",
      language: "en",
    });
    expect(useOfflineQueryStore.getState().queue).toHaveLength(1);
    expect(item.question).toBe("Is riba haram?");
    useOfflineQueryStore.getState().dequeue(item.id);
    expect(useOfflineQueryStore.getState().queue).toHaveLength(0);
  });
});
