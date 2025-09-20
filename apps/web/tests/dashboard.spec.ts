import { describe, expect, it } from "vitest";
import { renderToString } from "react-dom/server";

import DashboardPage from "../app/(dashboard)/page";

describe("DashboardPage", () => {
  it("renders position and bias sections", () => {
    const html = renderToString(<DashboardPage />);
    expect(html).toContain("Trading Dashboard");
    expect(html).toContain("Open Positions");
    expect(html).toContain("Bias Snapshot");
  });
});
