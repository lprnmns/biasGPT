import { useState } from "react";
import { sampleChatHistory } from "@/lib/sampleData";

export default function ChatPage() {
  const [messages, setMessages] = useState(sampleChatHistory);
  const [input, setInput] = useState("");

  const sendMessage = (event: React.FormEvent) => {
    event.preventDefault();
    if (!input.trim()) return;
    setMessages((prev) => [
      ...prev,
      { role: "user", content: input, citations: [], confidence: null }
    ]);
    setInput("");
  };

  return (
    <main style={{ padding: "2rem", maxWidth: "720px", margin: "0 auto" }}>
      <h1>Chat Assistant</h1>
      <p>Streaming mock UI — substitute websocket once backend is ready.</p>

      <section style={{ display: "grid", gap: "1rem", marginTop: "2rem" }}>
        {messages.map((message, index) => (
          <article
            key={index}
            style={{
              border: "1px solid #1f2937",
              borderRadius: "0.75rem",
              padding: "1rem",
              background: message.role === "assistant" ? "#111827" : "#0b132b"
            }}
          >
            <header style={{ fontWeight: "bold", marginBottom: "0.5rem" }}>
              {message.role === "assistant" ? "Assistant" : "You"}
            </header>
            <p>{message.content}</p>
            {message.citations && message.citations.length > 0 && (
              <footer>
                <h4>Citations</h4>
                <ul>
                  {message.citations.map((citation) => (
                    <li key={citation}>{citation}</li>
                  ))}
                </ul>
              </footer>
            )}
            {message.confidence !== null && (
              <p style={{ opacity: 0.7 }}>Confidence: {message.confidence}</p>
            )}
          </article>
        ))}
      </section>

      <form onSubmit={sendMessage} style={{ marginTop: "2rem", display: "flex", gap: "0.5rem" }}>
        <input
          value={input}
          onChange={(event) => setInput(event.target.value)}
          placeholder="Ask about whale activity"
          style={{ flex: 1, padding: "0.75rem", borderRadius: "0.5rem", border: "1px solid #1f2937" }}
        />
        <button type="submit" style={{ padding: "0.75rem 1.5rem" }}>
          Send
        </button>
      </form>
    </main>
  );
}
