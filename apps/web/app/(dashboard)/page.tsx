import Link from "next/link";
import { sampleBias, samplePositions, sampleWhaleEvents } from "@/lib/sampleData";

export default function DashboardPage() {
  return (
    <main style={{ padding: "2rem", display: "grid", gap: "1.5rem" }}>
      <header>
        <h1>Trading Dashboard</h1>
        <p>Mocked overview — wire real-time data once services are available.</p>
      </header>

      <section>
        <h2>Open Positions</h2>
        <div style={{ display: "grid", gap: "1rem" }}>
          {samplePositions.map((position) => (
            <article
              key={position.id}
              style={{ border: "1px solid #1f2937", borderRadius: "0.75rem", padding: "1rem" }}
            >
              <h3>{position.asset}</h3>
              <p>
                {position.side} @ {position.entryPrice} — size {position.size}
              </p>
              <p>P&amp;L: {position.pnl}</p>
            </article>
          ))}
        </div>
      </section>

      <section>
        <h2>Bias Snapshot</h2>
        <ul>
          {sampleBias.map((bias) => (
            <li key={bias.asset}>
              <strong>{bias.asset}</strong>: {bias.value} (confidence {bias.confidence})
            </li>
          ))}
        </ul>
      </section>

      <section>
        <h2>Recent Whale Events</h2>
        <ul>
          {sampleWhaleEvents.map((event) => (
            <li key={event.txHash}>
              <span>{event.wallet}</span> {event.action} {event.amount} {event.asset}
              <br />
              <small>{event.timestamp}</small>
            </li>
          ))}
        </ul>
      </section>

      <footer>
        <Link href="/">Return home</Link>
      </footer>
    </main>
  );
}
