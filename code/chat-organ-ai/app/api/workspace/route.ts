import { NextResponse } from "next/server";
import { getWorkspaceSnapshot } from "@/lib/mock-data";

export async function GET() {
  const snapshot = getWorkspaceSnapshot();
  return NextResponse.json(snapshot);
}
