import { NextResponse } from "next/server";
import { updateTask } from "@/lib/mock-data";

type Params = {
  params: {
    taskId: string;
  };
};

export async function PATCH(request: Request, { params }: Params) {
  const payload = await request.json();
  const updated = updateTask(params.taskId, payload);
  if (!updated) {
    return NextResponse.json({ error: "Task not found" }, { status: 404 });
  }
  return NextResponse.json(updated);
}
