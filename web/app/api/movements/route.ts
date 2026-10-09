import { NextResponse } from "next/server";
import { getStore, resetStore, statusFor } from "@/lib/store";
import type { MovementType } from "@/lib/types";

export const dynamic = "force-dynamic";

export async function POST(request: Request) {
  const body = (await request.json()) as {
    action?: string;
    skuId?: string;
    qty?: number;
    type?: MovementType;
  };

  if (body.action === "reset") {
    resetStore();
    return NextResponse.json({ ok: true });
  }

  const store = getStore();
  const sku = store.skus.find((s) => s.id === body.skuId || s.sku === body.skuId);
  if (!sku || !body.qty || !body.type) {
    return NextResponse.json({ error: "skuId, qty, and type are required" }, { status: 400 });
  }

  const qty = Math.abs(Math.round(body.qty));
  if (body.type === "received") sku.onHand += qty;
  if (body.type === "shipped") sku.onHand = Math.max(0, sku.onHand - qty);
  if (body.type === "adjusted") sku.onHand = Math.max(0, sku.onHand + Math.round(body.qty));

  store.movements.unshift({
    id: `m-${Date.now()}`,
    at: new Date().toISOString(),
    type: body.type,
    sku: sku.sku,
    name: sku.name,
    qty: body.type === "adjusted" ? Math.round(body.qty) : qty,
    from: body.type === "shipped" ? sku.warehouse : undefined,
    to: body.type === "received" ? sku.warehouse : undefined,
    note: "Operator action from command center",
  });

  return NextResponse.json({ ok: true, sku: { ...sku, status: statusFor(sku) } });
}
