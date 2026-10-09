import Link from "next/link";

export default function HomePage() {
  return (
    <>
      <nav className="site-nav">
        <div className="brand">
          <span className="brand-mark">L</span>
          LOGICISTICS
        </div>
        <div className="nav-links">
          <a href="#product">Product</a>
          <a href="#ops">Ops</a>
          <Link href="/command">Command Center</Link>
          <Link className="btn small" href="/command">
            Launch live demo
          </Link>
        </div>
      </nav>

      <section className="hero">
        <div>
          <p className="kicker">INVENTORY · FREIGHT · EXCEPTIONS · AI</p>
          <h1>See every SKU. Move first.</h1>
          <p className="lede">
            Logicistics is an AI-powered inventory command center. It watches stock health,
            inbound freight, and warehouse exceptions so operators act before a line goes dark.
          </p>
          <div className="hero-actions">
            <Link className="btn" href="/command">
              Open command center
            </Link>
            <a className="btn ghost" href="#product">
              How it works
            </a>
          </div>
          <div className="stats">
            <div className="stat">
              <b>99.1%</b>
              <span>DEMO FILL RATE</span>
            </div>
            <div className="stat">
              <b>4</b>
              <span>NODES IN NETWORK</span>
            </div>
            <div className="stat">
              <b>&lt;2s</b>
              <span>OPERATOR ANSWERS</span>
            </div>
          </div>
        </div>
        <aside className="radar" aria-label="Live operations snapshot">
          <h3>LIVE NETWORK · DFW · ATL · ORD · LAX</h3>
          <div className="pulse-row">
            <span>
              <i className="dot crit" /> SEAL-NYL-500 stockout
            </span>
            <span className="mono muted">LAX-04</span>
          </div>
          <div className="pulse-row">
            <span>
              <i className="dot crit" /> Cold-chain gel reserved out
            </span>
            <span className="mono muted">DFW-01</span>
          </div>
          <div className="pulse-row">
            <span>
              <i className="dot warn" /> PO-10488 delayed 11h
            </span>
            <span className="mono muted">ATL-03</span>
          </div>
          <div className="pulse-row">
            <span>
              <i className="dot" /> Pallet inbound docked
            </span>
            <span className="mono muted">DFW-01</span>
          </div>
          <div className="pulse-row">
            <span>
              <i className="dot warn" /> Labels below reorder
            </span>
            <span className="mono muted">ORD-02</span>
          </div>
        </aside>
      </section>

      <section className="section" id="product">
        <p className="kicker">PRODUCT</p>
        <h2>A command surface, not a spreadsheet.</h2>
        <div className="grid-3">
          <article className="card">
            <h3>Stock truth</h3>
            <p>
              On-hand, reserved, and available by warehouse and bin. Reorder points and velocity
              drive status without a nightly batch job.
            </p>
          </article>
          <article className="card">
            <h3>Movement ledger</h3>
            <p>
              Receive, ship, and adjust in one feed. Every operator action writes an immutable
              event so interview demos stay honest and live.
            </p>
          </article>
          <article className="card">
            <h3>Operator copilot</h3>
            <p>
              Ask “what’s out of stock?” or a SKU code. The copilot reads live KPIs and tells you
              the next four moves — no API key required for the demo.
            </p>
          </article>
        </div>
      </section>

      <section className="section" id="ops">
        <p className="kicker">FOR INTERVIEWS</p>
        <h2>Run the live path.</h2>
        <div className="grid-3">
          <article className="card">
            <h3>1. Open the board</h3>
            <p>Start on Command Center. Call out fill rate, stockouts, and delayed POs.</p>
          </article>
          <article className="card">
            <h3>2. Ask the copilot</h3>
            <p>Type a question. The answer is generated from the same backend the tables use.</p>
          </article>
          <article className="card">
            <h3>3. Post a movement</h3>
            <p>Receive seals or ship wrap. Watch on-hand and the ledger update immediately.</p>
          </article>
        </div>
      </section>

      <footer className="footer">
        <span>LOGICISTICS · Inventory Command Center</span>
        <span className="mono">BLACK / WHITE / GREEN</span>
      </footer>
    </>
  );
}
