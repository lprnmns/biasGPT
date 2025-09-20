import { describe, expect, it } from "vitest";
import { renderToString } from "react-dom/server";

import ChatPage from "../app/chat/page";

describe("ChatPage", () => {
  it("renders assistant messages", () => {
    const html = renderToString(<ChatPage />);
    expect(html).toContain("Chat Assistant");
    expect(html).toContain("Whale deposit detected");
  });
});
