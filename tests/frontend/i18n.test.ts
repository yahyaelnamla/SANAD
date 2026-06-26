import { describe, expect, it } from "vitest";

import { isRtl, translate } from "@/lib/i18n";

describe("i18n", () => {
  it("translates Arabic keys", () => {
    expect(translate("ar", "app.name")).toBe("سند");
    expect(translate("ar", "explainability.evidence")).toBe("الأدلة");
  });

  it("translates English keys", () => {
    expect(translate("en", "app.name")).toBe("SANAD");
    expect(translate("en", "explainability.evidence")).toBe("Evidence");
  });

  it("detects RTL for Arabic", () => {
    expect(isRtl("ar")).toBe(true);
    expect(isRtl("en")).toBe(false);
  });

  it("returns key for missing translation", () => {
    expect(translate("en", "missing.key")).toBe("missing.key");
  });

  it("translates admin panel keys", () => {
    expect(translate("en", "admin.title")).toBe("Admin Panel");
    expect(translate("ar", "admin.formAuthenticatedHint")).toContain("الاستدلال");
  });
});
