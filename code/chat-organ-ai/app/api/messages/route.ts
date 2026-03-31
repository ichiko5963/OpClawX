import { NextResponse } from "next/server";
import { createMessage, listMessages } from "@/lib/mock-data";

export async function GET() {
  return NextResponse.json(listMessages());
}

export async function POST(request: Request) {
  const body = await request.json();
  if (!body?.content) {
    return NextResponse.json(
      { error: "content is required" },
      { status: 400 }
    );
  }
  const message = createMessage({
    author: body.author ?? "あなた (Owner)",
    role: body.role ?? "Owner",
    department: body.department ?? "運営",
    content: body.content,
  });
  return NextResponse.json(message, { status: 201 });
}
