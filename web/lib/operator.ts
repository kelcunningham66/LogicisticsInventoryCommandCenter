import { available, computeKpis, getStore, statusFor } from "./store";

export function answerOperator(question: string): string {
  const q = question.trim().toLowerCase();
  const store = getStore();
  const kpis = computeKpis(store);

  if (!q) {
    return "Ask about stockouts, inbound freight, a SKU, or what to do next.";
  }

  if (q.includes("stockout") || q.includes("out of stock") || q.includes("zero")) {
    const outs = store.skus.filter((s) => statusFor(s) === "stockout");
    if (!outs.length) return "No stockouts right now. Fill rate is holding.";
    return `Stockouts: ${outs.map((s) => `${s.sku} (${s.name} @ ${s.warehouse})`).join("; ")}. Expedite inbound and freeze non-critical allocations.`;
  }

  if (q.includes("reorder") || q.includes("buy") || q.includes("purchase")) {
    const needs = store.skus
      .filter((s) => statusFor(s) !== "healthy")
      .sort((a, b) => available(a) / a.reorderPoint - available(b) / b.reorderPoint)
      .slice(0, 4);
    return `Priority buys: ${needs
      .map((s) => `${s.sku} — on-hand ${s.onHand}, reorder ${s.reorderPoint}`)
      .join("; ")}.`;
  }

  if (q.includes("delay") || q.includes("inbound") || q.includes("po-") || q.includes("shipment")) {
    const delayed = store.shipments.filter((s) => s.status === "delayed");
    const next = store.shipments.filter((s) => s.status === "in-transit");
    return `${delayed.length} delayed PO(s)${
      delayed.length ? `: ${delayed.map((s) => `${s.po} ${s.supplier}`).join(", ")}` : ""
    }. In-transit: ${next.map((s) => `${s.po} ETA ${s.eta.slice(0, 10)}`).join("; ") || "none"}.`;
  }

  const skuHit = store.skus.find(
    (s) => q.includes(s.sku.toLowerCase()) || q.includes(s.name.toLowerCase().slice(0, 10)),
  );
  if (skuHit) {
    return `${skuHit.sku} ${skuHit.name}: ${skuHit.onHand} on hand, ${skuHit.reserved} reserved, ${available(skuHit)} available at ${skuHit.warehouse} ${skuHit.bin}. Status ${statusFor(skuHit)}.`;
  }

  if (q.includes("kpi") || q.includes("health") || q.includes("summary") || q.includes("status")) {
    return `Network: ${kpis.skus} SKUs, ${kpis.onHandUnits.toLocaleString()} units, $${kpis.inventoryValue.toLocaleString()} on hand. Fill rate ${kpis.fillRate}%. ${kpis.stockouts} stockout(s), ${kpis.lowStock} below reorder, ${kpis.exceptions} exception(s).`;
  }

  if (q.includes("next") || q.includes("do") || q.includes("priority") || q.includes("risk")) {
    return "1) Recover SEAL-NYL-500 at LAX-04 so trailers can close. 2) Expedite PO-10488 cells or ATL pack idles. 3) Protect cold-chain gel (COLD-GEL-5L) until CryoPack lands. 4) Replenish thermal labels at ORD-02 before the parcel surge misses SLA.";
  }

  return `I read ${kpis.exceptions} live exceptions and ${kpis.stockouts} stockouts. Try: "What's out of stock?", "What should we reorder?", or a SKU like WRAP-72-CLR.`;
}
