import { describe, expect, it } from "vitest";

import { isAdminRole } from "@/lib/roles";

describe("isAdminRole", () => {
  it("returns true for admin and reviewer", () => {
    expect(isAdminRole("admin")).toBe(true);
    expect(isAdminRole("reviewer")).toBe(true);
  });

  it("returns false for regular users", () => {
    expect(isAdminRole("user")).toBe(false);
    expect(isAdminRole(undefined)).toBe(false);
  });
});
