import { NextResponse } from "next/server";
import { getStore, upsertSku } from "@/lib/store";

export const dynamic = "force-dynamic";

export async function GET() {
  return NextResponse.json(getStore().skus);
}

export async function POST(request: Request) {
  const body = await request.json();
  if (!body.sku) return NextResponse.json({ error: "sku required" }, { status: 400 });
  return NextResponse.json(upsertSku(body));
}
