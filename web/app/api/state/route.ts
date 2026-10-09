import { NextResponse } from "next/server";
import { computeKpis, getStore, statusFor } from "@/lib/store";

export const dynamic = "force-dynamic";

export function GET() {
  const store = getStore();
  return NextResponse.json({
    kpis: computeKpis(store),
    skus: store.skus.map((s) => ({ ...s, status: statusFor(s), available: s.onHand - s.reserved })),
    movements: store.movements,
    shipments: store.shipments,
    alerts: store.alerts,
  });
}
