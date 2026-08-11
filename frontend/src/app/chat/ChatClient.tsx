"use client";

import { FormEvent, useState } from "react";

type ChatMessage = {
  role: "user" | "worker";
  content: string;
  escalated?: boolean;
  intent?: string;
};

// MVP: a fixed demo customer id until real session auth (plan Section 16).
const CUSTOMER_ID = process.env.NEXT_PUBLIC_CUSTOMER_ID || "demo-customer-1";

export default function ChatClient() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [conversationId, setConversationId] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function send(e: FormEvent) {
    e.preventDefault();
    const text = input.trim();
    if (!text || loading) return;
    setInput("");
    setMessages((m) => [...m, { role: "user", content: text }]);
    setLoading(true);
    try {
      const resp = await fetch("/api/chat", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-Customer-Id": CUSTOMER_ID,
        },
        body: JSON.stringify({ conversation_id: conversationId, message: text }),
      });
      if (!resp.ok) throw new Error(`request failed: ${resp.status}`);
      const data = await resp.json();
      setConversationId(data.conversation_id);
      setMessages((m) => [
        ...m,
        {
          role: "worker",
          content: data.reply,
          escalated: data.escalated,
          intent: data.intent,
        },
      ]);
    } catch (err) {
      setMessages((m) => [
        ...m,
        { role: "worker", content: "Sorry, something went wrong. Please try again." },
      ]);
      console.error(err);
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="app">
      <h1>AI Support Worker</h1>
      <p className="subtitle">Ask about returns, passwords, orders, or hours.</p>
      <div className="chatbox">
        {messages.length === 0 && (
          <p style={{ color: "#888", margin: "auto", textAlign: "center" }}>
            Start a conversation — I answer from approved knowledge only.
          </p>
        )}
        {messages.map((m, i) => (
          <div key={i} className={`msg ${m.role}`}>
            {m.escalated && <span className="badge escalated">escalated to human</span>}
            {m.intent === "create_ticket" && !m.escalated && (
              <span className="badge created">ticket created</span>
            )}
            <div>{m.content}</div>
          </div>
        ))}
      </div>
      <form className="form" onSubmit={send}>
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Type your question…"
          disabled={loading}
        />
        <button type="submit" disabled={loading || !input.trim()}>
          {loading ? "…" : "Send"}
        </button>
      </form>
    </main>
  );
}
