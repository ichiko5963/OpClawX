import { NextResponse } from "next/server";
import { addTask, recordMinutes } from "@/lib/mock-data";

export async function POST(request: Request) {
  const body = await request.json();

  if (!body?.meetingTitle) {
    return NextResponse.json(
      { error: "meetingTitle is required" },
      { status: 400 }
    );
  }

  const minutes = recordMinutes({
    meetingTitle: body.meetingTitle,
    transcriptUrl: body.transcriptUrl,
    agenda: body.agenda ?? [],
    decisions: body.decisions ?? [],
    actions: body.actions ?? [],
  });

  minutes.actions.forEach((action, index) => {
    addTask({
      id: `${minutes.id}-task-${index}`,
      title: action.title,
      status: "todo",
      priority: "medium",
      dueAt: action.dueCandidates[0] ?? "",
      assignee: action.assigneeCandidates[0] ?? "未確定",
      department: "未設定",
      tags: ["Minutes"],
      reminders: ["3日前", "1日前", "当日AM"],
    });
  });

  return NextResponse.json(
    {
      minutes,
      actionsSpawned: minutes.actions.length,
    },
    { status: 201 }
  );
}
