import { NextResponse } from "next/server";
import { answerOperator } from "@/lib/operator";

export const dynamic = "force-dynamic";

export async function POST(request: Request) {
  const body = (await request.json()) as { question?: string };
  const answer = answerOperator(body.question ?? "");
  return NextResponse.json({ answer });
}
