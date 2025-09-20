import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "BiasGPT",
  description: "Whale-driven AI trader dashboard",
  manifest: "/manifest.json"
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
