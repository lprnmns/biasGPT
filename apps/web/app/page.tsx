import Link from "next/link";

export default function HomePage() {
  return (
    <main style={{ padding: "2rem" }}>
      <h1>BiasGPT</h1>
      <p>Progressive trading assistant PWA.</p>
      <p>
        <Link href="/(dashboard)">View dashboard mock</Link>
      </p>
    </main>
  );
}
