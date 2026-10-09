"use client";

import Link from "next/link";
import { useCallback, useEffect, useMemo, useState } from "react";

type Status = "healthy" | "low" | "critical" | "stockout";

type State = {
  kpis: {
    skus: number;
    onHandUnits: number;
    inventoryValue: number;
    fillRate: number;
    lowStock: number;
    stockouts: number;
    inbound: number;
    exceptions: number;
  };
  skus: Array<{
    id: string;
    sku: string;
    name: string;
    category: string;
    warehouse: string;
    bin: string;
    onHand: number;
    reserved: number;
    available: number;
    reorderPoint: number;
    unitCost: number;
    velocity: string;
    status: Status;
  }>;
  movements: Array<{
    id: string;
    at: string;
    type: string;
    sku: string;
    name: string;
    qty: number;
    note: string;
  }>;
  shipments: Array<{
    id: string;
    po: string;
    supplier: string;
    eta: string;
    status: string;
    lines: number;
    value: number;
  }>;
  alerts: Array<{
    id: string;
    severity: string;
    title: string;
    detail: string;
    sku?: string;
    at: string;
  }>;
};

type Tab = "overview" | "inventory" | "inbound" | "exceptions";

export default function CommandPage() {
  const [state, setState] = useState<State | null>(null);
  const [tab, setTab] = useState<Tab>("overview");
  const [question, setQuestion] = useState("What should we do next?");
  const [messages, setMessages] = useState<{ role: "user" | "bot"; text: string }[]>([
    {
      role: "bot",
      text: "Operator online. I can brief stockouts, delayed POs, reorder priorities, or a SKU.",
    },
  ]);
  const [skuId, setSkuId] = useState("s5");
  const [qty, setQty] = useState(250);
  const [moveType, setMoveType] = useState("received");
  const [busy, setBusy] = useState(false);

  const load = useCallback(async () => {
    const res = await fetch("/api/state", { cache: "no-store" });
    setState(await res.json());
  }, []);

  useEffect(() => {
    load();
  }, [load]);

  const ask = async (e: React.FormEvent) => {
    e.preventDefault();
    const q = question.trim();
    if (!q) return;
    setMessages((m) => [...m, { role: "user", text: q }]);
    setQuestion("");
    const res = await fetch("/api/ai", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question: q }),
    });
    const data = await res.json();
    setMessages((m) => [...m, { role: "bot", text: data.answer }]);
  };

  const postMove = async (e: React.FormEvent) => {
    e.preventDefault();
    setBusy(true);
    await fetch("/api/movements", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ skuId, qty, type: moveType }),
    });
    setBusy(false);
    await load();
  };

  const reset = async () => {
    await fetch("/api/movements", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ action: "reset" }),
    });
    await load();
  };

  const clock = useMemo(() => new Date().toISOString().slice(0, 16).replace("T", " "), []);

  if (!state) {
    return (
      <div className="workspace">
        <p className="muted">Syncing network…</p>
      </div>
    );
  }

  return (
    <div className="shell">
      <aside className="side">
        <Link href="/" className="brand" style={{ marginBottom: 18 }}>
          <span className="brand-mark">L</span>
          LOGICISTICS
        </Link>
        <button className={`linkish ${tab === "overview" ? "active" : ""}`} onClick={() => setTab("overview")}>
          Overview
        </button>
        <button className={`linkish ${tab === "inventory" ? "active" : ""}`} onClick={() => setTab("inventory")}>
          Inventory
        </button>
        <button className={`linkish ${tab === "inbound" ? "active" : ""}`} onClick={() => setTab("inbound")}>
          Inbound
        </button>
        <button className={`linkish ${tab === "exceptions" ? "active" : ""}`} onClick={() => setTab("exceptions")}>
          Exceptions
        </button>
        <div style={{ flex: 1 }} />
        <button className="linkish" onClick={reset}>
          Reset demo data
        </button>
        <Link href="/">Marketing site</Link>
      </aside>

      <div>
        <header className="topbar">
          <div>
            <div className="live">
              <i className="dot" /> LIVE DEMO NETWORK
            </div>
            <p className="muted" style={{ fontSize: 12, marginTop: 4 }}>
              DFW-01 · ATL-03 · ORD-02 · LAX-04 · {clock}Z
            </p>
          </div>
          <div className="tabs">
            {(["overview", "inventory", "inbound", "exceptions"] as Tab[]).map((t) => (
              <button key={t} className={tab === t ? "on" : ""} onClick={() => setTab(t)}>
                {t}
              </button>
            ))}
          </div>
        </header>

        <main className="workspace">
          <section className="kpi-grid">
            <div className="kpi">
              <div className="label">Fill rate</div>
              <div className="value green">{state.kpis.fillRate}%</div>
            </div>
            <div className="kpi">
              <div className="label">On-hand value</div>
              <div className="value">${state.kpis.inventoryValue.toLocaleString()}</div>
            </div>
            <div className="kpi">
              <div className="label">Stockouts</div>
              <div className="value" style={{ color: state.kpis.stockouts ? "#ff5c5c" : "#3dff7a" }}>
                {state.kpis.stockouts}
              </div>
            </div>
            <div className="kpi">
              <div className="label">Exceptions</div>
              <div className="value">{state.kpis.exceptions}</div>
            </div>
          </section>

          {tab === "overview" && (
            <section className="split">
              <div className="panel">
                <h3>Needs attention</h3>
                {state.alerts.slice(0, 5).map((a) => (
                  <div className="alert" key={a.id}>
                    <div className="title">
                      <span className={`badge ${a.severity === "critical" ? "critical" : a.severity === "warning" ? "low" : "healthy"}`}>
                        {a.severity}
                      </span>{" "}
                      {a.title}
                    </div>
                    <p className="muted">{a.detail}</p>
                  </div>
                ))}
              </div>
              <div className="panel chat">
                <h3>Operator copilot</h3>
                <div className="chat-log">
                  {messages.map((m, i) => (
                    <div key={i} className={`bubble ${m.role === "user" ? "user" : "bot"}`}>
                      {m.text}
                    </div>
                  ))}
                </div>
                <form className="chat-form" onSubmit={ask}>
                  <input value={question} onChange={(e) => setQuestion(e.target.value)} placeholder="Ask the network…" />
                  <button className="btn small" type="submit">
                    Ask
                  </button>
                </form>
              </div>
            </section>
          )}

          {tab === "inventory" && (
            <section className="panel">
              <h3>Catalog · {state.kpis.skus} SKUs · {state.kpis.onHandUnits.toLocaleString()} units</h3>
              <form className="move-form" onSubmit={postMove}>
                <select value={skuId} onChange={(e) => setSkuId(e.target.value)}>
                  {state.skus.map((s) => (
                    <option key={s.id} value={s.id}>
                      {s.sku}
                    </option>
                  ))}
                </select>
                <select value={moveType} onChange={(e) => setMoveType(e.target.value)}>
                  <option value="received">Receive</option>
                  <option value="shipped">Ship</option>
                  <option value="adjusted">Adjust (+/−)</option>
                </select>
                <input type="number" value={qty} onChange={(e) => setQty(Number(e.target.value))} />
                <button className="btn small" disabled={busy} type="submit">
                  Post movement
                </button>
              </form>
              <table>
                <thead>
                  <tr>
                    <th>SKU</th>
                    <th>Item</th>
                    <th>Node</th>
                    <th>On hand</th>
                    <th>Avail</th>
                    <th>Status</th>
                  </tr>
                </thead>
                <tbody>
                  {state.skus.map((s) => (
                    <tr key={s.id}>
                      <td className="mono">{s.sku}</td>
                      <td>
                        {s.name}
                        <div className="muted">{s.category}</div>
                      </td>
                      <td className="mono">
                        {s.warehouse}
                        <div className="muted">{s.bin}</div>
                      </td>
                      <td>{s.onHand}</td>
                      <td>{s.available}</td>
                      <td>
                        <span className={`badge ${s.status}`}>{s.status}</span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </section>
          )}

          {tab === "inbound" && (
            <section className="split">
              <div className="panel">
                <h3>Purchase orders</h3>
                <table>
                  <thead>
                    <tr>
                      <th>PO</th>
                      <th>Supplier</th>
                      <th>Status</th>
                      <th>Value</th>
                    </tr>
                  </thead>
                  <tbody>
                    {state.shipments.map((s) => (
                      <tr key={s.id}>
                        <td className="mono">{s.po}</td>
                        <td>{s.supplier}</td>
                        <td>
                          <span className={`badge ${s.status === "delayed" ? "critical" : "healthy"}`}>{s.status}</span>
                        </td>
                        <td>${s.value.toLocaleString()}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
              <div className="panel">
                <h3>Ledger</h3>
                {state.movements.map((m) => (
                  <div className="alert" key={m.id}>
                    <div className="title">
                      <span className="badge healthy">{m.type}</span> {m.sku} · {m.qty}
                    </div>
                    <p className="muted">
                      {m.note} · {m.at.replace("T", " ").slice(0, 16)}
                    </p>
                  </div>
                ))}
              </div>
            </section>
          )}

          {tab === "exceptions" && (
            <section className="panel">
              <h3>Exception queue</h3>
              {state.alerts.map((a) => (
                <div className="alert" key={a.id}>
                  <div className="title">
                    <span className={`badge ${a.severity === "info" ? "healthy" : a.severity === "warning" ? "low" : "critical"}`}>
                      {a.severity}
                    </span>{" "}
                    {a.title}
                    {a.sku ? <span className="mono muted"> · {a.sku}</span> : null}
                  </div>
                  <p className="muted">{a.detail}</p>
                </div>
              ))}
            </section>
          )}
        </main>
      </div>
    </div>
  );
}
