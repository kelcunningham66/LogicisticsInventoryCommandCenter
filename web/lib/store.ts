import { seedStore } from "./seed";
import type { Kpis, Sku, StockStatus, Store } from "./types";

declare global {
  var __logicisticsStore: Store | undefined;
}

function clone<T>(value: T): T {
  return JSON.parse(JSON.stringify(value)) as T;
}

export function getStore(): Store {
  if (!globalThis.__logicisticsStore) {
    globalThis.__logicisticsStore = clone(seedStore);
  }
  return globalThis.__logicisticsStore;
}

export function resetStore(): Store {
  globalThis.__logicisticsStore = clone(seedStore);
  return globalThis.__logicisticsStore;
}

export function available(sku: Sku): number {
  return Math.max(0, sku.onHand - sku.reserved);
}

export function statusFor(sku: Sku): StockStatus {
  const qty = available(sku);
  if (qty <= 0) return "stockout";
  if (qty < sku.reorderPoint * 0.25) return "critical";
  if (qty < sku.reorderPoint) return "low";
  return "healthy";
}

export function getState(): Store {
  return getStore();
}

export function getKpis(): Kpis {
  return computeKpis(getStore());
}

export function upsertSku(input: Partial<Sku> & { sku: string }): Sku {
  const store = getStore();
  const existing = store.skus.find((s) => s.sku === input.sku || s.id === input.id);
  if (existing) {
    Object.assign(existing, input);
    return existing;
  }
  const created: Sku = {
    id: input.id ?? `s-${Date.now()}`,
    sku: input.sku,
    name: input.name ?? input.sku,
    category: input.category ?? "Uncategorized",
    warehouse: input.warehouse ?? "DFW-01",
    bin: input.bin ?? "UNASSIGNED",
    onHand: input.onHand ?? 0,
    reserved: input.reserved ?? 0,
    reorderPoint: input.reorderPoint ?? 50,
    unitCost: input.unitCost ?? 0,
    velocity: input.velocity ?? "medium",
  };
  store.skus.unshift(created);
  return created;
}

export function computeKpis(store: Store): Kpis {
  const lowStock = store.skus.filter((s) => {
    const st = statusFor(s);
    return st === "low" || st === "critical";
  }).length;
  const stockouts = store.skus.filter((s) => statusFor(s) === "stockout").length;
  const onHandUnits = store.skus.reduce((n, s) => n + s.onHand, 0);
  const inventoryValue = store.skus.reduce((n, s) => n + s.onHand * s.unitCost, 0);
  const inbound = store.shipments.filter((s) => s.status !== "docked").length;
  const fillable = store.skus.filter((s) => available(s) > 0).length;

  return {
    skus: store.skus.length,
    onHandUnits,
    inventoryValue: Math.round(inventoryValue),
    fillRate: Math.round((fillable / store.skus.length) * 1000) / 10,
    lowStock,
    stockouts,
    inbound,
    exceptions: store.alerts.filter((a) => a.severity !== "info").length,
  };
}
