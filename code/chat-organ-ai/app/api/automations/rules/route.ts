import { NextResponse } from "next/server";
import { listAutomationRules } from "@/lib/mock-data";

export async function GET() {
  return NextResponse.json(listAutomationRules());
}
