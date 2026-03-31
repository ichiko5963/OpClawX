import { NextResponse } from "next/server";
import { listTasks } from "@/lib/mock-data";
import type { TaskStatus } from "@/lib/types/workspace";

export async function GET(request: Request) {
  const { searchParams } = new URL(request.url);
  const status = searchParams.get("status") as TaskStatus | null;
  return NextResponse.json(listTasks(status ?? undefined));
}
