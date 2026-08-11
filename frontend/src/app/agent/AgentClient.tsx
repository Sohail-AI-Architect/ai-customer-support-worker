"use client";

import { useCallback, useEffect, useState } from "react";

type Escalation = {
  id: string;
  conversation_id: string;
  reason: string;
  context: string;
  status: string;
  created_at: string | null;
};

type Approval = {
  id: string;
  conversation_id: string;
  proposed_action: string;
  payload: Record<string, unknown>;
  status: string;
  created_at: string | null;
};

// MVP: a fixed demo agent id until real session auth (plan Section 16).
const AGENT_USER_ID = process.env.NEXT_PUBLIC_AGENT_USER_ID || "demo-agent-1";
const DATA_HEADERS = { "Content-Type": "application/json", "X-User-Id": AGENT_USER_ID };

export default function AgentClient() {
  const [escalations, setEscalations] = useState<Escalation[]>([]);
  const [approvals, setApprovals] = useState<Approval[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const [escRes, apprRes] = await Promise.all([
        fetch("/api/agent/escalations", { headers: { "X-User-Id": AGENT_USER_ID } }),
        fetch("/api/agent/approvals", { headers: { "X-User-Id": AGENT_USER_ID } }),
      ]);
      if (!escRes.ok || !apprRes.ok) throw new Error("request failed");
      setEscalations(await escRes.json());
      setApprovals(await apprRes.json());
    } catch (err) {
      setError("Unable to load the agent queue. Check the agent user id and backend.");
      console.error(err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    load();
  }, [load]);

  async function resolve(id: string) {
    try {
      const resp = await fetch(`/api/agent/escalations/${id}/resolve`, {
        method: "POST",
        headers: { "X-User-Id": AGENT_USER_ID },
      });
      if (!resp.ok) throw new Error(`request failed: ${resp.status}`);
      await load();
    } catch (err) {
      setError("Unable to mark escalation resolved.");
      console.error(err);
    }
  }

  async function decide(id: string, decision: "approved" | "denied") {
    try {
      const resp = await fetch(`/api/agent/approvals/${id}/decision`, {
        method: "POST",
        headers: DATA_HEADERS,
        body: JSON.stringify({ decision }),
      });
      if (!resp.ok) throw new Error(`request failed: ${resp.status}`);
      await load();
    } catch (err) {
      setError("Unable to record the approval decision.");
      console.error(err);
    }
  }

  return (
    <main className="app">
      <h1>Agent Queue</h1>
      <p className="subtitle">
        Escalations handed to a human, and sensitive actions awaiting approval.
      </p>

      {error && <p style={{ color: "#b91c1c" }}>{error}</p>}

      {loading ? (
        <p style={{ color: "#888" }}>Loading…</p>
      ) : (
        <>
          <section>
            <h2>Approvals</h2>
            {approvals.length === 0 ? (
              <p style={{ color: "#888" }}>No pending approvals.</p>
            ) : (
              approvals.map((a) => (
                <div key={a.id} className="card">
                  <div className="card-head">
                    <span className="badge approvals">{a.proposed_action}</span>
                  </div>
                  <div className="card-body">
                    {a.payload.message
                      ? `Customer request: ${a.payload.message}`
                      : "A sensitive action has been proposed."}
                  </div>
                  <div className="card-actions">
                    <button
                      onClick={() => decide(a.id, "approved")}
                      className="btn-approve"
                    >
                      Approve
                    </button>
                    <button
                      onClick={() => decide(a.id, "denied")}
                      className="btn-deny"
                    >
                      Deny
                    </button>
                  </div>
                </div>
              ))
            )}
          </section>

          <section>
            <h2>Escalations</h2>
            {escalations.length === 0 ? (
              <p style={{ color: "#888" }}>No open escalations.</p>
            ) : (
              escalations.map((e) => (
                <div key={e.id} className="card">
                  <div className="card-head">
                    <span className="badge escalated">{e.reason}</span>
                    <button onClick={() => resolve(e.id)} className="btn-resolve">
                      Mark resolved
                    </button>
                  </div>
                  <div className="card-body">{e.context}</div>
                </div>
              ))
            )}
          </section>
        </>
      )}
    </main>
  );
}
