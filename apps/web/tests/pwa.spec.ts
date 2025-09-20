import { describe, expect, it } from "vitest";
import fs from "node:fs";
import path from "node:path";

const root = path.resolve(__dirname, "..", "public");

describe("PWA manifest", () => {
  it("contains required fields", () => {
    const manifestPath = path.join(root, "manifest.json");
    const raw = fs.readFileSync(manifestPath, "utf8");
    const manifest = JSON.parse(raw);
    expect(manifest.name).toBe("BiasGPT");
    expect(manifest.display).toBe("standalone");
  });
});
